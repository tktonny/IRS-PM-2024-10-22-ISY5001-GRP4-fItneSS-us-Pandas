from flask import Blueprint, request, jsonify
from app import db
from models import ViewedPost, Post
from auth import token_required
from sqlalchemy import func

viewed_posts_bp = Blueprint('viewed_posts', __name__)

@viewed_posts_bp.route('/view_post/<int:post_id>', methods=['POST', 'OPTIONS'])
@token_required
def view_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404

        viewed_post = ViewedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        if viewed_post:
            # 如果已经有浏览记录，更新浏览时间
            viewed_post.viewed_at = func.now()
        else:
            # 如果没有浏览记录，创建新记录
            new_view = ViewedPost(user_id=current_user.id, post_id=post_id)
            db.session.add(new_view)

        post.views += 1
        db.session.commit()
        return jsonify({"message": "View recorded successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in view_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@viewed_posts_bp.route('/viewed_posts', methods=['GET', 'OPTIONS'])
@token_required
def get_viewed_posts(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        viewed_posts = db.session.query(Post).join(ViewedPost).filter(ViewedPost.user_id == current_user.id).order_by(ViewedPost.viewed_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "user": {
                "id": current_user.id,
                "username": current_user.username
            },
            "viewed_posts": [{
                "id": post.id,
                "title": post.title,
                "text": post.text[:100] + "..." if post.text and len(post.text) > 100 else post.text,
                "related_workout": post.related_workout,
                "views": post.views,
                "likes": post.likes,
                "collections": post.collections,
                "created_at": post.created_at,
                "author": post.user.username,
                "viewed_at": ViewedPost.query.filter_by(user_id=current_user.id, post_id=post.id).first().viewed_at
            } for post in viewed_posts.items],
            "total": viewed_posts.total,
            "pages": viewed_posts.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_viewed_posts: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500