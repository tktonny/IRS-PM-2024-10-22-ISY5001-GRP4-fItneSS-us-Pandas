from flask import Blueprint, request, jsonify
from app import db
from models import UserFollows, User
from auth import token_required
from sqlalchemy import func

user_follows_bp = Blueprint('user_follows', __name__)

@user_follows_bp.route('/follow/<int:user_id>', methods=['POST', 'OPTIONS'])
@token_required
def follow_user(current_user, user_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        if current_user.id == user_id:
            return jsonify({"message": "You cannot follow yourself"}), 400

        user_to_follow = User.query.get(user_id)
        if not user_to_follow:
            return jsonify({"message": "User not found"}), 404

        existing_follow = UserFollows.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
        if existing_follow:
            return jsonify({"message": "You are already following this user"}), 400

        new_follow = UserFollows(follower_id=current_user.id, followed_id=user_id)
        db.session.add(new_follow)

        # Update follower and followed counts
        current_user.following_count = UserFollows.query.filter_by(follower_id=current_user.id).count() + 1
        user_to_follow.followers_count = UserFollows.query.filter_by(followed_id=user_id).count() + 1

        db.session.commit()
        return jsonify({"message": "Successfully followed user"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in follow_user: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@user_follows_bp.route('/unfollow/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def unfollow_user(current_user, user_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        follow = UserFollows.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
        if not follow:
            return jsonify({"message": "You are not following this user"}), 404

        db.session.delete(follow)

        # Update follower and followed counts
        current_user.following_count = UserFollows.query.filter_by(follower_id=current_user.id).count() - 1
        user_unfollowed = User.query.get(user_id)
        if user_unfollowed:
            user_unfollowed.followers_count = UserFollows.query.filter_by(followed_id=user_id).count() - 1

        db.session.commit()
        return jsonify({"message": "Successfully unfollowed user"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in unfollow_user: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@user_follows_bp.route('/followers', methods=['GET', 'OPTIONS'])
@token_required
def get_followers(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        followers = db.session.query(User).join(UserFollows, User.id == UserFollows.follower_id).filter(UserFollows.followed_id == current_user.id).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "followers": [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "followers_count": user.followers_count,
                "following_count": user.following_count
            } for user in followers.items],
            "total": followers.total,
            "pages": followers.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_followers: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@user_follows_bp.route('/following', methods=['GET', 'OPTIONS'])
@token_required
def get_following(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        following = db.session.query(User).join(UserFollows, User.id == UserFollows.followed_id).filter(UserFollows.follower_id == current_user.id).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "following": [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "followers_count": user.followers_count,
                "following_count": user.following_count
            } for user in following.items],
            "total": following.total,
            "pages": following.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_following: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500