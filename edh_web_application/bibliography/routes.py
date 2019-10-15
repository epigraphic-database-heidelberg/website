from flask import render_template

from . import bp_bibliography
from ..models.Publication import Publication
from flask_babel import _


@bp_bibliography.route('/bibliographie/suche')
def search_bibliography():
    return render_template('bibliography/index.html', title=_("Bibliographic Database: Search"))


@bp_bibliography.route('/edh/bibliographie/<b_nr>')
def detail_view(b_nr):
    results = Publication.query("b_nr:" + b_nr)
    if results is None:
        return render_template('bibliography/no_hits.html',
                               title=_("Epigraphic Bibliography Database: Detail View"))
    else:
        return render_template('bibliography/detail_view.html',
                               title=_("Epigraphic Bibliography Database: Detail View"),
                               data=results[0])
