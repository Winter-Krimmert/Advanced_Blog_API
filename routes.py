# routes.py or post_routes.py

from flask import Blueprint, request, jsonify
from models import Post, db
from auth import login_required  # Ensure correct import path

post_bp = Blueprint('post', __name__)

@post_bp.route('/create_post', methods=['POST'])
@login_required
def create_post(user_id):
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing title or content"}), 400

    post = Post(title=data['title'], content=data['content'], user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return jsonify({"message": "Post created successfully"}), 201
