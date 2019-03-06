from flask import (
    Blueprint, render_template
)
from flask_babel import _

bp = Blueprint('search_inscriptions', __name__)


@bp.route('/inschrift/suche')
def simple_search():
    return render_template('search_inscriptions/simple_search.html', title=_("Epigraphic Text Database: Simple Search"))


@bp.route('/inschrift/erweiterteSuche')
def extended_search():
    return render_template('search_inscriptions/extended_search.html',
                           title=_("Epigraphic Text Database: Extended Search"))


@bp.route('/inschrift/browse')
def browse_inscriptions():
    return render_template('search_inscriptions/browse.html', title=_("Epigraphic Text Database: Browse Inscriptions"))
