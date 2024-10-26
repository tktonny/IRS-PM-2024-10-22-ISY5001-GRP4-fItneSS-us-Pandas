from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Post, Comment, LikedPost, CollectedPost, ViewedPost, PostImage, Image, User
from auth import token_required
from sqlalchemy import and_, not_
from sqlalchemy.orm import aliased
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from recommendation.recommendation import create_post_embedding

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/post', methods=['POST', 'OPTIONS'])
@token_required
def create_post(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        title = request.form.get('title')
        text = request.form.get('text')
        related_workout = request.form.get('related_workout')

        if not title:
            return jsonify({"message": "Title is required"}), 400

        new_post = Post(
            user_id=current_user.id,
            title=title,
            text=text,
            related_workout=related_workout
        )
        db.session.add(new_post)
        db.session.flush()
        img_path = ""
        images = request.files.getlist('images')
        if not images:
            return jsonify({"message": "At least one image is required"}), 400
        for i, file in enumerate(images):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                img_path = file_path
                
                new_image = Image(
                    file_name=unique_filename,
                    file_path=file_path,
                    file_type=file.content_type,
                    file_size=os.path.getsize(file_path),
                    image_metadata=json.dumps({"original_filename": filename})
                )
                db.session.add(new_image)
                db.session.flush()

                new_post_image = PostImage(post_id=new_post.id, image_id=new_image.id, image_order=i)
                db.session.add(new_post_image)

        db.session.commit()
        #post_embedding = create_post_embedding(img_path, title, text)
        #print(post_embedding)
        return jsonify({
            "message": "Post created successfully with images",
            "post_id": new_post.id,
            "image_count": len(images)
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route('/post/<int:post_id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404
        if post.user_id != current_user.id:
            return jsonify({"message": "You can only update your own posts"}), 403

        title = request.form.get('title')
        text = request.form.get('text')
        related_workout = request.form.get('related_workout')
        
        if title:
            post.title = title
        if text:
            post.text = text
        if related_workout:
            post.related_workout = related_workout

        new_images = request.files.getlist('new_images')
        removed_image_ids = request.form.getlist('removed_image_ids')

        for image_id in removed_image_ids:
            post_image = PostImage.query.filter_by(post_id=post.id, image_id=image_id).first()
            if post_image:
                db.session.delete(post_image)
                if not PostImage.query.filter(PostImage.image_id == image_id, PostImage.post_id != post.id).first():
                    image = Image.query.get(image_id)
                    if image:
                        db.session.delete(image)
                        if os.path.exists(image.file_path):
                            os.remove(image.file_path)

        for i, file in enumerate(new_images):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                new_image = Image(
                    file_name=unique_filename,
                    file_path=file_path,
                    file_type=file.content_type,
                    file_size=os.path.getsize(file_path),
                    image_metadata=json.dumps({"original_filename": filename})
                )
                db.session.add(new_image)
                db.session.flush()

                new_post_image = PostImage(post_id=post.id, image_id=new_image.id, image_order=i)
                db.session.add(new_post_image)

        db.session.commit()
        return jsonify({"message": "Post updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@posts_bp.route('/post/<int:post_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_post(current_user, post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404
        if post.user_id != current_user.id:
            return jsonify({"message": "You can only delete your own posts"}), 403

        # 删除相关的评论
        Comment.query.filter_by(post_id=post_id).delete()
        
        # 删除相关的点赞、收藏和浏览记录
        LikedPost.query.filter_by(post_id=post_id).delete()
        CollectedPost.query.filter_by(post_id=post_id).delete()
        ViewedPost.query.filter_by(post_id=post_id).delete()

        # 获取与这个帖子相关的所有图片ID
        post_images = PostImage.query.filter_by(post_id=post_id).all()
        image_ids = [pi.image_id for pi in post_images]

        # 删除PostImage记录
        PostImage.query.filter_by(post_id=post_id).delete()

        # 删除那些只与这个帖子相关的Image记录
        for image_id in image_ids:
            # 检查这个图片是否只与当前帖子相关
            if not PostImage.query.filter(PostImage.image_id == image_id, PostImage.post_id != post_id).first():
                image = Image.query.get(image_id)
                if image:
                    # 删除物理文件
                    if os.path.exists(image.file_path):
                        os.remove(image.file_path)
                    # 删除数据库记录
                    db.session.delete(image)

        # 删除帖子本身
        db.session.delete(post)

        # 提交所有更改
        db.session.commit()
        return jsonify({"message": "Post and all related data deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@posts_bp.route('/posts', methods=['GET', 'OPTIONS'])
@token_required
def get_posts(current_user):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        response = {
            "posts": [{
                "id": post.id,
                "title": post.title,
                "text": post.text[:100] + "..." if post.text and len(post.text) > 100 else post.text,
                "related_workout": post.related_workout,
                "views": post.views,
                "likes": post.likes,
                "collections": post.collections,
                "created_at": post.created_at,
                "author": current_user.username
            } for post in posts.items],
            "total": posts.total,
            "pages": posts.pages,
            "current_page": page
        }
        current_app.logger.debug(f"Final response: {response}")
        return jsonify(response), 200
    except Exception as e:
        print(f"Error in get_posts: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@posts_bp.route('/post/<int:post_id>', methods=['GET', 'OPTIONS'])
def get_post(post_id):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found"}), 404
        
        post.views += 1
        db.session.commit()

        post_images = PostImage.query.filter_by(post_id=post.id).order_by(PostImage.image_order).all()
        images = []
        for post_image in post_images:
            image = Image.query.get(post_image.image_id)
            if image:
                images.append({
                    "id": image.id,
                    "file_name": image.file_name,
                    "file_path": image.file_path,
                    "file_type": image.file_type,
                    "file_size": image.file_size,
                    "image_order": post_image.image_order
                })

        # 获取作者信息
        author = User.query.get(post.user_id)
        author_name = author.username if author else "Unknown"

        return jsonify({
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "related_workout": post.related_workout,
            "views": post.views,
            "likes": post.likes,
            "collections": post.collections,
            "created_at": post.created_at,
            "author": author_name,  # 使用查询到的作者名
            "images": images
        }), 200

    except Exception as e:
        print(f"Error in get_post: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500
    

'''
修改了/post,使得用户必须上传图片才能发布帖子
另外想问 那个功能 返回200和201有什么区别 为什么要返回201
'''