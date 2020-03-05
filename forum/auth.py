import functools
import time

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for)

# two hashing methods used...
from werkzeug.security import check_password_hash, generate_password_hash

from forum.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# registering...
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        time.sleep(2)  # Sleep for 2 seconds
        if not username:
            error = 'Username is required!.'
        elif not password:
            error = 'Password is required!.'
        elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            time.sleep(3)  # Sleep for 3 seconds
            error = 'Sorry! Username does not meet necessary criteria. Please try an alternative.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))  # problem
            )
            db.commit()
            time.sleep(2)  # Sleep for 2 seconds
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

    # login ...

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            time.sleep(2)  # Sleep for 2 seconds
            error = 'Incorrect username or password.'
        elif not check_password_hash(user['password'], password):
            time.sleep(2)  # Sleep for 2 seconds
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True  # !! added to defend against session hijacking
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# logout
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# require auth for other views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# ref https://flask.palletsprojects.com/en/1.1.x/
