import unittest
from unittest.mock import MagicMock, patch
from app import create_app, db
from models import User, Post, Comment
from faker import Faker

fake = Faker()

class TestBlogAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["testing"] = True  # Pass 'testing' config
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.client.application.app_context():
            db.drop_all()
    
    # Token Route
    def test_successful_authenticate(self):
            # First, register a user
            register_body = {
                "name": "Test User",
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpassword"
            }
            register_response = self.client.post('/register', json=register_body)

            self.assertEqual(register_response.status_code, 201)
            self.assertEqual(register_response.json['message'], 'User created successfully')

            # Then, authenticate the user
            auth_body = {
                "username": "testuser",
                "password": "testpassword"
            }
            auth_response = self.client.post('/token', json=auth_body)

            # Debugging response
            print("Response Status Code:", auth_response.status_code)
            print("Response Data:", auth_response.json)

            # Assert the response
            self.assertEqual(auth_response.status_code, 200)
            self.assertIn('token', auth_response.json)


    @patch('routes.db.session.execute')
    @patch('routes.check_password_hash')
    def test_unauthorized_user(self, mock_check_hash, mock_execute):
        mock_check_hash.return_value = False
        mock_execute.return_value.scalars = MagicMock()

        request_body = {
            "username": "wronguser",
            "password": "wrongpassword"
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

    @patch('auth.decode_token')
    def test_create_user(self, mock_decode_token):
        # Mock authentication
        mock_decode_token.return_value = 1  # Simulate a user ID from the token
        
        # Prepare request body
        request_body = {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        }
        
        # Perform the POST request
        response = self.client.post('/users', json=request_body)
        
        # Check for successful creation
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertEqual(response.json['name'], request_body['name'])
        self.assertEqual(response.json['username'], request_body['username'])
        self.assertEqual(response.json['email'], request_body['email'])

    @patch('flask_httpauth.HTTPTokenAuth.authenticate')
    def test_get_user(self, mock_authenticate):
        mock_authenticate.return_value = True
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'testuser')

    @patch('auth.decode_token')
    def test_update_user(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

        mock_decode_token.return_value = user_id

        request_body = {
            "name": "Updated Name"
        }

        response = self.client.put(f'/users/{user_id}', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')

    @patch('auth.decode_token')
    def test_delete_user(self, mock_decode_token):
        # Create a test user and add to the database
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()  # Ensure user ID is generated
            user_id = user.id
            db.session.commit()

            # Mock the authentication to return the test user
            mock_decode_token.return_value = user_id
            
            # Perform the delete request
            response = self.client.delete(f'/users/{user_id}')
            self.assertEqual(response.status_code, 204)

    # Post Routes
    @patch('auth.decode_token')
    def test_create_post(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

        mock_decode_token.return_value = user_id
        
        request_body = {
            "title": fake.sentence(),
            "content": fake.text()
        }

        response = self.client.post('/posts', json=request_body)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    def test_get_post(self):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

            post = Post(title='Test Post', content='Test Content', user_id=user_id)
            db.session.add(post)
            db.session.flush()
            post_id = post.id
            db.session.commit()

        response = self.client.get(f'/posts/{post_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Test Post')

    @patch('auth.decode_token')
    def test_update_post(self, mock_decode_token):
        # Create a test user and add to the database
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()  # Ensure user ID is generated
            user_id = user.id
            db.session.commit()

            # Create a test post and add to the database
            post = Post(title='Test Post', content='Test Content', user_id=user_id)
            db.session.add(post)
            db.session.flush()  # Ensure post ID is generated
            post_id = post.id
            db.session.commit()

            # Mock the authentication to return the test user ID
            mock_decode_token.return_value = user_id

            # Define the request body for the update
            request_body = {
                "title": "Updated Title"
            }

            # Perform the PUT request to update the post
            response = self.client.put(f'/posts/{post_id}', json=request_body)

            # Check for successful update
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['title'], 'Updated Title')

            # Verify the post is updated in the database
            updated_post = Post.query.get(post_id)
            self.assertEqual(updated_post.title, 'Updated Title')

    @patch('auth.decode_token')
    def test_delete_post(self, mock_decode_token):
        # Mock the token authentication to simulate a logged-in user
        mock_decode_token.return_value = 1  # Simulate a user ID from the token
        
        # Create a test user and add to the database
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()  # Ensure user ID is generated
            user_id = user.id
            
            # Create a test post and add to the database
            post = Post(title='Test Post', content='Test Content', user_id=user_id)
            db.session.add(post)
            db.session.flush()  # Ensure post ID is generated
            post_id = post.id
            db.session.commit()
        
        # Perform the delete request
        response = self.client.delete(f'/posts/{post_id}', headers={'Authorization': 'Bearer fake_token'})
        
        # Check for successful deletion
        self.assertEqual(response.status_code, 204)

    # Comment Routes
    @patch('auth.decode_token')
    def test_create_comment(self, mock_decode_token):
        # Set up the user and post
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

            post = Post(title='Test Post', content='Test Content', user_id=user.id)
            db.session.add(post)
            db.session.flush()
            post_id = post.id
            db.session.commit()

        # Mock the authentication to return the test user
        mock_decode_token.return_value = user_id

        # Perform the POST request to create a comment
        request_body = {
            "content": fake.text(),
            "post_id": post_id
        }

        response = self.client.post('/comments', json=request_body)

        # Check for successful creation
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)

    @patch('auth.decode_token')
    def test_get_comment(self, mock_decode_token):
        # Mock the token authentication to simulate a logged-in user
        mock_decode_token.return_value = 1  # Simulate a user ID from the token
        
        # Set up the user, post, and comment
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

            post = Post(title='Test Post', content='Test Content', user_id=user.id)
            db.session.add(post)
            db.session.flush()
            post_id = post.id
            db.session.commit()

            comment = Comment(content='Test Comment', post_id=post_id, user_id=user.id)
            db.session.add(comment)
            db.session.flush()
            comment_id = comment.id
            db.session.commit()
        
        # Perform the GET request to retrieve the comment
        response = self.client.get(f'/comments/{comment_id}', headers={'Authorization': 'Bearer fake_token'})
        
        # Check for successful retrieval
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['content'], 'Test Comment')
        self.assertEqual(response.json['post_id'], post_id)

    @patch('auth.decode_token')
    def test_update_comment(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

            post = Post(title='Test Post', content='Test Content', user_id=user_id)
            db.session.add(post)
            db.session.flush()
            post_id = post.id
            db.session.commit()

            comment = Comment(content='Test Comment', post_id=post_id, user_id=user_id)
            db.session.add(comment)
            db.session.flush()
            comment_id = comment.id
            db.session.commit()

        mock_decode_token.return_value = user_id

        request_body = {
            "content": "Updated Comment"
        }

        response = self.client.put(f'/comments/{comment_id}', json=request_body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['content'], 'Updated Comment')

    @patch('auth.decode_token')
    def test_delete_comment(self, mock_decode_token):
        user = User(name='Test User', username='testuser', email='test@example.com', password='testpass')
        with self.app.app_context():
            db.session.add(user)
            db.session.flush()
            user_id = user.id
            db.session.commit()

            post = Post(title='Test Post', content='Test Content', user_id=user_id)
            db.session.add(post)
            db.session.flush()
            post_id = post.id
            db.session.commit()

            comment = Comment(content='Test Comment', post_id=post_id, user_id=user_id)
            db.session.add(comment)
            db.session.flush()
            comment_id = comment.id
            db.session.commit()

        mock_decode_token.return_value = user_id

        response = self.client.delete(f'/comments/{comment_id}')
        self.assertEqual(response.status_code, 204)
