import json
import hashlib
import hmac
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http import cookiejar
from pathlib import Path
from urllib import error, parse, request
from unittest import mock

import server
import decants_handler


class TestHTTPServer(server.DecantsHTTPServer):
    pass


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = server.DB_PATH
        self.original_upload_dir = server.UPLOAD_DIR
        self.original_private_upload_dir = server.PRIVATE_UPLOAD_DIR
        self.original_secret_key = server.SECRET_KEY
        self.original_whatsapp_reservation_minutes = server.WHATSAPP_RESERVATION_MINUTES
        server.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        server.UPLOAD_DIR = Path(self.temp_dir.name) / "uploads"
        server.PRIVATE_UPLOAD_DIR = Path(self.temp_dir.name) / "private-uploads"
        server.SECRET_KEY = "test-secret-key-with-at-least-32-characters"
        server.WHATSAPP_RESERVATION_MINUTES = 30
        server.init_db()
        self.httpd = TestHTTPServer(("127.0.0.1", 0), server.DecantsHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.httpd.server_port}"
        self.cookie_jar = cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cookie_jar))

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        server.DB_PATH = self.original_db_path
        server.UPLOAD_DIR = self.original_upload_dir
        server.PRIVATE_UPLOAD_DIR = self.original_private_upload_dir
        server.SECRET_KEY = self.original_secret_key
        server.WHATSAPP_RESERVATION_MINUTES = self.original_whatsapp_reservation_minutes
        self.temp_dir.cleanup()

    def request_json(self, path, method="GET", payload=None, headers=None):
        body = None
        request_headers = dict(headers or {})
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        with self.opener.open(
            request.Request(self.base_url + path, data=body, headers=request_headers, method=method),
            timeout=5,
        ) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def request_status(self, path, method="GET"):
        try:
            with request.urlopen(
                request.Request(self.base_url + path, method=method),
                timeout=5,
            ) as response:
                return response.status
        except error.HTTPError as exc:
            status = exc.code
            exc.close()
            return status

    def insert_order(self):
        with server.connect_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO orders (
                    reference, customer_name, customer_email, customer_phone,
                    customer_address, total, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "DEC1234ABCD",
                    "Cliente Teste",
                    "cliente@example.com",
                    "88999999999",
                    "Rua Teste, 123",
                    59.99,
                    "to_separate",
                ),
            )
            conn.execute(
                """
                INSERT INTO order_items (
                    order_id, product_id, product_name, volume, quantity, unit_price, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (cursor.lastrowid, 1, "Dior Sauvage", 5, 1, 59.99, 59.99),
            )

    def test_invalid_lead_returns_once_and_server_stays_available(self):
        with self.assertRaises(error.HTTPError) as context:
            self.request_json(
                "/api/leads",
                method="POST",
                payload={"nome": "Teste", "email": "invalido", "telefone": "1"},
            )
        self.assertEqual(context.exception.code, 400)
        context.exception.close()

        status, products = self.request_json("/api/products")
        self.assertEqual(status, 200)
        self.assertGreater(len(products), 0)

    def test_customer_orders_require_reference_and_matching_contact(self):
        self.insert_order()

        with self.assertRaises(error.HTTPError) as context:
            self.request_json("/api/customer/orders?contact=cliente%40example.com")
        self.assertEqual(context.exception.code, 400)
        context.exception.close()

        wrong_query = parse.urlencode(
            {"reference": "DEC1234ABCD", "contact": "outra@example.com"}
        )
        _, wrong = self.request_json(f"/api/customer/orders?{wrong_query}")
        self.assertEqual(wrong["orders"], [])

        correct_query = parse.urlencode(
            {"reference": "DEC1234ABCD", "contact": "cliente@example.com"}
        )
        _, correct = self.request_json(f"/api/customer/orders?{correct_query}")
        self.assertEqual(len(correct["orders"]), 1)
        self.assertEqual(correct["orders"][0]["reference"], "DEC1234ABCD")

        with self.assertRaises(error.HTTPError) as context:
            self.request_json("/api/orders/DEC1234ABCD")
        self.assertEqual(context.exception.code, 400)
        context.exception.close()

        detail_query = parse.urlencode({"contact": "cliente@example.com"})
        _, detail = self.request_json(f"/api/orders/DEC1234ABCD?{detail_query}")
        self.assertEqual(detail["reference"], "DEC1234ABCD")

    def test_customer_can_login_with_email_and_phone_and_list_orders(self):
        self.insert_order()
        _, session = self.request_json("/api/customer/session")
        self.assertFalse(session["authenticated"])

        _, login = self.request_json(
            "/api/customer/login",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={"email": "cliente@example.com", "phone": "(88) 99999-9999"},
        )
        self.assertTrue(login["ok"])

        _, orders = self.request_json("/api/customer/orders")
        self.assertEqual(len(orders["orders"]), 1)
        self.assertEqual(orders["orders"][0]["reference"], "DEC1234ABCD")

    def test_public_privacy_request_creates_protocol(self):
        _, session = self.request_json("/api/customer/session")
        status, result = self.request_json(
            "/api/customer/requests",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={
                "requestType": "privacy",
                "name": "Titular Teste",
                "email": "titular@example.com",
                "phone": "(88) 99999-9999",
                "category": "access",
                "details": "Gostaria de receber uma copia dos meus dados pessoais.",
            },
        )
        self.assertEqual(status, 201)
        self.assertTrue(result["protocol"].startswith("LGPD"))
        with server.connect_db() as conn:
            row = conn.execute(
                "SELECT request_type, category, status FROM service_requests WHERE protocol = ?",
                (result["protocol"],),
            ).fetchone()
        self.assertEqual(dict(row), {"request_type": "privacy", "category": "access", "status": "pending"})

    def test_admin_login_loads_all_dashboard_resources(self):
        with (
            mock.patch.object(decants_handler, "ADMIN_USER", "admin@example.com"),
            mock.patch.object(decants_handler, "ADMIN_PASSWORD", "SenhaTeste123!"),
            mock.patch.object(decants_handler, "ADMIN_PASSWORD_HASH", ""),
            mock.patch.object(decants_handler, "IS_PRODUCTION", False),
        ):
            _, session = self.request_json("/api/session")
            status, login = self.request_json(
                "/api/login",
                method="POST",
                headers={"X-CSRF-Token": session["csrfToken"]},
                payload={"user": "admin@example.com", "password": "SenhaTeste123!"},
            )
            self.assertEqual(status, 200)
            self.assertTrue(login["ok"])

            for path in (
                "/api/admin/dashboard",
                "/api/products",
                "/api/admin/orders",
                "/api/admin/customers",
                "/api/admin/requests",
                "/api/admin/logs",
            ):
                resource_status, _ = self.request_json(path)
                self.assertEqual(resource_status, 200, path)

    def test_customer_creates_and_lists_return_request_for_own_order(self):
        self.insert_order()
        _, session = self.request_json("/api/customer/session")
        self.request_json(
            "/api/customer/login",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={"email": "cliente@example.com", "phone": "(88) 99999-9999"},
        )
        status, created = self.request_json(
            "/api/customer/requests",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={
                "requestType": "return",
                "orderReference": "DEC1234ABCD",
                "category": "vazamento",
                "reason": "Frasco com vazamento",
                "details": "O frasco chegou com liquido dentro da embalagem.",
                "acceptedPolicy": True,
            },
        )
        self.assertEqual(status, 201)
        self.assertTrue(created["protocol"].startswith("DEV"))

        _, result = self.request_json("/api/customer/requests")
        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["requests"][0]["order_reference"], "DEC1234ABCD")
        self.assertEqual(result["requests"][0]["category"], "vazamento")

    def test_customer_cannot_create_return_for_another_order(self):
        self.insert_order()
        _, session = self.request_json("/api/customer/session")
        self.request_json(
            "/api/customer/login",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={"email": "cliente@example.com", "phone": "(88) 99999-9999"},
        )
        with self.assertRaises(error.HTTPError) as context:
            self.request_json(
                "/api/customer/requests",
                method="POST",
                headers={"X-CSRF-Token": session["csrfToken"]},
                payload={
                    "requestType": "return",
                    "orderReference": "DECFFFFFFFF",
                    "category": "outro",
                    "reason": "Outro pedido",
                    "details": "Tentativa de acessar um pedido que nao pertence ao cliente.",
                    "acceptedPolicy": True,
                },
            )
        self.assertEqual(context.exception.code, 404)
        context.exception.close()

    def test_customer_can_request_cancellation_before_separation(self):
        self.insert_order()
        _, session = self.request_json("/api/customer/session")
        self.request_json(
            "/api/customer/login",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={"email": "cliente@example.com", "phone": "(88) 99999-9999"},
        )
        status, created = self.request_json(
            "/api/customer/requests",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={
                "requestType": "return",
                "orderReference": "DEC1234ABCD",
                "category": "cancelamento_antes_separacao",
                "reason": "Desisti antes da separacao",
                "details": "Solicito o cancelamento antes de o pedido ser separado.",
                "acceptedPolicy": True,
            },
        )
        self.assertEqual(status, 201)
        self.assertTrue(created["protocol"].startswith("DEV"))

    def test_customer_cannot_use_pre_separation_cancellation_after_separation(self):
        self.insert_order()
        with server.connect_db() as conn:
            conn.execute("UPDATE orders SET status = 'separated' WHERE reference = 'DEC1234ABCD'")
        _, session = self.request_json("/api/customer/session")
        self.request_json(
            "/api/customer/login",
            method="POST",
            headers={"X-CSRF-Token": session["csrfToken"]},
            payload={"email": "cliente@example.com", "phone": "(88) 99999-9999"},
        )
        with self.assertRaises(error.HTTPError) as context:
            self.request_json(
                "/api/customer/requests",
                method="POST",
                headers={"X-CSRF-Token": session["csrfToken"]},
                payload={
                    "requestType": "return",
                    "orderReference": "DEC1234ABCD",
                    "category": "cancelamento_antes_separacao",
                    "reason": "Pedido ja separado",
                    "details": "Tentativa de cancelar depois de o pedido ser separado.",
                    "acceptedPolicy": True,
                },
            )
        self.assertEqual(context.exception.code, 409)
        context.exception.close()

    def test_public_business_endpoint_exposes_only_configured_public_fields(self):
        _, business = self.request_json("/api/public/business")
        self.assertEqual(business["tradeName"], server.BUSINESS_TRADE_NAME)
        self.assertIn("formalized", business)

    def test_retention_policy_anonymizes_old_orders_and_deletes_old_leads(self):
        self.insert_order()
        with server.connect_db() as conn:
            conn.execute(
                "UPDATE orders SET created_at = datetime('now', '-2000 days')"
            )
            conn.execute(
                """
                INSERT INTO leads (nome, email, telefone, created_at)
                VALUES ('Lead Antigo', 'antigo@example.com', '88999999999', datetime('now', '-800 days'))
                """
            )
        server.apply_retention_policy()
        with server.connect_db() as conn:
            order = conn.execute("SELECT * FROM orders LIMIT 1").fetchone()
            lead_count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        self.assertTrue(order["customer_email"].startswith("anonimizado-"))
        self.assertEqual(order["customer_address"], "")
        self.assertEqual(lead_count, 0)

    def test_mercado_pago_refund_uses_idempotency_key(self):
        original_token = server.MERCADO_PAGO_ACCESS_TOKEN
        server.MERCADO_PAGO_ACCESS_TOKEN = "token-test"

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({"id": 987, "status": "approved"}).encode()

        try:
            with mock.patch.object(server.request, "urlopen", return_value=FakeResponse()) as urlopen:
                result = server.refund_mercado_pago_payment("123", "refund-protocol")
            sent_request = urlopen.call_args.args[0]
            self.assertEqual(sent_request.full_url, "https://api.mercadopago.com/v1/payments/123/refunds")
            self.assertEqual(sent_request.headers["X-idempotency-key"], "refund-protocol")
            self.assertEqual(result["id"], 987)
        finally:
            server.MERCADO_PAGO_ACCESS_TOKEN = original_token

    def test_mercado_pago_refund_requires_explicit_approval(self):
        original_token = server.MERCADO_PAGO_ACCESS_TOKEN
        server.MERCADO_PAGO_ACCESS_TOKEN = "token-test"

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({"id": 987, "status": "pending"}).encode()

        try:
            with mock.patch.object(server.request, "urlopen", return_value=FakeResponse()):
                with self.assertRaisesRegex(ValueError, "nao confirmou"):
                    server.refund_mercado_pago_payment("123", "refund-protocol")
        finally:
            server.MERCADO_PAGO_ACCESS_TOKEN = original_token

    def test_mercado_pago_webhook_rejects_expired_signature(self):
        original_secret = server.MERCADO_PAGO_WEBHOOK_SECRET
        original_max_age = server.MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS
        try:
            server.MERCADO_PAGO_WEBHOOK_SECRET = "webhook-secret"
            server.MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS = 300
            timestamp = str(int(time.time()) - 301)
            request_id = "request-123"
            payment_id = "456"
            manifest = f"id:{payment_id};request-id:{request_id};ts:{timestamp};"
            signature = hmac.new(
                server.MERCADO_PAGO_WEBHOOK_SECRET.encode(),
                manifest.encode(),
                hashlib.sha256,
            ).hexdigest()
            headers = {
                "x-signature": f"ts={timestamp},v1={signature}",
                "x-request-id": request_id,
            }
            self.assertFalse(
                server.verify_mercado_pago_webhook_signature(
                    headers, payment_id, {"data.id": [payment_id]}
                )
            )
        finally:
            server.MERCADO_PAGO_WEBHOOK_SECRET = original_secret
            server.MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS = original_max_age

    def test_antifraud_webhook_blocks_order_and_is_idempotent(self):
        self.insert_order()
        with server.connect_db() as conn:
            conn.execute(
                """
                UPDATE orders
                SET payment_id = 'PAY123', payment_method = 'credit_card'
                WHERE reference = 'DEC1234ABCD'
                """
            )

        event_id = "PAY123"
        request_id = "risk-request-1"
        timestamp = str(int(time.time()))
        original_secret = server.MERCADO_PAGO_WEBHOOK_SECRET
        server.MERCADO_PAGO_WEBHOOK_SECRET = "webhook-secret"
        manifest = f"id:{event_id.lower()};request-id:{request_id};ts:{timestamp};"
        signature = hmac.new(
            server.MERCADO_PAGO_WEBHOOK_SECRET.encode(),
            manifest.encode(),
            hashlib.sha256,
        ).hexdigest()
        headers = {
            "X-Signature": f"ts={timestamp},v1={signature}",
            "X-Request-Id": request_id,
        }
        path = f"/api/payments/webhook?data.id={event_id}&type=stop_delivery_op_wh"
        payment = {
            "id": event_id,
            "external_reference": "DEC1234ABCD",
            "transaction_amount": 59.99,
            "currency_id": "BRL",
        }
        try:
            with (
                mock.patch.object(decants_handler, "fetch_mercado_pago_payment", return_value=payment),
                mock.patch.object(decants_handler, "send_admin_payment_risk_notification") as notify,
            ):
                for _ in range(2):
                    status, result = self.request_json(
                        path,
                        method="POST",
                        headers=headers,
                        payload={
                            "type": "stop_delivery_op_wh",
                            "data": {"id": event_id},
                        },
                    )
                    self.assertEqual(status, 200)
                    self.assertTrue(result["blocked"])
                notify.assert_called_once()
        finally:
            server.MERCADO_PAGO_WEBHOOK_SECRET = original_secret

        with server.connect_db() as conn:
            order = conn.execute(
                """
                SELECT status, payment_risk_status
                FROM orders WHERE reference = 'DEC1234ABCD'
                """
            ).fetchone()
            alert_count = conn.execute("SELECT COUNT(*) FROM payment_alerts").fetchone()[0]
        self.assertEqual(order["status"], "risk_review")
        self.assertEqual(order["payment_risk_status"], "fraud_alert")
        self.assertEqual(alert_count, 1)

    def test_checkout_logs_customer_in_and_keeps_order_available(self):
        payload = {
            "customer": {
                "name": "Cliente Checkout",
                "email": "checkout@example.com",
                "phone": "(88) 98765-4321",
                "address": "Rua Teste, 123",
                "document": "52998224725",
                "postalCode": "60000-000",
            },
            "items": [
                {
                    "productId": 1,
                    "productName": "Dior Sauvage",
                    "volume": 5,
                    "quantity": 1,
                }
            ],
            "paymentMethod": "whatsapp",
        }
        status, checkout = self.request_json("/api/checkout", method="POST", payload=payload)
        self.assertEqual(status, 201)

        _, orders = self.request_json("/api/customer/orders")
        self.assertEqual(len(orders["orders"]), 1)
        self.assertEqual(orders["orders"][0]["reference"], checkout["reference"])

    def test_sqlite_connections_enable_concurrency_and_integrity_pragmas(self):
        with server.connect_db() as conn:
            self.assertEqual(conn.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(
                conn.execute("PRAGMA busy_timeout").fetchone()[0],
                server.SQLITE_BUSY_TIMEOUT_SECONDS * 1000,
            )

    def test_sqlite_backup_is_created_and_readable(self):
        original_backup_dir = server.SQLITE_BACKUP_DIR
        server.SQLITE_BACKUP_DIR = Path(self.temp_dir.name) / "backups"
        try:
            backup_path = server.backup_database()
            self.assertTrue(backup_path.exists())
            with server.sqlite3.connect(backup_path) as conn:
                self.assertEqual(conn.execute("PRAGMA quick_check").fetchone()[0], "ok")
                self.assertGreater(conn.execute("SELECT COUNT(*) FROM products").fetchone()[0], 0)
        finally:
            server.SQLITE_BACKUP_DIR = original_backup_dir

    def test_concurrent_checkouts_do_not_oversell_stock(self):
        with server.connect_db() as conn:
            conn.execute("UPDATE products SET estoque = 1 WHERE id = 1")

        barrier = threading.Barrier(2)
        customer_names = {1: "Cliente Um", 2: "Cliente Dois"}

        def checkout(index):
            payload = {
                "customer": {
                    "name": customer_names[index],
                    "email": f"cliente{index}@example.com",
                    "phone": f"8898765432{index}",
                    "address": "Rua Teste, 123",
                    "document": "52998224725",
                    "postalCode": "60000-000",
                },
                "items": [{"productId": 1, "volume": 5, "quantity": 1}],
                "paymentMethod": "whatsapp",
            }
            body = json.dumps(payload).encode("utf-8")
            barrier.wait(timeout=5)
            try:
                with request.urlopen(
                    request.Request(
                        self.base_url + "/api/checkout",
                        data=body,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    ),
                    timeout=10,
                ) as response:
                    return response.status
            except error.HTTPError as exc:
                status = exc.code
                exc.close()
                return status

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = sorted(executor.map(checkout, (1, 2)))

        self.assertEqual(statuses, [201, 400])
        with server.connect_db() as conn:
            self.assertEqual(
                conn.execute("SELECT estoque FROM products WHERE id = 1").fetchone()["estoque"],
                0,
            )
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 1)

    def test_stock_reservation_rolls_back_all_items_on_failure(self):
        with server.connect_db() as conn:
            conn.execute("UPDATE products SET estoque = 2 WHERE id = 1")
            conn.execute("UPDATE products SET estoque = 0 WHERE id = 2")
            cursor = conn.execute(
                """
                INSERT INTO orders (
                    reference, customer_name, customer_email, customer_phone,
                    customer_address, total, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "DECROLLBACK",
                    "Cliente Rollback",
                    "rollback@example.com",
                    "88999999998",
                    "Rua Teste, 123",
                    100,
                    "pending",
                ),
            )
            order_id = cursor.lastrowid
            conn.executemany(
                """
                INSERT INTO order_items (
                    order_id, product_id, product_name, volume, quantity, unit_price, subtotal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (order_id, 1, "Produto 1", 5, 1, 50, 50),
                    (order_id, 2, "Produto 2", 5, 1, 50, 50),
                ),
            )

        with self.assertRaisesRegex(ValueError, "Estoque insuficiente"):
            with server.connect_db() as conn:
                server.begin_immediate(conn)
                server.reserve_order_stock(conn, order_id)

        with server.connect_db() as conn:
            stocks = conn.execute(
                "SELECT id, estoque FROM products WHERE id IN (1, 2) ORDER BY id"
            ).fetchall()
            order = conn.execute(
                "SELECT stock_reserved FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
        self.assertEqual([row["estoque"] for row in stocks], [2, 0])
        self.assertEqual(order["stock_reserved"], 0)

    def test_admin_session_is_stored_and_can_be_revoked(self):
        secret = "s" * 32
        signed_session = server.create_admin_session(server.connect_db, secret, 3600)

        with server.connect_db() as conn:
            count = conn.execute("SELECT COUNT(*) FROM admin_sessions").fetchone()[0]
        self.assertEqual(count, 1)
        self.assertTrue(server.verify_admin_session(server.connect_db, signed_session, secret))

        server.revoke_admin_session(server.connect_db, signed_session, secret)
        self.assertFalse(server.verify_admin_session(server.connect_db, signed_session, secret))

    def test_private_files_are_not_served(self):
        for path in ("/.env", "/server.py", "/data/decants.sqlite3", "/.gitignore"):
            with self.subTest(path=path, method="GET"):
                self.assertEqual(self.request_status(path), 404)
            with self.subTest(path=path, method="HEAD"):
                self.assertEqual(self.request_status(path, method="HEAD"), 404)

        self.assertEqual(self.request_status("/index.html"), 200)
        self.assertEqual(self.request_status("/css/style.css"), 200)
        with request.urlopen(self.base_url + "/index.html", timeout=5) as response:
            self.assertEqual(response.headers.get("Cache-Control"), "no-cache, must-revalidate")
            csp = response.headers.get("Content-Security-Policy", "")
            self.assertIn("default-src 'self'", csp)
            self.assertIn("object-src 'none'", csp)
            self.assertEqual(
                response.headers.get("Permissions-Policy"),
                "camera=(), microphone=(), geolocation=()",
            )
        for page in (
            "/politica-de-privacidade.html",
            "/trocas-e-devolucoes.html",
            "/termos-de-compra.html",
            "/prazos-de-entrega.html",
        ):
            with self.subTest(page=page):
                self.assertEqual(self.request_status(page), 200)

        for asset in (
            "/css/base.css",
            "/css/legal.css",
            "/css/store.css",
            "/css/store-layout.css",
            "/css/catalog.css",
            "/css/dialogs.css",
            "/css/marketing.css",
            "/css/effects.css",
            "/css/product-modal.css",
            "/css/responsive.css",
            "/js/store-core.js",
            "/js/store-catalog.js",
            "/js/store-product.js",
            "/js/store-cart.js",
            "/js/store-checkout.js",
            "/js/store-navigation.js",
            "/js/store-init.js",
        ):
            with self.subTest(asset=asset):
                with request.urlopen(self.base_url + asset, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(
                        response.headers.get("Cache-Control"),
                        "public, max-age=604800",
                    )

        server.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (server.UPLOAD_DIR / "produto.png").write_bytes(b"image")
        with request.urlopen(self.base_url + "/img/uploads/produto.png", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get("Cache-Control"), "public, max-age=3600")

        with request.urlopen(self.base_url + "/api/products", timeout=5) as response:
            self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_shipping_threshold_is_inclusive(self):
        paid_query = parse.urlencode({"postalCode": "60000000", "productAmount": "299.99"})
        _, paid_quote = self.request_json(f"/api/shipping/quote?{paid_query}")
        self.assertEqual(paid_quote["shippingAmount"], server.SHIPPING_FEE)

        free_query = parse.urlencode({"postalCode": "60000000", "productAmount": "300.00"})
        _, free_quote = self.request_json(f"/api/shipping/quote?{free_query}")
        self.assertEqual(free_quote["shippingAmount"], 0)

    def test_price_parser_accepts_brazilian_and_international_formats(self):
        cases = {
            "49,90": 49.90,
            "49.90": 49.90,
            "1.234,56": 1234.56,
            "1,234.56": 1234.56,
            "R$ 59,99": 59.99,
            49.90: 49.90,
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(server.parse_price(value), expected)

    def test_expired_whatsapp_order_releases_reserved_stock(self):
        payload = {
            "customer": {
                "name": "Cliente WhatsApp",
                "email": "whatsapp@example.com",
                "phone": "(88) 98765-4321",
                "address": "Rua Teste, 123",
                "document": "52998224725",
                "postalCode": "60000-000",
            },
            "items": [
                {
                    "productId": 1,
                    "productName": "Dior Sauvage",
                    "volume": 5,
                    "quantity": 2,
                }
            ],
            "paymentMethod": "whatsapp",
        }
        with server.connect_db() as conn:
            initial_stock = conn.execute(
                "SELECT estoque FROM products WHERE id = 1"
            ).fetchone()["estoque"]

        _, checkout = self.request_json("/api/checkout", method="POST", payload=payload)
        with server.connect_db() as conn:
            reserved_stock = conn.execute(
                "SELECT estoque FROM products WHERE id = 1"
            ).fetchone()["estoque"]
            conn.execute(
                """
                UPDATE orders
                SET updated_at = datetime('now', '-31 minutes')
                WHERE reference = ?
                """,
                (checkout["reference"],),
            )
        self.assertEqual(reserved_stock, initial_stock - 2)

        self.request_json("/api/products")

        with server.connect_db() as conn:
            restored_stock = conn.execute(
                "SELECT estoque FROM products WHERE id = 1"
            ).fetchone()["estoque"]
            order = conn.execute(
                "SELECT id, status, stock_reserved FROM orders WHERE reference = ?",
                (checkout["reference"],),
            ).fetchone()
            history = conn.execute(
                "SELECT new_status FROM order_history WHERE order_id = ? ORDER BY id DESC LIMIT 1",
                (order["id"],),
            ).fetchone()

        self.assertEqual(restored_stock, initial_stock)
        self.assertEqual(order["status"], "expired")
        self.assertEqual(order["stock_reserved"], 0)
        self.assertEqual(history["new_status"], "expired")

    def test_checkout_contract_requires_and_accepts_postal_code(self):
        payload = {
            "customer": {
                "name": "Joao Silva",
                "email": "cliente@example.com",
                "phone": "88987654321",
                "address": "Rua Teste, 123",
                "document": "52998224725",
            },
            "items": [
                {
                    "productId": 1,
                    "productName": "Dior Sauvage",
                    "volume": 5,
                    "quantity": 1,
                }
            ],
            "paymentMethod": "whatsapp",
        }
        with self.assertRaisesRegex(ValueError, "CEP"):
            server.normalize_checkout(payload)

        payload["customer"]["postalCode"] = "60000-000"
        normalized = server.normalize_checkout(payload)
        self.assertEqual(normalized["customer"]["postal_code"], "60000000")
        self.assertEqual(normalized["customer"]["document"], "52998224725")

    def test_shipping_kit_pdf_contains_two_pages(self):
        order = {
            "reference": "DEC1234ABCD",
            "customer_name": "Joao Silva",
            "customer_phone": "88987654321",
            "customer_document": "52998224725",
            "customer_address": "Rua Teste, 123, Centro, Sao Paulo SP",
            "customer_postal_code": "01001000",
            "total": 59.99,
        }
        items = [
            {
                "product_name": "Dior Sauvage",
                "volume": 5,
                "quantity": 1,
                "unit_price": 59.99,
                "subtotal": 59.99,
            }
        ]
        original = (
            server.BUSINESS_LEGAL_NAME,
            server.BUSINESS_TAX_ID,
            server.BUSINESS_ADDRESS,
            server.BUSINESS_POSTAL_CODE,
        )
        try:
            server.BUSINESS_LEGAL_NAME = "Decants Perfumaria LTDA"
            server.BUSINESS_TAX_ID = "11222333000181"
            server.BUSINESS_ADDRESS = "Rua da Loja, 100, Centro, Fortaleza CE"
            server.BUSINESS_POSTAL_CODE = "60000000"
            pdf = server.build_shipping_label_pdf(order, items)
        finally:
            (
                server.BUSINESS_LEGAL_NAME,
                server.BUSINESS_TAX_ID,
                server.BUSINESS_ADDRESS,
                server.BUSINESS_POSTAL_CODE,
            ) = original
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"/Count 2", pdf)

    def test_mercado_pago_owner_mismatch_is_rejected(self):
        original_collector_id = server.MERCADO_PAGO_COLLECTOR_ID
        try:
            server.MERCADO_PAGO_COLLECTOR_ID = "123"
            with self.assertRaisesRegex(ValueError, "collector_id"):
                server.validate_mercado_pago_owner({"collector_id": 456})
        finally:
            server.MERCADO_PAGO_COLLECTOR_ID = original_collector_id

    def test_mercado_pago_payment_requires_exact_amount_and_brl(self):
        order = {
            "reference": "DEC1234ABCD",
            "customer_email": "cliente@example.com",
            "total": 59.99,
        }
        payment = {
            "external_reference": "DEC1234ABCD",
            "payer": {"email": "cliente@example.com"},
            "transaction_amount": 59.99,
            "currency_id": "BRL",
        }
        server.validate_payment_for_order(payment, order)

        with self.assertRaisesRegex(ValueError, "valor"):
            server.validate_payment_for_order({**payment, "transaction_amount": 0}, order)
        with self.assertRaisesRegex(ValueError, "Moeda"):
            server.validate_payment_for_order({**payment, "currency_id": "USD"}, order)


class RuntimeConfigTestCase(unittest.TestCase):
    def test_production_rejects_missing_admin_configuration(self):
        original = (
            server.ADMIN_USER,
            server.ADMIN_PASSWORD,
            server.ADMIN_PASSWORD_HASH,
            server.SECRET_KEY,
            server.IS_PRODUCTION,
        )
        try:
            server.ADMIN_USER = ""
            server.ADMIN_PASSWORD = ""
            server.ADMIN_PASSWORD_HASH = ""
            server.SECRET_KEY = ""
            server.IS_PRODUCTION = True
            with self.assertRaises(RuntimeError):
                server.validate_runtime_config()
        finally:
            (
                server.ADMIN_USER,
                server.ADMIN_PASSWORD,
                server.ADMIN_PASSWORD_HASH,
                server.SECRET_KEY,
                server.IS_PRODUCTION,
            ) = original


if __name__ == "__main__":
    unittest.main()
