from flask import render_template, request
from flask_babel import _
from ..models.Place import Place
from . import bp_geography


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



