from flask import render_template, request
from flask_babel import _
import json
from ..models.Place import Place
from . import bp_geography
from .forms import GeographySearch


@bp_geography.route('/geographie/lastUpdates', methods=['GET', 'POST'])
def last_updates():
    """
    route for displaying last updates in geographic database
    :return: orderedDictionary of geographic entries grouped by date
    """
    results = Place.last_updates()
    results_grouped_by_date = Place.group_results_by_date(results)
    return render_template('geography/last_updates.html',
                           title=_("Epigraphic Geographic Database: Last Updates"),
                           data=results_grouped_by_date)


@bp_geography.route('/edh/geographie/<geo_id>')
def detail_view(geo_id):
    """
    route for displaying detail view of geographical record
    :param geo_id: identifier of geographical record
    :return: html template
    """
    results = Place.query("id:" + geo_id)
    if results is None:
        return render_template('geography/no_hits.html',
                               title=_("Epigraphic Geography Database: Detail View"))
    else:
        return render_template('geography/detail_view.html',
                               title=_("Epigraphic Geography Database: Detail View"),
                               data=results[0])


@bp_geography.route('/geographie/suche', methods=['GET', 'POST'])
def search_geography():
    """
    route for geographical search mask
    :return: html template of geographical search mask
    """
    form = GeographySearch()
    if len(request.args) > 0:
        # create query string
        query_string = Place.create_query_string(request.args)
        # run query
        results = Place.query(query_string)
        number_of_hits = Place.get_number_of_hits_for_query(query_string)
        # return results to client
        if results:
            return render_template('geography/search_results.html', title=_("Geographic Database: Search"), form=form, data=results, number_of_hits=number_of_hits)
        else:
            return render_template('geography/no_hits.html', title=_("Geographic Database: Search"), form=form)
    else:
        return render_template('geography/search.html', title=_("Geographic Database: Search"), form=form)


@bp_geography.route('/geographie/ac/fo_modern', methods=['GET', 'POST'])
def autocomplete_fo_modern():
    """
    route for retrieving autocomplete entries for field fo_modern
    :return: list of entries for autocomplete
    """
    return json.dumps(Place.get_autocomplete_entries("fo_modern", request.args['term']))


@bp_geography.route('/geographie/ac/fo_antik', methods=['GET', 'POST'])
def autocomplete_fo_antik():
    """
    route for retrieving autocomplete entries for field fo_antik
    :return: list of entries for autocomplete
    """
    return json.dumps(Place.get_autocomplete_entries("fo_antik", request.args['term']))


@bp_geography.route('/geographie/ac/fundstelle', methods=['GET', 'POST'])
def autocomplete_fundstelle():
    """
    route for retrieving autocomplete entries for field fundstelle
    :return: list of entries for autocomplete
    """
    return json.dumps(Place.get_autocomplete_entries("fundstelle", request.args['term']))
