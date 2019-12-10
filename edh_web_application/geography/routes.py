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