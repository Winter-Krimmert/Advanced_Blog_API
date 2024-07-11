from flask import Flask
from models import db
from auth import auth_bp  # Import the auth blueprint
from routes import post_bp  # Import the post blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Ensure this is set

db.init_app(app)

with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(post_bp, url_prefix='/post')

if __name__ == '__main__':
    app.run(debug=True)
