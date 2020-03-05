import os

from flask import Flask, jsonify




def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'forum.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

        # NEW -- defence against session hijacking ----
        app.config.update(
            PERMANENT_SESSION_LIFETIME=300
        )
        app.config.update(
         #   SESSION_COOKIE_SECURE=True, # limits to https traffic only
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
        )

    # test page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'



    from . import db
    db.init_app(app)


    from . import auth
    app.register_blueprint(auth.bp)

    from . import inside
    app.register_blueprint(inside.bp)
    app.add_url_rule('/', endpoint='index')


    return app

# ref https://flask.palletsprojects.com/en/1.1.x/