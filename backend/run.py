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

        # 检查是否已有电影数据
        if Movie.query.count() == 0:
            # 添加默认电影
            default_movies = [
                {
                    'title': '我不是药神',
                    'description': '一个印度神油店老板，为救白血病患者，走私特效药',
                    'release_date': date(2018, 7, 5),
                    'movie_type': '剧情/喜剧',
                    'poster_url': 'https://img1.doubanio.com/view/photo/l/public/p2519631635.jpg',
                    'director': '文牧野',
                    'rating': 9.0
                },
                {
                    'title': '孤注一掷',
                    'description': '讲述了在菲律宾博彩厂牌上班的程序员潘生的经历',
                    'release_date': date(2023, 8, 8),
                    'movie_type': '剧情/犯罪',
                    'poster_url': 'https://img1.doubanio.com/view/photo/l/public/p2893981308.jpg',
                    'director': '申奥',
                    'rating': 8.6
                },
                {
                    'title': '哪吒之魔童降世',
                    'description': '讲述了哪吒虽被命运为魔，却逆天而行，追求自我的故事',
                    'release_date': date(2019, 7, 26),
                    'movie_type': '动画/动作/奇幻',
                    'poster_url': 'https://img9.doubanio.com/view/photo/l/public/p2563780504.jpg',
                    'director': '饺子',
                    'rating': 8.5
                },
                {
                    'title': '唐人街探案3',
                    'description': '唐仁为巨额奖金欺骗秦风到东京参加世界名侦探大赛',
                    'release_date': date(2021, 2, 12),
                    'movie_type': '喜剧/悬疑',
                    'poster_url': 'https://img9.doubanio.com/view/photo/l/public/p2622388982.jpg',
                    'director': '陈思诚',
                    'rating': 6.8
                },
                {
                    'title': '奇迹·笨小孩',
                    'description': '讲述了一个建筑工地上发生的奇迹故事',
                    'release_date': date(2022, 2, 1),
                    'movie_type': '剧情',
                    'poster_url': 'https://img2.doubanio.com/view/photo/l/public/p2745167308.jpg',
                    'director': '文牧野',
                    'rating': 7.8
                }
            ]
            
            for movie_data in default_movies:
                movie = Movie(**movie_data)
                db.session.add(movie)
            
            db.session.commit()
            print("已添加默认电影数据")

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