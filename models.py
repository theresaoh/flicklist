from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    movies = db.relationship('Movie', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.email

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    watched = db.Column(db.Boolean)
    rating = db.Column(db.String(20))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.watched = False
        self.owner = owner

    def __repr__(self):
        return '<Movie %r>' % self.name

def add_user(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user

def rate_watched_movie(movie, rating): 
    movie.rating = rating
    db.session.add(movie)
    db.session.commit()

def cross_off_movie(crossed_off_movie):
    crossed_off_movie.watched = True
    db.session.add(crossed_off_movie)
    db.session.commit()

def add_new_movie(new_movie_name, user):
    movie = Movie(new_movie_name, user)
    db.session.add(movie)
    db.session.commit()