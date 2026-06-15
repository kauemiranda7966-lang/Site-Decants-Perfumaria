import hashlib
import hmac
import http.server
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import threading
import time
from http import cookies
from pathlib import Path
from urllib import error, parse, request
from urllib.parse import unquote

from decants_auth import (
    check_password as verify_admin_password,
    create_customer_session,
    create_session as create_admin_session,
    revoke_session as revoke_admin_session,
    verify_customer_session,
    verify_session as verify_admin_session,
)
from decants_pdf import build_pdf_pages, build_simple_pdf
from decants_uploads import parse_multipart_image, safe_upload_name
from decants_validation import (
    money_to_brl,
    normalize_checkout,
    normalize_lead,
    normalize_product,
    parse_price,
    product_from_row,
    valid_brazilian_document,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = ROOT / "data" / "decants.sqlite3"
SESSION_COOKIE = "decants_session"
CUSTOMER_SESSION_COOKIE = "decants_customer_session"
CSRF_COOKIE = "decants_csrf"
SESSION_MAX_AGE = 60 * 60 * 8
CUSTOMER_SESSION_MAX_AGE = 60 * 60 * 24 * 30
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
PRIVATE_UPLOAD_DIR = Path(
    os.environ.get("DECANTS_PRIVATE_UPLOAD_DIR", DB_PATH.parent / "private-uploads")
)
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
MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS = max(
    60, int(os.environ.get("MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS", "300"))
)
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
try:
    WHATSAPP_RESERVATION_MINUTES = max(
        5, int(os.environ.get("DECANTS_WHATSAPP_RESERVATION_MINUTES", "30"))
    )
except ValueError:
    WHATSAPP_RESERVATION_MINUTES = 30
try:
    SQLITE_BUSY_TIMEOUT_SECONDS = max(
        1, int(os.environ.get("DECANTS_SQLITE_BUSY_TIMEOUT_SECONDS", "15"))
    )
except ValueError:
    SQLITE_BUSY_TIMEOUT_SECONDS = 15
try:
    SQLITE_WRITE_RETRIES = max(
        0, min(5, int(os.environ.get("DECANTS_SQLITE_WRITE_RETRIES", "2")))
    )
except ValueError:
    SQLITE_WRITE_RETRIES = 2
SQLITE_BACKUP_DIR = Path(
    os.environ.get("DECANTS_SQLITE_BACKUP_DIR", DB_PATH.parent / "backups")
)
try:
    SQLITE_BACKUP_INTERVAL_HOURS = max(
        1, int(os.environ.get("DECANTS_SQLITE_BACKUP_INTERVAL_HOURS", "24"))
    )
except ValueError:
    SQLITE_BACKUP_INTERVAL_HOURS = 24
try:
    SQLITE_BACKUP_RETENTION_DAYS = max(
        1, int(os.environ.get("DECANTS_SQLITE_BACKUP_RETENTION_DAYS", "7"))
    )
except ValueError:
    SQLITE_BACKUP_RETENTION_DAYS = 7
try:
    MAX_REQUEST_THREADS = max(
        4, min(256, int(os.environ.get("DECANTS_MAX_REQUEST_THREADS", "64")))
    )
except ValueError:
    MAX_REQUEST_THREADS = 64
WHATSAPP_CLOUD_TOKEN = os.environ.get("WHATSAPP_CLOUD_TOKEN", "")
WHATSAPP_CLOUD_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_PHONE_NUMBER_ID", "")
WHATSAPP_ADMIN_NUMBER = re.sub(r"\D+", "", os.environ.get("WHATSAPP_ADMIN_NUMBER", STORE_WHATSAPP_NUMBER))
PUBLIC_BASE_URL = os.environ.get("DECANTS_PUBLIC_BASE_URL", "")
BUSINESS_TRADE_NAME = os.environ.get("DECANTS_BUSINESS_TRADE_NAME", "Decant's Perfumaria").strip()
BUSINESS_LEGAL_NAME = os.environ.get("DECANTS_BUSINESS_LEGAL_NAME", "").strip()
BUSINESS_TAX_ID = os.environ.get("DECANTS_BUSINESS_TAX_ID", "").strip()
BUSINESS_ADDRESS = os.environ.get("DECANTS_BUSINESS_ADDRESS", "").strip()
BUSINESS_POSTAL_CODE = re.sub(
    r"\D+", "", os.environ.get("DECANTS_BUSINESS_POSTAL_CODE", "")
)
BUSINESS_EMAIL = os.environ.get("DECANTS_BUSINESS_EMAIL", "").strip()
try:
    RETENTION_ORDER_DAYS = max(365, int(os.environ.get("DECANTS_RETENTION_ORDER_DAYS", "1825")))
except ValueError:
    RETENTION_ORDER_DAYS = 1825
try:
    RETENTION_LEAD_DAYS = max(30, int(os.environ.get("DECANTS_RETENTION_LEAD_DAYS", "730")))
except ValueError:
    RETENTION_LEAD_DAYS = 730
try:
    RETENTION_LOG_DAYS = max(30, int(os.environ.get("DECANTS_RETENTION_LOG_DAYS", "365")))
except ValueError:
    RETENTION_LOG_DAYS = 365
try:
    RETENTION_ATTACHMENT_DAYS = max(
        30, int(os.environ.get("DECANTS_RETENTION_ATTACHMENT_DAYS", "180"))
    )
except ValueError:
    RETENTION_ATTACHMENT_DAYS = 180


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

    conn = sqlite3.connect(db_path, timeout=SQLITE_BUSY_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_SECONDS * 1000}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def begin_immediate(conn, retries=None):
    retry_count = SQLITE_WRITE_RETRIES if retries is None else max(0, int(retries))
    for attempt in range(retry_count + 1):
        try:
            conn.execute("BEGIN IMMEDIATE")
            return
        except sqlite3.OperationalError as exc:
            message = str(exc).lower()
            if ("locked" not in message and "busy" not in message) or attempt >= retry_count:
                raise
            time.sleep(0.1 * (attempt + 1))


def backup_database():
    SQLITE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    destination_path = SQLITE_BACKUP_DIR / f"decants-{timestamp}.sqlite3"
    temporary_path = destination_path.with_suffix(".tmp")

    source = connect_db()
    destination = sqlite3.connect(temporary_path)
    try:
        source.backup(destination)
        destination.commit()
    finally:
        destination.close()
        source.close()
    temporary_path.replace(destination_path)

    cutoff = time.time() - (SQLITE_BACKUP_RETENTION_DAYS * 24 * 60 * 60)
    for backup_path in SQLITE_BACKUP_DIR.glob("decants-*.sqlite3"):
        if backup_path.stat().st_mtime < cutoff:
            backup_path.unlink()
    return destination_path


def start_backup_worker():
    if not IS_PRODUCTION:
        return None

    def worker():
        while True:
            try:
                backup_path = backup_database()
                print(f"Backup SQLite criado em {backup_path}")
                retention = apply_retention_policy()
                print(f"Politica de retencao executada: {retention}")
            except Exception as exc:
                print(f"Falha na manutencao programada: {exc}")
            time.sleep(SQLITE_BACKUP_INTERVAL_HOURS * 60 * 60)

    thread = threading.Thread(target=worker, name="sqlite-backup", daemon=True)
    thread.start()
    return thread


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
                customer_document TEXT NOT NULL DEFAULT '',
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
                payment_risk_status TEXT NOT NULL DEFAULT '',
                payment_risk_reason TEXT NOT NULL DEFAULT '',
                payment_risk_event_id TEXT NOT NULL DEFAULT '',
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
        if "customer_document" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN customer_document TEXT NOT NULL DEFAULT ''")
        if "product_amount" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN product_amount REAL NOT NULL DEFAULT 0")
        if "shipping_amount" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN shipping_amount REAL NOT NULL DEFAULT 0")
        if "payment_method" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT NOT NULL DEFAULT ''")
        if "payment_risk_status" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_risk_status TEXT NOT NULL DEFAULT ''")
        if "payment_risk_reason" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_risk_reason TEXT NOT NULL DEFAULT ''")
        if "payment_risk_event_id" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_risk_event_id TEXT NOT NULL DEFAULT ''")
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_id TEXT NOT NULL,
                payment_id TEXT NOT NULL DEFAULT '',
                order_id INTEGER,
                status TEXT NOT NULL DEFAULT 'received',
                details TEXT NOT NULL DEFAULT '',
                payload TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_type, event_id),
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_payment_alerts_order ON payment_alerts(order_id, created_at)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol TEXT NOT NULL UNIQUE,
                request_type TEXT NOT NULL,
                order_id INTEGER,
                customer_name TEXT NOT NULL DEFAULT '',
                customer_email TEXT NOT NULL,
                customer_phone TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                details TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                resolution TEXT NOT NULL DEFAULT '',
                reverse_code TEXT NOT NULL DEFAULT '',
                refund_id TEXT NOT NULL DEFAULT '',
                refund_status TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                stored_name TEXT NOT NULL UNIQUE,
                original_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(request_id) REFERENCES service_requests(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_service_requests_customer ON service_requests(customer_email, customer_phone)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status, created_at)"
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
    if IS_PRODUCTION and payment.get("live_mode") is not True:
        raise ValueError("Pagamento de teste recebido no ambiente de producao.")
    reference = str(payment.get("external_reference") or "").strip()
    if reference != order["reference"]:
        raise ValueError("Referencia do pagamento nao corresponde ao pedido.")

    payer = payment.get("payer") if isinstance(payment, dict) else {}
    payer_email = str((payer or {}).get("email") or "").strip().lower()
    if payer_email and payer_email != str(order["customer_email"]).strip().lower():
        raise ValueError("E-mail do pagador nao corresponde ao pedido.")

    amount = payment_amount(payment)
    if amount <= 0:
        raise ValueError("Pagamento sem valor confirmado.")
    if abs(amount - float(order["total"])) > 0.01:
        raise ValueError("Valor pago nao corresponde ao total do pedido.")
    currency = str(payment.get("currency_id") or "").strip().upper()
    if currency and currency != "BRL":
        raise ValueError("Moeda do pagamento nao corresponde a BRL.")


