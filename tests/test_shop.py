import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from backend.models import Database
from backend.services import ShopService, BusinessError
from backend.controllers import AdminSessions, make_handler

ROOT = Path(__file__).resolve().parents[1]


def payload():
    return {'customer': {'name': 'Cliente de teste', 'phone': '(41) 99999-1234', 'email': 'teste@example.com'},
            'address': {'street': 'Rua de Teste, 123', 'neighborhood': 'Centro', 'postal_code': '80000-000', 'complement': 'Dados fictícios'},
            'items': [{'product_id': 1, 'quantity': 2}], 'payment': 'pix', 'notes': 'Pedido de teste'}


class ShopTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / 'shop.sqlite3')
        self.database.initialize()
        self.service = ShopService(self.database)

    def tearDown(self):
        self.temp.cleanup()

    def test_catalog_seed_and_persistence(self):
        self.assertEqual(len(self.database.products()), 6)
        self.service.update_product(1, {'price_cents': 1501, 'active': False})
        self.database.initialize()
        self.assertEqual(len(self.database.products()), 5)
        self.assertEqual(self.database.products(True)[0]['price_cents'], 1501)

    def test_quote_server_prices_pix_and_rounding(self):
        data = payload()
        data['items'][0]['price_cents'] = 1
        result = self.service.quote(data)
        self.assertEqual((result['subtotal_cents'], result['discount_cents'], result['delivery_cents'], result['total_cents']), (2400, 120, 500, 2780))
        self.service.update_product(1, {'price_cents': 101, 'active': True})
        self.assertEqual(self.service.quote(data)['discount_cents'], 10)
        data['payment'] = 'dinheiro'
        self.assertEqual(self.service.quote(data)['discount_cents'], 0)

    def test_invalid_quantity_and_payment(self):
        for value in [0, -1, 100, 1.5, True, '2', None]:
            with self.subTest(value=value):
                data = payload(); data['items'][0]['quantity'] = value
                with self.assertRaises(BusinessError): self.service.quote(data)
        for value in [[], {}, 'invalido', None]:
            data = payload(); data['payment'] = value
            with self.assertRaises(BusinessError): self.service.quote(data)

    def test_empty_unknown_and_inactive_products(self):
        for items in [[], None, [{'product_id': 999, 'quantity': 1}]]:
            data = payload(); data['items'] = items
            with self.assertRaises(BusinessError): self.service.quote(data)
        self.service.update_product(1, {'price_cents': 1200, 'active': False})
        with self.assertRaises(BusinessError): self.service.quote(payload())

    def test_create_and_idempotency(self):
        order, replayed = self.service.place_order(payload(), 'test-request-key-00001')
        self.assertFalse(replayed)
        self.assertEqual(order['total_cents'], 2780)
        self.assertEqual(len(order['items']), 1)
        self.assertEqual(order['history'][0]['status'], 'recebido')
        replay, replayed = self.service.place_order(payload(), 'test-request-key-00001')
        self.assertTrue(replayed)
        self.assertEqual(order['id'], replay['id'])
        self.assertEqual(self.service.orders()['total'], 1)
        changed = payload(); changed['notes'] = 'Outra tentativa'
        with self.assertRaises(BusinessError) as raised: self.service.place_order(changed, 'test-request-key-00001')
        self.assertEqual(raised.exception.status, 409)

    def test_rollback_on_unavailable_product(self):
        data = payload(); data['items'].append({'product_id': 999, 'quantity': 1})
        with self.assertRaises(BusinessError): self.service.place_order(data, 'test-request-key-00002')
        with self.database.connect() as db:
            for table in ['orders', 'order_items', 'customers', 'addresses']:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0], 0)

    def test_order_snapshots_survive_catalog_change(self):
        order, _ = self.service.place_order(payload(), 'test-request-key-00003')
        self.service.update_product(1, {'price_cents': 5000, 'active': True})
        self.assertEqual(self.service.orders()['orders'][0]['items'][0]['unit_price_cents'], 1200)
        self.assertEqual(self.service.orders()['orders'][0]['total_cents'], order['total_cents'])

    def test_status_flow_history_and_concurrency(self):
        order, _ = self.service.place_order(payload(), 'test-request-key-00004')
        with self.assertRaises(BusinessError): self.service.change_status(order['id'], {'status': 'entregue', 'version': 1})
        self.service.change_status(order['id'], {'status': 'preparando', 'version': 1})
        with self.assertRaises(BusinessError) as raised: self.service.change_status(order['id'], {'status': 'cancelado', 'version': 1})
        self.assertEqual(raised.exception.status, 409)
        self.service.change_status(order['id'], {'status': 'saiu_entrega', 'version': 2})
        result = self.service.change_status(order['id'], {'status': 'entregue', 'version': 3})
        self.assertEqual(len(result['history']), 4)
        with self.assertRaises(BusinessError): self.service.change_status(order['id'], {'status': 'recebido', 'version': 4})

    def test_search_filters_and_cancel(self):
        order, _ = self.service.place_order(payload(), 'test-request-key-00005')
        self.service.change_status(order['id'], {'status': 'cancelado', 'version': 1})
        self.assertEqual(self.service.orders('cancelado')['total'], 1)
        self.assertEqual(self.service.orders(query='Cliente')['total'], 1)
        self.assertEqual(self.service.orders(query='%')['total'], 0)
        self.assertEqual(self.service.orders('recebido')['total'], 0)

    def test_customer_validation(self):
        for field, value in [('name', 'A'), ('phone', 'abc'), ('email', 'sem-arroba')]:
            data = payload(); data['customer'][field] = value
            with self.assertRaises(BusinessError): self.service.place_order(data, 'test-request-key-00006')

    def test_concurrent_duplicate_requests_create_one_order(self):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(lambda _: self.service.place_order(payload(), 'test-request-concurrent'), range(3)))
        self.assertEqual({result[0]['id'] for result in results}, {1})
        self.assertEqual(self.service.orders()['total'], 1)


class HttpTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        database = Database(Path(cls.temp.name) / 'http.sqlite3'); database.initialize()
        cls.sessions = AdminSessions('senha-forte-de-teste')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(ROOT, ShopService(database), cls.sessions))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(); cls.temp.cleanup()

    def request(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        request_headers = {'Content-Type': 'application/json', **(headers or {})}
        connection.request(method, path, json.dumps(data) if data is not None else None, request_headers)
        response = connection.getresponse(); body = response.read(); received_headers = dict(response.getheaders())
        status = response.status; connection.close()
        return status, body, received_headers

    def login(self):
        status, body, headers = self.request('POST', '/api/admin/login', {'password': 'senha-forte-de-teste'})
        self.assertEqual(status, 200)
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Strict', headers['Set-Cookie'])
        return {'Cookie': headers['Set-Cookie'].split(';')[0], 'X-CSRF-Token': json.loads(body)['csrf']}

    def test_static_files_deny_private_source_and_data(self):
        for path in ['/app.py', '/backend/models.py', '/data/admin-password.txt', '/.git/config', '/css/../data/admin-password.txt']:
            for method in ['GET', 'HEAD']:
                self.assertEqual(self.request(method, path)[0], 404)
        status, body, headers = self.request('GET', '/checkout.html?v=1')
        self.assertEqual(status, 200); self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_admin_requires_login_and_csrf(self):
        self.assertEqual(self.request('GET', '/api/admin/orders')[0], 401)
        headers = self.login()
        self.assertEqual(self.request('GET', '/api/admin/orders', headers=headers)[0], 200)
        no_csrf = {'Cookie': headers['Cookie']}
        self.assertEqual(self.request('PATCH', '/api/admin/products/1', {'price_cents': 1200, 'active': True}, no_csrf)[0], 403)
        self.assertEqual(self.request('PATCH', '/api/admin/products/1', {'price_cents': 1200, 'active': True}, headers)[0], 200)
        self.assertEqual(self.request('POST', '/api/admin/logout', {}, headers)[0], 200)
        self.assertEqual(self.request('GET', '/api/admin/orders', headers=headers)[0], 401)

    def test_origin_rejected_and_http_order_idempotency(self):
        self.assertEqual(self.request('POST', '/api/quote', payload(), {'Origin': 'https://outro-site.example'})[0], 403)
        headers = {'Idempotency-Key': 'http-test-order-key-0001'}
        first = self.request('POST', '/api/orders', payload(), headers)
        second = self.request('POST', '/api/orders', payload(), headers)
        self.assertEqual(first[0], 201); self.assertEqual(second[0], 200)
        self.assertEqual(json.loads(first[1])['order']['id'], json.loads(second[1])['order']['id'])

    def test_login_rate_limit(self):
        sessions = AdminSessions('senha-forte-de-teste')
        for _ in range(5):
            with self.assertRaises(BusinessError) as raised: sessions.login('errada', 'teste')
            self.assertEqual(raised.exception.status, 401)
        with self.assertRaises(BusinessError) as raised: sessions.login('senha-forte-de-teste', 'teste')
        self.assertEqual(raised.exception.status, 429)


if __name__ == '__main__': unittest.main()
