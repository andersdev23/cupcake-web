"""Sweet Bloom PI II. Python 3.10+; somente biblioteca padrão."""
from http.server import ThreadingHTTPServer
from pathlib import Path
import argparse
import os
import secrets
import socket
from backend.models import Database
from backend.services import ShopService
from backend.controllers import AdminSessions, make_handler

ROOT = Path(__file__).resolve().parent


class ShopServer(ThreadingHTTPServer):
    def server_bind(self):
        if os.name == 'nt':
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def admin_password():
    configured = os.environ.get('SWEETBLOOM_ADMIN_PASSWORD')
    if configured:
        if len(configured) < 8:
            raise ValueError('SWEETBLOOM_ADMIN_PASSWORD precisa ter ao menos 8 caracteres.')
        return configured
    password_file = ROOT / 'data' / 'admin-password.txt'
    password_file.parent.mkdir(parents=True, exist_ok=True)
    if not password_file.exists():
        password_file.write_text(secrets.token_urlsafe(18), encoding='utf-8')
        password_file.chmod(0o600)
    return password_file.read_text(encoding='utf-8').strip()


def create_server(port=8010):
    database = Database(os.environ.get('SWEETBLOOM_DB', ROOT / 'data' / 'sweetbloom.sqlite3'))
    database.initialize()
    return ShopServer(('127.0.0.1', port), make_handler(ROOT, ShopService(database), AdminSessions(admin_password())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sweet Bloom — servidor local do PI II')
    parser.add_argument('--port', type=int, default=8010)
    parser.add_argument('--show-admin-password', action='store_true')
    args = parser.parse_args()
    if args.show_admin_password:
        print(admin_password())
    else:
        try:
            server = create_server(args.port)
            print(f'Sweet Bloom: http://127.0.0.1:{server.server_port}', flush=True)
            print(f'Painel: http://127.0.0.1:{server.server_port}/admin.html', flush=True)
            print('Senha: execute python app.py --show-admin-password ou veja data/admin-password.txt', flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        except (OSError, ValueError) as error:
            parser.exit(1, f'Não foi possível iniciar: {error}\n')
