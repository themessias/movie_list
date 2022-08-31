import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db, cursor = get_db()
        error = None
        
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                cursor.execute(
                    "INSERT INTO users (email, password) values (%s, %s)",
                    (email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f'Already registered.'
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db, cursor = get_db()
        error = None
        cursor.execute(
            'SELECT * FROM users WHERE email = %s', [email]
        )
        user = cursor.fetchone()
        
        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user[1], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_email'] = user[0]
            return redirect(url_for('movies.index'))

        flash(error, 'danger')
        
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_email = session.get('user_email')
    
    if user_email is None:
        g.user = None
    else:
        db, cursor = get_db()
        cursor.execute(
            'SELECT * FROM users WHERE email = %s', [user_email]
        )
        g.user = cursor.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view