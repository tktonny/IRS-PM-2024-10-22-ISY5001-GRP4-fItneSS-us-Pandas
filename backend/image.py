from flask import Blueprint, request, jsonify, current_app
from app import db
from models import Image
from auth import token_required
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime

image_bp = Blueprint('image', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_bp.route('/upload', methods=['POST', 'OPTIONS'])
@token_required
def upload_image(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
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
            db.session.commit()
            
            return jsonify({
                "message": "Image uploaded successfully",
                "image_id": new_image.id,
                "file_name": new_image.file_name
            }), 201
        else:
            return jsonify({"message": "File type not allowed"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in upload_image: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@image_bp.route('/image/<int:image_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_image(current_user, image_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        image = Image.query.get(image_id)
        if not image:
            return jsonify({"message": "Image not found"}), 404
        
        # Delete the file from the filesystem
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        db.session.delete(image)
        db.session.commit()
        return jsonify({"message": "Image deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_image: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@image_bp.route('/images', methods=['GET', 'OPTIONS'])
@token_required
def get_images(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        images = Image.query.all()
        return jsonify({
            "images": [{
                "id": img.id,
                "file_name": img.file_name,
                "file_type": img.file_type,
                "file_size": img.file_size,
                "upload_date": img.upload_date.isoformat(),
                "metadata": json.loads(img.image_metadata) if img.image_metadata else None
            } for img in images]
        }), 200
    except Exception as e:
        print(f"Error in get_images: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500