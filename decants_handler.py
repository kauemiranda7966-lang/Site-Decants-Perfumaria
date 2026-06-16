import decants_app as app
from decants_app import *
from decants_customer_handler import DecantsCustomerMixin
from decants_http import DecantsHTTPMixin
from decants_routes import DecantsRoutingMixin


class DecantsHandler(
    DecantsRoutingMixin,
    DecantsCustomerMixin,
    DecantsHTTPMixin,
    http.server.SimpleHTTPRequestHandler,
):
    protocol_version = "HTTP/1.1"

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
                app.SECRET_KEY,
                app.CUSTOMER_SESSION_MAX_AGE,
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
        signed_session = create_admin_session(
            connect_db,
            app.SECRET_KEY,
            SESSION_MAX_AGE,
        )
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
        revoke_admin_session(connect_db, session, app.SECRET_KEY)
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
