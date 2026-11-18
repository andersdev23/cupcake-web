"""Regras de domínio: orçamento, pedidos idempotentes e transições de status."""
import hashlib
import json
import re
import sqlite3


class BusinessError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def text(value, label, minimum=0, maximum=200):
    if not isinstance(value, str):
        raise BusinessError(f'{label}: informe um texto válido.')
    value = value.strip()
    if not minimum <= len(value) <= maximum:
        raise BusinessError(f'{label}: use entre {minimum} e {maximum} caracteres.')
    return value


def integer(value, label, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise BusinessError(f'{label}: informe um inteiro entre {minimum} e {maximum}.')
    return value


class ShopService:
    PAYMENTS = {'pix', 'cartao', 'debito', 'dinheiro'}
    TRANSITIONS = {
        'recebido': {'preparando', 'cancelado'},
        'preparando': {'saiu_entrega', 'cancelado'},
        'saiu_entrega': {'entregue'},
        'entregue': set(), 'cancelado': set(),
    }

    def __init__(self, database):
        self.database = database

    def quote(self, payload, db=None):
        payment = payload.get('payment', 'pix')
        if not isinstance(payment, str) or payment not in self.PAYMENTS:
            raise BusinessError('Selecione uma forma de pagamento válida.')
        items = payload.get('items')
        if not isinstance(items, list) or not 1 <= len(items) <= 20:
            raise BusinessError('Adicione entre 1 e 20 produtos diferentes ao carrinho.')
        quantities = {}
        for item in items:
            if not isinstance(item, dict):
                raise BusinessError('Item do carrinho inválido.')
            product_id = integer(item.get('product_id'), 'Produto', 1, 2147483647)
            quantity = integer(item.get('quantity'), 'Quantidade', 1, 99)
            quantities[product_id] = integer(quantities.get(product_id, 0) + quantity, 'Quantidade por produto', 1, 99)
        if sum(quantities.values()) > 200:
            raise BusinessError('O limite por pedido é de 200 unidades.')
        products = {product['id']: product for product in (self.database.products() if db is None else [dict(row) for row in db.execute('SELECT * FROM products WHERE active=1')])}
        result = []
        for product_id, quantity in quantities.items():
            product = products.get(product_id)
            if product is None:
                raise BusinessError('Um produto do carrinho não está mais disponível. Revise o carrinho.')
            result.append({'product_id': product_id, 'product_name': product['name'], 'unit_price_cents': product['price_cents'], 'quantity': quantity})
        subtotal = sum(item['unit_price_cents'] * item['quantity'] for item in result)
        discount = (subtotal * 5 + 50) // 100 if payment == 'pix' else 0
        return {'items': result, 'payment': payment, 'subtotal_cents': subtotal, 'discount_cents': discount, 'delivery_cents': 500, 'total_cents': subtotal - discount + 500}

    def place_order(self, payload, request_key):
        request_key = text(request_key, 'Identificador do pedido', 16, 100)
        if not re.fullmatch(r'[A-Za-z0-9_-]+', request_key):
            raise BusinessError('Identificador do pedido inválido.')
        customer = payload.get('customer')
        address = payload.get('address')
        if not isinstance(customer, dict) or not isinstance(address, dict):
            raise BusinessError('Informe seus dados e o endereço de entrega.')
        name = text(customer.get('name'), 'Nome completo', 2, 120)
        phone_raw = text(customer.get('phone'), 'Telefone', 8, 30)
        phone = re.sub(r'\D', '', phone_raw)
        if not 8 <= len(phone) <= 15:
            raise BusinessError('Telefone: informe de 8 a 15 dígitos.')
        email = text(customer.get('email', ''), 'E-mail', 0, 160)
        if email and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            raise BusinessError('Informe um e-mail válido ou deixe o campo vazio.')
        street = text(address.get('street'), 'Rua e número', 3, 200)
        neighborhood = text(address.get('neighborhood'), 'Bairro', 2, 100)
        postal_code = text(address.get('postal_code', ''), 'CEP', 0, 9)
        if postal_code and not re.fullmatch(r'\d{5}-?\d{3}', postal_code):
            raise BusinessError('CEP: use 8 dígitos, com ou sem hífen.')
        complement = text(address.get('complement', ''), 'Complemento', 0, 150)
        notes = text(payload.get('notes', ''), 'Observações', 0, 500)
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        with self.database.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT id,request_hash FROM orders WHERE request_key=?', (request_key,)).fetchone()
            if existing:
                if existing['request_hash'] != fingerprint:
                    raise BusinessError('Este identificador já pertence a outro pedido. Revise os dados e tente novamente.', 409)
                return self.database.order(db, existing['id']), True
            quote = self.quote(payload, db)
            db.execute('''INSERT INTO customers(name,phone,email) VALUES(?,?,?)
                          ON CONFLICT(phone) DO UPDATE SET name=excluded.name,email=excluded.email''', (name, phone, email))
            customer_id = db.execute('SELECT id FROM customers WHERE phone=?', (phone,)).fetchone()['id']
            address_id = db.execute('INSERT INTO addresses(customer_id,street,neighborhood,postal_code,complement) VALUES(?,?,?,?,?)', (customer_id, street, neighborhood, postal_code, complement)).lastrowid
            order_id = db.execute('''INSERT INTO orders(request_key,request_hash,customer_id,address_id,recipient_name,recipient_phone,recipient_email,payment,subtotal_cents,discount_cents,delivery_cents,total_cents,notes)
                                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (request_key, fingerprint, customer_id, address_id, name, phone, email, quote['payment'], quote['subtotal_cents'], quote['discount_cents'], quote['delivery_cents'], quote['total_cents'], notes)).lastrowid
            db.executemany('INSERT INTO order_items(order_id,product_id,product_name,unit_price_cents,quantity) VALUES(?,?,?,?,?)', [(order_id, item['product_id'], item['product_name'], item['unit_price_cents'], item['quantity']) for item in quote['items']])
            db.execute('INSERT INTO order_history(order_id,status) VALUES(?,?)', (order_id, 'recebido'))
            return self.database.order(db, order_id), False

    def orders(self, status='todos', query='', page=1):
        if not isinstance(status, str) or (status != 'todos' and status not in self.TRANSITIONS):
            raise BusinessError('Filtro de status inválido.')
        query = text(query, 'Busca', 0, 120)
        page = integer(page, 'Página', 1, 100000)
        conditions, values = [], []
        if status != 'todos':
            conditions.append('status=?'); values.append(status)
        if query:
            conditions.append('(recipient_name LIKE ? ESCAPE \'\\\' OR CAST(id AS TEXT)=?)')
            escaped = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            values.extend(['%' + escaped + '%', query])
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        with self.database.connect() as db:
            total = db.execute('SELECT COUNT(*) FROM orders' + where, values).fetchone()[0]
            ids = db.execute('SELECT id FROM orders' + where + ' ORDER BY id DESC LIMIT 25 OFFSET ?', values + [(page - 1) * 25]).fetchall()
            return {'orders': [self.database.order(db, row['id']) for row in ids], 'total': total, 'page': page, 'pages': max(1, (total + 24) // 25)}

    def change_status(self, order_id, payload):
        status = payload.get('status')
        version = integer(payload.get('version'), 'Versão do pedido', 1, 2147483647)
        with self.database.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            order = self.database.order(db, order_id)
            if order is None:
                raise BusinessError('Pedido não encontrado.', 404)
            if order['version'] != version:
                raise BusinessError('Este pedido foi atualizado em outra tela. Atualize a lista e tente novamente.', 409)
            if not isinstance(status, str) or status not in self.TRANSITIONS[order['status']]:
                raise BusinessError('Essa alteração de status não é permitida para este pedido.')
            db.execute('UPDATE orders SET status=?,version=version+1 WHERE id=?', (status, order_id))
            db.execute('INSERT INTO order_history(order_id,status) VALUES(?,?)', (order_id, status))
            return self.database.order(db, order_id)

    def update_product(self, product_id, payload):
        price = integer(payload.get('price_cents'), 'Preço em centavos', 1, 1000000)
        active = payload.get('active')
        if not isinstance(active, bool):
            raise BusinessError('Disponibilidade: informe verdadeiro ou falso.')
        with self.database.connect() as db:
            if not db.execute('UPDATE products SET price_cents=?,active=? WHERE id=?', (price, int(active), product_id)).rowcount:
                raise BusinessError('Produto não encontrado.', 404)
            return dict(db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone())
