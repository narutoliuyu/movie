from flask import Blueprint, jsonify, request
from app.models.search_history import SearchHistory
from app.models.movie_ranking import MovieRanking
from app.models.movie import Movie
from app.extensions import db
from datetime import datetime, timedelta

bp = Blueprint('search', __name__)

@bp.route('/search/history', methods=['GET'])
def get_search_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '用户ID不能为空'}), 400
    
    # 获取最近7天的搜索记录
    recent_history = SearchHistory.query.filter(
        SearchHistory.user_id == user_id,
        SearchHistory.created_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(SearchHistory.created_at.desc()).limit(8).all()
    
    return jsonify({
        'status': 'success',
        'data': [history.to_dict() for history in recent_history]
    })

@bp.route('/search/history', methods=['POST'])
def add_search_history():
    data = request.get_json()
    user_id = data.get('user_id')
    search_query = data.get('search_query')
    
    if not user_id or not search_query:
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400
    
    # 检查是否存在相同的搜索记录
    existing_history = SearchHistory.query.filter_by(
        user_id=user_id,
        search_query=search_query
    ).first()
    
    if existing_history:
        # 如果存在，更新创建时间
        existing_history.created_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success', 'message': '搜索记录已更新'})
    
    # 如果不存在，创建新记录
    history = SearchHistory(
        user_id=user_id,
        search_query=search_query
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '搜索记录已添加'})

@bp.route('/search/history/<int:history_id>', methods=['DELETE'])
def delete_search_history(history_id):
    history = SearchHistory.query.get_or_404(history_id)
    db.session.delete(history)
    db.session.commit()
    return jsonify({'status': 'success', 'message': '搜索记录已删除'})

@bp.route('/search/history/clear', methods=['DELETE'])
def clear_search_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '用户ID不能为空'}), 400
    
    # 删除指定用户的所有搜索历史
    SearchHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '搜索历史已清空'})

@bp.route('/search/rankings', methods=['GET'])
def get_movie_rankings():
    rankings = MovieRanking.query.order_by(MovieRanking.rank.asc()).limit(8).all()
    
    # 添加调试信息
    print("电影排名列表:")
    for rank in rankings:
        movie_info = rank.movie.to_dict() if rank.movie else None
        print(f"ID: {rank.id}, 电影ID: {rank.movie_id}, 排名: {rank.rank}, 电影名: {movie_info['title'] if movie_info else 'None'}")
    
    return jsonify({
        'status': 'success',
        'data': [ranking.to_dict() for ranking in rankings]
    }) 