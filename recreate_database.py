from app import app
from models import db, User, Post

def recreate_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create a test user
        test_user = User(username='testuser')
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.commit()
        print('Database recreated and test user added')

if __name__ == '__main__':
    recreate_database()
