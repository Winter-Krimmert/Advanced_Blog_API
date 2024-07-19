import os
import datetime  # Import the datetime module
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
    
    # Set default to SQLite if DATABASE_URL is not provided
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///adv_db2.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False



