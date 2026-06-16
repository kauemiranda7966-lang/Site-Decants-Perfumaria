import os
import re
from pathlib import Path
from urllib import parse


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
