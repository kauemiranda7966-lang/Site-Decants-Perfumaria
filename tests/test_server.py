import json
import tempfile
import threading
import unittest
from http import cookiejar
from pathlib import Path
from urllib import error, parse, request

import server


class TestHTTPServer(server.http.server.ThreadingHTTPServer):
    daemon_threads = True


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_path = server.DB_PATH
        self.original_upload_dir = server.UPLOAD_DIR
        self.original_secret_key = server.SECRET_KEY
        server.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        server.UPLOAD_DIR = Path(self.temp_dir.name) / "uploads"
        server.SECRET_KEY = "test-secret-key-with-at-least-32-characters"
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
        server.SECRET_KEY = self.original_secret_key
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

    def test_checkout_logs_customer_in_and_keeps_order_available(self):
        payload = {
            "customer": {
                "name": "Cliente Checkout",
                "email": "checkout@example.com",
                "phone": "(88) 98765-4321",
                "address": "Rua Teste, 123",
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
                self.assertEqual(self.request_status(asset), 200)

        server.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (server.UPLOAD_DIR / "produto.png").write_bytes(b"image")
        self.assertEqual(self.request_status("/img/uploads/produto.png"), 200)

    def test_shipping_threshold_is_inclusive(self):
        paid_query = parse.urlencode({"postalCode": "60000000", "productAmount": "299.99"})
        _, paid_quote = self.request_json(f"/api/shipping/quote?{paid_query}")
        self.assertEqual(paid_quote["shippingAmount"], server.SHIPPING_FEE)

        free_query = parse.urlencode({"postalCode": "60000000", "productAmount": "300.00"})
        _, free_quote = self.request_json(f"/api/shipping/quote?{free_query}")
        self.assertEqual(free_quote["shippingAmount"], 0)

    def test_checkout_contract_requires_and_accepts_postal_code(self):
        payload = {
            "customer": {
                "name": "Joao Silva",
                "email": "cliente@example.com",
                "phone": "88987654321",
                "address": "Rua Teste, 123",
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

    def test_mercado_pago_owner_mismatch_is_rejected(self):
        original_collector_id = server.MERCADO_PAGO_COLLECTOR_ID
        try:
            server.MERCADO_PAGO_COLLECTOR_ID = "123"
            with self.assertRaisesRegex(ValueError, "collector_id"):
                server.validate_mercado_pago_owner({"collector_id": 456})
        finally:
            server.MERCADO_PAGO_COLLECTOR_ID = original_collector_id


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
