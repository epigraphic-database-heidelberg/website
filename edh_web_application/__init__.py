from flask import Flask, render_template, request, session
from config import Config
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from .models.Publication import Publication
from .models.Foto import Foto
from .models.Place import Place
from .models.Inscription import Inscription
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
        number_of_biblio_records = Publication.get_number_of_records()
        number_of_foto_records = Foto.get_number_of_records()
        number_of_geo_records = Place.get_number_of_records()
        number_of_text_records = Inscription.get_number_of_records()
        date_of_last_biblio_update = Publication.get_date_of_last_update()
        date_of_last_foto_update = Foto.get_date_of_last_update()
        date_of_last_geo_update = Place.get_date_of_last_update()
        date_of_last_text_update = Inscription.get_date_of_last_update()

        return render_template('home.html', title="Home",
                               number_of_biblio_records=number_of_biblio_records,
                               date_of_last_biblio_update=date_of_last_biblio_update,
                               number_of_foto_records=number_of_foto_records,
                               date_of_last_foto_update=date_of_last_foto_update,
                               number_of_geo_records=number_of_geo_records,
                               date_of_last_geo_update=date_of_last_geo_update,
                               number_of_text_records=number_of_text_records,
                               date_of_last_text_update=date_of_last_text_update
                               )
    app.add_url_rule('/', endpoint='home')

    #
    # 404 page
    #
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    #
    # 500 page
    #
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500


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
    from edh_web_application.geography import bp_geography
    from edh_web_application.foto import bp_foto
    from edh_web_application.inscription import bp_inscription
    from edh_web_application.person import bp_people
    from edh_web_application.data import bp_data
    from edh_web_application.project import bp_project
    from edh_web_application.api import bp_api

    app.register_blueprint(bp_bibliography)
    app.register_blueprint(bp_geography)
    app.register_blueprint(bp_foto)
    app.register_blueprint(bp_inscription)
    app.register_blueprint(bp_people)
    app.register_blueprint(bp_data)
    app.register_blueprint(bp_project)
    app.register_blueprint(bp_api)
