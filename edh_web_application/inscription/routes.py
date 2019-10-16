from flask import render_template

from . import bp_inscription
from ..models.Inscription import Inscription
from flask_babel import _


@bp_inscription.route('/inschrift/suche')
def simple_search():
    return render_template('inscription/simple_search.html', title=_("Epigraphic Text Database: Simple Search"))


@bp_inscription.route('/inschrift/erweiterteSuche')
def extended_search():
    return render_template('inscription/extended_search.html',
                           title=_("Epigraphic Text Database: Extended Search"))


@bp_inscription.route('/inschrift/browse')
def browse_inscriptions():
    return render_template('inscription/browse.html', title=_("Epigraphic Text Database: Browse Inscriptions"))


@bp_inscription.route('/edh/inschrift/<hd_nr>')
def detail_view(hd_nr):
    results = Inscription.query("hd_nr:" + hd_nr)
    if results is None:
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database: Detail View"))
    else:
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database: Detail View"),
                               data=results[0])
