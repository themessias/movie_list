import psycopg2

import click, os
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host="localhost",
            database="flask_db",
            user=os.environ["POSTGRES_USERNAME"],
            password=os.environ["POSTGRES_PASSWORD"]
        )
        g.db.autocommit = True
        g.cursor = g.db.cursor()

    return g.db, g.cursor

def close_db(e=None):
    cursor = g.pop("cur", None)
    if cursor is not None:
        cursor.close()
    
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db, cursor = get_db()
    sql = open('.\\flaskr\schema.sql', 'r')
    cursor.execute(sql.read())
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)