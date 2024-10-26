from flask import Blueprint, request, jsonify
from models import UserBodyInformation
from extensions import db
from auth import token_required

body_info_bp = Blueprint('body_info', __name__)

@body_info_bp.route('/body_info', methods=['POST'])
@token_required
def add_body_info(current_user):
    try:
        data = request.get_json()
        
        # 检查是否已存在该用户的体型信息
        existing_info = UserBodyInformation.query.get(current_user.id)
        if existing_info:
            return jsonify({"message": "Body information already exists for this user"}), 400

        new_body_info = UserBodyInformation(
            id=current_user.id,
            gender=data['gender'],
            age=data['age'],
            height=data['height'],
            current_weight=data['current_weight'],
            target_weight=data['target_weight'],
            experience_level=data['experience_level']
        )

        db.session.add(new_body_info)
        db.session.commit()

        return jsonify({"message": "Body information added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding body information: {str(e)}"}), 500

@body_info_bp.route('/body_info', methods=['PATCH'])
@token_required
def update_body_info(current_user):
    try:
        data = request.get_json()
        
        body_info = UserBodyInformation.query.get(current_user.id)
        if not body_info:
            return jsonify({"message": "Body information not found for this user"}), 404

        # 只更新提供的字段
        if 'gender' in data:
            body_info.gender = data['gender']
        if 'age' in data:
            body_info.age = data['age']
        if 'height' in data:
            body_info.height = data['height']
        if 'current_weight' in data:
            body_info.current_weight = data['current_weight']
        if 'target_weight' in data:
            body_info.target_weight = data['target_weight']
        if 'experience_level' in data:
            body_info.experience_level = data['experience_level']

        db.session.commit()

        return jsonify({"message": "Body information updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating body information: {str(e)}"}), 500
#fetch('/body_info', {      此处的示例为更新体重
#  method: 'PATCH',
#  headers: {
#    'Content-Type': 'application/json',
#    'Authorization': 'Bearer YOUR_TOKEN_HERE'
#  },
#  body: JSON.stringify({
#    current_weight: 75.5
##})
#.then(response => response.json())
#.then(data => console.log(data))
#.catch(error => console.error('Error:', error));

@body_info_bp.route('/body_info', methods=['DELETE'])
@token_required
def delete_body_info(current_user):
    try:
        body_info = UserBodyInformation.query.get(current_user.id)
        if not body_info:
            return jsonify({"message": "Body information not found for this user"}), 404

        db.session.delete(body_info)
        db.session.commit()

        return jsonify({"message": "Body information deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting body information: {str(e)}"}), 500

@body_info_bp.route('/body_info', methods=['GET'])
@token_required
def get_body_info(current_user):
    try:
        body_info = UserBodyInformation.query.get(current_user.id)
        if not body_info:
            return jsonify({"message": "Body information not found for this user"}), 404

        info = {
            "gender": body_info.gender,
            "age": body_info.age,
            "height": float(body_info.height),
            "current_weight": float(body_info.current_weight),
            "target_weight": float(body_info.target_weight),
            "experience_level": body_info.experience_level,
            "created_at": body_info.created_at.isoformat(),
            "updated_at": body_info.updated_at.isoformat()
        }

        return jsonify(info), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving body information: {str(e)}"}), 500