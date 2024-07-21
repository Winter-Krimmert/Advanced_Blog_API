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
from sqlalchemy.exc import SQLAlchemyError

#function to get remote address
def get_remote_address():
    return request.remote_addr

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
    # @app.route('/register', methods=['POST'])
    # @limiter.limit("50 per minute", key_func=get_remote_address)
    # def register():
    #     return jsonify({'message': 'Register route is working'}), 200

    @app.route('/register', methods=['POST'])
    @limiter.limit("50 per minute", key_func=get_remote_address)
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
    @limiter.limit("5 per minute", key_func=get_remote_address)
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
    #User routes
    @app.route('/users', methods=["POST"])
    @limiter.limit("5 per minute", key_func=get_remote_address)
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

            # Serialize the user and return as JSON
            result = user_schema.dump(new_user)
            return jsonify(result), 201  # Created
        except ValidationError as err:
            return err.messages, 400


    @app.route('/users/<int:id>', methods=["GET"])
    @token_auth.login_required
    @cache.cached(timeout=60)
    def get_user(id):
        user = User.query.get_or_404(id)
        user_data = user_schema.dump(user)
        return jsonify(user_data)

    @app.route('/users/<int:id>', methods=["PUT"])
    @token_auth.login_required
    @limiter.limit("5 per minute", key_func=get_remote_address)
    def update_user(id):
        logged_in_user = token_auth.current_user()
        if logged_in_user.id != id:
            return {"error": "Unauthorized"}, 401
        user = User.query.get_or_404(id)
        try:
            data = request.json
            # Load data into the schema
            user_data = user_schema.load(data, partial=True)
            # Update user instance with new data
            for key, value in user_data.items():
                setattr(user, key, value)
            db.session.commit()
            return jsonify(user_schema.dump(user))  # Corrected line
        except ValidationError as err:
            return err.messages, 400

    @app.route('/users/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    @limiter.limit("5 per minute", key_func=get_remote_address)
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
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def create_post():
        logged_in_user = token_auth.current_user()
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request by Client
        try:
            post_data = request.get_json()
            new_post = Post(
                title=post_data['title'],
                content=post_data['content'],
                user_id=logged_in_user.id  # Assuming the post is created by the logged-in user
            )
            db.session.add(new_post)
            db.session.commit()
            return jsonify(post_schema.dump(new_post)), 201  # Created
        except ValidationError as err:
            return jsonify(err.messages), 400  # Bad request
    
    @app.route('/posts/<int:id>', methods=["PUT"])
    @token_auth.login_required
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def update_post(id):
        logged_in_user = token_auth.current_user()
        post = Post.query.get_or_404(id)
        
        if post.user_id != logged_in_user.id:
            return jsonify({"error": "Unauthorized"}), 401
        
        try:
            data = request.json
            # Load the data into the schema, but without updating the instance
            loaded_data = post_schema.load(data, partial=True)
            
            # Update the post instance with the loaded data
            for key, value in loaded_data.items():
                setattr(post, key, value)
            
            db.session.commit()
            
            # Serialize the updated post instance
            result = post_schema.dump(post)
            return jsonify(result)
        
        except ValidationError as err:
            return jsonify(err.messages), 400

    @app.route('/posts/<int:id>', methods=["GET"])
    @cache.cached(timeout=60)
    def get_post(id):
        post = Post.query.get_or_404(id)
        post_data = post_schema.dump(post)
        return jsonify(post_data)

    @app.route('/posts/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def delete_post(id):
        logged_in_user = token_auth.current_user()
        post = Post.query.get_or_404(id)
        if post.user_id != logged_in_user.id:
            return jsonify({"error": "Unauthorized"}), 401
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted successfully"}), 204
    
    @app.route('/posts', methods=['GET'])
    @cache.cached(timeout=60, query_string=True)
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def list_posts():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        try:
            # Using SQLAlchemy to query with LIKE for SQLite
            query = Post.query.filter(Post.title.like(f'%{search}%')).paginate(page=page, per_page=per_page, error_out=False)
            posts = query.items
            
            # Serialize data with the desired fields
            serialized_posts = []
            for post in posts:
                serialized_posts.append({
                    'content': post.content,
                    'id': post.id,
                    'title': post.title,
                    'user_id': post.user_id
                })
            
            # Return JSON response
            return jsonify(serialized_posts)
        except SQLAlchemyError as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/comments', methods=["POST"])
    @token_auth.login_required
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def create_comment():
        logged_in_user = token_auth.current_user()
        if not request.is_json:
            return {"error": "Request body must be application/json"}, 400  # Bad Request

        try:
            data = request.json
            # Include post_id in the data being validated
            comment_data = comment_schema.load(data)
          
            # Make sure the post_id is provided and valid
            post_id = comment_data.get('post_id')
            if not post_id:
                return {"error": "Post ID is required"}, 400  # Bad Request
            
            # Create the new comment
            new_comment = Comment(
                content=comment_data['content'],
                user_id=logged_in_user.id,
                post_id=post_id
            )
            db.session.add(new_comment)
            db.session.commit()

            serialized_comment = comment_schema.dump(new_comment)
            return jsonify(serialized_comment), 201  # Created


        except ValidationError as err:
            return err.messages, 400  # Bad Request

    @app.route('/comments/<int:id>', methods=["GET"])
    @token_auth.login_required
    @cache.cached(timeout=60)
    def get_comment(id):
        comment = Comment.query.get_or_404(id)
        comment_data = comment_schema.dump(comment)
        return jsonify(comment_data)

    @app.route('/comments/<int:id>', methods=["PUT"])
    @token_auth.login_required
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def update_comment(id):
        logged_in_user = token_auth.current_user()
        comment = Comment.query.get_or_404(id)
        
        if comment.user_id != logged_in_user.id:
            return jsonify({"error": "Unauthorized"}), 401
        
        try:
            data = request.json
            # Load the data into the schema, but without updating the instance
            loaded_data = comment_schema.load(data, partial=True)
            
            # Update the comment instance with the loaded data
            for key, value in loaded_data.items():
                setattr(comment, key, value)
            
            db.session.commit()
            
            # Serialize the updated comment instance
            result = comment_schema.dump(comment)
            return jsonify(result)
        
        except ValidationError as err:
            return jsonify(err.messages), 400


    @app.route('/comments/<int:id>', methods=["DELETE"])
    @token_auth.login_required
    @limiter.limit("10 per minute", key_func=get_remote_address)
    def delete_comment(id):
        logged_in_user = token_auth.current_user()
        comment = Comment.query.get_or_404(id)
        if comment.user_id != logged_in_user.id:
            return {"error": "Unauthorized"}, 401
        db.session.delete(comment)
        db.session.commit()
        return '', 204
