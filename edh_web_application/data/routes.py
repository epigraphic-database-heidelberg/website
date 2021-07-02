from flask import render_template, send_from_directory, send_file, request, jsonify

from . import bp_data
from flask_babel import _
from edh_web_application.models.Inscription import Inscription
from edh_web_application.models.Publication import Publication
from edh_web_application.models.Foto import Foto


@bp_data.route('/data', strict_slashes=False)
def data():
    return render_template('data/index.html', title=_("Data"), subtitle=_("Open Data Repository"))


@bp_data.route('/data/api/inschrift/suche', strict_slashes=False)
def api_inscription_search():
    if len(request.args) > 0:
        # create query string
        offset = 0
        limit = 20
        if request.args.get('offset'):
            offset = request.args.get('offset')
        if request.args.get('limit'):
            limit = request.args.get('limit') 
        query_string = Inscription.create_query_string(request.args)    
        results = Inscription.query(query_string, start=offset, number_of_results=limit, no_highlighting=True)
        number_of_hits = results['metadata']['number_of_hits']
        items_as_list_of_dict = Inscription.get_items_as_list_of_dicts(results)
        return_dict = {
            "limit" : limit,
            "offset": offset,
            "items" : items_as_list_of_dict,
            "total" : number_of_hits
        }
        return_dict_json = jsonify(return_dict)
    else:
        return_dict = {
            "limit" : "20",
            "items" : [],
            "total" : 0}
        return_dict_json = jsonify(return_dict)
    return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
    return return_dict_json


@bp_data.route('/data/api/bibliographie/suche', strict_slashes=False)
def api_bibliography_search():
    if len(request.args) > 0:
        # create query string
        offset = 0
        limit = 20
        if request.args.get('offset'):
            offset = request.args.get('offset')
        if request.args.get('limit'):
            limit = request.args.get('limit') 
        query_string = Publication.create_query_string(request.args)
        results = Publication.query(query_string, start=offset, number_of_results=limit)
        number_of_hits = results['metadata']['number_of_hits']
        items_as_list_of_dict = Publication.get_items_as_list_of_dicts(results)
        return_dict = {
            "limit" : limit,
            "offset": offset,
            "items" : items_as_list_of_dict,
            "total" : number_of_hits
        }
        return_dict_json = jsonify(return_dict)
    else:
        return_dict = {
            "limit" : "20",
            "items" : [],
            "total" : 0}
        return_dict_json = jsonify(return_dict)
    return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
    return return_dict_json


@bp_data.route('/data/api/foto/suche', strict_slashes=False)
def api_foto_search():
    if len(request.args) > 0:
        # create query string
        offset = 0
        limit = 20
        if request.args.get('offset'):
            offset = request.args.get('offset')
        if request.args.get('limit'):
            limit = request.args.get('limit') 
        query_string = Foto.create_query_string(request.args)
        results = Foto.query(query_string, start=offset, number_of_results=limit)
        number_of_hits = results['metadata']['number_of_hits']
        items_as_list_of_dict = Foto.get_items_as_list_of_dicts(results)
        return_dict = {
            "limit" : limit,
            "offset": offset,
            "items" : items_as_list_of_dict,
            "total" : number_of_hits
        }
        return_dict_json = jsonify(return_dict)
    else:
        return_dict = {
            "limit" : "20",
            "items" : [],
            "total" : 0}
        return_dict_json = jsonify(return_dict)
    return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
    return return_dict_json


@bp_data.route('/data/api', strict_slashes=False)
def api():
    return render_template('data/api.html', title=_("Data"), subtitle=_("Application Programming Interface (API)"))


@bp_data.route('/data/download/<filename>', strict_slashes=False)
def download_file(filename):
    return send_from_directory('data/files/',filename,
                            as_attachment=True)


@bp_data.route('/data/download', strict_slashes=False)
def download():
    return render_template('data/download.html', title=_("Data"), subtitle=_("Download Data Dumps"))
