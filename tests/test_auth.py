# tests/test_auth.py
import unittest
from app import create_app, db
from models import User
import json

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.client.post('/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        self.client.post('/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123'
        })
        response = self.client.post('/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', json.loads(response.data))

if __name__ == '__main__':
    unittest.main()
