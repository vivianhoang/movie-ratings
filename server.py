"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie
from sqlalchemy.orm import exc


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

    return render_template("homepage.html")

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

    try:
        User.query.filter_by(email=user_email).one()
        print "User already exist in db."
    except NoResultFound:
        new_user = User(email=user_email, password=user_password, age=None, zipcode=None)
        db.session.add(new_user)
        db.session.commit()

    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
