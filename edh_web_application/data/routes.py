from flask import render_template, send_from_directory, send_file, request, jsonify

from . import bp_data
from flask_babel import _
from edh_web_application.models.Inscription import Inscription


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
        items_list = []
        for i in results['items']:
            item = {}
            item['id'] = i.hd_nr
            item['commentary'] = i.kommentar
            item['diplomatic_text'] = i.btext
            item['country'] = i.land
            item['year_of_find'] = i.fundjahr
            item['present_location'] = i.aufbewahrung
            item['work_status'] = _("beleg-"+i.beleg)
            item['width'] = i.breite + " cm" if i.breite is not None else None
            item['depth'] = i.tiefe + " cm" if i.tiefe is not None else None
            item['height'] = i.hoehe + " cm" if i.hoehe is not None else None
            if i.literatur and '#' in i.literatur:
                item['literature'] =  i.literatur.replace("#", ";")
            else:
                item['literature'] =  i.literatur
            item['religion'] = i.religion_str
            item['last_update'] = i.datum
            item['findspot_modern'] = i.fo_modern
            item['findspot_ancient'] = i.fo_antik
            item['findspot'] = i.fundstelle
            item['social_economic_legal_history'] = i.sowire
            item['material'] = i.material
            item['not_after'] = str(i.dat_jahr_a)
            item['not_before'] = str(i.dat_jahr_e)
            item['modern_region'] = i.verw_bezirk
            item['language'] = i.nl_text
            item['type_of_monument'] = i.i_traeger_str
            item['type_of_inscription'] = i.i_gattung_str
            item['transcription'] = i.atext
            item['letter_size'] = i.bh + " cm" if i.bh is not None else None
            item['responsible_individual'] = i.bearbeiter
            item['trismegistos_uri'] = "https://www.trismegistos.org/text/"+str(i.tm_nr) if i.tm_nr is not None else None
            items_list.append(item)
        return_dict = {
            "limit" : limit,
            "offset": offset,
            "items" : items_list,
            "total" : number_of_hits
        }
        return_dict_json = jsonify(return_dict)
        return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
        return return_dict_json
    else:
        return_dict = {
            "limit" : "20",
            "items" : [],
            "total" : 0}
        return_dict_json = jsonify(return_dict)
    return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
    return return_dict_json
    #return render_template('data/api.html', title=_("Data"), subtitle=_("Application Programming Interface (API)"))


@bp_data.route('/data/api', strict_slashes=False)
def api():
    return render_template('data/api.html', title=_("Data"), subtitle=_("Application Programming Interface (API)"))


@bp_data.route('/data/download/<filename>', strict_slashes=False)
def download_file(filename):
    print(filename)
    return send_from_directory('data/files/',filename,
                            as_attachment=True)


@bp_data.route('/data/download', strict_slashes=False)
def download():
    return render_template('data/download.html', title=_("Data"), subtitle=_("Download Data Dumps"))
