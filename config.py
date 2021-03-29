import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    LANGUAGES = ['en', 'de']
    BABEL_DEFAULT_LOCALE = 'en'
    SOLR_BASE_URL = 'http://localhost:8983/solr/'
    BASE_HREF = "/"
    HOST = 'https://edh-ww.adw.uni-heidelberg.de'
    JSON_AS_ASCII = False


class DevelopmentConfig(Config):
    SOLR_BASE_URL = 'http://147.142.112.176:8983/solr/'
    BASE_HREF = "/test/"

