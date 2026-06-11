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

from decants_auth import (
    check_password as verify_admin_password,
    create_session as create_admin_session,
    revoke_session as revoke_admin_session,
    verify_session as verify_admin_session,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT / "data" / "decants.sqlite3"
SESSION_COOKIE = "decants_session"
CSRF_COOKIE = "decants_csrf"
SESSION_MAX_AGE = 60 * 60 * 8
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

DB_PATH = Path(os.environ.get("DECANTS_DB_PATH", DEFAULT_DB_PATH))
UPLOAD_DIR = Path(os.environ.get("DECANTS_UPLOAD_DIR", ROOT / "img" / "uploads"))
ADMIN_USER = os.environ.get("DECANTS_ADMIN_USER", "").strip()
ADMIN_PASSWORD = os.environ.get("DECANTS_ADMIN_PASSWORD", "")
ADMIN_PASSWORD_HASH = os.environ.get("DECANTS_ADMIN_PASSWORD_HASH", "")
SECRET_KEY = os.environ.get("DECANTS_SECRET_KEY", "")
STORE_WHATSAPP_NUMBER = re.sub(r"\D+", "", os.environ.get("DECANTS_WHATSAPP_NUMBER", "558899641605"))
ADMIN_DOMAIN = os.environ.get("DECANTS_ADMIN_DOMAIN", "admin.decantperfumaria.com.br")
MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", "")
MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY", "")
MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET", "")
MERCADO_PAGO_COLLECTOR_ID = os.environ.get("MERCADO_PAGO_COLLECTOR_ID", "").strip()
try:
    SHIPPING_FEE = max(0.0, float(os.environ.get("DECANTS_SHIPPING_FEE", "19.90").replace(",", ".")))
except ValueError:
    SHIPPING_FEE = 19.90
try:
    FREE_SHIPPING_THRESHOLD = max(
        0.0, float(os.environ.get("DECANTS_FREE_SHIPPING_THRESHOLD", "300").replace(",", "."))
    )
except ValueError:
    FREE_SHIPPING_THRESHOLD = 300.0
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
IS_PRODUCTION = (
    os.environ.get("DECANTS_ENV", "").strip().lower() == "production"
    or bool(os.environ.get("RENDER"))
)


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
                customer_postal_code TEXT NOT NULL DEFAULT '',
                product_amount REAL NOT NULL DEFAULT 0,
                shipping_amount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                payment_method TEXT NOT NULL DEFAULT '',
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
        if "customer_postal_code" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN customer_postal_code TEXT NOT NULL DEFAULT ''")
        if "product_amount" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN product_amount REAL NOT NULL DEFAULT 0")
        if "shipping_amount" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN shipping_amount REAL NOT NULL DEFAULT 0")
        if "payment_method" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT NOT NULL DEFAULT ''")
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token_hash TEXT PRIMARY KEY,
                expires_at INTEGER NOT NULL,
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
    script = (ROOT / "js" / "catalog-data.js").read_text(encoding="utf-8")
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
    postal_code = re.sub(r"\D+", "", str(customer.get("postalCode", "")))
    items = payload.get("items") or []
    coupon = str(payload.get("coupon", "")).strip().upper()
    payment_method = str(payload.get("paymentMethod", "mercado_pago")).strip()

    normalized_name = re.sub(r"\s+", " ", name)
    name_parts = normalized_name.split()
    inappropriate_names = {
        "admin", "administrador", "teste", "test", "null", "undefined",
        "palavrao", "xingamento", "porra", "caralho", "merda", "puta",
        "puto", "foda", "fdp",
    }
    if (
        len(normalized_name) < 5
        or len(name_parts) < 2
        or any(len(part) < 2 for part in name_parts)
        or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ ]+", normalized_name)
        or any(part.lower() in inappropriate_names for part in name_parts)
    ):
        raise ValueError("Informe o nome completo.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(phone) not in {10, 11} or len(set(phone)) == 1:
        raise ValueError("Informe um WhatsApp com DDD.")
    if len(postal_code) != 8 or len(set(postal_code)) == 1:
        raise ValueError("Informe um CEP valido com 8 digitos.")
    if (
        len(address) < 10
        or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ,.\/-]+", address)
        or not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", address)
        or not re.search(r"\d", address)
    ):
        raise ValueError("Informe endereco completo com rua, numero, bairro e cidade.")
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
        "customer": {
            "name": normalized_name,
            "email": email,
            "phone": phone,
            "address": re.sub(r"\s+", " ", address),
            "postal_code": postal_code,
        },
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

    preference_items = [
        {
            "id": str(item["product_id"]),
            "title": f"{item['product_name']} {item['volume']}ml",
            "quantity": item["quantity"],
            "currency_id": "BRL",
            "unit_price": item["unit_price"],
        }
        for item in items
    ]
    products_total = round(sum(item["subtotal"] for item in items), 2)
    shipping_amount = round(max(0.0, total - products_total), 2)
    if shipping_amount:
        preference_items.append(
            {
                "id": "shipping",
                "title": "Frete",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": shipping_amount,
            }
        )

    preference = {
        "external_reference": reference,
        "items": preference_items,
        "payer": {
            "name": customer["name"],
            "email": customer["email"],
            "phone": {"number": customer["phone"]},
            "address": {
                "zip_code": customer["postal_code"],
                "street_name": customer["address"],
            },
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


#BUILD_SHIPPING_LABEL_PDF
def build_shipping_label_pdf(order, items):
    def clean(value):
        text = str(value or "").encode("latin-1", errors="replace").decode("latin-1")
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = [
        ("ETIQUETA DE ENVIO", 18),
        ("DECANT'S PERFUMARIA", 12),
        ("", 10),
        (f"PEDIDO: {order['reference']}", 14),
        (f"DESTINATARIO: {order['customer_name']}", 12),
        (f"TELEFONE: {order['customer_phone']}", 11),
        (f"CEP: {order['customer_postal_code']}", 14),
        ("ENDERECO:", 11),
    ]
    address_words = str(order["customer_address"] or "").split()
    address_lines = []
    current = ""
    for word in address_words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > 62 and current:
            address_lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        address_lines.append(current)
    lines.extend((line, 11) for line in address_lines[:4])
    lines.extend([
        ("", 10),
        (f"VOLUMES/ITENS: {sum(int(item['quantity']) for item in items)}", 11),
        (f"VALOR DO PEDIDO: R$ {float(order['total']):.2f}".replace(".", ","), 11),
        ("", 10),
        ("REMETENTE: DECANT'S PERFUMARIA", 11),
        (f"PEDIDO {order['reference']} - NAO DOBRAR", 10),
    ])

    commands = ["BT", "/F1 12 Tf", "48 790 Td"]
    for index, (text, size) in enumerate(lines):
        if index:
            commands.append("0 -28 Td")
        commands.extend([f"/F1 {size} Tf", f"({clean(text)}) Tj"])
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


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


def validate_runtime_config():
    errors = []
    admin_configured = bool(ADMIN_USER or ADMIN_PASSWORD or ADMIN_PASSWORD_HASH or SECRET_KEY)
    if IS_PRODUCTION or admin_configured:
        if not ADMIN_USER:
            errors.append("DECANTS_ADMIN_USER")
        if not ADMIN_PASSWORD_HASH and not (ADMIN_PASSWORD and not IS_PRODUCTION):
            errors.append("DECANTS_ADMIN_PASSWORD_HASH")
        if not SECRET_KEY or len(SECRET_KEY) < 32:
            errors.append("DECANTS_SECRET_KEY (minimo de 32 caracteres)")
        if IS_PRODUCTION and ADMIN_PASSWORD:
            errors.append("remova DECANTS_ADMIN_PASSWORD e use apenas DECANTS_ADMIN_PASSWORD_HASH")
    if errors:
        raise RuntimeError("Configuracao administrativa insegura: " + ", ".join(errors))



from decants_handler import DecantsHandler

#MAIN
def main():
    validate_runtime_config()
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), DecantsHandler)
    print(f"Decant's Perfumaria rodando em http://localhost:{port}")
    if ADMIN_USER:
        print("Painel administrativo protegido por credenciais configuradas no ambiente.")
    else:
        print("Painel administrativo desativado ate configurar as variaveis DECANTS_ADMIN_*.")
    server.serve_forever()


if __name__ == "__main__":
    main()
