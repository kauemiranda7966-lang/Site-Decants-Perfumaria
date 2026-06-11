import base64
import hashlib
import hmac
import secrets
import time

try:
    import bcrypt
except ImportError:
    bcrypt = None


def check_password(password, password_hash="", plain_password=""):
    password_bytes = str(password).encode("utf-8")
    if password_hash:
        if bcrypt is None:
            return False
        try:
            return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
        except ValueError:
            return False
    return bool(plain_password) and hmac.compare_digest(str(password), plain_password)


def sign_session(token, secret_key):
    signature = hmac.new(secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).digest()
    encoded = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{token}.{encoded}"


def create_session(connect_db, secret_key, max_age):
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + int(max_age)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO admin_sessions (token_hash, expires_at) VALUES (?, ?)",
            (token_hash, expires_at),
        )
    return sign_session(token, secret_key)


def verify_session(connect_db, value, secret_key):
    if not value or "." not in value or not secret_key:
        return False

    token, signature = value.rsplit(".", 1)
    expected = sign_session(token, secret_key).rsplit(".", 1)[1]
    if not hmac.compare_digest(signature, expected):
        return False

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = int(time.time())
    with connect_db() as conn:
        conn.execute("DELETE FROM admin_sessions WHERE expires_at <= ?", (now,))
        session = conn.execute(
            "SELECT expires_at FROM admin_sessions WHERE token_hash = ?",
            (token_hash,),
        ).fetchone()
    return bool(session and int(session["expires_at"]) > now)


def revoke_session(connect_db, value, secret_key):
    if not value or "." not in value or not secret_key:
        return

    token, signature = value.rsplit(".", 1)
    expected = sign_session(token, secret_key).rsplit(".", 1)[1]
    if not hmac.compare_digest(signature, expected):
        return

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect_db() as conn:
        conn.execute("DELETE FROM admin_sessions WHERE token_hash = ?", (token_hash,))
