"""Controller HTTP: rotas, autenticação, sessão e serialização JSON."""
from http.server import SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
import hashlib
import hmac
import json
import secrets
import sqlite3
import threading
import time
from .services import BusinessError


class AdminSessions:
    def __init__(self, password):
        self.password_hash = hashlib.sha256(password.encode()).digest()
        self.sessions = {}
        self.attempts = {}
        self.lock = threading.Lock()

    def login(self, password, ip):
        now = time.monotonic()
        with self.lock:
            attempts = [stamp for stamp in self.attempts.get(ip, []) if now - stamp < 300]
            self.attempts[ip] = attempts
            if len(attempts) >= 5:
                raise BusinessError('Muitas tentativas. Aguarde cinco minutos para tentar novamente.', 429)
            valid = isinstance(password, str) and len(password) <= 256 and hmac.compare_digest(hashlib.sha256(password.encode()).digest(), self.password_hash)
            if not valid:
                attempts.append(now)
                raise BusinessError('Senha de administração incorreta.', 401)
            self.attempts.pop(ip, None)
            self.sessions = {key: item for key, item in self.sessions.items() if item['expires'] > now}
            token = secrets.token_urlsafe(32)
            session = {'csrf': secrets.token_urlsafe(24), 'expires': now + 7200}
            self.sessions[token] = session
            return token, session

    def find(self, token):
        with self.lock:
            session = self.sessions.get(token)
            if session and session['expires'] > time.monotonic():
                return session
            self.sessions.pop(token, None)
            return None


def make_handler(root, service, sessions):
    root = Path(root).resolve()

    class ShopHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'same-origin')
            super().end_headers()

        def log_message(self, fmt, *args):
            # Do not log query strings, customer bodies, credentials or tokens.
            if args:
                print(self.command, urlparse(self.path).path, flush=True)

        def respond(self, status, data, cookie=None):
            body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            if cookie:
                self.send_header('Set-Cookie', cookie)
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)

        def payload(self):
            if self.headers.get_content_type() != 'application/json':
                raise BusinessError('Envie os dados como JSON.', 415)
            try:
                size = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                raise BusinessError('Tamanho da solicitação inválido.')
            if not 0 < size <= 32000:
                raise BusinessError('Solicitação vazia ou grande demais.', 413)
            try:
                value = json.loads(self.rfile.read(size))
                if not isinstance(value, dict):
                    raise ValueError()
                return value
            except (ValueError, UnicodeDecodeError):
                raise BusinessError('JSON inválido.')

        def session_token(self):
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get('Cookie', ''))
                return cookie['sweetbloom_session'].value if 'sweetbloom_session' in cookie else ''
            except Exception:
                return ''

        def authenticated(self, mutation=False):
            session = sessions.find(self.session_token())
            if not session:
                raise BusinessError('Sua sessão expirou. Entre novamente.', 401)
            if mutation and not hmac.compare_digest(self.headers.get('X-CSRF-Token', ''), session['csrf']):
                raise BusinessError('Sessão inválida. Atualize a página e entre novamente.', 403)
            return session

        def same_origin(self):
            origin = self.headers.get('Origin')
            expected = {'http://127.0.0.1:' + str(self.server.server_port), 'http://localhost:' + str(self.server.server_port)}
            if (origin and origin not in expected) or self.headers.get('Sec-Fetch-Site') == 'cross-site':
                raise BusinessError('Origem da solicitação não permitida.', 403)

        def static_allowed(self):
            path = unquote(urlparse(self.path).path)
            if path in ('/', '/index.html', '/produtos.html', '/carrinho.html', '/checkout.html', '/admin.html'):
                return True
            parts = Path(path.lstrip('/')).parts
            target = (root / path.lstrip('/')).resolve()
            return (bool(parts) and parts[0] in ('css', 'js', 'assets') and target.is_relative_to(root)
                    and target.suffix.lower() in ('.css', '.js', '.svg', '.png', '.jpg', '.webp', '.woff2', '.ttf'))

        def do_HEAD(self):
            if not self.static_allowed():
                self.respond(404, {'error': 'Recurso não encontrado.'}); return
            super().do_HEAD()

        def list_directory(self, path):
            self.respond(404, {'error': 'Recurso não encontrado.'})

        def do_GET(self):
            path = urlparse(self.path).path
            try:
                if path == '/api/products':
                    self.respond(200, {'products': service.database.products()}); return
                if path == '/api/admin/session':
                    session = sessions.find(self.session_token())
                    self.respond(200, {'authenticated': bool(session), 'csrf': session['csrf'] if session else ''}); return
                if path == '/api/admin/products':
                    self.authenticated()
                    self.respond(200, {'products': service.database.products(True)}); return
                if path == '/api/admin/orders':
                    self.authenticated()
                    query = parse_qs(urlparse(self.path).query)
                    try:
                        page = int(query.get('page', ['1'])[0])
                    except ValueError:
                        raise BusinessError('Página inválida.')
                    self.respond(200, service.orders(query.get('status', ['todos'])[0], query.get('q', [''])[0], page)); return
                if path.startswith('/api/') or not self.static_allowed():
                    self.respond(404, {'error': 'Recurso não encontrado.'}); return
                super().do_GET()
            except BusinessError as error:
                self.respond(error.status, {'error': str(error)})
            except sqlite3.Error:
                self.respond(503, {'error': 'O banco está temporariamente indisponível. Tente novamente.'})

        def do_POST(self):
            try:
                self.same_origin()
                path = urlparse(self.path).path
                data = self.payload()
                if path == '/api/quote':
                    self.respond(200, service.quote(data)); return
                if path == '/api/orders':
                    order, replayed = service.place_order(data, self.headers.get('Idempotency-Key', ''))
                    # Return a receipt only to the caller; listing personal data requires login.
                    self.respond(200 if replayed else 201, {'order': order, 'replayed': replayed}); return
                if path == '/api/admin/login':
                    token, session = sessions.login(data.get('password'), self.client_address[0])
                    self.respond(200, {'authenticated': True, 'csrf': session['csrf']}, 'sweetbloom_session=' + token + '; Path=/; HttpOnly; SameSite=Strict; Max-Age=7200'); return
                if path == '/api/admin/logout':
                    self.authenticated(True)
                    with sessions.lock:
                        sessions.sessions.pop(self.session_token(), None)
                    self.respond(200, {'ok': True}, 'sweetbloom_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'); return
                raise BusinessError('Recurso não encontrado.', 404)
            except BusinessError as error:
                self.respond(error.status, {'error': str(error)})
            except sqlite3.Error:
                self.respond(503, {'error': 'Não foi possível salvar agora. Tente novamente; o identificador evita pedidos duplicados.'})

        def do_PATCH(self):
            try:
                self.same_origin()
                self.authenticated(True)
                data = self.payload()
                parts = urlparse(self.path).path.strip('/').split('/')
                if len(parts) != 4 or parts[:2] != ['api', 'admin'] or not parts[3].isdigit():
                    raise BusinessError('Recurso não encontrado.', 404)
                if parts[2] == 'orders':
                    self.respond(200, {'order': service.change_status(int(parts[3]), data)}); return
                if parts[2] == 'products':
                    self.respond(200, {'product': service.update_product(int(parts[3]), data)}); return
                raise BusinessError('Recurso não encontrado.', 404)
            except BusinessError as error:
                self.respond(error.status, {'error': str(error)})
            except sqlite3.Error:
                self.respond(503, {'error': 'Não foi possível atualizar agora. Tente novamente.'})

    return ShopHandler
