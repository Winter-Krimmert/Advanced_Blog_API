from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(db.Model):
    __tablename__ = 'users'  # Table name in the database

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    username: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'posts'  # Table name in the database

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    body: Mapped[str] = mapped_column(db.String, nullable=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments: Mapped[list['Comment']] = relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'  # Table name in the database

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
