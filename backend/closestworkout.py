from flask import Blueprint, jsonify, current_app
from extensions import db
from models import UserBodyInformation
from auth import token_required
from workoutrecommendation.workout_recommender_predict2 import WorkoutRecommender
import logging
import warnings
import os


# 创建蓝图
workout_recommender_bp = Blueprint('workout_recommender', __name__)

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

# 抑制所有 FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# 初始化推荐器并加载模型
recommender = WorkoutRecommender()

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建到 workoutrecommendation/models 文件夹的路径
models_dir = os.path.join(current_dir, 'workoutrecommendation', 'models')

# 加载模型
recommender.load_models(models_dir)

@workout_recommender_bp.route('/recommend_workout', methods=['GET'])
@token_required
def recommend_workout(current_user):
    try:
        # 从数据库获取用户的身体信息
        user_info = UserBodyInformation.query.get(current_user.id)
        
        if not user_info:
            return jsonify({"error": "User body information not found"}), 404

        # 使用数据库中的信息
        age = user_info.age
        gender = user_info.gender.capitalize()  # 确保首字母大写
        weight = float(user_info.current_weight)  # kg
        height = float(user_info.height) / 100  # 转换为米
        experience_level = int(user_info.experience_level)

        current_app.logger.debug(f"User info from database: age={age}, gender={gender}, weight={weight}, height={height}, experience_level={experience_level}")

        # 获取推荐
        recommendations = recommender.get_recommendation(age, gender, weight, height, experience_level)
        
        # 确保recommendations是一个字典
        if not isinstance(recommendations, dict):
            recommendations = {"workouts": recommendations}

        # 添加用户信息到返回的对象中
        response_object = {
            "user_info": {
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "experience_level": experience_level
            },
            "recommendations": recommendations
        }

        current_app.logger.debug(f"Final response: {response_object}")

        return jsonify(response_object), 200
    except ValueError as ve:
        current_app.logger.error(f"Value error occurred: {str(ve)}")
        return jsonify({"error": "Invalid input data"}), 400
    except AttributeError as ae:
        current_app.logger.error(f"Attribute error occurred: {str(ae)}")
        return jsonify({"error": "Missing required user information"}), 400
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during recommendation"}), 500

@workout_recommender_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({"error": "Internal Server Error"}), 500

@workout_recommender_bp.errorhandler(404)
def not_found_error(error):
    current_app.logger.error(f"Not Found Error: {str(error)}")
    return jsonify({"error": "Resource not found"}), 404

@workout_recommender_bp.errorhandler(400)
def bad_request_error(error):
    current_app.logger.error(f"Bad Request Error: {str(error)}")
    return jsonify({"error": "Bad request"}), 400
