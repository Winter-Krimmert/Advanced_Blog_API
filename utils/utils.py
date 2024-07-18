import jwt
from datetime import datetime, timedelta
from flask import current_app
import pytz  # Ensure pytz is imported for consistent UTC handling


def encode_token(user_id):
    """
    Generate JWT token with user ID and expiration time.
    """
    try:
        utc = pytz.UTC
        payload = {
            'exp': datetime.now(utc) + timedelta(days=1),
            'iat': datetime.now(utc),
            'sub': str(user_id)  # Ensure user_id is a string
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token  # Return as bytes, which is default behavior of jwt.encode
    except Exception as e:
        return str(e)  # Convert exception to string for better error handling

def decode_token(token):
    """
    Decode JWT token to retrieve the payload.
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
