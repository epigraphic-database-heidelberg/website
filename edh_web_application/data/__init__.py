"""
The data blueprint allows for searching and displaying
EDH data via various APIs.
"""
from flask import Blueprint

bp_data = Blueprint('data', __name__, template_folder='templates')

from . import routes
