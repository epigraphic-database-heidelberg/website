"""
The bibliography blueprint allows for searching and displaying
EDH bibliographical data.
"""
from flask import Blueprint

bp_bibliography = Blueprint('bibliography', __name__, template_folder='templates')

from . import routes
