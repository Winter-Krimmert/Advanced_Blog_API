from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)

class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    content = fields.Str()
    date_posted = fields.DateTime(dump_only=True)
    author = fields.Nested(UserSchema, only=['id', 'username'])

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    date_posted = fields.DateTime(dump_only=True)
    post_id = fields.Int(required=True)
    author = fields.Nested(UserSchema, only=['id', 'username'])
    post = fields.Nested(PostSchema, only=['id', 'title'])

# Create instances of the schemas for different use cases
user_input_schema = UserSchema()  # For creating or updating a user
user_output_schema = UserSchema(exclude=["password"])  # For returning user data, excluding password
users_schema = UserSchema(many=True, exclude=["password"])  # For listing multiple users

post_schema = PostSchema()  # For single post operations
posts_schema = PostSchema(many=True)  # For listing multiple posts

comment_schema = CommentSchema()  # For single comment operations
comments_schema = CommentSchema(many=True)  # For listing multiple comments
