from flask import render_template

from . import bp_foto
from ..models.Foto import Foto
from flask_babel import _


@bp_foto.route('/foto/suche')
def search_bibliography():
    return render_template('foto/index.html', title=_("Foto Database: Search"))


@bp_foto.route('/edh/foto/<f_nr>')
def detail_view(f_nr):
    results = Foto.query("f_nr:" + f_nr)
    if results is None:
        return render_template('foto/no_hits.html',
                               title=_("Epigraphic Foto Database: Detail View"))
    else:
        return render_template('foto/detail_view.html',
                               title=_("Epigraphic Foto Database: Detail View"),
                               data=results[0])
