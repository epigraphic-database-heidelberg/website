"""
The project blueprint allows for browsing all
EDH web pages.
"""
from flask import Blueprint

bp_project = Blueprint('project', __name__, template_folder='templates')

from . import routes
