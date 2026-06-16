import hmac
import http.cookies
import json
from pathlib import Path
from urllib import parse
from urllib.parse import unquote

import decants_app as app


class DecantsHTTPMixin:
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

    def translate_path(self, path):
        path = unquote(path.split("?", 1)[0].split("#", 1)[0])
        if path.startswith("/img/uploads/"):
            return str(app.UPLOAD_DIR / Path(path).name)
        parts = [part for part in path.split("/") if part and part not in {".", ".."}]
        return str(app.ROOT.joinpath(*parts))

    def is_public_static_request(self):
        path = parse.urlparse(self.path).path
        if path == "/" or path in self.PUBLIC_FILES:
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

    def end_headers(self):
        path = parse.urlparse(self.path).path
        suffix = Path(path).suffix.lower()
        admin_paths = (
            "/login",
            "/dashboard",
            "/produtos",
            "/pedidos",
            "/clientes",
            "/solicitacoes",
            "/logs",
        )
        if path == "/" or path in self.PUBLIC_FILES or path.startswith(admin_paths):
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
        if app.IS_PRODUCTION:
            directives.append("upgrade-insecure-requests")
        return "; ".join(directives)

    def add_cors_headers(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        if origin not in app.ADMIN_ALLOWED_ORIGINS:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Vary", "Origin")

    def is_admin_host(self):
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        return (
            host in app.ADMIN_HOSTS
            or host.startswith("localhost")
            or host.startswith("127.0.0.1")
        )

    def is_admin_page_request(self):
        if not self.is_admin_host():
            return False
        path = parse.urlparse(self.path).path
        return path in {
            "/login",
            "/dashboard",
            "/produtos",
            "/pedidos",
            "/clientes",
            "/solicitacoes",
            "/logs",
        }

    def serve_admin_app(self):
        content = (app.ROOT / "admin.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def cookie_same_site(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        host = self.headers.get("Host", "")
        same_origin = not origin or origin.endswith(host)
        host_name = host.split(":", 1)[0].lower()
        secure = (
            "; Secure"
            if self.headers.get("X-Forwarded-Proto") == "https"
            or host_name in app.ADMIN_HOSTS
            else ""
        )
        return f"SameSite=Lax{secure}" if same_origin else "SameSite=None; Secure"

    def read_json(self):
        size = int(self.headers.get("Content-Length", 0))
        if size == 0:
            return {}
        return json.loads(self.rfile.read(size).decode("utf-8"))

    def send_json(self, payload, status=200, headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers or []:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def get_cookie(self, name):
        jar = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return jar[name].value if name in jar else ""

    def get_customer_session(self):
        return app.verify_customer_session(
            self.get_cookie(app.CUSTOMER_SESSION_COOKIE),
            app.SECRET_KEY,
        )

    def customer_session_cookie(self, value):
        return (
            f"{app.CUSTOMER_SESSION_COOKIE}={value}; HttpOnly; "
            f"{self.cookie_same_site()}; Path=/; "
            f"Max-Age={app.CUSTOMER_SESSION_MAX_AGE}"
        )

    def is_authenticated(self):
        return app.verify_admin_session(
            app.connect_db,
            self.get_cookie(app.SESSION_COOKIE),
            app.SECRET_KEY,
        )

    def require_auth(self):
        if not self.is_authenticated():
            self.send_json({"error": "Login necessario."}, status=401)
            return False
        return True

    def require_csrf(self):
        expected = self.get_cookie(app.CSRF_COOKIE)
        received = self.headers.get("X-CSRF-Token", "")
        if not expected or not received or not hmac.compare_digest(expected, received):
            self.send_json(
                {"error": "Token CSRF invalido. Recarregue a pagina."},
                status=403,
            )
            return False
        return True

    def log_admin_action(self, action, entity="", entity_id="", details=""):
        try:
            with app.connect_db() as conn:
                conn.execute(
                    """
                    INSERT INTO admin_logs (
                        admin_user, action, entity, entity_id, ip, details
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        app.ADMIN_USER,
                        action,
                        entity,
                        str(entity_id),
                        app.admin_client_ip(self),
                        str(details)[:500],
                    ),
                )
        except Exception as exc:
            print(f"Falha ao gravar log administrativo: {exc}")

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))
