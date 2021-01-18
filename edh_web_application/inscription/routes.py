from flask import render_template, request
from flask_babel import _

from . import bp_inscription
from .forms import InscriptionSearchDe, InscriptionSearchEn
from ..models.Inscription import Inscription


@bp_inscription.route('/inschrift/suche')
def simple_search():
    if _('lang') == "de":
        form = InscriptionSearchDe(data=request.args)
    else:
        form = InscriptionSearchEn(data=request.args)
    return render_template('inscription/search.html', title=_("Epigraphic Text Database"), subtitle=_("Simple Search"), form=form)


@bp_inscription.route('/inschrift/erweiterteSuche')
def extended_search():
    return render_template('inscription/extended_search.html',
                           title=_("Epigraphic Text Database"), subtitle=_("Extended Search"))


@bp_inscription.route('/edh/inschrift/<hd_nr>')
def detail_view(hd_nr):
    results = Inscription.query("hd_nr:" + hd_nr)
    title_str = results[0].get_title()
    if results is None:
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database"), subtitle=_("Detail View"))
    else:
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database"), subtitle=title_str,
                               data=results[0])
