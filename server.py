import base64
import hashlib
import hmac
import http.server
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import time
from email import policy
from email.parser import BytesParser
from http import cookies
from pathlib import Path
from urllib import error, parse, request
from urllib.parse import unquote

try:
    import bcrypt
except ImportError:
    bcrypt = None


ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT / "data" / "decants.sqlite3"
DB_PATH = Path(os.environ.get("DECANTS_DB_PATH", DEFAULT_DB_PATH))
SESSION_COOKIE = "decants_session"
CSRF_COOKIE = "decants_csrf"
SESSION_MAX_AGE = 60 * 60 * 8
UPLOAD_DIR = ROOT / "img" / "uploads"
LOGIN_ATTEMPTS = {}
LOGIN_LIMIT = 5
LOGIN_WINDOW = 15 * 60


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
ADMIN_PASSWORD = os.environ.get("DECANTS_ADMIN_PASSWORD", "Wellida123")
ADMIN_PASSWORD_HASH = os.environ.get("DECANTS_ADMIN_PASSWORD_HASH", "")
SECRET_KEY = os.environ.get("DECANTS_SECRET_KEY", "troque-esta-chave-em-producao")
STORE_WHATSAPP_NUMBER = re.sub(r"\D+", "", os.environ.get("DECANTS_WHATSAPP_NUMBER", "558899641605"))
ADMIN_DOMAIN = os.environ.get("DECANTS_ADMIN_DOMAIN", "admin.decantperfumaria.com.br")
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY", "")
MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET", "")
MERCADO_PAGO_COLLECTOR_ID = os.environ.get("MERCADO_PAGO_COLLECTOR_ID", "").strip()
WHATSAPP_CLOUD_TOKEN = os.environ.get("WHATSAPP_CLOUD_TOKEN", "")
WHATSAPP_CLOUD_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_PHONE_NUMBER_ID", "")
WHATSAPP_ADMIN_NUMBER = re.sub(r"\D+", "", os.environ.get("WHATSAPP_ADMIN_NUMBER", STORE_WHATSAPP_NUMBER))
PUBLIC_BASE_URL = os.environ.get("DECANTS_PUBLIC_BASE_URL", "")


def host_from_setting(value):
    if not value:
        return ""
    parsed = parse.urlparse(value if "://" in value else f"https://{value}")
    return (parsed.hostname or "").lower()


PUBLIC_HOST = host_from_setting(PUBLIC_BASE_URL)
ADMIN_HOSTS = {
    host
    for host in {
        host_from_setting(ADMIN_DOMAIN),
        PUBLIC_HOST,
        host_from_setting(os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")),
    }
    if host
}
ADMIN_ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "DECANTS_ALLOWED_ORIGINS",
        "https://kauemiranda7966-lang.github.io,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
}
for admin_host in ADMIN_HOSTS:
    ADMIN_ALLOWED_ORIGINS.add(f"https://{admin_host}")
SESSIONS = {}


