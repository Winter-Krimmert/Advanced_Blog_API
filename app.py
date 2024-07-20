from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from dotenv import load_dotenv
import os
from extensions import db
from caching import cache
from models import User, Post, Comment
from routes import init_app

# Initialize SQLAlchemy globally
# db = SQLAlchemy()

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

    # Initialize cache with the app
    cache.init_app(app)

    # Reference the models to ensure they are detected
    with app.app_context():
        db.create_all()

    # Call init_app to register routes
    init_app(app)

    # Swagger UI configuration
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger/swagger.yaml'  # Path to your Swagger YAML file

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Advanced Blog API"
        }
    )

    # Register the Swagger UI blueprint
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Serve the Swagger YAML file
    @app.route('/swagger/swagger.yaml')
    def swagger_yaml():
        return send_from_directory('swagger', 'swagger.yaml')

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
