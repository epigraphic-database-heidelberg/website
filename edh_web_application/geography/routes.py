from flask import render_template, request
from flask_babel import _
import json
import re
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
    query = ""
    if re.match("^[0-9]*$", geo_id) and int(geo_id) >= 900000 and int(geo_id) <= 900061:
        # province detail view
        prov_data = {}
        prov_data['province_name'] = _(Place.province_id_dict[geo_id])
        prov_data['province_id'] = geo_id
        prov_data['province_pleiades_id'] = Place.province_pleiades_dict[Place.province_id_dict[geo_id]]
        prov_data['province_wikidata_id'] = Place.province_wikidata_dict[Place.province_id_dict[geo_id]]
        prov_data['province_tm_id'] = Place.province_tm_dict[Place.province_id_dict[geo_id]]
        prov_status = Place.province_status_dict[Place.province_id_dict[geo_id]]
        prov_data['province_status'] = _(prov_status)
        prov_data['findspots'] = Place.get_findspots_for_province(Place.province_id_dict[geo_id])
        prov_data['polygon'] = Place.get_polygon_for_province(Place.province_id_dict[geo_id])
        prov_data['polygon_center'] = Place.get_center_of_polygon(prov_data['polygon'])
        return render_template('geography/detail_view_province.html',
                               title=_("Geographic Database"), subtitle=prov_data['province_name'],
                               data=prov_data)
    else:
        # find spot detail view
        results = Place.query("id:" + geo_id)
        if results is None:
            return render_template('geography/no_hits.html',
                                   title=_("Geographic Database"), subtitle=_("Detail View"))
        else:
            return render_template('geography/detail_view.html',
                                   title=_("Geographic Database"), subtitle=_("Detail View"),
                                   data=results['items'][0])


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
        if request.args.get('view') == 'table' or request.args.get('view') == 'map':
            results = Place.query(query_string, hits=10000)
        else:
            results = Place.query(query_string)
        number_of_hits = Place.get_number_of_hits_for_query(query_string)
        # return results to client
        if results:
            if request.args.get('view') == 'table':
                return render_template('geography/search_results_table.html', title=_("Geographic Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=number_of_hits)
            elif request.args.get('view') == 'map':
                return render_template('geography/search_results.html', title=_("Geographic Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=number_of_hits)
            else:
                return render_template('geography/search_results.html', title=_("Geographic Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=number_of_hits)
        else:
            return render_template('geography/no_hits.html', title=_("Geographic Database"),
                                   subtitle=_("Search results"), form=form)
    else:
        return render_template('geography/search.html', title=_("Geographic Database"), subtitle=_("Search"), form=form)


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


@bp_geography.route('/geographie/ac/region', methods=['GET', 'POST'])
def autocomplete_region():
    """
    route for retrieving autocomplete entries for field verw_bezirk/region
    :return: list of entries for autocomplete
    """
    return json.dumps(Place.get_autocomplete_entries("verw_bezirk", request.args['term']))
