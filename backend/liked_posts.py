from flask import Blueprint, request, jsonify
from app import db
from models import LikedPost, Post
from auth import token_required

liked_posts_bp = Blueprint('liked_posts', __name__)

@liked_posts_bp.route('/like_post/<int:post_id>', methods=['POST', 'OPTIONS'])
@token_required
def like_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        existing_like = LikedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if existing_like:
            return jsonify({"message": "You've already liked this post"}), 400

        new_like = LikedPost(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        post.likes += 1
        db.session.commit()
        return jsonify({"message": "Post liked successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in like_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@liked_posts_bp.route('/unlike_post/<int:post_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def unlike_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        like = LikedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not like:
            return jsonify({"message": "You haven't liked this post"}), 404

        db.session.delete(like)
        post = Post.query.get(post_id)
        if post:
            post.likes = max(0, post.likes - 1)
        db.session.commit()
        return jsonify({"message": "Post unliked successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in unlike_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@liked_posts_bp.route('/liked_posts', methods=['GET', 'OPTIONS'])
@token_required
def get_liked_posts(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        liked_posts = db.session.query(Post).join(LikedPost).filter(LikedPost.user_id == current_user.id).order_by(LikedPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "liked_posts": [{
                "id": post.id,
                "title": post.title,
                "text": post.text[:100] + "..." if post.text and len(post.text) > 100 else post.text,
                "related_workout": post.related_workout,
                "views": post.views,
                "likes": post.likes,
                "collections": post.collections,
                "created_at": post.created_at,
                "author": post.user.username
            } for post in liked_posts.items],
            "total": liked_posts.total,
            "pages": liked_posts.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_liked_posts: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500