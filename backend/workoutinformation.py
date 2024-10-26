from flask import Blueprint, request, jsonify
from app import db
from models import WorkoutInformation
from auth import token_required
from datetime import datetime

workout_info_bp = Blueprint('workout_info', __name__)

@workout_info_bp.route('/workout', methods=['POST', 'OPTIONS'])
@token_required
def add_workout(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        new_workout = WorkoutInformation(
            user_id=current_user.id,
            workout_type=data.get('workout_type'),
            duration=data.get('duration'),
            calories_burned=data.get('calories_burned'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else None
        )
        db.session.add(new_workout)
        db.session.commit()
        return jsonify({"message": "Workout information added successfully", "id": new_workout.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_workout: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@workout_info_bp.route('/workout/<int:workout_id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_workout(current_user, workout_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        workout = WorkoutInformation.query.get(workout_id)
        if not workout:
            return jsonify({"message": "Workout information not found"}), 404
        if workout.user_id != current_user.id:
            return jsonify({"message": "Unauthorized to update this workout information"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        workout.workout_type = data.get('workout_type', workout.workout_type)
        workout.duration = data.get('duration', workout.duration)
        workout.calories_burned = data.get('calories_burned', workout.calories_burned)
        if data.get('date'):
            workout.date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({"message": "Workout information updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_workout: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@workout_info_bp.route('/workout/<int:workout_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_workout(current_user, workout_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        workout = WorkoutInformation.query.get(workout_id)
        if not workout:
            return jsonify({"message": "Workout information not found"}), 404
        if workout.user_id != current_user.id:
            return jsonify({"message": "Unauthorized to delete this workout information"}), 403
        
        db.session.delete(workout)
        db.session.commit()
        return jsonify({"message": "Workout information deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_workout: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@workout_info_bp.route('/workouts', methods=['GET', 'OPTIONS'])
@token_required
def get_workouts(current_user):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        workouts = WorkoutInformation.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            "workouts": [{
                "id": w.id,
                "workout_type": w.workout_type,
                "duration": w.duration,
                "calories_burned": w.calories_burned,
                "date": w.date.strftime('%Y-%m-%d') if w.date else None
            } for w in workouts]
        }), 200
    except Exception as e:
        print(f"Error in get_workouts: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500