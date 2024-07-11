from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import User
from utils.utils import encode_token, decode_token
from functools import wraps

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        print("Missing username or password")
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user:
        print(f"User found: {user.username}")
    else:
        print("User not found")

    if user and check_password_hash(user.password, data['password']):
        token = encode_token(user.id)
        print(f"Generated token: {token}")
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        print("Invalid credentials")
        return jsonify({"error": "Invalid credentials"}), 401

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            print("Missing or invalid token")
            return jsonify({"error": "Missing or invalid token"}), 401

        token = token.split()[1]  # Extract the token part
        try:
            user_id = decode_token(token)  # Decode and verify the token
            kwargs['user_id'] = user_id  # Pass the user ID to the route function
        except Exception as e:
            print(f"Token decoding error: {e}")
            return jsonify({"error": str(e)}), 401

        return func(*args, **kwargs)

    return wrapper
