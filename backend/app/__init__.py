from flask import Flask, jsonify
from flask_cors import CORS
from app.config.config import Config
from .extensions import db
from .routes.movies import movies_bp
# 使用新创建的auth_bp
from .routes.auth import auth_bp  
from .routes.categories import categories_bp
from .routes.user import user_bp
from .routes.history import history_bp
from .routes.search import bp as search_bp
from flask_jwt_extended import JWTManager

# 删除临时的auth_bp蓝图
# from flask import Blueprint, request
# auth_bp = Blueprint('auth', __name__)

# 删除临时登录路由
# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         
#         # 简化版登录，返回固定token供测试
#         return jsonify({
#             'status': 'success',
#             'token': 'test_token_12345',
#             'user_id': 1,
#             'username': username or 'test_user'
#         })
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': f'登录失败: {str(e)}'
#         }), 500

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:5174"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "User-Agent"],
            "supports_credentials": True
        }
    })
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 注册蓝图
    app.register_blueprint(movies_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(user_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(search_bp, url_prefix='/api')
    
    # 添加开发环境信息中间件
    @app.before_request
    def add_dev_to_user_agent():
        """在开发环境中向请求添加DEV标记"""
        if app.debug or app.config.get('TESTING'):
            from flask import request
            # 将DEV标记添加到现有的User-Agent中
            if not request.headers.get('User-Agent', '').endswith('DEV'):
                request.environ['HTTP_USER_AGENT'] = request.headers.get('User-Agent', '') + ' DEV'
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 添加错误处理
    @app.errorhandler(500)
    def handle_500_error(e):
        print(f"服务器错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'服务器内部错误: {str(e)}'
        }), 500
    
    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({
            'status': 'error',
            'message': '请求的资源不存在'
        }), 404
    
    # 添加路由测试
    @app.route('/api/test')
    def test():
        return {'message': 'API is working'}
    
    return app 