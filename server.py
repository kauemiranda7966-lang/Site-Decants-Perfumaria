import base64
import hashlib
import hmac
import http.server
import json
import os
import re
import secrets
import sqlite3
import time
from http import cookies
from pathlib import Path
from urllib import error, parse, request
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DECANTS_DB_PATH", ROOT / "data" / "decants.sqlite3"))
SESSION_COOKIE = "decants_session"
SESSION_MAX_AGE = 60 * 60 * 8


#LOAD_ENV_FILE
def load_env_file():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()

ADMIN_USER = os.environ.get("DECANTS_ADMIN_USER", "decantsperfumaria1@gmail.com")
ADMIN_PASSWORD = os.environ.get("DECANTS_ADMIN_PASSWORD", "Wellida123 senha")
SECRET_KEY = os.environ.get("DECANTS_SECRET_KEY", "troque-esta-chave-em-producao")
STORE_WHATSAPP_NUMBER = re.sub(r"\D+", "", os.environ.get("DECANTS_WHATSAPP_NUMBER", "558899641605"))
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY", "")
MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("DECANTS_PUBLIC_BASE_URL", "")
SESSIONS = {}


#CONNECT_DB
def connect_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


#INIT_DB
def init_db():
    with connect_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                img TEXT NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 10,
                preco5 TEXT NOT NULL,
                preco10 TEXT NOT NULL,
                promocao INTEGER NOT NULL DEFAULT 0,
                precoPromocional5 TEXT NOT NULL DEFAULT '',
                precoPromocional10 TEXT NOT NULL DEFAULT '',
                destaque INTEGER NOT NULL DEFAULT 0,
                selo TEXT NOT NULL DEFAULT '',
                chamada TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, telefone)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT NOT NULL DEFAULT '',
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                payment_id TEXT NOT NULL DEFAULT '',
                payment_url TEXT NOT NULL DEFAULT '',
                whatsapp_url TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                volume INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            seed_products(conn)


#SEED_PRODUCTS
def seed_products(conn):
    products = load_default_products()
    featured = {"Dior Sauvage", "La Vie Est Belle", "Versace Eros", "Yara Rosa"}
    for index, product in enumerate(products):
        product.setdefault("estoque", 10)
        product.setdefault("promocao", False)
        product.setdefault("precoPromocional5", "")
        product.setdefault("precoPromocional10", "")
        product.setdefault("destaque", product.get("nome") in featured)
        product.setdefault("selo", "")
        product.setdefault("chamada", "")
        insert_product(conn, product, index)


#LOAD_DEFAULT_PRODUCTS
def load_default_products():
    script = (ROOT / "js" / "script.js").read_text(encoding="utf-8")
    match = re.search(r"const produtosPadrao = (\[.*?\]);", script, re.S)
    if not match:
        return []
    data = re.sub(r"(\w+):", r'"\1":', match.group(1))
    return json.loads(data)


#PRODUCT_FROM_ROW
def product_from_row(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "categoria": row["categoria"],
        "img": row["img"],
        "estoque": row["estoque"],
        "preco5": row["preco5"],
        "preco10": row["preco10"],
        "promocao": bool(row["promocao"]),
        "precoPromocional5": row["precoPromocional5"],
        "precoPromocional10": row["precoPromocional10"],
        "destaque": bool(row["destaque"]),
        "selo": row["selo"],
        "chamada": row["chamada"],
    }


#NORMALIZE_PRODUCT
def normalize_product(payload):
    product = {
        "nome": str(payload.get("nome", "")).strip(),
        "categoria": str(payload.get("categoria", "masculino")).strip(),
        "img": str(payload.get("img", "")).strip(),
        "estoque": max(0, int(payload.get("estoque") or 0)),
        "preco5": str(payload.get("preco5", "")).strip(),
        "preco10": str(payload.get("preco10", "")).strip(),
        "promocao": 1 if payload.get("promocao") else 0,
        "precoPromocional5": str(payload.get("precoPromocional5", "")).strip(),
        "precoPromocional10": str(payload.get("precoPromocional10", "")).strip(),
        "destaque": 1 if payload.get("destaque") else 0,
        "selo": str(payload.get("selo", "")).strip(),
        "chamada": str(payload.get("chamada", "")).strip(),
    }

    if not product["nome"] or not product["img"] or not product["preco5"] or not product["preco10"]:
        raise ValueError("Nome, imagem e precos sao obrigatorios.")
    if product["categoria"] not in {"masculino", "feminino"}:
        raise ValueError("Categoria invalida.")

    return product


