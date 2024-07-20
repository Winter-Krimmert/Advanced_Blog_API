import os
import datetime  # Import the datetime module
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
    

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('SQLALCHEMY_DATABASE_URL')

    SQLALCHEMY_TRACK_MODIFICATIONS = False



