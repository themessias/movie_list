from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.blueprints.auth import login_required
from flaskr.db import get_db

bp = Blueprint('movies', __name__)

@bp.route('/')
@login_required
def index():
    db, cursor = get_db()
    movies = cursor.execute(
        'SELECT * FROM movies WHERE user_email = %s ', [g.user[0]]
    )
    movies = cursor.fetchall()
    return render_template('movies/index.html', movies=movies)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        link = request.form['link']
        error = None
        
        if not title:
            error = 'Title is required.'
        
        if not link:
            link = None
        
        if error is not None:
            flash(error)
        else:
            db, cursor = get_db()
            cursor.execute(
                'INSERT INTO movies (title, user_email, year, link) VALUES (%s, %s, %s, %s);',
                [title, g.user[0], year, link]
            )
            return redirect(url_for('movies.index'))
    return render_template('movies/create.html')

def get_movie(id: int, check_author=True):
    db, cursor = get_db()
    cursor.execute(
        'SELECT id, title, user_email, year, link FROM movies WHERE id = %s',
        [id]
    )
    movie = cursor.fetchone()
    
    if movie is None:
        abort(404, f"Movie id {id} doesn't exist.")
    if check_author and movie[2] != g.user[0]:
        abort(403)
    
    return movie

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
    movie = get_movie(id)
    
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        link = request.form['link']
        error = None
        
        if not year:
            year = movie[3]
        
        if not link:
            link = movie[4]
        
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db, cursor = get_db()
            cursor.execute(
                """UPDATE movies SET title = %s, year = %s, link = %s
                WHERE id = %s;""",
                [title, year, link, id]
            )
            return redirect(url_for('movies.index'))
    return render_template('movies/update.html', movie=movie)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    get_movie(id)
    db, cursor = get_db()
    cursor.execute(
        'DELETE FROM movies WHERE id = %s', [id]
    )
    return redirect(url_for('movies.index'))
    