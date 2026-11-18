"""Models e repositório SQLite. Dinheiro é armazenado em centavos inteiros."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3

PRODUCTS = [
    ('chocolate', 'Cupcake Chocolate', 'Massa de cacau com cobertura de ganache.', 1200),
    ('morango', 'Cupcake Morango', 'Massa leve, morangos e chantilly.', 1400),
    ('red-velvet', 'Cupcake Red Velvet', 'Massa red velvet com cream cheese.', 1500),
    ('nutella', 'Cupcake Nutella', 'Massa de avelã com recheio de Nutella.', 1600),
    ('limao', 'Cupcake Limão Siciliano', 'Massa cítrica com lemon curd.', 1300),
    ('amendoim', 'Cupcake Amendoim', 'Chocolate com pasta de amendoim.', 1300),
]


class Database:
    def __init__(self, path):
        self.path = Path(path)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute('PRAGMA foreign_keys=ON')
            with conn:
                yield conn
        finally:
            conn.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY, slug TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                    price_cents INTEGER NOT NULL CHECK(price_cents BETWEEN 1 AND 1000000),
                    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
                );
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE, email TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS addresses (
                    id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
                    street TEXT NOT NULL, neighborhood TEXT NOT NULL,
                    postal_code TEXT NOT NULL DEFAULT '', complement TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY, request_key TEXT NOT NULL UNIQUE,
                    request_hash TEXT NOT NULL, customer_id INTEGER NOT NULL REFERENCES customers(id),
                    address_id INTEGER NOT NULL REFERENCES addresses(id),
                    recipient_name TEXT NOT NULL, recipient_phone TEXT NOT NULL, recipient_email TEXT NOT NULL,
                    payment TEXT NOT NULL CHECK(payment IN ('pix','cartao','debito','dinheiro')),
                    subtotal_cents INTEGER NOT NULL, discount_cents INTEGER NOT NULL,
                    delivery_cents INTEGER NOT NULL, total_cents INTEGER NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'recebido' CHECK(status IN ('recebido','preparando','saiu_entrega','entregue','cancelado')),
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                );
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    product_name TEXT NOT NULL, unit_price_cents INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 99),
                    UNIQUE(order_id, product_id)
                );
                CREATE TABLE IF NOT EXISTS order_history (
                    id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
                    status TEXT NOT NULL, changed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
                );
                CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
                CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);
                CREATE INDEX IF NOT EXISTS idx_history_order ON order_history(order_id);
            ''')
            # Seed only once: changing a product in the panel survives restarts.
            if not db.execute('SELECT 1 FROM products LIMIT 1').fetchone():
                db.executemany('INSERT INTO products(slug,name,description,price_cents) VALUES(?,?,?,?)', PRODUCTS)

    def products(self, include_inactive=False):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM products' + ('' if include_inactive else ' WHERE active=1') + ' ORDER BY id')]

    @staticmethod
    def order(db, order_id):
        row = db.execute('''SELECT o.*, a.street, a.neighborhood, a.postal_code, a.complement
                            FROM orders o JOIN addresses a ON a.id=o.address_id WHERE o.id=?''', (order_id,)).fetchone()
        if row is None:
            return None
        order = dict(row)
        order.pop('request_hash', None)
        order.pop('request_key', None)
        order['items'] = [dict(item) for item in db.execute('SELECT product_id,product_name,unit_price_cents,quantity FROM order_items WHERE order_id=?', (order_id,))]
        order['history'] = [dict(item) for item in db.execute('SELECT status,changed_at FROM order_history WHERE order_id=? ORDER BY id', (order_id,))]
        return order
