from flask import Blueprint, request, jsonify
from app import db
from models import PostImage, Post, Image
from auth import token_required
from sqlalchemy.exc import IntegrityError

post_images_bp = Blueprint('post_images', __name__)

@post_images_bp.route('/post/<int:post_id>/image', methods=['POST', 'OPTIONS'])
@token_required
def add_image_to_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post or post.user_id != current_user.id:
            return jsonify({"message": "Post not found or unauthorized"}), 404

        data = request.get_json()
        image_id = data.get('image_id')
        image_order = data.get('image_order', 0)

        if not Image.query.get(image_id):
            return jsonify({"message": "Image not found"}), 404

        new_post_image = PostImage(post_id=post_id, image_id=image_id, image_order=image_order)
        db.session.add(new_post_image)
        db.session.commit()
        return jsonify({"message": "Image added to post successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "This image is already associated with the post"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_image_to_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@post_images_bp.route('/post/<int:post_id>/image/<int:image_id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_post_image(current_user, post_id, image_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post or post.user_id != current_user.id:
            return jsonify({"message": "Post not found or unauthorized"}), 404

        post_image = PostImage.query.filter_by(post_id=post_id, image_id=image_id).first()
        if not post_image:
            return jsonify({"message": "Image not associated with this post"}), 404

        data = request.get_json()
        new_image_order = data.get('image_order')
        if new_image_order is not None:
            post_image.image_order = new_image_order
            db.session.commit()
            return jsonify({"message": "Image order updated successfully"}), 200
        else:
            return jsonify({"message": "No update data provided"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_post_image: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@post_images_bp.route('/post/<int:post_id>/image/<int:image_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def remove_image_from_post(current_user, post_id, image_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        post = Post.query.get(post_id)
        if not post or post.user_id != current_user.id:
            return jsonify({"message": "Post not found or unauthorized"}), 404

        post_image = PostImage.query.filter_by(post_id=post_id, image_id=image_id).first()
        if not post_image:
            return jsonify({"message": "Image not associated with this post"}), 404

        db.session.delete(post_image)
        db.session.commit()
        return jsonify({"message": "Image removed from post successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in remove_image_from_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500