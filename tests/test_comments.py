import unittest
import json
from app import create_app, db
from models import User, Post, Comment

class CommentsTestCase(unittest.TestCase):
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

    def test_create_comment(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        response = self.client.post(f'/posts/{post.id}/comments', json={
            'content': 'Great post!',
            'author_id': user.id
        })
        self.assertEqual(response.status_code, 201)

    def test_get_comment(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Great post!', author_id=user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        
        response = self.client.get(f'/posts/{post.id}/comments/{comment.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['content'], 'Great post!')

    def test_update_comment(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Great post!', author_id=user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()

        updated_data = {'content': 'Updated comment'}

        response = self.client.put(f'/posts/{post.id}/comments/{comment.id}', json=updated_data)
        self.assertEqual(response.status_code, 200)

        updated_comment = Comment.query.get(comment.id)
        self.assertEqual(updated_comment.content, 'Updated comment')

    def test_delete_comment(self):
        user = User(name='John Doe', email='john@example.com', username='johndoe', password='password')
        db.session.add(user)
        db.session.commit()

        post = Post(title='First Post', content='This is my first post!', author_id=user.id)
        db.session.add(post)
        db.session.commit()

        comment = Comment(content='Great post!', author_id=user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()

        response = self.client.delete(f'/posts/{post.id}/comments/{comment.id}')
        self.assertEqual(response.status_code, 204)

        deleted_comment = Comment.query.get(comment.id)
        self.assertIsNone(deleted_comment)

if __name__ == '__main__':
    unittest.main()
