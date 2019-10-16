from flask import Flask, render_template, request, session
from config import Config
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from edh_web_application.models import Publication
import os


def create_app(test_config=None):
    #
    # create and configure the app
    #
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.environ['APP_SETTINGS'])
    bootstrap = Bootstrap(app)
    babel = Babel(app)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    #
    # Blueprints
    #
    register_blueprints(app)

    #
    # Routes: EDH start page
    #
    @app.route('/home')
    def home():
        return render_template('home.html', title="Home")
    app.add_url_rule('/', endpoint='home')

    #
    # 404 page
    #
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    #
    # i18n
    #
    @babel.localeselector
    def get_locale():
        if request.args.get('lang'):
            session['lang'] = request.args.get('lang')
        return session.get('lang', 'en')

    return app


def register_blueprints(app):
    from edh_web_application.bibliography import bp_bibliography
    from edh_web_application.foto import bp_foto
    from edh_web_application.inscription import bp_inscription
    from edh_web_application.data import bp_data
    from edh_web_application.project import bp_project

    app.register_blueprint(bp_bibliography)
    app.register_blueprint(bp_foto)
    app.register_blueprint(bp_inscription)
    app.register_blueprint(bp_data)
    app.register_blueprint(bp_project)
