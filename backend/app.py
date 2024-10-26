from flask import Flask
from flask_cors import CORS
from extensions import db, bcrypt, mail
import ssl
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    # 配置应用
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:TONNY21tonny21@localhost/fItneSS_us'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'  # 请更改为一个安全的密钥
    
    # 邮件配置
    app.config['MAIL_SERVER'] = 'smtp.qq.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = '3192593037@qq.com'
    app.config['MAIL_PASSWORD'] = 'chtirrhvxzhfddec'  # 请确保这是正确的授权码
    app.config['MAIL_DEFAULT_SENDER'] = '3192593037@qq.com'

    # SSL Context
    context = ssl.create_default_context()
    app.config['MAIL_SSL_CONTEXT'] = context

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # 更新 CORS 配置
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    CORS(app, resources={r"/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": "*"
    }})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    # 导入并注册蓝图
    from auth import auth_bp
    from posts import posts_bp
    from comments import comments_bp
    from liked_posts import liked_posts_bp 
    from collected_posts import collected_posts_bp
    from viewed_posts import viewed_posts_bp
    from user_follows import user_follows_bp
    from workoutinformation import workout_info_bp
    from image import image_bp
    from post_images import post_images_bp
    from body_info import body_info_bp
    from closestworkout import workout_recommender_bp
    from estimatecalorie import estimate_bp
    from gymfinder import gym_finder_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(liked_posts_bp)
    app.register_blueprint(collected_posts_bp)
    app.register_blueprint(viewed_posts_bp)
    app.register_blueprint(user_follows_bp)
    app.register_blueprint(workout_info_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(post_images_bp)
    app.register_blueprint(body_info_bp)
    app.register_blueprint(estimate_bp)
    app.register_blueprint(workout_recommender_bp)
    app.register_blueprint(gym_finder_bp)


    return app

if __name__ == '__main__':
    app = create_app()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
       os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)