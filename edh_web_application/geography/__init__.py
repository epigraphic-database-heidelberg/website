"""
The geography blueprint allows for searching and displaying
EDH geographic data.
"""
from flask import Blueprint

bp_geography = Blueprint('geography', __name__, template_folder='templates')

from . import routes