#NORMALIZE_LEAD
def normalize_lead(payload):
    email = str(payload.get("email", "")).strip().lower()
    telefone = re.sub(r"\D+", "", str(payload.get("telefone", "")))

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(telefone) < 10:
        raise ValueError("Informe um telefone com DDD.")

    return {"email": email, "telefone": telefone}


#PARSE_PRICE
def parse_price(value):
    clean = str(value or "0").strip().replace(".", "").replace(",", ".")
    try:
        return round(float(clean), 2)
    except ValueError:
        return 0.0


#MONEY_TO_BRL
def money_to_brl(value):
    return f"{value:.2f}".replace(".", ",")


#GET_PUBLIC_BASE_URL
def get_public_base_url(handler):
    if PUBLIC_BASE_URL:
        return PUBLIC_BASE_URL.rstrip("/")

    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    if render_url:
        return render_url.rstrip("/")

    host = handler.headers.get("Host", "localhost:8000")
    protocol = "https" if handler.headers.get("X-Forwarded-Proto") == "https" else "http"
    return f"{protocol}://{host}"


#IS_PUBLIC_BASE_URL
def is_public_base_url(base_url):
    host = parse.urlparse(base_url).hostname or ""
    return host not in {"localhost", "127.0.0.1", "::1"}


#PRODUCT_PRICE
def product_price(product, volume):
    promo_key = "precoPromocional10" if volume == 10 else "precoPromocional5"
    base_key = "preco10" if volume == 10 else "preco5"
    price = product[promo_key] if product["promocao"] and product[promo_key] else product[base_key]
    return parse_price(price)


