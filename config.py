import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    LANGUAGES = ['en', 'de']
    BABEL_DEFAULT_LOCALE = 'en'
    SOLR_BASE_URL = 'http://localhost:8983/solr/'
    BASE_HREF = "/"
    HOST = 'https://edh-www.adw.uni-heidelberg.de'
    JSON_AS_ASCII = False


class DevelopmentConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    LANGUAGES = ['en', 'de']
    BABEL_DEFAULT_LOCALE = 'en'
    SOLR_BASE_URL = 'http://localhost:8983/solr/'
    BASE_HREF = "/"
    HOST = 'https://edh-www.adw.uni-heidelberg.de'
    JSON_AS_ASCII = False
    FLASK_DEBUG=1

