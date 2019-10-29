from flask import render_template, request
from flask_babel import _
from ..models.Publication import Publication
from . import bp_bibliography
from .forms import BibliographySearch


@bp_bibliography.route('/bibliographie/suche', methods=['GET', 'POST'])
def search_bibliography():
    form = BibliographySearch()
    if len(request.args) > 0:
        # create query string
        query_string = Publication.create_query_string(request.args)
        # run query
        results = Publication.query(query_string)
        # return results to client
        if results:
            return render_template('bibliography/search_results.html', title=_("Bibliographic Database: Search"), form=form, data=results)
        else:
            return render_template('bibliography/no_hits.html', title=_("Bibliographic Database: Search"), form=form)
    else:
        return render_template('bibliography/search.html', title=_("Bibliographic Database: Search"), form=form)


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
