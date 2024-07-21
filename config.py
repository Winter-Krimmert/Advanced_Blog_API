import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
    
    # Determine the database URI to use
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite').lower()
    
    if DATABASE_TYPE == 'sqlite':
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///default.db'
    elif DATABASE_TYPE == 'mysql':
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'mysql+mysqlconnector://root:password@localhost/dbname'
    elif DATABASE_TYPE == 'postgresql':
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'postgresql://user:password@localhost/dbname'
    else:
        raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
