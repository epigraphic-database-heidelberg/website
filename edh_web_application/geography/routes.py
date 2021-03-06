import json
import re
import io
import csv
from flask import render_template, request, jsonify, Response
from flask_babel import _

from . import bp_geography
from .forms import GeographySearchDe, GeographySearchEn
from ..models.Place import Place


@bp_geography.route('/geographie/lastUpdates', methods=['GET', 'POST'], strict_slashes=False)
def last_updates():
    """
    route for displaying last updates in geographic database
    :return: orderedDictionary of geographic entries grouped by date
    """
    results = Place.last_updates()
    results_grouped_by_date = Place.group_results_by_date(results)
    return render_template('geography/last_updates.html',
                           title=_("Geographic Database"), subtitle=_("Last Updates"),
                           data=results_grouped_by_date)


@bp_geography.route('/edh/geographie/<geo_id>', strict_slashes=False)
@bp_geography.route('/edh/geographie/<geo_id>/<conv_format>', strict_slashes=False)
def detail_view(geo_id, conv_format = ''):
    """
    route for displaying detail view of geographical record
    :param geo_id: identifier of geographical record
    :param conv_format: conversion format (json)
    :return: html template or json
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
        # reformat Geo ID if necessary
        geo_id = re.sub(r'G0*?', r'', geo_id)
        geo_id = "G" + "{:06d}".format(int(geo_id))
        if conv_format == '':
            results = Place.query("id:" + geo_id)
            inscriptions_list = Place.get_inscriptions_from_place(geo_id)
            if results['metadata']['number_of_hits'] == 0:
                results['metadata']['query_params'] = {'Geo-ID': geo_id}
                return render_template('geography/no_hits.html',
                                       title=_("Geographic Database"), subtitle=_("Search results"), data=results)
            else:

                return render_template('geography/detail_view.html',
                                       title=_("Geographic Database"), subtitle=_("Detail View"),
                                       data=results['items'][0], inscriptions_list=inscriptions_list)
        else:
            # data export
            return_dict = Place.get_json_for_geo_record(geo_id)
            return_dict_json = jsonify(return_dict)
            return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
            return return_dict_json


@bp_geography.route('/geographie/suche', methods=['GET', 'POST'], strict_slashes=False)
def search_geography():
    """
    route for geographical search mask
    :return: html template of geographical search mask
    """
    if _('lang') == "de":
        form = GeographySearchDe(data=request.args)
    else:
        form = GeographySearchEn(data=request.args)
    form.fo_antik.data = request.args.get('fo_antik')
    form.fo_modern.data = request.args.get('fo_modern')
    form.fundstelle.data = request.args.get('fundstelle')
    form.region.data = request.args.get('region')
    form.kommentar.data = request.args.get('kommentar')
    form.bearbeiter.data = request.args.get('bearbeiter')
    form.provinz.data = request.args.getlist('provinz')
    form.land.data = request.args.getlist('land')
    if request.args.get('bearbeitet_abgeschlossen'):
        form.bearbeitet_abgeschlossen.data = True
    if request.args.get('bearbeitet_provisorisch'):
        form.bearbeitet_provisorisch.data = True

    if len(request.args) > 0:
        # create query string
        query_string = Place.create_query_string(request.args)
        if request.args.get('view') == 'table' or request.args.get('view') == 'map':
            results = Place.query(query_string, hits=10000)
        else:
            results = Place.query(query_string)
        # return results to client
        if results['metadata']['number_of_hits'] > 0:
            # CSV export of results
            if request.args.get('export') and request.args.get('export') == 'csv':
                results = Place.query(query_string, number_of_results=100000, start=0)
                output = io.StringIO()
                writer = csv.writer(output)
                first_row = ['geo-no', 'province / Italic region', 'country', 'ancient find spot', 
                            'modern find spot', 'findspot', 'region', 'comment', 'pleiades_id', 'tm_geo_id', 'geonames_id', 'coordinates (lat,lng)' ]
                writer.writerow(first_row)
                for i in results['items']:
                    writer.writerow((
                        i.id,
                        i.provinz,
                        i.land,
                        i.fo_antik,
                        i.fo_modern,
                        i.fundstelle,
                        i.verw_bezirk,
                        i.kommentar,
                        i.pleiades_id_1,
                        i.trismegistos_geo_id,
                        i.geonames_id_1,
                        i.koordinaten_1,
                    ))
                output.seek(0)    
                return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=edh_geography.csv"})
            else:

                if request.args.get('view') == 'table':
                    return render_template('geography/search_results_table.html', title=_("Geographic Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=results['metadata']['number_of_hits'], form=form)
                elif request.args.get('view') == 'map':
                    return render_template('geography/search_results_map.html', title=_("Geographic Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=results['metadata']['number_of_hits'], form=form)
                else:
                    return render_template('geography/search_results.html', title=_("Geographic Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=results['metadata']['number_of_hits'], form=form)





        else:
            return render_template('geography/no_hits.html', title=_("Geographic Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
    else:
        return render_template('geography/search.html', title=_("Geographic Database"), subtitle=_("Search"), form=form)


@bp_geography.route('/geographie/ac/fo_modern', methods=['GET', 'POST'], strict_slashes=False)
@bp_geography.route('/geographie/ac/fo_modern/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_modern(short=None):
    """
    route for retrieving autocomplete entries for field fo_modern
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Place.get_autocomplete_entries("fo_modern", request.args['term'], 10))
    else:
        return json.dumps(Place.get_autocomplete_entries("fo_modern", request.args['term'], 20))


@bp_geography.route('/geographie/ac/fo_antik', methods=['GET', 'POST'], strict_slashes=False)
@bp_geography.route('/geographie/ac/fo_antik/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_antik(short=None):
    """
    route for retrieving autocomplete entries for field fo_antik
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Place.get_autocomplete_entries("fo_antik", request.args['term'], 10))
    else:
        return json.dumps(Place.get_autocomplete_entries("fo_antik", request.args['term'], 20))


@bp_geography.route('/geographie/ac/fundstelle', methods=['GET', 'POST'], strict_slashes=False)
@bp_geography.route('/geographie/ac/fundstelle/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fundstelle(short=None):
    """
    route for retrieving autocomplete entries for field fundstelle
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Place.get_autocomplete_entries("fundstelle", request.args['term'], 10))
    else:
        return json.dumps(Place.get_autocomplete_entries("fundstelle", request.args['term'], 20))


@bp_geography.route('/geographie/ac/region', methods=['GET', 'POST'], strict_slashes=False)
@bp_geography.route('/geographie/ac/region/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_region(short=None):
    """
    route for retrieving autocomplete entries for field verw_bezirk/region
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Place.get_autocomplete_entries("verw_bezirk", request.args['term'], 10))
    else:
        return json.dumps(Place.get_autocomplete_entries("verw_bezirk", request.args['term'], 20))