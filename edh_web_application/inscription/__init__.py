"""
The foto blueprint allows for searching and displaying
EDH inscription data.
"""
from flask import Blueprint

bp_inscription = Blueprint('inscription', __name__, 
                            template_folder='templates',
                            static_folder='static_inscription')

from . import routes
