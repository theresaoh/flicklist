from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import cgi
from models import User, Movie, add_user, rate_watched_movie, cross_off_movie, add_new_movie
from app import app, db

# a list of movie names that nobody should have to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives",
    "Starship Troopers"
]

def get_current_watchlist():
    return Movie.query.filter_by(watched=False).all()

def get_watched_movies():
    owner = User.query.filter_by(email=session['user']).first()
    return Movie.query.filter_by(watched=True).filter_by(owner_id=owner.id).all()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = add_user(email, password)
        session['user'] = user.email
        return redirect("/")
    else:
        return render_template('register.html')

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/")

# Create a new route called rate_movie which handles a POST request on /rating-confirmation
@app.route("/rating-confirmation", methods=['POST'])
def rate_movie():
    movie_id = request.form['movie_id']
    rating = request.form['rating']

    movie = Movie.query.get(movie_id)
    if movie not in get_watched_movies():
        # the user tried to rate a movie that isn't in their list,
        # so we redirect back to the front page and tell them what went wrong
        error = "'{0}' is not in your Watched Movies list, so you can't rate it!".format(movie)

        # redirect to homepage, and include error as a query parameter in the URL
        return redirect("/?error=" + error)

    # if we didn't redirect by now, then all is well
    rate_watched_movie(movie, rating)
    return render_template('rating-confirmation.html', movie=movie, rating=rating)


# Creates a new route called movie_ratings which handles a GET on /ratings
@app.route("/ratings", methods=['GET'])
def movie_ratings():
    # owner = User.query.filter_by(email=session['user']).first()
    # movies = Movie.query.filter_by(owner_id = owner.id).all()
    return render_template('ratings.html', movies = get_watched_movies())

@app.route("/crossoff", methods=['POST'])
def crossoff_movie():
    crossed_off_movie_id = request.form['crossed-off-movie']

    crossed_off_movie = Movie.query.get(crossed_off_movie_id)
    if not crossed_off_movie:
        return redirect("/?error=Attempt to watch a movie unknown to this database")

    # if we didn't redirect by now, then all is well
    cross_off_movie(crossed_off_movie)
    return render_template('crossoff.html', crossed_off_movie=crossed_off_movie)

@app.route("/add", methods=['POST'])
def add_movie():
    # look inside the request to figure out what the user typed
    new_movie_name = request.form['new-movie']

    # if the user typed nothing at all, redirect and tell them the error
    if (not new_movie_name) or (new_movie_name.strip() == ""):
        error = "Please specify the movie you want to add."
        return redirect("/?error=" + error)

    # if the user wants to add a terrible movie, redirect and tell them the error
    if new_movie_name in terrible_movies:
        error = "Trust me, you don't want to add '{0}' to your Watchlist".format(new_movie_name)
        return redirect("/?error=" + error)

    #add new movie to database
    user = User.query.filter_by(email=session['user']).first()
    add_new_movie(new_movie_name, user)
    return render_template('add-confirmation.html', movie=new_movie_name)

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    return render_template('edit.html', watchlist=get_current_watchlist(), error=encoded_error)


endpoints_without_login = ['login', 'register']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/register")


# In a real application, this should be kept secret (i.e. not on github)
# As a consequence of this secret being public, I think connection snoopers or
# rival movie sites' javascript could hijack our session and act as us,
# perhaps giving movies bad ratings - the HORROR.
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()
