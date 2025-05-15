from app.extensions import db
from datetime import datetime

class Movie(db.Model):
    __tablename__ = 'movie'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    movie_type = db.Column(db.String(50))
    poster_url = db.Column(db.String(200))
    director = db.Column(db.String(100))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.strftime('%Y-%m-%d') if self.release_date else None,
            'movie_type': self.movie_type,
            'poster_url': self.poster_url,
            'director': self.director,
            'rating': self.rating,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } 