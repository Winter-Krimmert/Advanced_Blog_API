import unittest
import json
from app import create_app, db
from models import User

class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        response = self.client.post('/users', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'username': 'johndoe',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 201)

    def test_get_user(self):
        user = User(name='Jane Smith', email='jane@example.com', username='janesmith', password='password')
        db.session.add(user)
        db.session.commit()
        
        response = self.client.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Jane Smith')

    def test_update_user(self):
        user = User(name='Jane Smith', email='jane@example.com', username='janesmith', password='password')
        db.session.add(user)
        db.session.commit()

        updated_data = {'name': 'Jane Doe'}

        response = self.client.put(f'/users/{user.id}', json=updated_data)
        self.assertEqual(response.status_code, 200)

        updated_user = User.query.get(user.id)
        self.assertEqual(updated_user.name, 'Jane Doe')

    def test_delete_user(self):
        user = User(name='Jane Smith', email='jane@example.com', username='janesmith', password='password')
        db.session.add(user)
        db.session.commit()

        response = self.client.delete(f'/users/{user.id}')
        self.assertEqual(response.status_code, 204)

        deleted_user = User.query.get(user.id)
        self.assertIsNone(deleted_user)

if __name__ == '__main__':
    unittest.main()
