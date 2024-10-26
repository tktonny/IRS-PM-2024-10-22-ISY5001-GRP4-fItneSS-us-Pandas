from extensions import db
from datetime import datetime
from sqlalchemy import Enum

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Post(db.Model):
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    related_workout = db.Column(db.String(255))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    collections = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'Comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LikedPost(db.Model):
    __tablename__ = 'LikedPosts'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CollectedPost(db.Model):
    __tablename__ = 'CollectedPosts'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ViewedPost(db.Model):
    __tablename__ = 'ViewedPosts'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), primary_key=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserFollows(db.Model):
    __tablename__ = 'UserFollows'
    follower_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkoutInformation(db.Model):
    __tablename__ = 'WorkoutInformation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    workout_type = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    date = db.Column(db.Date)

class Image(db.Model):
    __tablename__ = 'Images'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_metadata = db.Column(db.JSON)

class PostImage(db.Model):
    __tablename__ = 'PostImages'
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('Images.id'), primary_key=True)
    image_order = db.Column(db.Integer, default=0)

class UserBodyInformation(db.Model):
    __tablename__ = 'Users_BodyInformation'
    id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    gender = db.Column(Enum('male', 'female', name='gender_types'), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Numeric(5, 2), nullable=False, comment='unit: cm')
    current_weight = db.Column(db.Numeric(5, 2), nullable=False, comment='unit: kg')
    target_weight = db.Column(db.Numeric(5, 2), nullable=False, comment='unit: kg')
    experience_level = db.Column(Enum('1', '2', '3', name='experience_levels'), nullable=False, comment='1: beginner, 2: intermediate, 3: advanced')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
