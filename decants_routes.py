import re
from urllib import parse

import decants_app as app


class DecantsRoutingMixin:
    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.is_admin_page_request():
            self.serve_admin_app()
            return

        path = parse.urlparse(self.path).path
        match = re.match(r"/api/admin/requests/(\d+)/attachments/(\d+)$", path)
        if match:
            if self.require_auth():
                self.handle_request_attachment(
                    int(match.group(1)), int(match.group(2)), admin=True
                )
            return
        match = re.match(r"/api/admin/requests/(\d+)/reverse-label\.pdf$", path)
        if match:
            if self.require_auth():
                self.handle_reverse_label(int(match.group(1)), admin=True)
            return
        match = re.match(r"/api/admin/requests/(\d+)$", path)
        if match:
            if self.require_auth():
                self.handle_admin_request_detail(int(match.group(1)))
            return

        authenticated_routes = (
            ("/api/admin/requests", self.handle_admin_requests),
            ("/api/admin/dashboard", self.handle_admin_dashboard),
            ("/api/admin/orders", self.handle_admin_orders),
            ("/api/admin/customers", self.handle_admin_customers),
            ("/api/admin/logs", self.handle_admin_logs),
        )
        label_match = re.match(r"/api/admin/orders/(\d+)/label\.pdf", self.path)
        if label_match:
            if self.require_auth():
                self.handle_admin_shipping_label(int(label_match.group(1)))
            return
        if self.path.startswith("/api/admin/orders/"):
            if self.require_auth():
                self.handle_admin_order_detail()
            return
        for prefix, handler in authenticated_routes:
            if self.path.startswith(prefix):
                if self.require_auth():
                    handler()
                return

        public_routes = (
            ("/api/products", self.handle_get_products),
            ("/api/shipping/quote", self.handle_shipping_quote),
            ("/api/customer/session", self.handle_customer_session),
            ("/api/customer/orders", self.handle_customer_orders),
            ("/api/customer/requests", self.handle_customer_requests),
            ("/api/public/business", self.handle_public_business),
            ("/api/orders/", self.handle_get_order),
            ("/api/session", self.handle_session),
        )
        match = re.match(r"/api/customer/requests/(\d+)/attachments/(\d+)$", path)
        if match:
            self.handle_request_attachment(
                int(match.group(1)), int(match.group(2)), admin=False
            )
            return
        match = re.match(r"/api/customer/requests/(\d+)/reverse-label\.pdf$", path)
        if match:
            self.handle_reverse_label(int(match.group(1)), admin=False)
            return
        for prefix, handler in public_routes:
            if self.path.startswith(prefix):
                handler()
                return
        self.serve_public_static()

    def do_HEAD(self):
        self.serve_public_static(head_only=True)

    def do_POST(self):
        path = parse.urlparse(self.path).path
        if self.path.startswith("/api/leads"):
            self.handle_create_lead()
            return
        if self.path.startswith("/api/login"):
            if self.require_csrf():
                self.handle_login()
            return
        if self.path.startswith("/api/logout"):
            if self.require_csrf():
                self.handle_logout()
            return
        if self.path.startswith("/api/customer/login"):
            if self.require_csrf():
                self.handle_customer_login()
            return
        if self.path.startswith("/api/customer/logout"):
            if self.require_csrf():
                self.handle_customer_logout()
            return

        match = re.match(r"/api/customer/requests/(\d+)/attachments$", path)
        if match:
            if self.require_csrf():
                self.handle_customer_request_attachment(int(match.group(1)))
            return
        if self.path.startswith("/api/customer/requests"):
            if self.require_csrf():
                self.handle_create_customer_request()
            return
        match = re.match(r"/api/admin/requests/(\d+)/refund$", path)
        if match:
            if self.require_auth() and self.require_csrf():
                self.handle_admin_request_refund(int(match.group(1)))
            return
        if self.path.startswith("/api/checkout"):
            self.handle_checkout()
            return
        if self.path.startswith("/api/payments/webhook"):
            self.handle_payment_webhook()
            return
        if self.path.startswith("/api/admin/upload"):
            if self.require_auth() and self.require_csrf():
                self.handle_admin_upload()
            return
        if self.path.startswith("/api/products"):
            if not self.require_auth() or not self.require_csrf():
                return
            product = app.normalize_product(self.read_json())
            with app.connect_db() as conn:
                position = conn.execute(
                    "SELECT COALESCE(MAX(position), -1) + 1 FROM products"
                ).fetchone()[0]
                app.insert_product(conn, product, position)
                product_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self.log_admin_action(
                "product_create", "products", str(product_id), product["nome"]
            )
            self.send_json({"ok": True}, status=201)
            return
        self.send_error(404)

    def do_PUT(self):
        path = parse.urlparse(self.path).path
        match = re.match(r"/api/admin/requests/(\d+)$", path)
        if match:
            if self.require_auth() and self.require_csrf():
                self.handle_admin_update_request(int(match.group(1)))
            return
        match = re.match(r"/api/admin/orders/(\d+)/status", self.path)
        if match:
            if self.require_auth() and self.require_csrf():
                self.handle_admin_update_order_status(int(match.group(1)))
            return

        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth() or not self.require_csrf():
            return
        product_id = int(match.group(1))
        product = app.normalize_product(self.read_json())
        with app.connect_db() as conn:
            result = conn.execute(
                """
                UPDATE products SET
                    nome = ?, categoria = ?, img = ?, estoque = ?,
                    preco5 = ?, preco10 = ?, promocao = ?,
                    precoPromocional5 = ?, precoPromocional10 = ?,
                    destaque = ?, selo = ?, chamada = ?
                WHERE id = ?
                """,
                (
                    product["nome"],
                    product["categoria"],
                    product["img"],
                    product["estoque"],
                    product["preco5"],
                    product["preco10"],
                    product["promocao"],
                    product["precoPromocional5"],
                    product["precoPromocional10"],
                    product["destaque"],
                    product["selo"],
                    product["chamada"],
                    product_id,
                ),
            )
            if result.rowcount == 0:
                self.send_error(404)
                return
        self.log_admin_action(
            "product_update", "products", str(product_id), product["nome"]
        )
        self.send_json({"ok": True})

    def do_DELETE(self):
        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth() or not self.require_csrf():
            return
        with app.connect_db() as conn:
            result = conn.execute(
                "DELETE FROM products WHERE id = ?", (int(match.group(1)),)
            )
            if result.rowcount == 0:
                self.send_error(404)
                return
        self.log_admin_action("product_delete", "products", match.group(1), "")
        self.send_json({"ok": True})
