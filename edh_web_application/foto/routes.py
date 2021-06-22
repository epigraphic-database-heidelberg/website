import json
import re
import urllib.request

from flask import render_template, request, jsonify
from flask_babel import _

from . import bp_foto
from .forms import FotoSearchDe, FotoSearchEn
from ..models.Foto import Foto


@bp_foto.route('/foto/suche', strict_slashes=False)
def search_foto():
    if _('lang') == "de":
        form = FotoSearchDe(data=request.args)
    else:
        form = FotoSearchEn(data=request.args)
    form.fo_antik.data = request.args.get('fo_antik')
    form.fo_modern.data = request.args.get('fo_modern')
    form.kommentar.data = request.args.get('kommentar')
    form.provinz.data = request.args.getlist('provinz')
    form.land.data = request.args.getlist('land')
    form.aufbewahrung.data = request.args.get('aufbewahrung')
    form.cil.data = request.args.get('cil')
    form.ae.data = request.args.get('ae')
    form.andere.data = request.args.get('andere')
    if len(request.args) > 0:
        # create query string
        query_string = Foto.create_query_string(request.args)
        results = Foto.query(query_string)
        if results['metadata']['number_of_hits'] > 0:
            if request.args.get('view') == 'grid':
                return render_template('foto/search_results_grid.html',
                        title=_("Foto Database"),
                        subtitle=_("Search results"),
                        data=results,
                        number_of_hits=results['metadata']['number_of_hits'], form=form)
            else:
                return render_template('foto/search_results.html',
                        title=_("Foto Database"),
                        subtitle=_("Search results"),
                        data=results,
                        number_of_hits=results['metadata']['number_of_hits'], form=form)
        else:
            return render_template('foto/no_hits.html', title=_("Foto Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
    else:
        return render_template('foto/search.html', title=_("Foto Database"), subtitle=_("Search"), form=form)


@bp_foto.route('/edh/foto/<f_nr>', strict_slashes=False)
@bp_foto.route('/edh/foto/<f_nr>/<conv_format>', strict_slashes=False)
def detail_view(f_nr, conv_format = ''):
    results = Foto.query("f_nr:" + f_nr)
    if results['metadata']['number_of_hits'] == 0:
        results['metadata']['query_params'] = {'f_nr': f_nr}
        return render_template('foto/no_hits.html',
                               title=_("Foto Database"), subtitle=_("Detail View"), data=results)
    else:
        if conv_format == '':
            # image size from IIIF info.json
            f_nr = re.sub(r'F0*?', r'', f_nr, flags=re.IGNORECASE)
            if re.match(r'^\d*$', f_nr):
                f_number = "{:06d}".format(int(f_nr))
                f_nr = "F" + "{:06d}".format(int(f_nr))
            try:
                with urllib.request.urlopen(
                        "https://edh-www.adw.uni-heidelberg.de/iiif2/iiif/2/f" + f_number + ".tif/info.json") as url:
                    data = json.loads(url.read().decode())
                    img_size = {"x": data['width'], "y": data['height']}
            except:
                img_size = {"x": 0, "y": 0}
            return render_template('foto/detail_view.html',
                                   title=_("Foto Database"), subtitle=_("Detail View"),
                                   data={"results": results['items'][0], "image_size": img_size})
        else:
            return_dict = Foto.get_json_for_foto_record(f_nr)
            return_dict_json = jsonify(return_dict)
            return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
            return return_dict_json


@bp_foto.route('/foto/ac/fo_modern', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/fo_modern/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_modern(short=None):
    """
    route for retrieving autocomplete entries for field fo_modern
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("fo_modern", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("fo_modern", request.args['term'], 20))


@bp_foto.route('/foto/ac/fo_antik', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/fo_antik/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_antik(short=None):
    """
    route for retrieving autocomplete entries for field fo_antik
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("fo_antik", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("fo_antik", request.args['term'], 20))


@bp_foto.route('/foto/ac/aufbewahrung', methods=['GET', 'POST'], strict_slashes=False)
@bp_foto.route('/foto/ac/aufbewahrung/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_aufbewahrung(short=None):
    """
    route for retrieving autocomplete entries for field present location
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Foto.get_autocomplete_entries("aufbewahrung", request.args['term'], 10))
    else:
        return json.dumps(Foto.get_autocomplete_entries("aufbewahrung", request.args['term'], 20))


@bp_foto.route('/foto/lastUpdates', methods=['GET', 'POST'])
def last_updates():
    """
    route for displaying last updates in bibliographic database
    :return: orderedDictionary of bibliographic entries grouped by date
    """
    results = Foto.last_updates()
    results_grouped_by_date = Foto.group_results_by_date(results)
    return render_template('foto/last_updates.html',
                           title=_("Foto Database"),
                           subtitle=_("Last Updates"),
                           data=results_grouped_by_date)