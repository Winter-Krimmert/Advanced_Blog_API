import os
import datetime  # Import the datetime module
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'mysql+pymysql://root:sqlpass#4@localhost/blog_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    DEBUG = True  # Enable debug mode for detailed error messages
