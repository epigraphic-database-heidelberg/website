import json

from flask import render_template, request
from flask_babel import _

from . import bp_foto
from .forms import FotoSearch
from ..models.Foto import Foto
from ..models.Place import Place


@bp_foto.route('/foto/suche')
def search_bibliography():
    form = FotoSearch()
    return render_template('foto/search.html', title=_("Foto Database"), subtitle=_("Search"), form=form)


@bp_foto.route('/edh/foto/<f_nr>')
def detail_view(f_nr):
    results = Foto.query("f_nr:" + f_nr)
    if results is None:
        return render_template('foto/no_hits.html',
                               title=_("Foto Database"), subtitle=_("Detail View"))
    else:
        return render_template('foto/detail_view.html',
                               title=_("Foto Database"), subtitle=_("Detail View"),
                               data=results[0])


@bp_foto.route('/foto/ac/fo_modern', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/fo_modern/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_modern(short=None):
    """
    route for retrieving autocomplete entries for field fo_modern
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("fo_modern", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("fo_modern", request.args['term'], 20))


@bp_foto.route('/foto/ac/fo_antik', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/fo_antik/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_antik(short=None):
    """
    route for retrieving autocomplete entries for field fo_antik
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("fo_antik", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("fo_antik", request.args['term'], 20))


@bp_foto.route('/foto/ac/aufbewahrung', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/aufbewahrung/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_aufbewahrung(short=None):
    """
    route for retrieving autocomplete entries for field present location
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("aufbewahrung", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("aufbewahrung", request.args['term'], 20))