#CONNECT_DB
def connect_db():
    db_path = DB_PATH
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        db_path = DEFAULT_DB_PATH
        db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
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
                nome TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(email, telefone)
            )
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(leads)").fetchall()}
        if "nome" not in columns:
            conn.execute("ALTER TABLE leads ADD COLUMN nome TEXT NOT NULL DEFAULT ''")
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
                payment_preference_id TEXT NOT NULL DEFAULT '',
                payment_url TEXT NOT NULL DEFAULT '',
                whatsapp_url TEXT NOT NULL DEFAULT '',
                stock_reserved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        order_columns = {row["name"] for row in conn.execute("PRAGMA table_info(orders)").fetchall()}
        if "admin_whatsapp_sent_at" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN admin_whatsapp_sent_at TEXT NOT NULL DEFAULT ''")
        if "payment_preference_id" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_preference_id TEXT NOT NULL DEFAULT ''")
        if "stock_reserved" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN stock_reserved INTEGER NOT NULL DEFAULT 0")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                old_status TEXT NOT NULL DEFAULT '',
                new_status TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                admin_user TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(order_id) REFERENCES orders(id)
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                entity TEXT NOT NULL DEFAULT '',
                entity_id TEXT NOT NULL DEFAULT '',
                ip TEXT NOT NULL DEFAULT '',
                details TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    nome = str(payload.get("nome", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    telefone = re.sub(r"\D+", "", str(payload.get("telefone", "")))

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(telefone) < 10:
        raise ValueError("Informe um telefone com DDD.")

    return {"nome": nome[:120], "email": email, "telefone": telefone}


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


#MERCADO_PAGO_CONFIGURED
def mercado_pago_configured():
    token = MERCADO_PAGO_ACCESS_TOKEN.strip()
    if not token or "SEU_ACCESS_TOKEN" in token or "SUA_" in token:
        return False
    return token.startswith(("APP_USR-", "TEST-"))


#MERCADO_PAGO_CHECKOUT_READY
def mercado_pago_checkout_ready(base_url):
    return mercado_pago_configured() and is_public_base_url(base_url)


#VALIDATE_MERCADO_PAGO_OWNER
def validate_mercado_pago_owner(mp_payload):
    if MERCADO_PAGO_COLLECTOR_ID:
        collector_id = str(mp_payload.get("collector_id") or "").strip()
        if collector_id != MERCADO_PAGO_COLLECTOR_ID:
            raise ValueError("Credencial Mercado Pago nao pertence ao collector_id configurado.")


#PAYMENT_STATUS_GROUPS
PAID_ORDER_STATUSES = {"approved", "paid", "to_separate", "separated", "delivered", "completed"}
FAILED_PAYMENT_STATUSES = {"cancelled", "canceled", "refunded", "charged_back", "rejected", "expired"}


#NORMALIZE_MERCADO_PAGO_STATUS
def normalize_mercado_pago_status(status):
    if status == "canceled":
        return "cancelled"
    if status == "rejected":
        return "cancelled"
    return status or "pending"


#PAYMENT_AMOUNT
def payment_amount(payment):
    for key in ("transaction_amount", "total_paid_amount"):
        try:
            amount = float(payment.get(key) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount > 0:
            return round(amount, 2)
    return 0.0


#VALIDATE_PAYMENT_FOR_ORDER
def validate_payment_for_order(payment, order):
    validate_mercado_pago_owner(payment)
    reference = str(payment.get("external_reference") or "").strip()
    if reference != order["reference"]:
        raise ValueError("Referencia do pagamento nao corresponde ao pedido.")

    payer = payment.get("payer") if isinstance(payment, dict) else {}
    payer_email = str((payer or {}).get("email") or "").strip().lower()
    if payer_email and payer_email != str(order["customer_email"]).strip().lower():
        raise ValueError("E-mail do pagador nao corresponde ao pedido.")

    amount = payment_amount(payment)
    if amount and abs(amount - float(order["total"])) > 0.01:
        raise ValueError("Valor pago nao corresponde ao total do pedido.")


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
    coupon = str(payload.get("coupon", "")).strip().upper()
    payment_method = str(payload.get("paymentMethod", "mercado_pago")).strip()

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
        "coupon": coupon if coupon == "DECANTS5" else "",
        "payment_method": payment_method if payment_method in {"mercado_pago", "whatsapp"} else "mercado_pago",
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


#RESERVE_ORDER_STOCK
def reserve_order_stock(conn, order_id):
    order = conn.execute("SELECT id, stock_reserved FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order or order["stock_reserved"]:
        return

    items = conn.execute(
        "SELECT product_id, product_name, quantity FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()
    for item in items:
        result = conn.execute(
            """
            UPDATE products
            SET estoque = estoque - ?
            WHERE id = ? AND estoque >= ?
            """,
            (item["quantity"], item["product_id"], item["quantity"]),
        )
        if result.rowcount == 0:
            raise ValueError(f"Estoque insuficiente para {item['product_name']}.")

    conn.execute("UPDATE orders SET stock_reserved = 1 WHERE id = ?", (order_id,))


#RELEASE_ORDER_STOCK
def release_order_stock(conn, order_id):
    order = conn.execute("SELECT id, stock_reserved FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order or not order["stock_reserved"]:
        return False

    items = conn.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()
    for item in items:
        conn.execute(
            "UPDATE products SET estoque = estoque + ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )

    conn.execute("UPDATE orders SET stock_reserved = 0 WHERE id = ?", (order_id,))
    return True


#APPLY_CHECKOUT_COUPON
def apply_checkout_coupon(order_items, coupon):
    if coupon != "DECANTS5":
        return 0.0

    discount = 0.0
    for item in order_items:
        original_subtotal = item["subtotal"]
        item["unit_price"] = round(item["unit_price"] * 0.95, 2)
        item["subtotal"] = round(item["unit_price"] * item["quantity"], 2)
        discount += original_subtotal - item["subtotal"]

    return round(discount, 2)


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


#BUILD_ADMIN_ORDER_MESSAGE
def build_admin_order_message(reference, customer_name="", total=0):
    lines = [
        "Pagamento aprovado na Decant's Perfumaria.",
        f"Pedido: {reference}",
    ]
    if customer_name:
        lines.append(f"Cliente: {customer_name}")
    if total:
        lines.append(f"Total: R$ {money_to_brl(total)}")
    lines.append("Status: para separar")
    return "\n".join(lines)


#SEND_ADMIN_WHATSAPP_NOTIFICATION
def send_admin_whatsapp_notification(reference, customer_name="", total=0):
    if not WHATSAPP_CLOUD_TOKEN or not WHATSAPP_CLOUD_PHONE_NUMBER_ID or not WHATSAPP_ADMIN_NUMBER:
        return False

    body = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_ADMIN_NUMBER,
            "type": "text",
            "text": {"preview_url": False, "body": build_admin_order_message(reference, customer_name, total)},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = request.Request(
        f"https://graph.facebook.com/v19.0/{WHATSAPP_CLOUD_PHONE_NUMBER_ID}/messages",
        data=body,
        headers={
            "Authorization": f"Bearer {WHATSAPP_CLOUD_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=12):
            return True
    except Exception as exc:
        print(f"Falha ao enviar WhatsApp administrativo do pedido {reference}: {exc}")
        return False


#CREATE_MERCADO_PAGO_PREFERENCE
def create_mercado_pago_preference(reference, customer, items, total, base_url):
    if not mercado_pago_configured():
        raise ValueError("Mercado Pago nao configurado com Access Token de producao/teste.")
    if not is_public_base_url(base_url):
        raise ValueError("Configure DECANTS_PUBLIC_BASE_URL com o dominio publico da loja para pagar pelo Mercado Pago.")

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
        "back_urls": {
            "success": f"{base_url}/index.html?pedido={reference}&pagamento=aprovado",
            "failure": f"{base_url}/index.html?pedido={reference}&pagamento=recusado",
            "pending": f"{base_url}/index.html?pedido={reference}&pagamento=pendente",
        },
        "auto_return": "approved",
        "notification_url": f"{base_url}/api/payments/webhook",
        "payment_methods": {
            "installments": 6
        },
    }

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
            validate_mercado_pago_owner(data)
            payment_url = data.get("init_point") or data.get("sandbox_init_point") or ""
            preference_id = str(data.get("id") or "")
            if not payment_url or not preference_id:
                raise ValueError("Mercado Pago criou uma preferencia sem link de pagamento.")
            return {"id": preference_id, "url": payment_url}
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
        return False

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


#CHECK_PASSWORD
def check_password(password):
    password_bytes = password.encode("utf-8")
    if ADMIN_PASSWORD_HASH:
        if bcrypt is None:
            return False
        try:
            return bcrypt.checkpw(password_bytes, ADMIN_PASSWORD_HASH.encode("utf-8"))
        except ValueError:
            return False

    # Fallback only keeps local development usable. Production should set
    # DECANTS_ADMIN_PASSWORD_HASH with a bcrypt hash and remove plaintext secrets.
    return hmac.compare_digest(password, ADMIN_PASSWORD)


#CREATE_CSRF_TOKEN
def create_csrf_token():
    return secrets.token_urlsafe(32)


#SAFE_UPLOAD_NAME
def safe_upload_name(filename):
    stem = Path(filename or "produto").stem
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        suffix = ".png"
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-").lower() or "produto"
    return f"{int(time.time())}-{secrets.token_hex(4)}-{stem}{suffix}"


#PARSE_MULTIPART_IMAGE
def parse_multipart_image(headers, body):
    content_type = headers.get("Content-Type", "")
    message_bytes = (
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        + body
    )
    message = BytesParser(policy=policy.default).parsebytes(message_bytes)
    if not message.is_multipart():
        raise ValueError("Envie uma imagem em multipart/form-data.")

    for part in message.iter_parts():
        disposition = part.get_content_disposition()
        if disposition != "form-data":
            continue
        params = dict(part.get_params(header="content-disposition") or [])
        if params.get("name") != "image":
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if not filename or not payload:
            raise ValueError("Imagem obrigatoria.")
        return filename, payload

    raise ValueError("Imagem obrigatoria.")


#ADMIN_CLIENT_IP
def admin_client_ip(handler):
    forwarded = handler.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return handler.client_address[0] if handler.client_address else ""


#RATE_LIMITED
def rate_limited(ip):
    now = time.time()
    attempts = [stamp for stamp in LOGIN_ATTEMPTS.get(ip, []) if stamp > now - LOGIN_WINDOW]
    LOGIN_ATTEMPTS[ip] = attempts
    return len(attempts) >= LOGIN_LIMIT


#REGISTER_FAILED_LOGIN
def register_failed_login(ip):
    now = time.time()
    attempts = [stamp for stamp in LOGIN_ATTEMPTS.get(ip, []) if stamp > now - LOGIN_WINDOW]
    attempts.append(now)
    LOGIN_ATTEMPTS[ip] = attempts


#CLEAR_LOGIN_ATTEMPTS
def clear_login_attempts(ip):
    LOGIN_ATTEMPTS.pop(ip, None)


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
        if self.path.startswith("/api/customer/orders"):
            self.handle_customer_orders()
            return
        if self.path.startswith("/api/orders/"):
            self.handle_get_order()
            return
        if self.path.startswith("/api/session"):
            self.handle_session()
            return
        super().do_GET()

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
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        if host == host_from_setting(ADMIN_DOMAIN) and host != PUBLIC_HOST and path == "/":
            return True
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
                SELECT id, reference, customer_name, customer_email, customer_phone, total, status, created_at, updated_at
                FROM orders ORDER BY created_at DESC
                """
            ).fetchall()
        self.send_json([dict(row) for row in rows])

    #HANDLE_CUSTOMER_ORDERS
    def handle_customer_orders(self):
        query = parse.parse_qs(parse.urlparse(self.path).query)
        contact = str(query.get("contact", [""])[0]).strip()
        email = contact.lower()
        phone = re.sub(r"\D+", "", contact)

        if not contact or (not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) and len(phone) < 10):
            self.send_json({"error": "Informe o e-mail ou WhatsApp usado no pedido."}, status=400)
            return

        where = "LOWER(customer_email) = ?"
        params = [email]
        if len(phone) >= 10:
            where = "customer_phone = ?"
            params = [phone]

        with connect_db() as conn:
            orders = conn.execute(
                f"""
                SELECT id, reference, total, status, payment_url, whatsapp_url, created_at, updated_at
                FROM orders
                WHERE {where}
                ORDER BY created_at DESC
                LIMIT 50
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
        except Exception as error:
            self.send_json({"error": f"Nao foi possivel criar o pagamento: {error}"}, status=502)
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
                total = round(sum(item["subtotal"] for item in order_items), 2)
                payment_url = ""
                payment_preference_id = ""

                cursor = conn.execute(
                    """
                    INSERT INTO orders (
                        reference, customer_name, customer_email, customer_phone, customer_address,
                        total, status, payment_preference_id, payment_url, whatsapp_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference,
                        customer["name"],
                        customer["email"],
                        customer["phone"],
                        customer["address"],
                        total,
                        "creating_payment" if payment_method == "mercado_pago" else "whatsapp_pending",
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
                        "awaiting_payment" if payment_method == "mercado_pago" else "whatsapp_pending",
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
                    "status": "awaiting_payment" if payment_method == "mercado_pago" else "whatsapp_pending",
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
                        SET status = ?, payment_id = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE reference = ?
                        """,
                        (next_status, payment_id, reference),
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
        if payload.get("user") != ADMIN_USER or not check_password(str(payload.get("password", ""))):
            register_failed_login(ip)
            self.log_admin_action("login_failed", "auth", "", payload.get("user", ""))
            self.send_json({"error": "Usuario ou senha invalidos."}, status=401)
            return

        clear_login_attempts(ip)
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = time.time() + SESSION_MAX_AGE
        csrf = self.get_cookie(CSRF_COOKIE) or create_csrf_token()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header(
            "Set-Cookie",
            f"{SESSION_COOKIE}={sign_session(token)}; HttpOnly; {self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}",
        )
        self.send_header("Set-Cookie", f"{CSRF_COOKIE}={csrf}; {self.cookie_same_site()}; Path=/; Max-Age={SESSION_MAX_AGE}")
        self.end_headers()
        self.log_admin_action("login_success", "auth", "", ADMIN_USER)
        self.wfile.write(json.dumps({"ok": True, "user": ADMIN_USER, "csrfToken": csrf}).encode("utf-8"))

    #HANDLE_LOGOUT
    def handle_logout(self):
        session = self.get_cookie(SESSION_COOKIE)
        if session and "." in session:
            SESSIONS.pop(session.split(".", 1)[0], None)
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
        return verify_session(self.get_cookie(SESSION_COOKIE))

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


#MAIN
def main():
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), DecantsHandler)
    print(f"Decant's Perfumaria rodando em http://localhost:{port}")
    print("Login padrao do admin: decantsperfumaria1@gmail.com / Wellida123")
    print("Em producao, defina DECANTS_ADMIN_USER, DECANTS_ADMIN_PASSWORD e DECANTS_SECRET_KEY.")
    server.serve_forever()


if __name__ == "__main__":
    main()
