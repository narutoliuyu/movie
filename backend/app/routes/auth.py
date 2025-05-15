from flask import Blueprint, jsonify, request
from app.models.user import User
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # 验证必填字段
        if not all([username, email, password]):
            return jsonify({
                'status': 'error',
                'message': '用户名、邮箱和密码不能为空'
            }), 400
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 'error',
                'message': '用户名已存在'
            }), 400
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': '邮箱已被注册'
            }), 400
            
        # 创建新用户
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '注册成功',
            'data': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': '用户名和密码不能为空'
            }), 400
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({
                'status': 'error',
                'message': '用户名或密码错误'
            }), 401
            
        # 生成 JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=7)
            },
            os.getenv('SECRET_KEY', 'your-secret-key'),
            algorithm='HS256'
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'登录失败: {str(e)}'
        }), 500 