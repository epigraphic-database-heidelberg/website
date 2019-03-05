import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    bootstrap = Bootstrap(app)

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

    # EDH start page
    @app.route('/home')
    def home():
        return render_template('home.html', title="Home")

    from edh_web_application import project
    app.register_blueprint(project.bp)

    from edh_web_application import search_inscriptions
    app.register_blueprint(search_inscriptions.bp)

    from edh_web_application import search_fotos
    app.register_blueprint(search_fotos.bp)

    from edh_web_application import search_bibliography
    app.register_blueprint(search_bibliography.bp)

    from edh_web_application import data
    app.register_blueprint(data.bp)

    from edh_web_application import links
    app.register_blueprint(links.bp)

    app.add_url_rule('/', endpoint='home')

    return app