#PRODUCT_PRICE
def product_price(product, volume):
    promo_key = "precoPromocional10" if volume == 10 else "precoPromocional5"
    base_key = "preco10" if volume == 10 else "preco5"
    price = product[promo_key] if product["promocao"] and product[promo_key] else product[base_key]
    return parse_price(price)


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
    result = conn.execute(
        """
        UPDATE orders
        SET stock_reserved = 0
        WHERE id = ? AND stock_reserved = 1
        """,
        (order_id,),
    )
    if result.rowcount == 0:
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

    return True


def release_expired_whatsapp_reservations(conn, max_age_minutes=None):
    max_age = int(max_age_minutes or WHATSAPP_RESERVATION_MINUTES)
    query = """
        SELECT id, status
        FROM orders
        WHERE payment_method = 'WhatsApp'
          AND status = 'whatsapp_pending'
          AND stock_reserved = 1
          AND updated_at <= datetime('now', ?)
    """
    age_parameter = (f"-{max_age} minutes",)
    expired_orders = conn.execute(query, age_parameter).fetchall()
    if not expired_orders:
        return 0

    if not conn.in_transaction:
        begin_immediate(conn)
        expired_orders = conn.execute(query, age_parameter).fetchall()

    released = 0
    for order in expired_orders:
        if not release_order_stock(conn, order["id"]):
            continue
        conn.execute(
            """
            UPDATE orders
            SET status = 'expired', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (order["id"],),
        )
        conn.execute(
            """
            INSERT INTO order_history (order_id, old_status, new_status, note, admin_user)
            VALUES (?, ?, 'expired', ?, '')
            """,
            (
                order["id"],
                order["status"],
                f"Reserva via WhatsApp expirada apos {max_age} minutos.",
            ),
        )
        released += 1

    return released


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
    return send_admin_whatsapp_text(
        build_admin_order_message(reference, customer_name, total),
        f"pedido {reference}",
    )


def send_admin_payment_risk_notification(reference, reason, event_id):
    message = "\n".join(
        [
            "ALERTA FINANCEIRO - ENVIO BLOQUEADO",
            f"Pedido: {reference}",
            f"Motivo: {reason}",
            f"Evento Mercado Pago: {event_id}",
            "Acesse o painel e nao envie o pedido antes da analise.",
        ]
    )
    return send_admin_whatsapp_text(message, f"alerta do pedido {reference}")


def send_admin_whatsapp_text(message, context="notificacao"):
    if not WHATSAPP_CLOUD_TOKEN or not WHATSAPP_CLOUD_PHONE_NUMBER_ID or not WHATSAPP_ADMIN_NUMBER:
        return False

    body = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": WHATSAPP_ADMIN_NUMBER,
            "type": "text",
            "text": {"preview_url": False, "body": str(message)[:4000]},
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
        print(f"Falha ao enviar WhatsApp administrativo ({context}): {exc}")
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
            "identification": {
                "type": "CNPJ" if len(customer["document"]) == 14 else "CPF",
                "number": customer["document"],
            },
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
    if not BUSINESS_TAX_ID or not BUSINESS_ADDRESS or not BUSINESS_POSTAL_CODE:
        raise ValueError(
            "Configure CNPJ/CPF, endereco e CEP empresarial para gerar o kit de expedicao."
        )

    def wrap(value, width=72):
        words = str(value or "").split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > width and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines or [""]

    sender = BUSINESS_LEGAL_NAME or BUSINESS_TRADE_NAME
    label_lines = [
        ("ETIQUETA DE ENDERECAMENTO", 18),
        ("DOCUMENTO AUXILIAR - SEM FRANQUIA OU RASTREAMENTO", 9),
        ("", 8),
        ("DESTINATARIO", 12),
        (order["customer_name"], 14),
        (f"CPF/CNPJ: {order['customer_document']}", 10),
        (f"TELEFONE: {order['customer_phone']}", 10),
    ]
    label_lines.extend((line, 12) for line in wrap(order["customer_address"], 62))
    label_lines.extend([
        (f"CEP: {order['customer_postal_code']}", 16),
        ("", 8),
        ("REMETENTE", 12),
        (sender, 12),
        (f"CPF/CNPJ: {BUSINESS_TAX_ID}", 10),
    ])
    label_lines.extend((line, 10) for line in wrap(BUSINESS_ADDRESS, 68))
    label_lines.extend([
        (f"CEP: {BUSINESS_POSTAL_CODE}", 12),
        ("", 8),
        (f"PEDIDO: {order['reference']}", 12),
        ("ATENCAO: contrate a postagem para obter etiqueta oficial e rastreamento.", 9),
    ])

    declaration_lines = [
        ("DECLARACAO DE CONTEUDO", 18),
        (f"PEDIDO: {order['reference']}", 10),
        ("", 8),
        (f"REMETENTE: {sender}", 11),
        (f"CPF/CNPJ: {BUSINESS_TAX_ID}", 10),
        (f"ENDERECO: {BUSINESS_ADDRESS} - CEP {BUSINESS_POSTAL_CODE}", 9),
        ("", 8),
        (f"DESTINATARIO: {order['customer_name']}", 11),
        (f"CPF/CNPJ: {order['customer_document']}", 10),
        (f"ENDERECO: {order['customer_address']} - CEP {order['customer_postal_code']}", 9),
        ("", 8),
        ("CONTEUDO", 12),
    ]
    for index, item in enumerate(items, 1):
        description = f"{item['product_name']} - decant {item['volume']}ml"
        value = float(item["subtotal"])
        declaration_lines.append(
            (
                f"{index}. {description} | QTD {item['quantity']} | R$ {value:.2f}".replace(".", ","),
                9,
            )
        )
    declaration_lines.extend([
        ("", 8),
        (f"VALOR TOTAL DECLARADO: R$ {float(order['total']):.2f}".replace(".", ","), 11),
        ("", 8),
        (
            "Declaro que o conteudo descrito corresponde ao objeto apresentado para postagem "
            "e assumo responsabilidade pelas informacoes.",
            9,
        ),
        (
            "Esta declaracao nao substitui nota fiscal quando sua emissao for legalmente obrigatoria.",
            9,
        ),
        ("", 12),
        ("LOCAL E DATA: _________________________________________________", 10),
        ("", 12),
        ("ASSINATURA DO REMETENTE: ______________________________________", 10),
    ])
    return build_pdf_pages([label_lines, declaration_lines])


def build_reverse_label_pdf(service_request, order):
    if not BUSINESS_ADDRESS:
        raise ValueError("Configure DECANTS_BUSINESS_ADDRESS para emitir a etiqueta reversa.")
    return build_simple_pdf(
        [
            ("ETIQUETA DE LOGISTICA REVERSA", 18),
            (BUSINESS_TRADE_NAME.upper(), 12),
            ("", 10),
            (f"CODIGO: {service_request['reverse_code']}", 15),
            (f"PROTOCOLO: {service_request['protocol']}", 12),
            (f"PEDIDO: {order['reference']}", 12),
            ("", 10),
            ("DESTINATARIO:", 11),
            (BUSINESS_LEGAL_NAME or BUSINESS_TRADE_NAME, 12),
            (BUSINESS_ADDRESS, 11),
            (f"CNPJ: {BUSINESS_TAX_ID}" if BUSINESS_TAX_ID else "", 10),
            ("", 10),
            ("REMETENTE:", 11),
            (order["customer_name"], 12),
            (order["customer_address"], 11),
            (f"CEP: {order['customer_postal_code']}", 11),
            ("", 10),
            ("Apresente esta etiqueta conforme as instrucoes enviadas pela loja.", 9),
        ]
    )


def refund_mercado_pago_payment(payment_id, idempotency_key):
    if not MERCADO_PAGO_ACCESS_TOKEN:
        raise ValueError("Credencial do Mercado Pago nao configurada.")
    if not payment_id:
        raise ValueError("Pedido sem identificador de pagamento para reembolso.")

    req = request.Request(
        f"https://api.mercadopago.com/v1/payments/{parse.quote(str(payment_id))}/refunds",
        data=b"{}",
        headers={
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Idempotency-Key": idempotency_key,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=15) as response:
            refund = json.loads(response.read().decode("utf-8"))
            refund_id = str(refund.get("id") or "").strip()
            refund_status = str(refund.get("status") or "").strip().lower()
            if not refund_id or refund_status != "approved":
                raise ValueError(
                    f"Mercado Pago nao confirmou o reembolso: {refund_status or 'sem status'}."
                )
            return refund
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"Mercado Pago recusou o reembolso: {detail[:240]}")
    except error.URLError as exc:
        raise ValueError(f"Nao foi possivel conectar ao Mercado Pago: {exc.reason}")


def apply_retention_policy():
    removed_files = []
    with connect_db() as conn:
        begin_immediate(conn)
        attachments = conn.execute(
            """
            SELECT a.id, a.stored_name
            FROM request_attachments a
            JOIN service_requests r ON r.id = a.request_id
            WHERE r.resolved_at <> ''
              AND r.resolved_at <= datetime('now', ?)
            """,
            (f"-{RETENTION_ATTACHMENT_DAYS} days",),
        ).fetchall()
        if attachments:
            ids = [row["id"] for row in attachments]
            placeholders = ",".join("?" for _ in ids)
            conn.execute(f"DELETE FROM request_attachments WHERE id IN ({placeholders})", ids)
            removed_files = [row["stored_name"] for row in attachments]

        conn.execute(
            "DELETE FROM leads WHERE created_at <= datetime('now', ?)",
            (f"-{RETENTION_LEAD_DAYS} days",),
        )
        conn.execute(
            "DELETE FROM admin_logs WHERE created_at <= datetime('now', ?)",
            (f"-{RETENTION_LOG_DAYS} days",),
        )
        conn.execute(
            """
            UPDATE orders
            SET customer_name = 'Cliente anonimizado',
                customer_email = 'anonimizado-' || id || '@invalid.local',
                customer_phone = '',
                customer_address = '',
                customer_postal_code = '',
                customer_document = '',
                payment_url = '',
                whatsapp_url = ''
            WHERE created_at <= datetime('now', ?)
              AND customer_email NOT LIKE 'anonimizado-%@invalid.local'
            """,
            (f"-{RETENTION_ORDER_DAYS} days",),
        )

    for stored_name in removed_files:
        path = PRIVATE_UPLOAD_DIR / stored_name
        if path.exists():
            path.unlink()
    return {"attachmentsDeleted": len(removed_files)}


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


def fetch_mercado_pago_resource(path):
    if not MERCADO_PAGO_ACCESS_TOKEN:
        raise ValueError("Credencial do Mercado Pago nao configurada.")
    safe_path = str(path or "").strip()
    if not safe_path.startswith("/"):
        raise ValueError("Recurso Mercado Pago invalido.")
    req = request.Request(
        f"https://api.mercadopago.com{safe_path}",
        headers={"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"},
        method="GET",
    )
    with request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def payment_id_from_alert(event_type, event_id):
    if event_type == "stop_delivery_op_wh":
        return str(event_id)
    if event_type == "topic_claims_integration_wh":
        claim = fetch_mercado_pago_resource(f"/v1/claims/{parse.quote(str(event_id))}")
        return str(claim.get("resource_id") or claim.get("payment_id") or "")
    if event_type == "topic_chargebacks_wh":
        chargeback = fetch_mercado_pago_resource(f"/v1/chargebacks/{parse.quote(str(event_id))}")
        return str(chargeback.get("payment_id") or chargeback.get("resource_id") or "")
    return ""


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
    try:
        timestamp_value = int(timestamp)
    except ValueError:
        return False
    if timestamp_value > 10_000_000_000:
        timestamp_value //= 1000
    if abs(int(time.time()) - timestamp_value) > MERCADO_PAGO_WEBHOOK_MAX_AGE_SECONDS:
        return False

    data_id = str(query.get("data.id", [""])[0] or payment_id).lower()
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


class DecantsHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    block_on_close = False
    request_queue_size = 128

    def __init__(self, *args, **kwargs):
        self.request_slots = threading.BoundedSemaphore(MAX_REQUEST_THREADS)
        super().__init__(*args, **kwargs)

    def process_request(self, request_socket, client_address):
        self.request_slots.acquire()
        try:
            super().process_request(request_socket, client_address)
        except Exception:
            self.request_slots.release()
            raise

    def process_request_thread(self, request_socket, client_address):
        try:
            super().process_request_thread(request_socket, client_address)
        finally:
            self.request_slots.release()


#MAIN
def main():
    validate_runtime_config()
    init_db()
    start_backup_worker()
    port = int(os.environ.get("PORT", "8000"))
    server = DecantsHTTPServer(("0.0.0.0", port), DecantsHandler)
    print(f"Decant's Perfumaria rodando em http://localhost:{port}")
    if ADMIN_USER:
        print("Painel administrativo protegido por credenciais configuradas no ambiente.")
    else:
        print("Painel administrativo desativado ate configurar as variaveis DECANTS_ADMIN_*.")
    server.serve_forever()


if __name__ == "__main__":
    main()
