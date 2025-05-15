from flask import Blueprint, jsonify, request
from app.models.movie import Movie
from app.extensions import db
from sqlalchemy import text

movies_bp = Blueprint('movies', __name__)

@movies_bp.route('/movies', methods=['GET'])
def get_movies():
    try:
        # 获取查询参数
        category_id = request.args.get('category_id', type=int)
        print(f"接收到的category_id参数: {category_id}")
        
        # 获取分类名称
        category_name = None
        if category_id is not None:
            # 从分类表中获取分类名称
            category = db.session.execute(
                text('SELECT name FROM category WHERE id = :id'),
                {'id': category_id}
            ).fetchone()
            if category:
                category_name = category[0]
                print(f"找到分类名称: {category_name}")
        
        # 构建查询
        query = Movie.query
        
        # 如果提供了分类名称，则按分类筛选
        if category_name:
            print(f"按分类 {category_name} 查询电影")
            query = query.filter(Movie.movie_type == category_name)
        else:
            print("查询所有电影")
            
        # 执行查询
        movies = query.all()
        print(f"查询到 {len(movies)} 部电影")
        
        # 将结果转换为列表
        movies_list = []
        for movie in movies:
            movie_dict = {
                'id': movie.id,
                'title': movie.title,
                'description': movie.description,
                'release_date': movie.release_date.strftime('%Y-%m-%d') if movie.release_date else None,
                'movie_type': movie.movie_type,
                'poster_url': movie.poster_url,
                'director': movie.director,
                'rating': movie.rating
            }
            movies_list.append(movie_dict)
            print(f"处理电影: {movie_dict}")
        
        print("最终电影列表:", movies_list)
        
        return jsonify({
            'status': 'success',
            'data': movies_list
        })
    except Exception as e:
        print(f"获取电影错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取电影失败: {str(e)}'
        }), 500 

@movies_bp.route('/search', methods=['GET'])
def search_movies():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({
                'status': 'success',
                'data': {
                    'movies': [],
                    'total': 0
                }
            })
        
        # 使用 LIKE 进行模糊搜索
        movies = Movie.query.filter(
            db.or_(
                Movie.title.like(f'%{query}%'),
                Movie.description.like(f'%{query}%'),
                Movie.director.like(f'%{query}%'),
                Movie.movie_type.like(f'%{query}%')
            )
        ).all()
        
        # 将结果转换为字典列表
        movies_list = []
        for movie in movies:
            movie_dict = {
                'id': movie.id,
                'title': movie.title,
                'description': movie.description,
                'release_date': movie.release_date.strftime('%Y-%m-%d') if movie.release_date else None,
                'movie_type': movie.movie_type,
                'poster_url': movie.poster_url,
                'director': movie.director,
                'rating': movie.rating
            }
            movies_list.append(movie_dict)
        
        return jsonify({
            'status': 'success',
            'data': {
                'movies': movies_list,
                'total': len(movies_list)
            }
        })
    except Exception as e:
        print(f"搜索电影错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'搜索失败: {str(e)}'
        }), 500 

@movies_bp.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    try:
        # 查询电影详情
        movie = Movie.query.get(movie_id)
        
        if not movie:
            return jsonify({
                'status': 'error',
                'message': '电影不存在'
            }), 404
        
        # 将电影信息转换为字典
        movie_dict = {
            'id': movie.id,
            'title': movie.title,
            'description': movie.description,
            'release_date': movie.release_date.strftime('%Y-%m-%d') if movie.release_date else None,
            'movie_type': movie.movie_type,
            'poster_url': movie.poster_url,
            'director': movie.director,
            'rating': movie.rating,
            'created_at': movie.created_at.strftime('%Y-%m-%d %H:%M:%S') if movie.created_at else None,
            'updated_at': movie.updated_at.strftime('%Y-%m-%d %H:%M:%S') if movie.updated_at else None
        }
        
        return jsonify({
            'status': 'success',
            'data': movie_dict
        })
    except Exception as e:
        print(f"获取电影详情错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取电影详情失败: {str(e)}'
        }), 500 