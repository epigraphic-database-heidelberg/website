"""
The foto blueprint allows for searching and displaying
EDH foto data.
"""
from flask import Blueprint

bp_foto = Blueprint('foto', __name__, template_folder='templates')

from . import routes
