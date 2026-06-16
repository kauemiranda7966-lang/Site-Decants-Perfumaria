import decants_app as app
from decants_app import *


class DecantsCustomerMixin:
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
            app.SECRET_KEY,
            app.CUSTOMER_SESSION_MAX_AGE,
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
                "tradeName": app.BUSINESS_TRADE_NAME,
                "legalName": app.BUSINESS_LEGAL_NAME,
                "taxId": app.BUSINESS_TAX_ID,
                "address": app.BUSINESS_ADDRESS,
                "email": app.BUSINESS_EMAIL,
                "whatsapp": STORE_WHATSAPP_NUMBER,
                "formalized": bool(
                    app.BUSINESS_LEGAL_NAME
                    and app.BUSINESS_TAX_ID
                    and app.BUSINESS_ADDRESS
                ),
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
        app.PRIVATE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (app.PRIVATE_UPLOAD_DIR / stored_name).write_bytes(content)
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
        path = app.PRIVATE_UPLOAD_DIR / attachment["stored_name"]
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
