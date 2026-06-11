import decants_app as app
from decants_app import *

class DecantsHandler(http.server.SimpleHTTPRequestHandler):
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
        self.add_cors_headers()
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    #ADD_CORS_HEADERS
    def add_cors_headers(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        if origin not in ADMIN_ALLOWED_ORIGINS:
            return

        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
        if self.path.startswith("/api/customer/orders"):
            self.handle_customer_orders()
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
        return path in {"/login", "/dashboard", "/produtos", "/pedidos", "/clientes", "/logs"}

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
            rows = conn.execute(
                """
                SELECT id, reference, customer_name, customer_email, customer_phone,
                       product_amount, shipping_amount, total, status, payment_method, created_at, updated_at
                FROM orders ORDER BY created_at DESC
                """
            ).fetchall()
        self.send_json([dict(row) for row in rows])

    #HANDLE_CUSTOMER_ORDERS
    def handle_customer_orders(self):
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

        with connect_db() as conn:
            orders = conn.execute(
                f"""
                SELECT id, reference, total, status, payment_url, whatsapp_url, created_at, updated_at
                FROM orders
                WHERE {where}
                ORDER BY created_at DESC
                LIMIT 1
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
            order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if not order:
                self.send_error(404)
                return
            items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
            history = conn.execute(
                "SELECT old_status, new_status, note, admin_user, created_at FROM order_history WHERE order_id = ? ORDER BY created_at DESC",
                (order_id,),
            ).fetchall()
        payload = dict(order)
        payload["items"] = [dict(item) for item in items]
        payload["history"] = [dict(item) for item in history]
        self.send_json(payload)

    #HANDLE_ADMIN_SHIPPING_LABEL
    def handle_admin_shipping_label(self, order_id):
        with connect_db() as conn:
            order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if not order:
                self.send_error(404)
                return
            items = conn.execute(
                "SELECT quantity FROM order_items WHERE order_id = ? ORDER BY id",
                (order_id,),
            ).fetchall()

        pdf = build_shipping_label_pdf(order, items)
        disposition = "inline" if "print=1" in self.path else "attachment"
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(len(pdf)))
        self.send_header(
            "Content-Disposition",
            f'{disposition}; filename="etiqueta-{order["reference"]}.pdf"',
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
            "cancelled", "refunded", "charged_back", "rejected", "expired",
        }
        if new_status not in allowed:
            self.send_json({"error": "Status invalido."}, status=400)
            return

        try:
            with connect_db() as conn:
                order = conn.execute("SELECT id, status FROM orders WHERE id = ?", (order_id,)).fetchone()
                if not order:
                    self.send_error(404)
                    return
                old_status = order["status"]
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
                        customer_postal_code, product_amount, shipping_amount, total, status,
                        payment_method, payment_preference_id, payment_url, whatsapp_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference,
                        customer["name"],
                        customer["email"],
                        customer["phone"],
                        customer["address"],
                        customer["postal_code"],
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
                    preference = create_mercado_pago_preference(reference, customer, order_items, total, base_url)
                    payment_url = preference["url"]
                    payment_preference_id = preference["id"]

                whatsapp_url = build_whatsapp_url(reference, customer, order_items, total, payment_url)
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
            payment_id = extract_mercado_pago_payment_id(payload, query)
            if not verify_mercado_pago_webhook_signature(self.headers, payment_id, query):
                self.send_json({"ok": False, "error": "Assinatura invalida."}, status=401)
                return

            payment = fetch_mercado_pago_payment(payment_id)
            reference = str(payment.get("external_reference") or "").strip()
            status = normalize_mercado_pago_status(str(payment.get("status") or "pending").strip())

            if reference:
                notify_admin = None
                with connect_db() as conn:
                    current_order = conn.execute(
                        """
                        SELECT id, reference, status, customer_name, customer_email, total, stock_reserved,
                               admin_whatsapp_sent_at
                        FROM orders WHERE reference = ?
                        """,
                        (reference,),
                    ).fetchone()
                    if not current_order:
                        self.send_json({"ok": True})
                        return

                    validate_payment_for_order(payment, current_order)
                    next_status = "to_separate" if status == "approved" else status

                    if status == "approved":
                        if not current_order["stock_reserved"] and current_order["status"] not in PAID_ORDER_STATUSES:
                            reserve_order_stock(conn, current_order["id"])
                        if not current_order["admin_whatsapp_sent_at"]:
                            notify_admin = {
                                "reference": reference,
                                "customer_name": current_order["customer_name"],
                                "total": current_order["total"],
                            }
                    elif status in FAILED_PAYMENT_STATUSES:
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
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header(
            "Set-Cookie",
            f"{SESSION_COOKIE}={signed_session}; HttpOnly; {self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}",
        )
        self.send_header("Set-Cookie", f"{CSRF_COOKIE}={csrf}; {self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}")
        self.end_headers()
        self.log_admin_action("login_success", "auth", "", ADMIN_USER)
        self.wfile.write(json.dumps({"ok": True, "user": ADMIN_USER, "csrfToken": csrf}).encode("utf-8"))

    #HANDLE_LOGOUT
    def handle_logout(self):
        session = self.get_cookie(SESSION_COOKIE)
        revoke_admin_session(connect_db, session, SECRET_KEY)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; HttpOnly; {self.cookie_same_site()}; Path=/; Max-Age=0")
        self.send_header("Set-Cookie", f"{CSRF_COOKIE}=; {self.cookie_same_site()}; Path=/; Max-Age=0")
        self.end_headers()
        self.log_admin_action("logout", "auth", "", ADMIN_USER)
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

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
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    #GET_COOKIE
    def get_cookie(self, name):
        raw = self.headers.get("Cookie", "")
        jar = cookies.SimpleCookie(raw)
        return jar[name].value if name in jar else ""

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
