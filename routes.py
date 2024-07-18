from flask import request, jsonify
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from utils.utils import encode_token
from auth import token_auth
from models import User, Post, Comment
from schemas import UserSchema, PostSchema, CommentSchema
from caching import cache
from limiter import limiter
from models import db  # Import the db object

# Schemas
user_schema = UserSchema()
post_schema = PostSchema()
comment_schema = CommentSchema()

def init_app(app):
    @app.route('/')
    def index():
        return {"message": "Welcome to the Blog API"}

    # Token Route
    @app.route('/token', methods=["POST"])
    def get_token():
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request by Client
        try:
            data = request.json
            credentials = user_schema.load(data, partial=True)
            user = User.query.filter_by(username=credentials['username']).first()
            if user and check_password_hash(user.password, credentials['password']):
                auth_token = encode_token(user.id)
                return {'token': auth_token}, 200
            else:
                return {"error": "Username and/or password is incorrect"}, 401  # Unauthorized
        except ValidationError as err:
            return err.messages, 400

    # User Routes
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        new_user = User(
            name=data['name'],
            username=data['username'],
            email=data['email'],
            password=hashed_password
        )
        
        # Save new_user to the database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201

    # Route to login and generate JWT token
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            token = encode_token(user.id)
            return jsonify({'token': token}), 200

        return jsonify({'error': 'Invalid username or password'}), 401

    @app.route('/users', methods=["POST"])
    def create_user():
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request by Client
        try:
            data = request.json
            user_data = user_schema.load(data)
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                return {"error": "Username already exists"}, 400  # Bad Request by Client

            new_user = User(
                name=user_data['name'],
                email=user_data['email'],
                username=user_data['username'],
                password=generate_password_hash(user_data['password'])
            )
            db.session.add(new_user)
            db.session.commit()
            return user_schema.jsonify(new_user), 201  # Created
        except ValidationError as err:
            return err.messages, 400

    @app.route('/users/<int:id>', methods=["GET"])
    @token_auth.login_required
    def get_user(id):
        user = User.query.get_or_404(id)
        return user_schema.jsonify(user)

    @app.route('/users/<int:id>', methods=["PUT"])
    @token_auth.login_required
    def update_user(id):
        logged_in_user = token_auth.current_user()
        if logged_in_user.id != id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get_or_404(id)
        try:
            data = request.json
            user_schema.load(data, instance=user, partial=True)
            db.session.commit()
            return user_schema.jsonify(user)
        except ValidationError as err:
            return err.messages, 400

    @app.route('/users/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    def delete_user(id):
        logged_in_user = token_auth.current_user()
        if logged_in_user.id != id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

    # Post Routes
    @app.route('/posts', methods=["POST"])
    @token_auth.login_required
    def create_post():
        logged_in_user = token_auth.current_user()
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request by Client
        try:
            data = request.json
            post_data = post_schema.load(data)
            new_post = Post(
                title=post_data['title'],
                content=post_data['content'],
                user_id=logged_in_user.id
            )
            db.session.add(new_post)
            db.session.commit()
            return post_schema.jsonify(new_post), 201  # Created
        except ValidationError as err:
            return err.messages, 400

    @app.route('/posts/<int:id>', methods=["GET"])
    def get_post(id):
        post = Post.query.get_or_404(id)
        return post_schema.jsonify(post)

    @app.route('/posts/<int:id>', methods=["PUT"])
    @token_auth.login_required
    def update_post(id):
        logged_in_user = token_auth.current_user()
        post = Post.query.get_or_404(id)
        if post.user_id != logged_in_user.id:
            return {"error": "Unauthorized"}, 401
        try:
            data = request.json
            post_schema.load(data, instance=post, partial=True)
            db.session.commit()
            return post_schema.jsonify(post)
        except ValidationError as err:
            return err.messages, 400

    @app.route('/posts/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    def delete_post(id):
        logged_in_user = token_auth.current_user()
        post = Post.query.get_or_404(id)
        if post.user_id != logged_in_user.id:
            return {"error": "Unauthorized"}, 401
        db.session.delete(post)
        db.session.commit()
        return '', 204

    @app.route('/posts', methods=["GET"])
    @cache.cached(timeout=60)
    @limiter.limit("50 per hour")
    def list_posts():
        args = request.args
        page = args.get('page', 1, type=int)
        per_page = args.get('per_page', 10, type=int)
        search = args.get('search', '')
        query = Post.query.filter(Post.title.like(f'%{search}%')).paginate(page, per_page, False)
        posts = query.items
        return post_schema.jsonify(posts, many=True)

    # Comment Routes
    @app.route('/comments', methods=["POST"])
    @token_auth.login_required
    def create_comment():
        logged_in_user = token_auth.current_user()
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request by Client
        try:
            data = request.json
            comment_data = comment_schema.load(data)
            new_comment = Comment(
                content=comment_data['content'],
                user_id=logged_in_user.id
            )
            db.session.add(new_comment)
            db.session.commit()
            return comment_schema.jsonify(new_comment), 201  # Created
        except ValidationError as err:
            return err.messages, 400

    @app.route('/comments/<int:id>', methods=["GET"])
    def get_comment(id):
        comment = Comment.query.get_or_404(id)
        return comment_schema.jsonify(comment)

    @app.route('/comments/<int:id>', methods=["PUT"])
    @token_auth.login_required
    def update_comment(id):
        logged_in_user = token_auth.current_user()
        comment = Comment.query.get_or_404(id)
        if comment.user_id != logged_in_user.id:
            return {"error": "Unauthorized"}, 401
        try:
            data = request.json
            comment_schema.load(data, instance=comment, partial=True)
            db.session.commit()
            return comment_schema.jsonify(comment)
        except ValidationError as err:
            return err.messages, 400

    @app.route('/comments/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    def delete_comment(id):
        logged_in_user = token_auth.current_user()
        comment = Comment.query.get_or_404(id)
        if comment.user_id != logged_in_user.id:
            return {"error": "Unauthorized"}, 401
        db.session.delete(comment)
        db.session.commit()
        return '', 204
