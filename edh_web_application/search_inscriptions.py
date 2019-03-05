from flask import (
    Blueprint, render_template
)

bp = Blueprint('search_inscriptions', __name__)

@bp.route('/inschrift/suche')
def simple_search():
    return render_template('search_inscriptions/simple_search.html', title="Epigraphic Text Database: Simple Search")

@bp.route('/inschrift/erweiterteSuche')
def extended_search():
    return render_template('search_inscriptions/extended_search.html', title="Epigraphic Text Database: Extended Search")

@bp.route('/inschrift/browse')
def browse_inscriptions():
    return render_template('search_inscriptions/browse.html', title="Epigraphic Text Database: Browse Inscriptions")

