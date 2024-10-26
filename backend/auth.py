from flask import Blueprint, request, jsonify, url_for, render_template_string, current_app
from flask_mail import Message
from extensions import db, bcrypt, mail
from models import User
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

# 用于临时存储待验证用户信息的字典
pending_users = {}

# 验证邮件的模板内容，该内容可被替换
PASSWORD_RESET_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
</head>
<body>
    <h2>Reset Your Password</h2>
    <form method="POST">
        <label for="new_password">New Password:</label>
        <input type="password" id="new_password" name="new_password" required>
        <br>
        <input type="submit" value="Reset Password">
    </form>
</body>
</html>
'''

def get_url_scheme():
    # 默认使用 HTTPS，除非明确设置为 False
    use_https = os.environ.get('USE_HTTPS', 'True').lower() != 'false'
    scheme = 'https' if use_https else 'http'
    return scheme

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200  # 让 OPTIONS 请求直接通过

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            # 移除 'Bearer ' 前缀（如果存在）
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': f'Token error: {str(e)}'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not all(k in data for k in ("username", "email", "password")):
            return jsonify({"message": "Missing required fields"}), 400

        existing_user = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
        if existing_user:
            return jsonify({"message": "Username or email already exists"}), 409

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # 生成验证令牌
        token = jwt.encode({
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'])

        # 存储待验证用户信息
        pending_users[token] = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password
        }

        # 生成验证链接
        verification_link = f"{get_url_scheme()}://{request.host}{url_for('auth.verify_email', token=token)}"
        print(f"Debug - Verification link: {verification_link}")  # 调试用

        # 发送验证邮件
        msg = Message("Please verify your email", recipients=[data['email']])
        msg.body = f"Click the link to verify your email and complete registration: {verification_link}"
        mail.send(msg)

        return jsonify({"message": "Verification email sent. Please check your email to complete registration."}), 200
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    try:
        # 解码令牌
        user_info = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        
        # 检查令牌是否在待验证用户列表中
        if token not in pending_users:
            return jsonify({"message": "Invalid or expired verification link."}), 400

        # 从待验证用户列表中获取用户信息
        user_data = pending_users[token]

        # 创建新用户并添加到数据库
        new_user = User(username=user_data['username'], email=user_data['email'], password=user_data['password'])
        db.session.add(new_user)
        db.session.commit()

        # 从待验证用户列表中移除
        del pending_users[token]

        # 自动执行登录操作
        login_token = jwt.encode({
            'user_id': new_user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'])

        return jsonify({
            "message": "Email verified and logged in successfully!",
            "token": login_token,
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "The verification link has expired."}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid verification link."}), 400
    except Exception as e:
        print(f"Error in verify_email: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('login') or not data.get('password'):
            return jsonify({"message": "Missing login credentials"}), 400
        
        user = User.query.filter((User.username == data['login']) | (User.email == data['login'])).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        if bcrypt.check_password_hash(user.password, data['password']):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
            }, current_app.config['SECRET_KEY'])
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }), 200
        
        return jsonify({"message": "Invalid password"}), 401
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route('/password_recovery', methods=['POST'])
def password_recovery():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user:
            # 生成密码重置令牌
            token = jwt.encode({'user_id': user.id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)}, current_app.config['SECRET_KEY'])
            reset_link = f"{get_url_scheme()}://{request.host}{url_for('auth.reset_password', token=token)}"
            
            # 发送密码重置邮件
            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f"Click the following link to reset your password: {reset_link}"
            mail.send(msg)
            
            return jsonify({"message": "Password reset email sent"}), 200
        return jsonify({"message": "Email not found"}), 404
    except Exception as e:
        print(f"Error in password_recovery: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # 验证令牌
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"message": "User not found"}), 404

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            if not new_password:
                return jsonify({"message": "New password is required"}), 400

            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            return jsonify({"message": "Password has been reset successfully"}), 200
        else:
            # GET 请求：显示重置密码的表单
            return render_template_string(PASSWORD_RESET_TEMPLATE)

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "The password reset link has expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid password reset link"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in reset_password: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

@auth_bp.route('/check_login_status', methods=['GET'])
@token_required
def check_login_status(current_user):
    return jsonify({
        "logged_in": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    }), 200