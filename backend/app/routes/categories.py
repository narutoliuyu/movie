from flask import Blueprint, jsonify, request
from app.models.category import Category
from app import db
from sqlalchemy import text

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        # 测试数据库连接
        db.session.execute(text('SELECT 1'))
        print("数据库连接正常")
        
        # 检查表是否存在
        result = db.session.execute(text("SHOW TABLES LIKE 'category'"))
        if not result.fetchone():
            print("category表不存在")
            return jsonify({
                'status': 'error',
                'message': 'category表不存在'
            }), 500
            
        # 从category表中获取所有分类
        categories = Category.query.all()
        print("数据库查询结果:", categories)
        
        # 将结果转换为列表
        categories_list = []
        for category in categories:
            category_dict = category.to_dict()
            categories_list.append(category_dict)
            print(f"处理分类: {category_dict}")
        
        print("最终分类列表:", categories_list)
        
        return jsonify({
            'status': 'success',
            'data': categories_list
        })
    except Exception as e:
        print(f"获取分类错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取分类失败: {str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'status': 'success',
            'data': category.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 