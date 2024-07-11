import jwt
import datetime
from flask import current_app

def encode_token(user_id):
    """
    Generates the JWT token with user ID and expiration time as payload
    """
    try:
        payload = {
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'sub': str(user_id)  # Ensure user_id is a string
        }
        secret_key = current_app.config['SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        print(f"Encoded token: {token}")
        return token
    except Exception as e:
        print(f"Error encoding token: {e}")
        return str(e)

def decode_token(token):
    """
    Decodes the JWT token to get the user ID
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        print(f"Decoded payload: {payload}")
        return payload['sub']
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        print("Invalid token")
        return 'Invalid token. Please log in again.'
