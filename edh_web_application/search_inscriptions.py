from flask import (
    Blueprint, render_template
)
from flask_babel import _
from edh_web_application.models.Inscription import Inscription


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


@bp.route('/edh/inschrift/<hd_nr>')
def detail_view(hd_nr):
    results = Inscription.query("hd_nr:" + hd_nr)
    if results is None:
        return render_template('search_inscriptions/detail_view.html', title=_("Epigraphic Text Database: Detail View"))
    else:
        return render_template('search_inscriptions/detail_view.html', title=_("Epigraphic Text Database: Detail View"),
                               data=results[0])
