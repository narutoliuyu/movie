from datetime import datetime
from app.extensions import db

class MovieRanking(db.Model):
    __tablename__ = 'movie_rankings'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    views = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship('Movie', foreign_keys=[movie_id], backref=db.backref('ranking', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'rank': self.rank,
            'views': self.views,
            'movie': self.movie.to_dict() if self.movie else None
        } 