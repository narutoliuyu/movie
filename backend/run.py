from app import create_app, db
from app.models.category import Category

app = create_app()

def init_db():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有分类数据
        if Category.query.count() == 0:
            # 添加默认分类
            default_categories = [
                {'name': '动作', 'description': '动作类电影'},
                {'name': '喜剧', 'description': '喜剧类电影'},
                {'name': '科幻', 'description': '科幻类电影'},
                {'name': '爱情', 'description': '爱情类电影'},
                {'name': '动漫', 'description': '动漫类电影'},
                {'name': '剧情', 'description': '剧情类电影'},
                {'name': '恐怖', 'description': '恐怖类电影'},
                {'name': '纪录片', 'description': '纪录片类电影'}
            ]
            
            for category_data in default_categories:
                category = Category(**category_data)
                db.session.add(category)
            
            db.session.commit()
            print("已添加默认分类数据")

if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(debug=True, port=5000) 