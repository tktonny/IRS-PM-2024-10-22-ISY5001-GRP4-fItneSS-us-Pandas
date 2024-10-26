from flask import Blueprint, request, jsonify
from app import db
from models import Comment, Post
from auth import token_required

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/comment', methods=['POST', 'OPTIONS'])
@token_required
def create_comment(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.get_json()
        if not data or not data.get('text') or not data.get('post_id'):
            return jsonify({"message": "Comment text and post ID are required"}), 400

        post = Post.query.get(data['post_id'])
        if not post:
            return jsonify({"message": "Post not found"}), 404

        new_comment = Comment(
            user_id=current_user.id,
            post_id=data['post_id'],
            text=data['text']
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({
            "message": "Comment created successfully",
            "comment_id": new_comment.id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_comment: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@comments_bp.route('/comment/<int:comment_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_comment(current_user, comment_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"message": "Comment not found"}), 404
        
        if comment.user_id != current_user.id:
            return jsonify({"message": "You can only delete your own comments"}), 403

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_comment: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@comments_bp.route('/user/comments', methods=['GET', 'OPTIONS'])
@token_required
def get_user_comments(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "comments": [{
                "id": comment.id,
                "post_id": comment.post_id,
                "text": comment.text,
                "created_at": comment.created_at,
            } for comment in comments.items],
            "total": comments.total,
            "pages": comments.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_user_comments: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# 获取特定帖子的所有评论
@comments_bp.route('/post/<int:post_id>/comments', methods=['GET', 'OPTIONS'])
def get_post_comments(post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "comments": [{
                "id": comment.id,
                "user_id": comment.user_id,
                "text": comment.text,
                "created_at": comment.created_at,
            } for comment in comments.items],
            "total": comments.total,
            "pages": comments.pages,
            "current_page": page
        }), 200
    except Exception as e:
        print(f"Error in get_post_comments: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500