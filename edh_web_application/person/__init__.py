"""
The bibliography blueprint allows for searching and displaying
EDH prosopographical data.
"""
from flask import Blueprint

bp_people = Blueprint('people', __name__, template_folder='templates')

from . import routes
