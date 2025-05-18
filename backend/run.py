from app import create_app, db
from app.models.category import Category
from app.models.movie import Movie
from app.models.movie_ranking import MovieRanking
from app.models.search_history import SearchHistory
from datetime import datetime, date, timedelta

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

        

        # 检查是否已有电影排名数据
        if MovieRanking.query.count() == 0 and Movie.query.count() > 0:
            # 获取所有电影
            movies = Movie.query.all()
            
            # 为前5部电影添加排名
            for i, movie in enumerate(movies[:5], 1):
                ranking = MovieRanking(
                    movie_id=movie.id,
                    rank=i,
                    views=1000 - i * 100  # 简单的浏览量，排名越高浏览量越多
                )
                db.session.add(ranking)
            
            db.session.commit()
            print("已添加默认电影排名数据")
            
        # 检查是否已有搜索历史数据    
        if SearchHistory.query.count() == 0:
            # 添加默认搜索历史数据
            default_search_history = [
                {'user_id': 1, 'search_query': '你好-李焕英', 'created_at': datetime.utcnow() - timedelta(days=1)},
                {'user_id': 1, 'search_query': '你的婚礼', 'created_at': datetime.utcnow() - timedelta(days=2)},
                {'user_id': 1, 'search_query': '刺杀小说家', 'created_at': datetime.utcnow() - timedelta(days=3)}
            ]
            
            for history_data in default_search_history:
                history = SearchHistory(**history_data)
                db.session.add(history)
                
            db.session.commit()
            print("已添加默认搜索历史数据")

if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(debug=True, port=5000) 