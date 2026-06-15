import decants_app as app
from decants_app import *

class DecantsHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    PUBLIC_FILES = {
        "/index.html",
        "/produtos.html",
        "/carrinho.html",
        "/contatos.html",
        "/meus-pedidos.html",
        "/politica-de-privacidade.html",
        "/trocas-e-devolucoes.html",
        "/termos-de-compra.html",
        "/prazos-de-entrega.html",
    }
    PUBLIC_EXTENSIONS = {
        "/css/": {".css"},
        "/js/": {".js"},
        "/img/": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"},
    }

    #TRANSLATE_PATH
    def translate_path(self, path):
        path = unquote(path.split("?", 1)[0].split("#", 1)[0])
        if path.startswith("/img/uploads/"):
            filename = Path(path).name
            return str(app.UPLOAD_DIR / filename)
        parts = [part for part in path.split("/") if part and part not in {".", ".."}]
        return str(ROOT.joinpath(*parts))

    def is_public_static_request(self):
        path = parse.urlparse(self.path).path
        if path == "/":
            return True
        if path in self.PUBLIC_FILES:
            return True
        suffix = Path(path).suffix.lower()
        return any(
            path.startswith(directory) and suffix in extensions
            for directory, extensions in self.PUBLIC_EXTENSIONS.items()
        )

    def serve_public_static(self, head_only=False):
        if not self.is_public_static_request():
            self.send_error(404)
            return
        if parse.urlparse(self.path).path == "/":
            self.path = "/index.html"
        if head_only:
            super().do_HEAD()
        else:
            super().do_GET()

    #END_HEADERS
    def end_headers(self):
        path = parse.urlparse(self.path).path
        suffix = Path(path).suffix.lower()
        if path == "/" or path in self.PUBLIC_FILES or path.startswith(("/login", "/dashboard", "/produtos", "/pedidos", "/clientes", "/solicitacoes", "/logs")):
            self.send_header("Cache-Control", "no-cache, must-revalidate")
        elif path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        elif path.startswith("/img/uploads/"):
            self.send_header("Cache-Control", "public, max-age=3600")
        elif suffix in {".css", ".js"}:
            self.send_header("Cache-Control", "public, max-age=604800")
        elif suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}:
            self.send_header("Cache-Control", "public, max-age=2592000")
        self.add_cors_headers()
        self.send_header("Content-Security-Policy", self.content_security_policy())
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        super().end_headers()

    def content_security_policy(self):
        directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "script-src 'self'",
            "script-src-attr 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: blob:",
            "connect-src 'self'",
            "frame-src 'none'",
            "manifest-src 'self'",
        ]
        if IS_PRODUCTION:
            directives.append("upgrade-insecure-requests")
        return "; ".join(directives)

    #ADD_CORS_HEADERS
    def add_cors_headers(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        if origin not in ADMIN_ALLOWED_ORIGINS:
            return

        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Vary", "Origin")

    #DO_OPTIONS
    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    #DO_GET
    def do_GET(self):
        if self.is_admin_page_request():
            self.serve_admin_app()
            return
        admin_attachment_match = re.match(r"/api/admin/requests/(\d+)/attachments/(\d+)$", parse.urlparse(self.path).path)
        if admin_attachment_match:
            if not self.require_auth():
                return
            self.handle_request_attachment(
                int(admin_attachment_match.group(1)),
                int(admin_attachment_match.group(2)),
                admin=True,
            )
            return
        admin_reverse_match = re.match(r"/api/admin/requests/(\d+)/reverse-label\.pdf$", parse.urlparse(self.path).path)
        if admin_reverse_match:
            if not self.require_auth():
                return
            self.handle_reverse_label(int(admin_reverse_match.group(1)), admin=True)
            return
        admin_request_match = re.match(r"/api/admin/requests/(\d+)$", parse.urlparse(self.path).path)
        if admin_request_match:
            if not self.require_auth():
                return
            self.handle_admin_request_detail(int(admin_request_match.group(1)))
            return
        if self.path.startswith("/api/admin/requests"):
            if not self.require_auth():
                return
            self.handle_admin_requests()
            return
        if self.path.startswith("/api/admin/dashboard"):
            if not self.require_auth():
                return
            self.handle_admin_dashboard()
            return
        label_match = re.match(r"/api/admin/orders/(\d+)/label\.pdf", self.path)
        if label_match:
            if not self.require_auth():
                return
            self.handle_admin_shipping_label(int(label_match.group(1)))
            return
        if self.path.startswith("/api/admin/orders/"):
            if not self.require_auth():
                return
            self.handle_admin_order_detail()
            return
        if self.path.startswith("/api/admin/orders"):
            if not self.require_auth():
                return
            self.handle_admin_orders()
            return
        if self.path.startswith("/api/admin/customers"):
            if not self.require_auth():
                return
            self.handle_admin_customers()
            return
        if self.path.startswith("/api/admin/logs"):
            if not self.require_auth():
                return
            self.handle_admin_logs()
            return
        if self.path.startswith("/api/products"):
            self.handle_get_products()
            return
        if self.path.startswith("/api/shipping/quote"):
            self.handle_shipping_quote()
            return
        if self.path.startswith("/api/customer/session"):
            self.handle_customer_session()
            return
        if self.path.startswith("/api/customer/orders"):
            self.handle_customer_orders()
            return
        customer_attachment_match = re.match(r"/api/customer/requests/(\d+)/attachments/(\d+)$", parse.urlparse(self.path).path)
        if customer_attachment_match:
            self.handle_request_attachment(
                int(customer_attachment_match.group(1)),
                int(customer_attachment_match.group(2)),
                admin=False,
            )
            return
        customer_reverse_match = re.match(r"/api/customer/requests/(\d+)/reverse-label\.pdf$", parse.urlparse(self.path).path)
        if customer_reverse_match:
            self.handle_reverse_label(int(customer_reverse_match.group(1)), admin=False)
            return
        if self.path.startswith("/api/customer/requests"):
            self.handle_customer_requests()
            return
        if self.path.startswith("/api/public/business"):
            self.handle_public_business()
            return
        if self.path.startswith("/api/orders/"):
            self.handle_get_order()
            return
        if self.path.startswith("/api/session"):
            self.handle_session()
            return
        self.serve_public_static()

    def do_HEAD(self):
        self.serve_public_static(head_only=True)

    #DO_POST
    def do_POST(self):
        if self.path.startswith("/api/leads"):
            self.handle_create_lead()
            return
        if self.path.startswith("/api/login"):
            if not self.require_csrf():
                return
            self.handle_login()
            return
        if self.path.startswith("/api/logout"):
            if not self.require_csrf():
                return
            self.handle_logout()
            return
        if self.path.startswith("/api/customer/login"):
            if not self.require_csrf():
                return
            self.handle_customer_login()
            return
        if self.path.startswith("/api/customer/logout"):
            if not self.require_csrf():
                return
            self.handle_customer_logout()
            return
        attachment_match = re.match(r"/api/customer/requests/(\d+)/attachments$", parse.urlparse(self.path).path)
        if attachment_match:
            if not self.require_csrf():
                return
            self.handle_customer_request_attachment(int(attachment_match.group(1)))
            return
        if self.path.startswith("/api/customer/requests"):
            if not self.require_csrf():
                return
            self.handle_create_customer_request()
            return
        refund_match = re.match(r"/api/admin/requests/(\d+)/refund$", parse.urlparse(self.path).path)
        if refund_match:
            if not self.require_auth() or not self.require_csrf():
                return
            self.handle_admin_request_refund(int(refund_match.group(1)))
            return
        if self.path.startswith("/api/checkout"):
            self.handle_checkout()
            return
        if self.path.startswith("/api/payments/webhook"):
            self.handle_payment_webhook()
            return
        if self.path.startswith("/api/admin/upload"):
            if not self.require_auth():
                return
            if not self.require_csrf():
                return
            self.handle_admin_upload()
            return
        if self.path.startswith("/api/products"):
            if not self.require_auth():
                return
            if not self.require_csrf():
                return
            payload = self.read_json()
            product = normalize_product(payload)
            with connect_db() as conn:
                cursor = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM products")
                position = cursor.fetchone()[0]
                insert_product(conn, product, position)
                product_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self.log_admin_action("product_create", "products", str(product_id), product["nome"])
            self.send_json({"ok": True}, status=201)
            return
        self.send_error(404)

    #DO_PUT
    def do_PUT(self):
        request_match = re.match(r"/api/admin/requests/(\d+)$", parse.urlparse(self.path).path)
        if request_match:
            if not self.require_auth() or not self.require_csrf():
                return
            self.handle_admin_update_request(int(request_match.group(1)))
            return
        order_match = re.match(r"/api/admin/orders/(\d+)/status", self.path)
        if order_match:
            if not self.require_auth():
                return
            if not self.require_csrf():
                return
            self.handle_admin_update_order_status(int(order_match.group(1)))
            return

        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth():
            return
        if not self.require_csrf():
            return
        product_id = int(match.group(1))
        product = normalize_product(self.read_json())
        with connect_db() as conn:
            result = conn.execute(
                """
                UPDATE products SET
                    nome = ?, categoria = ?, img = ?, estoque = ?, preco5 = ?, preco10 = ?,
                    promocao = ?, precoPromocional5 = ?, precoPromocional10 = ?,
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
        self.log_admin_action("product_update", "products", str(product_id), product["nome"])
        self.send_json({"ok": True})

    #DO_DELETE
    def do_DELETE(self):
        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth():
            return
        if not self.require_csrf():
            return
        with connect_db() as conn:
            result = conn.execute("DELETE FROM products WHERE id = ?", (int(match.group(1)),))
            if result.rowcount == 0:
                self.send_error(404)
                return
        self.log_admin_action("product_delete", "products", match.group(1), "")
        self.send_json({"ok": True})

    #IS_ADMIN_HOST
    def is_admin_host(self):
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        return host in ADMIN_HOSTS or host.startswith("localhost") or host.startswith("127.0.0.1")

    #IS_ADMIN_PAGE_REQUEST
    def is_admin_page_request(self):
        if not self.is_admin_host():
            return False
        path = parse.urlparse(self.path).path
        return path in {"/login", "/dashboard", "/produtos", "/pedidos", "/clientes", "/solicitacoes", "/logs"}

    #SERVE_ADMIN_APP
    def serve_admin_app(self):
        path = ROOT / "admin.html"
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    #HANDLE_ADMIN_DASHBOARD
    def handle_admin_dashboard(self):
        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            metrics = conn.execute(
                """
                SELECT
                    SUM(CASE WHEN status IN ('approved', 'paid', 'to_separate', 'separated', 'delivered', 'completed') THEN total ELSE 0 END) AS total_sales,
                    COUNT(*) AS total_orders,
                    SUM(CASE WHEN status IN ('approved', 'paid', 'to_separate', 'separated', 'delivered', 'completed') THEN total ELSE 0 END) AS paid_sales
                FROM orders
                """
            ).fetchone()
            product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            customers = conn.execute("SELECT COUNT(DISTINCT customer_email) FROM orders").fetchone()[0]
            stock_value_rows = conn.execute("SELECT estoque, preco5, preco10, promocao, precoPromocional5, precoPromocional10 FROM products").fetchall()
            recent_orders = conn.execute(
                """
                SELECT id, reference, customer_name, total, status, created_at
                FROM orders ORDER BY created_at DESC LIMIT 6
                """
            ).fetchall()

        stock_value = sum(product_price(row, 10) * int(row["estoque"] or 0) for row in stock_value_rows)
        self.send_json(
            {
                "totalSales": round(float(metrics["total_sales"] or 0), 2),
                "paidSales": round(float(metrics["paid_sales"] or 0), 2),
                "totalOrders": int(metrics["total_orders"] or 0),
                "productCount": product_count,
                "customerCount": customers,
                "stockValue": round(stock_value, 2),
                "recentOrders": [dict(row) for row in recent_orders],
            }
        )

    #HANDLE_ADMIN_ORDERS
    def handle_admin_orders(self):
        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            rows = conn.execute(
                """
                SELECT id, reference, customer_name, customer_email, customer_phone,
                       product_amount, shipping_amount, total, status, payment_method,
                       payment_risk_status, payment_risk_reason, created_at, updated_at
                FROM orders ORDER BY created_at DESC
                """
            ).fetchall()
        self.send_json([dict(row) for row in rows])

    #HANDLE_CUSTOMER_ORDERS
    def handle_customer_orders(self):
        customer = self.get_customer_session()
        if customer:
            self.send_customer_orders(
                "LOWER(customer_email) = ? AND customer_phone = ?",
                [customer["email"], customer["phone"]],
            )
            return

        query = parse.parse_qs(parse.urlparse(self.path).query)
        reference = str(query.get("reference", [""])[0]).strip().upper()
        contact = str(query.get("contact", [""])[0]).strip()
        email = contact.lower()
        phone = re.sub(r"\D+", "", contact)

        if not re.fullmatch(r"DEC[A-F0-9]{8}", reference):
            self.send_json({"error": "Informe um numero de pedido valido."}, status=400)
            return
        if not contact or (not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) and len(phone) < 10):
            self.send_json({"error": "Informe o e-mail ou WhatsApp usado nesse pedido."}, status=400)
            return

        where = "reference = ? AND LOWER(customer_email) = ?"
        params = [reference, email]
        if len(phone) >= 10:
            where = "reference = ? AND customer_phone = ?"
            params = [reference, phone]

        self.send_customer_orders(where, params, limit=1)

    def send_customer_orders(self, where, params, limit=None):
        limit_sql = "LIMIT 1" if limit == 1 else ""
        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            orders = conn.execute(
                f"""
                SELECT id, reference, total, status, payment_url, whatsapp_url, created_at, updated_at
                FROM orders
                WHERE {where}
                ORDER BY created_at DESC
                {limit_sql}
                """,
                params,
            ).fetchall()
            order_ids = [row["id"] for row in orders]
            items_by_order = {order_id: [] for order_id in order_ids}
            if order_ids:
                placeholders = ",".join("?" for _ in order_ids)
                items = conn.execute(
                    f"""
                    SELECT order_id, product_name, volume, quantity, unit_price, subtotal
                    FROM order_items
                    WHERE order_id IN ({placeholders})
                    ORDER BY id
                    """,
                    order_ids,
                ).fetchall()
                for item in items:
                    item_data = dict(item)
                    items_by_order[item["order_id"]].append(
                        {key: value for key, value in item_data.items() if key != "order_id"}
                    )

        payload = []
        for order in orders:
            data = dict(order)
            data.pop("id", None)
            data["items"] = items_by_order.get(order["id"], [])
            payload.append(data)
        self.send_json({"orders": payload})

    def handle_customer_session(self):
        customer = self.get_customer_session()
        csrf = self.get_cookie(CSRF_COOKIE) or create_csrf_token()
        self.send_json(
            {
                "authenticated": bool(customer),
                "email": customer["email"] if customer else "",
                "phone": customer["phone"] if customer else "",
                "csrfToken": csrf,
            },
            headers=[
                (
                    "Set-Cookie",
                    f"{CSRF_COOKIE}={csrf}; {self.cookie_same_site()}; Path=/; Max-Age={CUSTOMER_SESSION_MAX_AGE}",
                )
            ],
        )

    def handle_customer_login(self):
        payload = self.read_json()
        email = str(payload.get("email", "")).strip().lower()
        phone = re.sub(r"\D+", "", str(payload.get("phone", "")))
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(phone) < 10:
            self.send_json({"error": "Informe o e-mail e o WhatsApp usados na compra."}, status=400)
            return

        with connect_db() as conn:
            exists = conn.execute(
                """
                SELECT 1 FROM orders
                WHERE LOWER(customer_email) = ? AND customer_phone = ?
                LIMIT 1
                """,
                (email, phone),
            ).fetchone()
        if not exists:
            self.send_json(
                {"error": "Nao encontramos pedidos com esse e-mail e WhatsApp."},
                status=401,
            )
            return

        signed_session = create_customer_session(
            email,
            phone,
            SECRET_KEY,
            CUSTOMER_SESSION_MAX_AGE,
        )
        self.send_json(
            {"ok": True},
            headers=[("Set-Cookie", self.customer_session_cookie(signed_session))],
        )

    def handle_customer_logout(self):
        self.send_json(
            {"ok": True},
            headers=[
                (
                    "Set-Cookie",
                    f"{CUSTOMER_SESSION_COOKIE}=; HttpOnly; {self.cookie_same_site()}; Path=/; Max-Age=0",
                )
            ],
        )

    def handle_public_business(self):
        self.send_json(
            {
                "tradeName": BUSINESS_TRADE_NAME,
                "legalName": BUSINESS_LEGAL_NAME,
                "taxId": BUSINESS_TAX_ID,
                "address": BUSINESS_ADDRESS,
                "email": BUSINESS_EMAIL,
                "whatsapp": STORE_WHATSAPP_NUMBER,
                "formalized": bool(BUSINESS_LEGAL_NAME and BUSINESS_TAX_ID and BUSINESS_ADDRESS),
            }
        )

    def handle_create_customer_request(self):
        payload = self.read_json()
        request_type = str(payload.get("requestType", "")).strip().lower()
        category = str(payload.get("category", "")).strip().lower()
        reason = re.sub(r"\s+", " ", str(payload.get("reason", "")).strip())[:180]
        details = str(payload.get("details", "")).strip()[:4000]
        customer = self.get_customer_session()

        if request_type not in {"privacy", "return"}:
            self.send_json({"error": "Tipo de solicitacao invalido."}, status=400)
            return
        if len(details) < 10:
            self.send_json({"error": "Descreva a solicitacao com pelo menos 10 caracteres."}, status=400)
            return

        order_id = None
        customer_name = re.sub(r"\s+", " ", str(payload.get("name", "")).strip())[:120]
        customer_email = str(payload.get("email", "")).strip().lower()
        customer_phone = re.sub(r"\D+", "", str(payload.get("phone", "")))

        with connect_db() as conn:
            begin_immediate(conn)
            if request_type == "return":
                if not customer:
                    self.send_json({"error": "Entre em Meus Pedidos para solicitar uma devolucao."}, status=401)
                    return
                if payload.get("acceptedPolicy") is not True:
                    self.send_json({"error": "Leia e aceite as regras da solicitacao."}, status=400)
                    return
                reference = str(payload.get("orderReference", "")).strip().upper()
                order = conn.execute(
                    """
                    SELECT id, customer_name, customer_email, customer_phone, status
                    FROM orders
                    WHERE reference = ? AND LOWER(customer_email) = ? AND customer_phone = ?
                    """,
                    (reference, customer["email"], customer["phone"]),
                ).fetchone()
                if not order:
                    self.send_json({"error": "Pedido nao encontrado para esta conta."}, status=404)
                    return
                order_id = order["id"]
                customer_name = order["customer_name"]
                customer_email = order["customer_email"].lower()
                customer_phone = order["customer_phone"]
                allowed_categories = {
                    "cancelamento_antes_separacao", "arrependimento", "produto_incorreto",
                    "avaria", "vazamento", "defeito", "outro"
                }
                cancellable_statuses = {
                    "creating_payment", "awaiting_payment", "pending", "approved",
                    "paid", "to_separate", "whatsapp_pending",
                }
                if category == "cancelamento_antes_separacao" and order["status"] not in cancellable_statuses:
                    self.send_json(
                        {
                            "error": (
                                "O pedido ja entrou em separacao ou envio. "
                                "Use a opcao adequada de troca ou devolucao."
                            )
                        },
                        status=409,
                    )
                    return
                duplicate = conn.execute(
                    """
                    SELECT protocol FROM service_requests
                    WHERE order_id = ? AND request_type = 'return'
                      AND status NOT IN ('rejected', 'refunded', 'completed')
                    LIMIT 1
                    """,
                    (order_id,),
                ).fetchone()
                if duplicate:
                    self.send_json(
                        {"error": f"Ja existe uma solicitacao aberta: {duplicate['protocol']}."},
                        status=409,
                    )
                    return
            else:
                if customer:
                    customer_email = customer["email"]
                    customer_phone = customer["phone"]
                    order = conn.execute(
                        """
                        SELECT customer_name FROM orders
                        WHERE LOWER(customer_email) = ? AND customer_phone = ?
                        ORDER BY created_at DESC LIMIT 1
                        """,
                        (customer_email, customer_phone),
                    ).fetchone()
                    if order:
                        customer_name = order["customer_name"]
                allowed_categories = {
                    "access", "correction", "deletion", "anonymization",
                    "sharing", "marketing_opt_out", "other"
                }

            if category not in allowed_categories:
                self.send_json({"error": "Categoria de solicitacao invalida."}, status=400)
                return
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", customer_email):
                self.send_json({"error": "Informe um e-mail valido."}, status=400)
                return
            if not customer_name:
                customer_name = "Titular de dados"

            protocol = ("LGPD" if request_type == "privacy" else "DEV") + secrets.token_hex(5).upper()
            cursor = conn.execute(
                """
                INSERT INTO service_requests (
                    protocol, request_type, order_id, customer_name, customer_email,
                    customer_phone, category, reason, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    protocol, request_type, order_id, customer_name, customer_email,
                    customer_phone, category, reason, details,
                ),
            )
            request_id = cursor.lastrowid

        self.send_json(
            {
                "ok": True,
                "id": request_id,
                "protocol": protocol,
                "message": "Solicitacao registrada. Guarde o protocolo.",
            },
            status=201,
        )

    def handle_customer_requests(self):
        customer = self.get_customer_session()
        if not customer:
            self.send_json({"error": "Entre para consultar suas solicitacoes."}, status=401)
            return
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT r.*, o.reference AS order_reference
                FROM service_requests r
                LEFT JOIN orders o ON o.id = r.order_id
                WHERE LOWER(r.customer_email) = ? AND r.customer_phone = ?
                ORDER BY r.created_at DESC
                """,
                (customer["email"], customer["phone"]),
            ).fetchall()
            payload = [self.serialize_service_request(conn, row) for row in rows]
        self.send_json({"requests": payload})

    def handle_customer_request_attachment(self, request_id):
        customer = self.get_customer_session()
        if not customer:
            self.send_json({"error": "Entre para anexar imagens."}, status=401)
            return
        with connect_db() as conn:
            service_request = conn.execute(
                """
                SELECT id FROM service_requests
                WHERE id = ? AND LOWER(customer_email) = ? AND customer_phone = ?
                """,
                (request_id, customer["email"], customer["phone"]),
            ).fetchone()
        if not service_request:
            self.send_json({"error": "Solicitacao nao encontrada."}, status=404)
            return
        try:
            original_name, content, mime = self.read_private_image()
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
            return
        stored_name = safe_upload_name(original_name)
        PRIVATE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (PRIVATE_UPLOAD_DIR / stored_name).write_bytes(content)
        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO request_attachments
                    (request_id, stored_name, original_name, mime_type, size)
                VALUES (?, ?, ?, ?, ?)
                """,
                (request_id, stored_name, original_name[:180], mime, len(content)),
            )
            attachment_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        self.send_json({"ok": True, "attachmentId": attachment_id}, status=201)

    def handle_admin_requests(self):
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT r.*, o.reference AS order_reference, o.payment_id, o.payment_method
                FROM service_requests r
                LEFT JOIN orders o ON o.id = r.order_id
                ORDER BY CASE r.status WHEN 'pending' THEN 0 WHEN 'in_review' THEN 1 ELSE 2 END,
                         r.created_at DESC
                """
            ).fetchall()
            payload = [self.serialize_service_request(conn, row) for row in rows]
        self.send_json(payload)

    def handle_admin_request_detail(self, request_id):
        with connect_db() as conn:
            row = conn.execute(
                """
                SELECT r.*, o.reference AS order_reference, o.payment_id, o.payment_method
                FROM service_requests r
                LEFT JOIN orders o ON o.id = r.order_id
                WHERE r.id = ?
                """,
                (request_id,),
            ).fetchone()
            if not row:
                self.send_error(404)
                return
            payload = self.serialize_service_request(conn, row)
        self.send_json(payload)

    def handle_admin_update_request(self, request_id):
        payload = self.read_json()
        status = str(payload.get("status", "")).strip()
        resolution = str(payload.get("resolution", "")).strip()[:4000]
        allowed = {
            "pending", "in_review", "awaiting_customer", "awaiting_return",
            "approved", "rejected", "refunded", "completed",
        }
        if status not in allowed:
            self.send_json({"error": "Status invalido."}, status=400)
            return
        with connect_db() as conn:
            begin_immediate(conn)
            row = conn.execute(
                "SELECT id, request_type, category, reverse_code FROM service_requests WHERE id = ?",
                (request_id,),
            ).fetchone()
            if not row:
                self.send_error(404)
                return
            reverse_code = row["reverse_code"]
            if (
                row["request_type"] == "return"
                and row["category"] != "cancelamento_antes_separacao"
                and status == "awaiting_return"
                and not reverse_code
            ):
                reverse_code = "REV" + secrets.token_hex(5).upper()
            resolved_at = (
                "CURRENT_TIMESTAMP"
                if status in {"rejected", "refunded", "completed"}
                else "''"
            )
            conn.execute(
                f"""
                UPDATE service_requests
                SET status = ?, resolution = ?, reverse_code = ?,
                    resolved_at = {resolved_at}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, resolution, reverse_code, request_id),
            )
        self.log_admin_action("service_request_update", "service_requests", request_id, status)
        self.send_json({"ok": True, "reverseCode": reverse_code})

    def handle_admin_request_refund(self, request_id):
        with connect_db() as conn:
            row = conn.execute(
                """
                SELECT r.*, o.payment_id, o.status AS order_status, o.id AS linked_order_id
                FROM service_requests r
                JOIN orders o ON o.id = r.order_id
                WHERE r.id = ? AND r.request_type = 'return'
                """,
                (request_id,),
            ).fetchone()
            if not row:
                self.send_json({"error": "Solicitacao de devolucao nao encontrada."}, status=404)
                return
            if row["refund_id"]:
                self.send_json(
                    {"ok": True, "refundId": row["refund_id"], "status": row["refund_status"]}
                )
                return
            cancellable_statuses = {
                "creating_payment", "awaiting_payment", "pending", "approved",
                "paid", "to_separate", "whatsapp_pending",
            }
            if (
                row["category"] == "cancelamento_antes_separacao"
                and row["order_status"] not in cancellable_statuses
            ):
                self.send_json(
                    {
                        "error": (
                            "O pedido avancou para separacao ou envio. "
                            "Converta o atendimento para o fluxo de devolucao antes de reembolsar."
                        )
                    },
                    status=409,
                )
                return
            payment_id = row["payment_id"]
            protocol = row["protocol"]
            if not payment_id:
                self.send_json(
                    {
                        "error": (
                            "Este pedido nao possui pagamento identificado no Mercado Pago. "
                            "O reembolso deve ser feito pelo meio de pagamento original."
                        )
                    },
                    status=409,
                )
                return

        refund = refund_mercado_pago_payment(payment_id, f"refund-{protocol.lower()}")
        refund_id = str(refund.get("id") or "")
        refund_status = str(refund.get("status") or "approved")
        with connect_db() as conn:
            begin_immediate(conn)
            release_order_stock(conn, row["linked_order_id"])
            conn.execute(
                """
                UPDATE service_requests
                SET status = 'refunded', refund_id = ?, refund_status = ?,
                    resolution = CASE WHEN resolution = '' THEN 'Reembolso processado pelo Mercado Pago.' ELSE resolution END,
                    resolved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (refund_id, refund_status, request_id),
            )
            conn.execute(
                "UPDATE orders SET status = 'refunded', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (row["linked_order_id"],),
            )
            conn.execute(
                """
                INSERT INTO order_history (order_id, old_status, new_status, note, admin_user)
                VALUES (?, ?, 'refunded', ?, ?)
                """,
                (
                    row["linked_order_id"],
                    row["order_status"],
                    f"Reembolso automatico. Protocolo {protocol}.",
                    ADMIN_USER,
                ),
            )
        self.log_admin_action("mercado_pago_refund", "service_requests", request_id, refund_id)
        self.send_json({"ok": True, "refundId": refund_id, "status": refund_status})

    def handle_reverse_label(self, request_id, admin=False):
        customer = None if admin else self.get_customer_session()
        if not admin and not customer:
            self.send_json({"error": "Entre para acessar a etiqueta."}, status=401)
            return
        with connect_db() as conn:
            where = "r.id = ?"
            params = [request_id]
            if customer:
                where += " AND LOWER(r.customer_email) = ? AND r.customer_phone = ?"
                params.extend([customer["email"], customer["phone"]])
            row = conn.execute(
                f"""
                SELECT r.*, o.*
                FROM service_requests r
                JOIN orders o ON o.id = r.order_id
                WHERE {where}
                """,
                params,
            ).fetchone()
        if not row or not row["reverse_code"]:
            self.send_json({"error": "Etiqueta reversa ainda nao disponivel."}, status=404)
            return
        pdf = build_reverse_label_pdf(row, row)
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(pdf)))
        self.send_header("Content-Disposition", f'attachment; filename="devolucao-{row["protocol"]}.pdf"')
        self.end_headers()
        self.wfile.write(pdf)

    def handle_request_attachment(self, request_id, attachment_id, admin=False):
        customer = None if admin else self.get_customer_session()
        if not admin and not customer:
            self.send_json({"error": "Entre para acessar o anexo."}, status=401)
            return
        with connect_db() as conn:
            where = "a.id = ? AND a.request_id = ?"
            params = [attachment_id, request_id]
            if customer:
                where += " AND LOWER(r.customer_email) = ? AND r.customer_phone = ?"
                params.extend([customer["email"], customer["phone"]])
            attachment = conn.execute(
                f"""
                SELECT a.* FROM request_attachments a
                JOIN service_requests r ON r.id = a.request_id
                WHERE {where}
                """,
                params,
            ).fetchone()
        if not attachment:
            self.send_error(404)
            return
        path = PRIVATE_UPLOAD_DIR / attachment["stored_name"]
        if not path.exists():
            self.send_error(404)
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", attachment["mime_type"])
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Content-Disposition", f'inline; filename="{safe_upload_name(attachment["original_name"])}"')
        self.end_headers()
        self.wfile.write(content)

    def serialize_service_request(self, conn, row):
        data = dict(row)
        attachments = conn.execute(
            """
            SELECT id, original_name, mime_type, size, created_at
            FROM request_attachments WHERE request_id = ? ORDER BY id
            """,
            (row["id"],),
        ).fetchall()
        data["attachments"] = [dict(item) for item in attachments]
        return data

    def read_private_image(self):
        content_type = self.headers.get("Content-Type", "")
        size = int(self.headers.get("Content-Length", 0))
        if not content_type.startswith("multipart/form-data") or size <= 0:
            raise ValueError("Envie uma imagem em multipart/form-data.")
        if size > 6 * 1024 * 1024:
            raise ValueError("Imagem maior que 5MB.")
        original_name, content = parse_multipart_image(self.headers, self.rfile.read(size))
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("Imagem maior que 5MB.")
        mime = mimetypes.guess_type(original_name)[0] or ""
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            raise ValueError("Use imagens JPG, PNG ou WebP.")
        return original_name, content, mime

    #HANDLE_SHIPPING_QUOTE
    def handle_shipping_quote(self):
        query = parse.parse_qs(parse.urlparse(self.path).query)
        postal_code = re.sub(r"\D+", "", str(query.get("postalCode", [""])[0]))
        try:
            product_amount = max(0.0, round(float(query.get("productAmount", ["0"])[0]), 2))
        except (TypeError, ValueError):
            product_amount = 0.0

        if len(postal_code) != 8 or len(set(postal_code)) == 1:
            self.send_json({"error": "Informe um CEP valido com 8 digitos."}, status=400)
            return

        shipping_amount = (
            0.0
            if FREE_SHIPPING_THRESHOLD and product_amount >= FREE_SHIPPING_THRESHOLD
            else round(SHIPPING_FEE, 2)
        )
        self.send_json(
            {
                "postalCode": postal_code,
                "productAmount": product_amount,
                "shippingAmount": shipping_amount,
                "freeShippingThreshold": FREE_SHIPPING_THRESHOLD,
                "total": round(product_amount + shipping_amount, 2),
            }
        )

    #HANDLE_ADMIN_ORDER_DETAIL
    def handle_admin_order_detail(self):
        match = re.match(r"/api/admin/orders/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        order_id = int(match.group(1))
        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if not order:
                self.send_error(404)
                return
            items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
            history = conn.execute(
                "SELECT old_status, new_status, note, admin_user, created_at FROM order_history WHERE order_id = ? ORDER BY created_at DESC",
                (order_id,),
            ).fetchall()
            payment_alerts = conn.execute(
                """
                SELECT event_type, event_id, payment_id, status, details, created_at
                FROM payment_alerts WHERE order_id = ? ORDER BY created_at DESC
                """,
                (order_id,),
            ).fetchall()
        payload = dict(order)
        payload["items"] = [dict(item) for item in items]
        payload["history"] = [dict(item) for item in history]
        payload["paymentAlerts"] = [dict(item) for item in payment_alerts]
        self.send_json(payload)

    #HANDLE_ADMIN_SHIPPING_LABEL
    def handle_admin_shipping_label(self, order_id):
        with connect_db() as conn:
            order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if not order:
                self.send_error(404)
                return
            if order["payment_risk_status"]:
                self.send_json(
                    {"error": "Etiqueta bloqueada enquanto houver alerta financeiro ativo."},
                    status=409,
                )
                return
            items = conn.execute(
                """
                SELECT product_name, volume, quantity, unit_price, subtotal
                FROM order_items WHERE order_id = ? ORDER BY id
                """,
                (order_id,),
            ).fetchall()

        try:
            pdf = build_shipping_label_pdf(order, items)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=409)
            return
        disposition = "inline" if "print=1" in self.path else "attachment"
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(pdf)))
        self.send_header(
            "Content-Disposition",
            f'{disposition}; filename="expedicao-{order["reference"]}.pdf"',
        )
        self.end_headers()
        self.wfile.write(pdf)

    #HANDLE_ADMIN_UPDATE_ORDER_STATUS
    def handle_admin_update_order_status(self, order_id):
        payload = self.read_json()
        new_status = str(payload.get("status", "")).strip()
        note = str(payload.get("note", "")).strip()
        allowed = {
            "creating_payment", "whatsapp_pending", "awaiting_payment", "pending", "approved",
            "to_separate", "separated", "preparing", "shipped", "delivered",
            "risk_review", "cancelled", "refunded", "charged_back", "rejected", "expired",
        }
        if new_status not in allowed:
            self.send_json({"error": "Status invalido."}, status=400)
            return

        try:
            with connect_db() as conn:
                begin_immediate(conn)
                order = conn.execute(
                    """
                    SELECT id, status, payment_method, payment_id, payment_risk_status
                    FROM orders WHERE id = ?
                    """,
                    (order_id,),
                ).fetchone()
                if not order:
                    self.send_error(404)
                    return
                old_status = order["status"]
                is_mercado_pago = order["payment_method"] != "WhatsApp"
                risk_release = bool(
                    order["payment_risk_status"]
                    and new_status not in {"cancelled", "refunded", "charged_back", "risk_review"}
                    and order["payment_id"]
                )
                if order["payment_risk_status"] and new_status not in {
                    "cancelled", "refunded", "charged_back", "risk_review"
                }:
                    if len(note) < 10:
                        self.send_json(
                            {
                                "error": (
                                    "Pedido bloqueado por risco financeiro. "
                                    "Registre uma observacao de pelo menos 10 caracteres para liberar."
                                )
                            },
                            status=409,
                        )
                        return
                if (
                    is_mercado_pago
                    and old_status not in PAID_ORDER_STATUSES
                    and new_status in PAID_ORDER_STATUSES
                    and not risk_release
                ):
                    self.send_json(
                        {
                            "error": (
                                "Pagamentos do Mercado Pago so podem ser confirmados "
                                "pelo webhook oficial."
                            )
                        },
                        status=409,
                    )
                    return
                if is_mercado_pago and new_status == "refunded":
                    self.send_json(
                        {
                            "error": (
                                "Reembolsos do Mercado Pago devem ser processados "
                                "pela solicitacao de devolucao."
                            )
                        },
                        status=409,
                    )
                    return
                if risk_release:
                    conn.execute(
                        """
                        UPDATE orders
                        SET payment_risk_status = '', payment_risk_reason = '',
                            payment_risk_event_id = ''
                        WHERE id = ?
                        """,
                        (order_id,),
                    )
                if new_status in {"cancelled", "refunded", "charged_back", "rejected", "expired"}:
                    release_order_stock(conn, order_id)
                elif (
                    old_status not in PAID_ORDER_STATUSES
                    and new_status in PAID_ORDER_STATUSES | {"whatsapp_pending", "awaiting_payment", "pending"}
                ):
                    reserve_order_stock(conn, order_id)

                conn.execute(
                    "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_status, order_id),
                )
                conn.execute(
                    """
                    INSERT INTO order_history (order_id, old_status, new_status, note, admin_user)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (order_id, old_status, new_status, note, ADMIN_USER),
                )
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
            return
        self.log_admin_action("order_status_update", "orders", str(order_id), f"{old_status} -> {new_status}")
        self.send_json({"ok": True})

    #HANDLE_ADMIN_CUSTOMERS
    def handle_admin_customers(self):
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT
                    customer_email AS email,
                    MAX(customer_name) AS name,
                    MAX(customer_phone) AS phone,
                    MAX(customer_address) AS address,
                    COUNT(*) AS order_count,
                    COALESCE(SUM(total), 0) AS total_spent,
                    MAX(created_at) AS last_order_at
                FROM orders
                GROUP BY customer_email
                ORDER BY last_order_at DESC
                """
            ).fetchall()
            leads = conn.execute(
                """
                SELECT email, nome AS name, telefone AS phone, created_at
                FROM leads
                WHERE email NOT IN (SELECT DISTINCT customer_email FROM orders)
                ORDER BY created_at DESC
                """
            ).fetchall()
        customers = [dict(row) for row in rows]
        for lead in leads:
            customers.append(
                {
                    "email": lead["email"],
                    "name": lead["name"] or "Lead Clube de Ofertas",
                    "phone": lead["phone"],
                    "address": "",
                    "order_count": 0,
                    "total_spent": 0,
                    "last_order_at": lead["created_at"],
                }
            )
        self.send_json(customers)

    #HANDLE_ADMIN_LOGS
    def handle_admin_logs(self):
        with connect_db() as conn:
            rows = conn.execute(
                "SELECT admin_user, action, entity, entity_id, ip, details, created_at FROM admin_logs ORDER BY created_at DESC LIMIT 100"
            ).fetchall()
        self.send_json([dict(row) for row in rows])

    #HANDLE_ADMIN_UPLOAD
    def handle_admin_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_json({"error": "Envie uma imagem em multipart/form-data."}, status=400)
            return

        size = int(self.headers.get("Content-Length", 0))
        if size <= 0:
            self.send_json({"error": "Imagem obrigatoria."}, status=400)
            return
        if size > 6 * 1024 * 1024:
            self.send_json({"error": "Imagem maior que 5MB."}, status=400)
            return

        try:
            original_filename, image_bytes = parse_multipart_image(self.headers, self.rfile.read(size))
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
            return

        if len(image_bytes) > 5 * 1024 * 1024:
            self.send_json({"error": "Imagem maior que 5MB."}, status=400)
            return

        filename = safe_upload_name(original_filename)
        mime = mimetypes.guess_type(filename)[0] or ""
        if not mime.startswith("image/"):
            self.send_json({"error": "Formato de imagem invalido."}, status=400)
            return

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        target = UPLOAD_DIR / filename
        target.write_bytes(image_bytes)

        url = f"/img/uploads/{filename}"
        self.log_admin_action("image_upload", "uploads", filename, url)
        self.send_json({"ok": True, "url": url}, status=201)

    #HANDLE_GET_PRODUCTS
    def handle_get_products(self):
        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            rows = conn.execute("SELECT * FROM products ORDER BY position, id").fetchall()
        self.send_json([product_from_row(row) for row in rows])

    #HANDLE_SESSION
    def handle_session(self):
        csrf = self.get_cookie(CSRF_COOKIE) or create_csrf_token()
        authenticated = self.is_authenticated()
        body = {"authenticated": authenticated, "user": ADMIN_USER if authenticated else "", "csrfToken": csrf}
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Set-Cookie", f"{CSRF_COOKIE}={csrf}; {self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}")
        self.end_headers()
        self.wfile.write(encoded)

    #HANDLE_CREATE_LEAD
    def handle_create_lead(self):
        try:
            lead = normalize_lead(self.read_json())
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
            return
        except Exception as error:
            self.send_json({"error": f"Nao foi possivel cadastrar o contato: {error}"}, status=500)
            return

        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO leads (nome, email, telefone)
                VALUES (?, ?, ?)
                ON CONFLICT(email, telefone) DO UPDATE SET
                    nome = excluded.nome,
                    created_at = CURRENT_TIMESTAMP
                """,
                (lead["nome"], lead["email"], lead["telefone"]),
            )

        self.send_json({"ok": True, "message": "Cadastro recebido."}, status=201)

    #HANDLE_CHECKOUT
    def handle_checkout(self):
        try:
            checkout = normalize_checkout(self.read_json())
            customer = checkout["customer"]
            payment_method = checkout["payment_method"]
            reference = "DEC" + secrets.token_hex(4).upper()
            base_url = get_public_base_url(self)

            with connect_db() as conn:
                begin_immediate(conn)
                release_expired_whatsapp_reservations(conn)
                order_items = build_order_items(conn, checkout["items"])
                discount = apply_checkout_coupon(order_items, checkout["coupon"])
                product_amount = round(sum(item["subtotal"] for item in order_items), 2)
                shipping_amount = (
                    0.0
                    if FREE_SHIPPING_THRESHOLD and product_amount >= FREE_SHIPPING_THRESHOLD
                    else round(SHIPPING_FEE, 2)
                )
                total = round(product_amount + shipping_amount, 2)
                payment_url = ""
                payment_preference_id = ""

                cursor = conn.execute(
                    """
                    INSERT INTO orders (
                        reference, customer_name, customer_email, customer_phone, customer_address,
                        customer_postal_code, customer_document,
                        product_amount, shipping_amount, total, status,
                        payment_method, payment_preference_id, payment_url, whatsapp_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference,
                        customer["name"],
                        customer["email"],
                        customer["phone"],
                        customer["address"],
                        customer["postal_code"],
                        customer["document"],
                        product_amount,
                        shipping_amount,
                        total,
                        "creating_payment" if payment_method == "mercado_pago" else "whatsapp_pending",
                        "Mercado Pago" if payment_method == "mercado_pago" else "WhatsApp",
                        payment_preference_id,
                        payment_url,
                        "",
                    ),
                )
                order_id = cursor.lastrowid

                for item in order_items:
                    conn.execute(
                        """
                        INSERT INTO order_items (
                            order_id, product_id, product_name, volume, quantity, unit_price, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            order_id,
                            item["product_id"],
                            item["product_name"],
                            item["volume"],
                            item["quantity"],
                            item["unit_price"],
                            item["subtotal"],
                        ),
                    )

                reserve_order_stock(conn, order_id)

            if payment_method == "mercado_pago":
                try:
                    preference = create_mercado_pago_preference(reference, customer, order_items, total, base_url)
                    payment_url = preference["url"]
                    payment_preference_id = preference["id"]
                except Exception:
                    with connect_db() as conn:
                        begin_immediate(conn)
                        release_order_stock(conn, order_id)
                        conn.execute(
                            """
                            UPDATE orders
                            SET status = 'payment_error', updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (order_id,),
                        )
                    raise

            whatsapp_url = build_whatsapp_url(reference, customer, order_items, total, payment_url)
            with connect_db() as conn:
                begin_immediate(conn)
                conn.execute(
                    """
                    UPDATE orders
                    SET status = ?, payment_preference_id = ?, payment_url = ?, whatsapp_url = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        "pending" if payment_method == "mercado_pago" else "whatsapp_pending",
                        payment_preference_id,
                        payment_url,
                        whatsapp_url,
                        order_id,
                    ),
                )

            signed_customer_session = create_customer_session(
                customer["email"],
                customer["phone"],
                SECRET_KEY,
                CUSTOMER_SESSION_MAX_AGE,
            )
            self.send_json(
                {
                    "ok": True,
                    "reference": reference,
                    "status": "pending" if payment_method == "mercado_pago" else "whatsapp_pending",
                    "productAmount": product_amount,
                    "shippingAmount": shipping_amount,
                    "total": total,
                    "paymentUrl": payment_url,
                    "whatsappUrl": whatsapp_url,
                    "discount": discount,
                    "message": "Pedido criado com sucesso.",
                },
                status=201,
                headers=[("Set-Cookie", self.customer_session_cookie(signed_customer_session))],
            )
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
        except Exception as error:
            self.send_json({"error": f"Nao foi possivel criar o pedido: {error}"}, status=500)

    #HANDLE_GET_ORDER
    def handle_get_order(self):
        parsed = parse.urlparse(self.path)
        reference = parsed.path.rsplit("/", 1)[-1].strip().upper()
        query = parse.parse_qs(parsed.query)
        contact = str(query.get("contact", [""])[0]).strip()
        email = contact.lower()
        phone = re.sub(r"\D+", "", contact)
        if not re.match(r"^DEC[A-F0-9]{8}$", reference):
            self.send_error(404)
            return
        if not contact or (not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) and len(phone) < 10):
            self.send_json({"error": "Informe o contato usado no pedido."}, status=400)
            return

        with connect_db() as conn:
            release_expired_whatsapp_reservations(conn)
            if len(phone) >= 10:
                order = conn.execute(
                    "SELECT * FROM orders WHERE reference = ? AND customer_phone = ?",
                    (reference, phone),
                ).fetchone()
            else:
                order = conn.execute(
                    "SELECT * FROM orders WHERE reference = ? AND LOWER(customer_email) = ?",
                    (reference, email),
                ).fetchone()
            if not order:
                self.send_error(404)
                return
            items = conn.execute(
                "SELECT product_name, volume, quantity, unit_price, subtotal FROM order_items WHERE order_id = ?",
                (order["id"],),
            ).fetchall()

        self.send_json(
            {
                "reference": order["reference"],
                "status": order["status"],
                "total": order["total"],
                "paymentUrl": order["payment_url"],
                "whatsappUrl": order["whatsapp_url"],
                "items": [dict(item) for item in items],
            }
        )

    #HANDLE_PAYMENT_WEBHOOK
    def handle_payment_webhook(self):
        try:
            payload = self.read_json()
            query = parse.parse_qs(parse.urlparse(self.path).query)
            event_id = extract_mercado_pago_payment_id(payload, query)
            event_type = str(
                payload.get("type")
                or payload.get("topic")
                or query.get("type", [""])[0]
                or query.get("topic", [""])[0]
                or "payment"
            ).strip()
            event_type = {
                "stop_delivery_op": "stop_delivery_op_wh",
                "claim": "topic_claims_integration_wh",
                "claims": "topic_claims_integration_wh",
                "chargeback": "topic_chargebacks_wh",
                "chargebacks": "topic_chargebacks_wh",
            }.get(event_type, event_type)
            if not verify_mercado_pago_webhook_signature(self.headers, event_id, query):
                self.send_json({"ok": False, "error": "Assinatura invalida."}, status=401)
                return

            risk_events = {
                "stop_delivery_op_wh": ("fraud_alert", "Alerta antifraude: interromper entrega."),
                "topic_claims_integration_wh": ("claim_open", "Reclamacao ou disputa aberta."),
                "topic_chargebacks_wh": ("chargeback", "Chargeback ou contestacao financeira."),
            }
            if event_type in risk_events:
                risk_status, reason = risk_events[event_type]
                payment_id = payment_id_from_alert(event_type, event_id)
                order = None
                if payment_id:
                    payment = fetch_mercado_pago_payment(payment_id)
                    reference = str(payment.get("external_reference") or "").strip()
                    with connect_db() as conn:
                        order = conn.execute(
                            "SELECT id, reference, status FROM orders WHERE payment_id = ? OR reference = ?",
                            (payment_id, reference),
                        ).fetchone()
                with connect_db() as conn:
                    begin_immediate(conn)
                    order_id = order["id"] if order else None
                    existing_alert = conn.execute(
                        """
                        SELECT id FROM payment_alerts
                        WHERE event_type = ? AND event_id = ?
                        """,
                        (event_type, event_id),
                    ).fetchone()
                    conn.execute(
                        """
                        INSERT INTO payment_alerts (
                            event_type, event_id, payment_id, order_id, status, details, payload
                        ) VALUES (?, ?, ?, ?, 'received', ?, ?)
                        ON CONFLICT(event_type, event_id) DO UPDATE SET
                            payment_id = excluded.payment_id,
                            order_id = COALESCE(excluded.order_id, payment_alerts.order_id),
                            details = excluded.details,
                            payload = excluded.payload,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (
                            event_type,
                            event_id,
                            payment_id,
                            order_id,
                            reason,
                            json.dumps(payload, ensure_ascii=True)[:8000],
                        ),
                    )
                    if order and not existing_alert:
                        next_status = "charged_back" if risk_status == "chargeback" else "risk_review"
                        conn.execute(
                            """
                            UPDATE orders
                            SET status = ?, payment_risk_status = ?,
                                payment_risk_reason = ?, payment_risk_event_id = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (next_status, risk_status, reason, event_id, order["id"]),
                        )
                        conn.execute(
                            """
                            INSERT INTO order_history (
                                order_id, old_status, new_status, note, admin_user
                            ) VALUES (?, ?, ?, ?, 'Mercado Pago')
                            """,
                            (order["id"], order["status"], next_status, reason),
                        )
                    if not existing_alert:
                        conn.execute(
                            """
                            INSERT INTO admin_logs (
                                admin_user, action, entity, entity_id, ip, details
                            ) VALUES ('Mercado Pago', 'payment_risk_alert', 'orders', ?, ?, ?)
                            """,
                            (
                                str(order_id or ""),
                                self.client_address[0],
                                f"{event_type}: {event_id} - {reason}",
                            ),
                        )
                if order and not existing_alert:
                    send_admin_payment_risk_notification(order["reference"], reason, event_id)
                self.send_json({"ok": True, "blocked": bool(order)})
                return

            payment_id = event_id

            payment = fetch_mercado_pago_payment(payment_id)
            reference = str(payment.get("external_reference") or "").strip()
            status = normalize_mercado_pago_status(str(payment.get("status") or "pending").strip())

            if reference:
                notify_admin = None
                with connect_db() as conn:
                    begin_immediate(conn)
                    current_order = conn.execute(
                        """
                        SELECT id, reference, status, customer_name, customer_email, total, stock_reserved,
                               admin_whatsapp_sent_at, payment_risk_status
                        FROM orders WHERE reference = ?
                        """,
                        (reference,),
                    ).fetchone()
                    if not current_order:
                        self.send_json({"ok": True})
                        return

                    validate_payment_for_order(payment, current_order)
                    duplicate_payment = conn.execute(
                        """
                        SELECT reference FROM orders
                        WHERE payment_id = ? AND payment_id <> '' AND reference <> ?
                        LIMIT 1
                        """,
                        (payment_id, reference),
                    ).fetchone()
                    if duplicate_payment:
                        raise ValueError("Pagamento ja vinculado a outro pedido.")
                    next_status = (
                        current_order["status"]
                        if current_order["payment_risk_status"]
                        else ("to_separate" if status == "approved" else status)
                    )

                    if status == "approved" and not current_order["payment_risk_status"]:
                        if not current_order["stock_reserved"] and current_order["status"] not in PAID_ORDER_STATUSES:
                            reserve_order_stock(conn, current_order["id"])
                        if not current_order["admin_whatsapp_sent_at"]:
                            notify_admin = {
                                "reference": reference,
                                "customer_name": current_order["customer_name"],
                                "total": current_order["total"],
                            }
                    elif status in FAILED_PAYMENT_STATUSES and not current_order["payment_risk_status"]:
                        release_order_stock(conn, current_order["id"])

                    conn.execute(
                        """
                        UPDATE orders
                        SET status = ?, payment_id = ?, payment_method = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE reference = ?
                        """,
                        (
                            next_status,
                            payment_id,
                            str(payment.get("payment_type_id") or payment.get("payment_method_id") or "Mercado Pago"),
                            reference,
                        ),
                    )

                if notify_admin and send_admin_whatsapp_notification(**notify_admin):
                    with connect_db() as conn:
                        conn.execute(
                            "UPDATE orders SET admin_whatsapp_sent_at = CURRENT_TIMESTAMP WHERE reference = ?",
                            (reference,),
                        )

            self.send_json({"ok": True})
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=200)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    #HANDLE_LOGIN
    def handle_login(self):
        ip = admin_client_ip(self)
        if rate_limited(ip):
            self.send_json({"error": "Muitas tentativas. Aguarde alguns minutos e tente novamente."}, status=429)
            return

        payload = self.read_json()
        if payload.get("user") != ADMIN_USER or not verify_admin_password(
            str(payload.get("password", "")),
            ADMIN_PASSWORD_HASH,
            ADMIN_PASSWORD if not IS_PRODUCTION else "",
        ):
            register_failed_login(ip)
            self.log_admin_action("login_failed", "auth", "", payload.get("user", ""))
            self.send_json({"error": "Usuario ou senha invalidos."}, status=401)
            return

        clear_login_attempts(ip)
        signed_session = create_admin_session(connect_db, SECRET_KEY, SESSION_MAX_AGE)
        csrf = self.get_cookie(CSRF_COOKIE) or create_csrf_token()
        self.log_admin_action("login_success", "auth", "", ADMIN_USER)
        self.send_json(
            {"ok": True, "user": ADMIN_USER, "csrfToken": csrf},
            headers=[
                (
                    "Set-Cookie",
                    f"{SESSION_COOKIE}={signed_session}; HttpOnly; "
                    f"{self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}",
                ),
                (
                    "Set-Cookie",
                    f"{CSRF_COOKIE}={csrf}; {self.cookie_same_site()}; "
                    f"Path=/; Max-Age={SESSION_MAX_AGE}",
                ),
            ],
        )

    #HANDLE_LOGOUT
    def handle_logout(self):
        session = self.get_cookie(SESSION_COOKIE)
        revoke_admin_session(connect_db, session, SECRET_KEY)
        self.log_admin_action("logout", "auth", "", ADMIN_USER)
        self.send_json(
            {"ok": True},
            headers=[
                (
                    "Set-Cookie",
                    f"{SESSION_COOKIE}=; HttpOnly; {self.cookie_same_site()}; "
                    "Path=/; Max-Age=0",
                ),
                (
                    "Set-Cookie",
                    f"{CSRF_COOKIE}=; {self.cookie_same_site()}; Path=/; Max-Age=0",
                ),
            ],
        )

    #COOKIE_SAME_SITE
    def cookie_same_site(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        host = self.headers.get("Host", "")
        same_origin = not origin or origin.endswith(host)
        host_name = host.split(":", 1)[0].lower()
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" or host_name in ADMIN_HOSTS else ""

        if same_origin:
            return f"SameSite=Lax{secure}"

        return "SameSite=None; Secure"

    #READ_JSON
    def read_json(self):
        size = int(self.headers.get("Content-Length", 0))
        if size == 0:
            return {}
        return json.loads(self.rfile.read(size).decode("utf-8"))

    #SEND_JSON
    def send_json(self, payload, status=200, headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers or []:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    #GET_COOKIE
    def get_cookie(self, name):
        raw = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie(raw)
        return jar[name].value if name in jar else ""

    def get_customer_session(self):
        return verify_customer_session(
            self.get_cookie(CUSTOMER_SESSION_COOKIE),
            SECRET_KEY,
        )

    def customer_session_cookie(self, value):
        return (
            f"{CUSTOMER_SESSION_COOKIE}={value}; HttpOnly; {self.cookie_same_site()}; "
            f"Path=/; Max-Age={CUSTOMER_SESSION_MAX_AGE}"
        )

    #IS_AUTHENTICATED
    def is_authenticated(self):
        return verify_admin_session(connect_db, self.get_cookie(SESSION_COOKIE), SECRET_KEY)

    #REQUIRE_AUTH
    def require_auth(self):
        if not self.is_authenticated():
            self.send_json({"error": "Login necessario."}, status=401)
            return False
        return True

    #REQUIRE_CSRF
    def require_csrf(self):
        expected = self.get_cookie(CSRF_COOKIE)
        received = self.headers.get("X-CSRF-Token", "")
        if not expected or not received or not hmac.compare_digest(expected, received):
            self.send_json({"error": "Token CSRF invalido. Recarregue a pagina."}, status=403)
            return False
        return True

    #LOG_ADMIN_ACTION
    def log_admin_action(self, action, entity="", entity_id="", details=""):
        try:
            with connect_db() as conn:
                conn.execute(
                    """
                    INSERT INTO admin_logs (admin_user, action, entity, entity_id, ip, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (ADMIN_USER, action, entity, str(entity_id), admin_client_ip(self), str(details)[:500]),
                )
        except Exception as exc:
            print(f"Falha ao gravar log administrativo: {exc}")

    #LOG_MESSAGE
    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))
