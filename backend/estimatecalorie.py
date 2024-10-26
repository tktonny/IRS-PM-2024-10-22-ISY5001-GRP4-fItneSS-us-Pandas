from flask import Blueprint, jsonify, current_app
from extensions import db
from models import UserBodyInformation
from auth import token_required
from workoutrecommendation.weight_loss_estimator_ver5 import WeightLossEstimator
import logging
import numpy as np

estimate_bp = Blueprint('estimate', __name__)
estimator = WeightLossEstimator()

logging.basicConfig(level=logging.DEBUG)

def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    return obj

@estimate_bp.route('/estimate', methods=['GET'])
@token_required
def estimate_weight_loss(current_user):
    try:
        # 从数据库获取用户的身体信息
        user_info = UserBodyInformation.query.get(current_user.id)
        
        if not user_info:
            return jsonify({"error": "User body information not found"}), 404

        # 使用数据库中的信息
        gender = user_info.gender
        age = user_info.age
        height = float(user_info.height)
        current_weight = float(user_info.current_weight)
        target_weight = float(user_info.target_weight)
        experience_level = user_info.experience_level

        current_app.logger.debug(f"User info from database: gender={gender}, age={age}, height={height}, current_weight={current_weight}, target_weight={target_weight}, experience_level={experience_level}")

        # 获取估算结果
        result = estimator.get_estimate_object(gender, age, height, current_weight, target_weight)
        current_app.logger.debug(f"Raw estimation result: {result}")

        # Convert NumPy types to Python native types recursively
        result = convert_numpy_types(result)

        # 构造新的响应对象
        response = {
            "message": result['message'],
            "input_params": result['input_params'],
            "single_plan": result['single_plan'],
            "mixed_plan": result['mixed_plan']
        }

        # 记录最终的响应
        current_app.logger.debug(f"Final response: {response}")

        return jsonify(response)

    except ValueError as ve:
        current_app.logger.error(f"Value error occurred: {str(ve)}")
        return jsonify({"error": "Invalid input data"}), 400
    except AttributeError as ae:
        current_app.logger.error(f"Attribute error occurred: {str(ae)}")
        return jsonify({"error": "Missing required user information"}), 400
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during estimation"}), 500

@estimate_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({"error": "Internal Server Error"}), 500

@estimate_bp.errorhandler(404)
def not_found_error(error):
    current_app.logger.error(f"Not Found Error: {str(error)}")
    return jsonify({"error": "Resource not found"}), 404

@estimate_bp.errorhandler(400)
def bad_request_error(error):
    current_app.logger.error(f"Bad Request Error: {str(error)}")
    return jsonify({"error": "Bad request"}), 400