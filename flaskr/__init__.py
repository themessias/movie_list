import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.getenv('SECRET_KEY'),
        DATABASE=os.path.join(app.instance_path, 'flask.psycopg2'),
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
  
    @app.errorhandler(404)
    def page_not_found(e):
        msg = 'Page not found'
        return msg, 404
    
    @app.route("/hello")
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)
    
    from .blueprints import auth
    app.register_blueprint(auth.bp)
    
    from .blueprints import movies
    app.register_blueprint(movies.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app