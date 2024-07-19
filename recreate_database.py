from app import create_app
from models import db, User

def recreate_database():
    # Create an app instance using the factory function
    app = create_app()

    # Use the application context for database operations
    with app.app_context():
        # Drop all tables and create new ones
        db.drop_all()
        db.create_all()

        # # Create a test user
        # test_user = User(username='testuser', name='Test User', email='testuser@example.com')
        # test_user.set_password('testpassword')
        # db.session.add(test_user)
        # db.session.commit()
        # print('Database recreated and test user added')

if __name__ == '__main__':
    recreate_database()
