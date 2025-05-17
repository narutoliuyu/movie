from ..extensions import db
from datetime import datetime

class WatchHistory(db.Model):
    __tablename__ = 'watch_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    watch_time = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Float, default=0)  # 观看进度，百分比(0-100)
    
    # 关系
    user = db.relationship('User', backref=db.backref('watch_history', lazy='dynamic'))
    movie = db.relationship('Movie', backref=db.backref('watch_history', lazy='dynamic'))
    
    def __init__(self, user_id, movie_id, progress=0):
        self.user_id = user_id
        self.movie_id = movie_id
        self.progress = progress
        
    def __repr__(self):
        return f'<WatchHistory {self.id} - User {self.user_id} - Movie {self.movie_id}>' 