from flask import render_template, request
from flask_babel import _
from ..models.Publication import Publication
from . import bp_bibliography
from .forms import BibliographySearch
import json
import re


@bp_bibliography.route('/bibliographie/suche', methods=['GET', 'POST'])
def search_bibliography():
    """
    route for bibliographical search mask
    :return: html template of bibliographical search mask
    """
    form = BibliographySearch()
    if len(request.args) > 0:
        # create query string
        query_string = Publication.create_query_string(request.args)
        # run query
        results = Publication.query(query_string)
        number_of_hits = Publication.get_number_of_hits_for_query(query_string)
        # return results to client
        if results:
            return render_template('bibliography/search_results.html', title=_("Bibliographic Database: Search"), form=form, data=results, number_of_hits=number_of_hits)
        else:
            return render_template('bibliography/no_hits.html', title=_("Bibliographic Database: Search"), form=form)
    else:
        return render_template('bibliography/search.html', title=_("Bibliographic Database: Search"), form=form)


@bp_bibliography.route('/edh/bibliographie/<b_nr>')
def detail_view(b_nr):
    """
    route for displaying detail view of bibliographical record
    :param b_nr: identifier of bibliographical record
    :return: html template
    """
    b_nr = format_b_nr(b_nr)
    results = Publication.query("b_nr:" + b_nr)
    if results is None:
        return render_template('bibliography/no_hits.html',
                               title=_("Epigraphic Bibliography Database: Detail View"))
    else:
        return render_template('bibliography/detail_view.html',
                               title=_("Epigraphic Bibliography Database: Detail View"),
                               data=results[0])


@bp_bibliography.route('/bibliographie/lastUpdates', methods=['GET', 'POST'])
def last_updates():
    """
    route for displaying last updates in bibliographic database
    :return: orderedDictionary of bibliographic entries grouped by date
    """
    results = Publication.last_updates()
    results_grouped_by_date = Publication.group_results_by_date(results)
    return render_template('bibliography/last_updates.html',
                           title=_("Epigraphic Bibliography Database: Last Updates"),
                           data=results_grouped_by_date)


@bp_bibliography.route('/bibliographie/ac/autor', methods=['GET', 'POST'])
def autocomplete_autor():
    """
    route for retrieving autocomplete entries for field autor
    :return: list of entries for autocomplete
    """
    return json.dumps(Publication.get_autocomplete_entries("autor", request.args['term']))


@bp_bibliography.route('/bibliographie/ac/publikation', methods=['GET', 'POST'])
def autocomplete_publikation():
    """
    route for retrieving autocomplete entries for field publikation
    :return: list of entries for autocomplete
    """
    return json.dumps(Publication.get_autocomplete_entries("publikation", request.args['term']))


def format_b_nr(b_nr):
    """
    formats user entered b_nr string into valid B-No like 'B004711'
    :param b_nr: user entered string of B-No
    :return: string of valid B-No, like 'B004711'
    """
    b_no_pattern = re.compile("^B\d\d\d\d\d\d$")
    if b_no_pattern.match(b_nr):
        return b_nr
    b_nr = re.sub("^[Bb]","",b_nr, re.IGNORECASE)
    b_nr = b_nr.lstrip("0")
    b_nr = b_nr.zfill(6)
    return "B"+b_nr
