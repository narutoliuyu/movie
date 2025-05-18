from flask import Blueprint, jsonify, request, current_app
from ..models.user import User
from ..models.history import WatchHistory
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        # 验证身份
        jwt_identity = get_jwt_identity()
        try:
            jwt_identity = int(jwt_identity)
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': '无效的用户ID'
            }), 400
        
        if jwt_identity != user_id:
            return jsonify({
                'status': 'error',
                'message': '无权访问此用户信息'
            }), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': '用户不存在'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@user_bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_user_by_params():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': '未提供用户ID'
            }), 400
            
        # 验证身份
        jwt_identity = get_jwt_identity()
        try:
            jwt_identity = int(jwt_identity)
            user_id = int(user_id)
        except (ValueError, TypeError):
            if 'DEV' in request.headers.get('User-Agent', ''):
                # 开发环境返回模拟数据
                user_id = 1
            else:
                return jsonify({
                    'status': 'error',
                    'message': '无效的用户ID'
                }), 400
        
        if jwt_identity != user_id:
            return jsonify({
                'status': 'error',
                'message': '无权访问此用户信息'
            }), 403
            
        user = User.query.get(user_id)
        if not user:
            if 'DEV' in request.headers.get('User-Agent', ''):
                # 开发环境返回模拟数据
                return jsonify({
                    'status': 'success',
                    'data': {
                        'id': user_id,
                        'username': '测试用户',
                        'email': 'test@example.com',
                        'created_at': datetime.now().isoformat(),
                        'avatar': ''
                    }
                })
            return jsonify({
                'status': 'error',
                'message': '用户不存在'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at,
                'avatar': user.avatar
            }
        })
    except Exception as e:
        # 开发环境返回模拟数据
        if 'DEV' in request.headers.get('User-Agent', ''):
            return jsonify({
                'status': 'success',
                'data': {
                    'id': 1,
                    'username': '测试用户',
                    'email': 'test@example.com',
                    'created_at': datetime.now().isoformat(),
                    'avatar': ''
                }
            })
        return jsonify({
            'status': 'error',
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@user_bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        # 从JWT获取用户ID
        user_id = get_jwt_identity()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': '用户不存在'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@user_bp.route('/api/user/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({
            'status': 'error',
            'message': '未提供头像文件'
        }), 400
        
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': '未选择文件'
        }), 400
        
    # 获取用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 确保上传目录存在
    upload_folder = os.path.join(current_app.root_path, 'static', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    filename = f"user_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # 更新用户头像URL - 使用相对路径存储
    avatar_relative_url = f"/static/avatars/{filename}"
    user.avatar = avatar_relative_url
    db.session.commit()
    
    # 构建完整URL以返回给前端
    # 从请求中获取主机和协议
    host = request.host_url.rstrip('/')
    avatar_full_url = f"{host}{avatar_relative_url}"
    
    print(f"头像保存成功: {file_path}")
    print(f"头像URL: {avatar_full_url}")
    
    return jsonify({
        'status': 'success',
        'message': '头像上传成功',
        'avatar_url': avatar_full_url,  # 返回完整URL
        'relative_url': avatar_relative_url  # 同时返回相对URL
    })

@user_bp.route('/api/user/update-username', methods=['PUT'])
@jwt_required()
def update_username():
    data = request.json
    if not data or 'username' not in data:
        return jsonify({
            'status': 'error',
            'message': '未提供用户名'
        }), 400
        
    # 获取用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 验证新用户名是否已存在
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user and existing_user.id != user.id:
        return jsonify({
            'status': 'error',
            'message': '用户名已存在'
        }), 400
    
    # 更新用户名
    user.username = data['username']
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '用户名更新成功',
        'username': user.username
    })

@user_bp.route('/api/user/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.json
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({
            'status': 'error',
            'message': '未提供完整的密码信息'
        }), 400
        
    # 获取用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 验证当前密码
    if not check_password_hash(user.password_hash, data['current_password']):
        return jsonify({
            'status': 'error',
            'message': '当前密码不正确'
        }), 400
    
    # 更新密码
    user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '密码修改成功'
    })

@user_bp.route('/api/user/history', methods=['GET'])
@jwt_required()
def get_user_history():
    # 获取用户ID
    user_id = get_jwt_identity()
    
    # 获取用户观看历史
    history = WatchHistory.query.filter_by(user_id=user_id).order_by(WatchHistory.watch_time.desc()).all()
    
    history_data = []
    for item in history:
        history_data.append({
            'id': item.id,
            'movie_id': item.movie_id,
            'title': item.movie.title if item.movie else '未知电影',
            'poster_url': item.movie.poster_url if item.movie else '',
            'watch_time': item.watch_time.isoformat(),
            'progress': item.progress
        })
    
    return jsonify({
        'status': 'success',
        'data': history_data
    })

@user_bp.route('/api/user/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({
            'status': 'error',
            'message': '未提供邮箱'
        }), 400
        
    # 获取用户ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 验证邮箱是否匹配
    if user.email != data['email']:
        return jsonify({
            'status': 'error',
            'message': '邮箱与账号不匹配'
        }), 400
    
    return jsonify({
        'status': 'success',
        'message': '邮箱验证成功'
    }) 