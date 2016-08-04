"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
#from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie
import sqlalchemy

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    user = session.get('user', False)

    return render_template("homepage.html", user=user)

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=['GET'])
def register_form():
    """Let user register to rate movies. """

    return render_template('register_form.html')

@app.route('/register', methods=['POST'])
def register_process():
    """Processes the sign in form checking to see if user with username exists,
    and if not, creating new user in database. 
    """

    user_email = request.form.get('email')
    user_password = request.form.get('password')

    session['user'] = user_email

    try:
        User.query.filter_by(email=user_email).one()
        # print "User already exist in db."
        msg = "Welcome back, %s! You're logged in." % (user_email)
    except Exception:
        # print "Oops. Add user anyways"
        msg = "Hi, %s. Welcome to our movie rating app! Have a look around and rate your heart away." % (user_email)
        new_user = User(email=user_email, password=user_password, age=None, zipcode=None)
        db.session.add(new_user)
        db.session.commit()
        
    flash(msg)

    # get user id using email, then pass to redirect url
    user_obj = User.query.filter_by(email=user_email).first()
    user_id = user_obj.user_id
    url = '/user/%s' % (user_id)

    return redirect(url)

@app.route('/log_out')
def log_out():
    """Log user out """
    del session['user']

    flash("Logged out")

    return redirect("/")


@app.route('/user/<int:id>')
def user_profile(id):
    """Display user information and list of movies they have rated."""

    user_info = User.query.get(id)
    email = user_info.email
    age = user_info.age
    zipcode = user_info.zipcode

    user_rated_movies = []


    # get user's rated movies - returns a list of ratings obj
    user_ratings = user_info.ratings

    # for each rating obj, use movie id to get movie object 
    for one_rating_obj in user_ratings:
        # one_movie_obj = Movie.query.get(one_rating_obj.movie_id)
        user_rated_movies.append((one_rating_obj.movie.title, one_rating_obj.score))

        # take title from movie obj and score from rating obj, store in list of tuples
        # user_rated_movies.append((one_movie_obj.title, one_rating_obj.score))

    return render_template('user.html', 
                            email=email, 
                            age=age,
                            zipcode=zipcode,
                            user_rated_movies=user_rated_movies)

@app.route('/movies')
def display_movies():
    """Display movies in alphabetical order."""

    movies_list = db.session.query(Movie.movie_id, Movie.title).order_by(Movie.title).all()

    return render_template('movie_list.html', movies_list=movies_list)

@app.route('/movie/<int:id>')
def movie_details(id):
    """Display movie details."""

    movie_info = Movie.query.get(id)
    title = movie_info.title
    released_at = movie_info.released_at
    imdb_url = movie_info.imdb_url

    all_movie_ratings = []

    movie_ratings = movie_info.ratings

    for rating in movie_ratings:
        all_movie_ratings.append((rating.user.email, rating.score))

    print all_movie_ratings

    return render_template('movie.html',
                            title=title,
                            released_at=released_at,
                            imdb_url=imdb_url,
                            all_movie_ratings=all_movie_ratings)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    #DebugToolbarExtension(app)

    app.run()
