from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv
import os

# Initialize SQLAlchemy globally
db = SQLAlchemy()

def create_app():
    """
    Application factory function to create and configure the Flask application.
    """
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Load configuration from config.py
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Initialize database with the app
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize migrate with the app

    # Import routes here to avoid circular import
    from routes import init_app
    init_app(app)

    # Define custom error handlers
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 Not Found error.
        """
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """
        Handle 400 Bad Request error.
        """
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 Internal Server Error.
        """
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import User, Post, Comment  # Import inside app_context to avoid circular import
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
