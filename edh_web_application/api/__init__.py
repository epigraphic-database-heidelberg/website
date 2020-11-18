"""
The api blueprint allows for querying the EDH APi.
"""
from flask import Blueprint

bp_api = Blueprint('api', __name__)

from . import routes