#NORMALIZE_CHECKOUT
def normalize_checkout(payload):
    customer = payload.get("customer") or {}
    name = str(customer.get("name", "")).strip()
    email = str(customer.get("email", "")).strip().lower()
    phone = re.sub(r"\D+", "", str(customer.get("phone", "")))
    address = str(customer.get("address", "")).strip()
    items = payload.get("items") or []

    if len(name) < 3:
        raise ValueError("Informe o nome completo.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(phone) < 10:
        raise ValueError("Informe um WhatsApp com DDD.")
    if not items:
        raise ValueError("Escolha ao menos um perfume.")

    normalized_items = []
    for item in items:
        product_id = int(item.get("productId") or 0)
        product_name = str(item.get("productName", "")).strip()
        volume = int(item.get("volume") or 0)
        quantity = max(1, min(20, int(item.get("quantity") or 1)))
        if (product_id <= 0 and not product_name) or volume not in {5, 10}:
            raise ValueError("Item invalido no carrinho.")
        normalized_items.append(
            {"product_id": product_id, "product_name": product_name, "volume": volume, "quantity": quantity}
        )

    return {
        "customer": {"name": name, "email": email, "phone": phone, "address": address},
        "items": normalized_items,
    }


#BUILD_ORDER_ITEMS
def build_order_items(conn, checkout_items):
    order_items = []
    for item in checkout_items:
        if item["product_id"] > 0:
            row = conn.execute("SELECT * FROM products WHERE id = ?", (item["product_id"],)).fetchone()
        else:
            row = conn.execute("SELECT * FROM products WHERE nome = ?", (item["product_name"],)).fetchone()

        if not row:
            raise ValueError("Produto nao encontrado.")
        if row["estoque"] < item["quantity"]:
            raise ValueError(f"Estoque insuficiente para {row['nome']}.")

        unit_price = product_price(row, item["volume"])
        if unit_price <= 0:
            raise ValueError(f"Preco invalido para {row['nome']}.")

        order_items.append(
            {
                "product_id": row["id"],
                "product_name": row["nome"],
                "volume": item["volume"],
                "quantity": item["quantity"],
                "unit_price": unit_price,
                "subtotal": round(unit_price * item["quantity"], 2),
            }
        )

    return order_items


#BUILD_WHATSAPP_URL
def build_whatsapp_url(reference, customer, items, total, payment_url=""):
    lines = [
        f"Ola! Pedido {reference} - Decant's Perfumaria",
        f"Cliente: {customer['name']}",
        f"WhatsApp: {customer['phone']}",
        "Itens:",
    ]
    for item in items:
        lines.append(
            f"- {item['quantity']}x {item['product_name']} {item['volume']}ml "
            f"(R$ {money_to_brl(item['unit_price'])})"
        )
    lines.append(f"Total: R$ {money_to_brl(total)}")
    if customer.get("address"):
        lines.append(f"Endereco: {customer['address']}")
    if payment_url:
        lines.append(f"Link de pagamento: {payment_url}")

    message = parse.quote("\n".join(lines))
    return f"https://wa.me/{STORE_WHATSAPP_NUMBER}?text={message}"


#CREATE_MERCADO_PAGO_PREFERENCE
def create_mercado_pago_preference(reference, customer, items, total, base_url):
    if not MERCADO_PAGO_ACCESS_TOKEN:
        return ""

    preference = {
        "external_reference": reference,
        "items": [
            {
                "id": str(item["product_id"]),
                "title": f"{item['product_name']} {item['volume']}ml",
                "quantity": item["quantity"],
                "currency_id": "BRL",
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
        "payer": {
            "name": customer["name"],
            "email": customer["email"],
            "phone": {"number": customer["phone"]},
        },
        "statement_descriptor": "DECANTS PERF",
        "metadata": {"order_reference": reference, "total": total},
    }

    if is_public_base_url(base_url):
        preference["back_urls"] = {
            "success": f"{base_url}/index.html?pedido={reference}&pagamento=aprovado",
            "failure": f"{base_url}/index.html?pedido={reference}&pagamento=recusado",
            "pending": f"{base_url}/index.html?pedido={reference}&pagamento=pendente",
        }
        preference["auto_return"] = "approved"

    if is_public_base_url(base_url):
        preference["notification_url"] = f"{base_url}/api/payments/webhook"

    body = json.dumps(preference, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        "https://api.mercadopago.com/checkout/preferences",
        data=body,
        headers={
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("init_point") or data.get("sandbox_init_point") or ""
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"Mercado Pago recusou a preferencia: {detail[:180]}")
    except error.URLError as exc:
        raise ValueError(f"Nao foi possivel conectar ao Mercado Pago: {exc.reason}")


#FETCH_MERCADO_PAGO_PAYMENT
def fetch_mercado_pago_payment(payment_id):
    if not MERCADO_PAGO_ACCESS_TOKEN or not payment_id:
        return {}

    req = request.Request(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"},
        method="GET",
    )
    with request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


#EXTRACT_MERCADO_PAGO_PAYMENT_ID
def extract_mercado_pago_payment_id(payload, query):
    data = payload.get("data") if isinstance(payload, dict) else {}
    candidates = [
        data.get("id") if isinstance(data, dict) else "",
        payload.get("id") if isinstance(payload, dict) else "",
        query.get("data.id", [""])[0],
        query.get("id", [""])[0],
    ]
    for candidate in candidates:
        payment_id = str(candidate or "").strip()
        if payment_id:
            return payment_id
    return ""


#VERIFY_MERCADO_PAGO_WEBHOOK_SIGNATURE
def verify_mercado_pago_webhook_signature(headers, payment_id, query):
    if not MERCADO_PAGO_WEBHOOK_SECRET:
        return True

    signature_header = headers.get("x-signature", "")
    request_id = headers.get("x-request-id", "")
    if not signature_header or not request_id or not payment_id:
        return False

    signature_parts = {}
    for part in signature_header.split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        signature_parts[key.strip()] = value.strip()

    timestamp = signature_parts.get("ts", "")
    signature = signature_parts.get("v1", "")
    if not timestamp or not signature:
        return False

    data_id = query.get("data.id", [""])[0] or payment_id
    manifest = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
    expected = hmac.new(
        MERCADO_PAGO_WEBHOOK_SECRET.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


#INSERT_PRODUCT
def insert_product(conn, product, position=None):
    if position is None:
        position = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM products").fetchone()[0]
    conn.execute(
        """
        INSERT INTO products (
            nome, categoria, img, estoque, preco5, preco10, promocao,
            precoPromocional5, precoPromocional10, destaque, selo, chamada, position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product["nome"],
            product["categoria"],
            product["img"],
            product["estoque"],
            product["preco5"],
            product["preco10"],
            int(product["promocao"]),
            product["precoPromocional5"],
            product["precoPromocional10"],
            int(product["destaque"]),
            product["selo"],
            product["chamada"],
            position,
        ),
    )


#RESET_PRODUCTS
def reset_products():
    with connect_db() as conn:
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'products'")
        seed_products(conn)


#PASSWORD_HASH
def password_hash(password):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        SECRET_KEY.encode("utf-8"),
        120000,
    )


#CHECK_PASSWORD
def check_password(password):
    expected = password_hash(ADMIN_PASSWORD)
    received = password_hash(password)
    return hmac.compare_digest(expected, received)


#SIGN_SESSION
def sign_session(token):
    signature = hmac.new(SECRET_KEY.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).digest()
    return token + "." + base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


#VERIFY_SESSION
def verify_session(value):
    if not value or "." not in value:
        return False
    token, signature = value.rsplit(".", 1)
    expected = sign_session(token).rsplit(".", 1)[1]
    if not hmac.compare_digest(signature, expected):
        return False
    expires_at = SESSIONS.get(token)
    if not expires_at or expires_at < time.time():
        SESSIONS.pop(token, None)
        return False
    return True


class DecantsHandler(http.server.SimpleHTTPRequestHandler):
    #TRANSLATE_PATH
    def translate_path(self, path):
        path = unquote(path.split("?", 1)[0].split("#", 1)[0])
        parts = [part for part in path.split("/") if part and part not in {".", ".."}]
        return str(ROOT.joinpath(*parts))

    #END_HEADERS
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    #DO_GET
    def do_GET(self):
        if self.path.startswith("/api/products"):
            self.handle_get_products()
            return
        if self.path.startswith("/api/orders/"):
            self.handle_get_order()
            return
        if self.path.startswith("/api/session"):
            self.send_json({"authenticated": self.is_authenticated(), "user": ADMIN_USER if self.is_authenticated() else ""})
            return
        super().do_GET()

    #DO_POST
    def do_POST(self):
        if self.path.startswith("/api/leads"):
            self.handle_create_lead()
            return
        if self.path.startswith("/api/login"):
            self.handle_login()
            return
        if self.path.startswith("/api/logout"):
            self.handle_logout()
            return
        if self.path.startswith("/api/checkout"):
            self.handle_checkout()
            return
        if self.path.startswith("/api/payments/webhook"):
            self.handle_payment_webhook()
            return
        if self.path.startswith("/api/products/reset"):
            if not self.require_auth():
                return
            reset_products()
            self.handle_get_products()
            return
        if self.path.startswith("/api/products"):
            if not self.require_auth():
                return
            payload = self.read_json()
            product = normalize_product(payload)
            with connect_db() as conn:
                insert_product(conn, product)
            self.send_json({"ok": True}, status=201)
            return
        self.send_error(404)

    #DO_PUT
    def do_PUT(self):
        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth():
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
        self.send_json({"ok": True})

    #DO_DELETE
    def do_DELETE(self):
        match = re.match(r"/api/products/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        if not self.require_auth():
            return
        with connect_db() as conn:
            result = conn.execute("DELETE FROM products WHERE id = ?", (int(match.group(1)),))
            if result.rowcount == 0:
                self.send_error(404)
                return
        self.send_json({"ok": True})

    #HANDLE_GET_PRODUCTS
    def handle_get_products(self):
        with connect_db() as conn:
            rows = conn.execute("SELECT * FROM products ORDER BY position, id").fetchall()
        self.send_json([product_from_row(row) for row in rows])

    #HANDLE_CREATE_LEAD
    def handle_create_lead(self):
        try:
            lead = normalize_lead(self.read_json())
        except ValueError as error:
            self.send_json({"error": str(error)}, status=400)
        except Exception as error:
            self.send_json({"error": f"Nao foi possivel criar o pagamento: {error}"}, status=502)
            return

        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO leads (email, telefone)
                VALUES (?, ?)
                ON CONFLICT(email, telefone) DO UPDATE SET created_at = CURRENT_TIMESTAMP
                """,
                (lead["email"], lead["telefone"]),
            )

        self.send_json({"ok": True, "message": "Cadastro recebido."}, status=201)

    #HANDLE_CHECKOUT
    def handle_checkout(self):
        try:
            checkout = normalize_checkout(self.read_json())
            customer = checkout["customer"]
            reference = "DEC" + secrets.token_hex(4).upper()
            base_url = get_public_base_url(self)

            with connect_db() as conn:
                order_items = build_order_items(conn, checkout["items"])
                total = round(sum(item["subtotal"] for item in order_items), 2)
                payment_error = ""
                try:
                    payment_url = create_mercado_pago_preference(reference, customer, order_items, total, base_url)
                except ValueError as error:
                    payment_url = ""
                    payment_error = str(error)
                whatsapp_url = build_whatsapp_url(reference, customer, order_items, total, payment_url)

                cursor = conn.execute(
                    """
                    INSERT INTO orders (
                        reference, customer_name, customer_email, customer_phone, customer_address,
                        total, status, payment_url, whatsapp_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference,
                        customer["name"],
                        customer["email"],
                        customer["phone"],
                        customer["address"],
                        total,
                        "awaiting_payment" if payment_url else "whatsapp_pending",
                        payment_url,
                        whatsapp_url,
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

            self.send_json(
                {
                    "ok": True,
                    "reference": reference,
                    "status": "awaiting_payment" if payment_url else "whatsapp_pending",
                    "total": total,
                    "paymentUrl": payment_url,
                    "whatsappUrl": whatsapp_url,
                    "paymentError": payment_error,
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
        reference = self.path.rsplit("/", 1)[-1].split("?", 1)[0].strip().upper()
        if not re.match(r"^DEC[A-F0-9]{8}$", reference):
            self.send_error(404)
            return

        with connect_db() as conn:
            order = conn.execute("SELECT * FROM orders WHERE reference = ?", (reference,)).fetchone()
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
            status = str(payment.get("status") or "pending").strip() or "pending"

            if reference:
                with connect_db() as conn:
                    current_order = conn.execute("SELECT id, status FROM orders WHERE reference = ?", (reference,)).fetchone()
                    if current_order and status == "approved" and current_order["status"] != "approved":
                        items = conn.execute(
                            "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
                            (current_order["id"],),
                        ).fetchall()
                        for item in items:
                            conn.execute(
                                "UPDATE products SET estoque = MAX(0, estoque - ?) WHERE id = ?",
                                (item["quantity"], item["product_id"]),
                            )

                    conn.execute(
                        """
                        UPDATE orders
                        SET status = ?, payment_id = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE reference = ?
                        """,
                        (status, payment_id, reference),
                    )

            self.send_json({"ok": True})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=200)

    #HANDLE_LOGIN
    def handle_login(self):
        payload = self.read_json()
        if payload.get("user") != ADMIN_USER or not check_password(str(payload.get("password", ""))):
            self.send_json({"error": "Usuario ou senha invalidos."}, status=401)
            return

        token = secrets.token_urlsafe(32)
        SESSIONS[token] = time.time() + SESSION_MAX_AGE
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header(
            "Set-Cookie",
            f"{SESSION_COOKIE}={sign_session(token)}; HttpOnly; SameSite=Lax; Path=/; Max-Age={SESSION_MAX_AGE}",
        )
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "user": ADMIN_USER}).encode("utf-8"))

    #HANDLE_LOGOUT
    def handle_logout(self):
        session = self.get_cookie(SESSION_COOKIE)
        if session and "." in session:
            SESSIONS.pop(session.split(".", 1)[0], None)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

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
        return verify_session(self.get_cookie(SESSION_COOKIE))

    #REQUIRE_AUTH
    def require_auth(self):
        if not self.is_authenticated():
            self.send_json({"error": "Login necessario."}, status=401)
            return False
        return True

    #LOG_MESSAGE
    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


#MAIN
def main():
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), DecantsHandler)
    print(f"Decant's Perfumaria rodando em http://localhost:{port}")
    print("Login padrao do admin: decantsperfumaria1@gmail.com / Wellida123 senha")
    print("Em producao, defina DECANTS_ADMIN_USER, DECANTS_ADMIN_PASSWORD e DECANTS_SECRET_KEY.")
    server.serve_forever()


if __name__ == "__main__":
    main()
