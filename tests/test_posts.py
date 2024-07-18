import unittest
import json
from app import create_app, db
from models import User, Post

class PostsTestCase(unittest.TestCase):
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

    def test_create_post(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/posts', json={
            'title': 'First Post',
            'content': 'This is my first post!',
            'author_id': user.id
        })
        self.assertEqual(response.status_code, 201)

    def test_get_post(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()
        
        response = self.client.get(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'First Post')

    def test_update_post(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        updated_data = {'title': 'Updated Post'}

        response = self.client.put(f'/posts/{post.id}', json=updated_data)
        self.assertEqual(response.status_code, 200)

        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Post')

    def test_delete_post(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        response = self.client.delete(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 204)

        deleted_post = Post.query.get(post.id)
        self.assertIsNone(deleted_post)

if __name__ == '__main__':
    unittest.main()
