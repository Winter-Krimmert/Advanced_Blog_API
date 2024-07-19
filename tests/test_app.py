import unittest
from unittest.mock import MagicMock, patch
from app import create_app, db
from models import User, Post, Comment
from faker import Faker

fake = Faker()

class TestBlogAPI(unittest.TestCase):
    def setUp(self):
        app = create_app(config_name='testing')  # Pass 'testing' config
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.client.application.app_context():
            db.drop_all()
    
    # Token Route
    @patch('app.routes.encode_token')
    @patch('app.routes.db.session.scalars')
    @patch('app.routes.check_password_hash')
    def test_successful_authenticate(self, mock_check_hash, mock_scalars, mock_encode_token):
        mock_user = MagicMock()
        mock_user.id = 123
        mock_query = MagicMock()
        mock_query.first.return_value = mock_user
        mock_scalars.return_value = mock_query
        mock_check_hash.return_value = True
        mock_encode_token.return_value = 'random.jwt.token'

        request_body = {
            "username": fake.user_name(),
            "password": fake.password()
        }

        response = self.client.post('/token', json=request_body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['token'], 'random.jwt.token')

    @patch('app.routes.db.session.scalars')
    @patch('app.routes.check_password_hash')
    def test_unauthorized_user(self, mock_check_hash, mock_scalars):
        mock_scalars.return_value = MagicMock()
        mock_check_hash.return_value = False

        request_body = {
            "username": fake.user_name(),
            "password": fake.password()
        }

        response = self.client.post('/token', json=request_body)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['error'], 'Username and/or password is incorrect')

    # User Routes
    def test_register_user(self):
        request_body = {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        }

        response = self.client.post('/register', json=request_body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'User created successfully')

    def test_create_user(self):
        request_body = {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        }

        response = self.client.post('/users', json=request_body)

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_get_user(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        response = self.client.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'testuser')

    def test_update_user(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        request_body = {
            "name": "Updated Name"
        }

        response = self.client.put(f'/users/{user.id}', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')

    def test_delete_user(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        response = self.client.delete(f'/users/{user.id}')
        self.assertEqual(response.status_code, 204)

    # Post Routes
    @patch('app.routes.decode_token')
    def test_create_post(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        mock_decode_token.return_value = {'user_id': user.id}
        self.client.post('/token', json={"username": "testuser", "password": "testpass"})

        request_body = {
            "title": fake.sentence(),
            "content": fake.text()
        }

        response = self.client.post('/posts', json=request_body)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_get_post(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        response = self.client.get(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Test Post')

    def test_update_post(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        request_body = {
            "title": "Updated Title"
        }

        response = self.client.put(f'/posts/{post.id}', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Updated Title')

    def test_delete_post(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        response = self.client.delete(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 204)

    # Comment Routes
    @patch('app.routes.decode_token')
    def test_create_comment(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        mock_decode_token.return_value = {'user_id': user.id}
        self.client.post('/token', json={"username": "testuser", "password": "testpass"})

        request_body = {
            "content": fake.text(),
            "post_id": post.id
        }

        response = self.client.post('/comments', json=request_body)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_get_comment(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Test Comment', post_id=post.id, user_id=user.id)
        db.session.add(comment)
        db.session.commit()

        response = self.client.get(f'/comments/{comment.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['content'], 'Test Comment')

    def test_update_comment(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Test Comment', post_id=post.id, user_id=user.id)
        db.session.add(comment)
        db.session.commit()

        request_body = {
            "content": "Updated Comment"
        }

        response = self.client.put(f'/comments/{comment.id}', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['content'], 'Updated Comment')

    def test_delete_comment(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        db.session.add(user)
        db.session.commit()

        post = Post(title='Test Post', content='Test Content', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Test Comment', post_id=post.id, user_id=user.id)
        db.session.add(comment)
        db.session.commit()

        response = self.client.delete(f'/comments/{comment.id}')
        self.assertEqual(response.status_code, 204)
