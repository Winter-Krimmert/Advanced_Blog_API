from app import create_app
from models import User  # Assuming User model is imported from models module


app = create_app()
with app.app_context():
    # Inside this block, current_app points to your Flask application
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username}, Password: {user.password}")
