from flask import Flask, jsonify
from flask_cors import CORS
from app.config.config import Config
from .extensions import db
from .routes.movies import movies_bp
from .routes.auth import auth_bp
from .routes.categories import categories_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(movies_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api')
    
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