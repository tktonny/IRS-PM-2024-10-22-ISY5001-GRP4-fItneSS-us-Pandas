from flask import Blueprint, request, jsonify
from app import db
from models import CollectedPost, Post
from auth import token_required

collected_posts_bp = Blueprint('collected_posts', __name__)

@collected_posts_bp.route('/collect_post/<int:post_id>', methods=['POST', 'OPTIONS'])
@token_required
def collect_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        existing_collection = CollectedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if existing_collection:
            return jsonify({"message": "You've already collected this post"}), 400

        new_collection = CollectedPost(user_id=current_user.id, post_id=post_id)
        db.session.add(new_collection)
        post.collections += 1
        db.session.commit()
        return jsonify({"message": "Post collected successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in collect_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@collected_posts_bp.route('/uncollect_post/<int:post_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def uncollect_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        collection = CollectedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if not collection:
            return jsonify({"message": "You haven't collected this post"}), 404

        db.session.delete(collection)
        post = Post.query.get(post_id)
        if post:
            post.collections = max(0, post.collections - 1)
        db.session.commit()
        return jsonify({"message": "Post uncollected successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in uncollect_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@collected_posts_bp.route('/collected_posts', methods=['GET', 'OPTIONS'])
@token_required
def get_collected_posts(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        collected_posts = db.session.query(Post).join(CollectedPost).filter(CollectedPost.user_id == current_user.id).order_by(CollectedPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "user": {
                "id": current_user.id,
                "username": current_user.username
            },
            "collected_posts": [{
                "id": post.id,
                "title": post.title,
                "text": post.text[:100] + "..." if post.text and len(post.text) > 100 else post.text,
                "related_workout": post.related_workout,
                "views": post.views,
                "likes": post.likes,
                "collections": post.collections,
                "created_at": post.created_at,
                "author": post.user.username
            } for post in collected_posts.items],
            "total": collected_posts.total,
            "pages": collected_posts.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_collected_posts: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500