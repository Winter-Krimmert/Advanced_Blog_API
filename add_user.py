from app import create_app  # Import your Flask app factory
from models import db, User
from werkzeug.security import generate_password_hash

# Initialize the app and database
app = create_app()
with app.app_context():
    # Create a new user
    new_user = User(
        name='John Doe',
        username='johndoe',
        email='johndoe@example.com',
        password=generate_password_hash('yourpassword', method='pbkdf2:sha256')
    )

    # Add the new user to the session and commit
    db.session.add(new_user)
    db.session.commit()

    print("User added successfully!")
