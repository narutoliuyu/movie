from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.history import WatchHistory
from ..models.movie import Movie
from ..extensions import db
from datetime import datetime

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    # 获取用户ID
    user_id = get_jwt_identity()
    
    # 获取用户观看历史
    history = WatchHistory.query.filter_by(user_id=user_id).order_by(WatchHistory.watch_time.desc()).all()
    
    history_data = []
    for item in history:
        movie = Movie.query.get(item.movie_id)
        if not movie:
            continue
            
        history_data.append({
            'id': item.id,
            'movie_id': item.movie_id,
            'title': movie.title,
            'poster_url': movie.poster_url,
            'watch_time': item.watch_time.isoformat(),
            'progress': item.progress
        })
    
    return jsonify({
        'status': 'success',
        'data': history_data
    })

@history_bp.route('/api/history', methods=['POST'])
@jwt_required()
def add_history():
    data = request.json
    user_id = get_jwt_identity()
    
    if not data or 'movie_id' not in data:
        return jsonify({
            'status': 'error',
            'message': '未提供电影ID'
        }), 400
        
    movie_id = data['movie_id']
    progress = data.get('progress', 0)
    
    # 检查电影是否存在
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({
            'status': 'error',
            'message': '电影不存在'
        }), 404
    
    # 查找是否已有观看记录
    history = WatchHistory.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    
    if history:
        # 更新现有记录
        history.watch_time = datetime.utcnow()
        history.progress = progress
    else:
        # 创建新记录
        history = WatchHistory(user_id=user_id, movie_id=movie_id, progress=progress)
        db.session.add(history)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '观看记录已保存',
        'data': {
            'id': history.id,
            'movie_id': movie_id,
            'watch_time': history.watch_time.isoformat(),
            'progress': history.progress
        }
    })

@history_bp.route('/api/history/clear', methods=['DELETE'])
@jwt_required()
def clear_history():
    user_id = get_jwt_identity()
    
    # 删除用户所有观看历史
    WatchHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '观看历史已清空'
    })

@history_bp.route('/api/history/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    user_id = get_jwt_identity()
    
    # 查找指定记录
    history = WatchHistory.query.filter_by(id=history_id, user_id=user_id).first()
    
    if not history:
        return jsonify({
            'status': 'error',
            'message': '记录不存在或无权限删除'
        }), 404
    
    # 删除记录
    db.session.delete(history)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '记录已删除'
    }) 