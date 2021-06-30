from flask import render_template, request, Response
from flask_babel import _
import io
import csv
import re
import json

from . import bp_inscription
from .forms import InscriptionSearchDe, InscriptionSearchEn
from ..models.Inscription import Inscription
from ..models.Person import Person
from ..models.Place import Place


@bp_inscription.route('/inschrift/lastUpdates', methods=['GET', 'POST'], strict_slashes=False)
def last_updates():
    """
    route for displaying last updates in inscription database
    :return: orderedDictionary of inscription entries grouped by date
    """
    results = Inscription.last_updates()
    results_grouped_by_date = Inscription.group_results_by_date(results)
    return render_template('inscription/last_updates.html',
                           title=_("Epigraphic Text Database"), subtitle=_("Last Updates"),
                           data=results_grouped_by_date)


@bp_inscription.route('/inschrift/suche', strict_slashes=False)
def simple_search():
    if _('lang') == "de":
        form = InscriptionSearchDe(data=request.args)
    else:
        form = InscriptionSearchEn(data=request.args)
    form.fo_antik.data = request.args.get('fo_antik')
    form.fo_modern.data = request.args.get('fo_modern')
    form.fundstelle.data = request.args.get('fundstelle')
    form.provinz.data = request.args.getlist('provinz')
    form.land.data = request.args.getlist('land')
    form.literatur.data = request.args.get('literatur')

    if len(request.args) > 0:
        # create query string
        query_string = Inscription.create_query_string(request.args)
        if request.args.get('view') == 'table' or request.args.get('view') == 'map' or (request.args.get('export') and request.args.get('export') == 'csv'):
            results = Inscription.query(query_string, number_of_results=100000, no_highlighting=True, start=0)
        else:
            results = Inscription.query(query_string)
        # return results to client
        if results['metadata']['number_of_hits'] > 0:
            # CSV export of results
            if request.args.get('export') and request.args.get('export') == 'csv':
                output = io.StringIO()
                writer = csv.writer(output)
                first_row = ['hd-no.', 'transcription', 'work status', 'province / Italic region', 'country', 'ancient find spot', 
                            'modern find spot', 'find spot (village, street, etc.)', 'chronological data', 'literature', 'coordinates (lat,lng)', 'type of monument', 'type of inscription', 'material']
                writer.writerow(first_row)
                for i in results['items']:
                    literatur = i.literatur
                    datierung = i.datierung
                    if literatur:
                        literatur = literatur.replace("#", "")
                    if datierung:
                        datierung = datierung.replace("&ndash;", "-")
                    writer.writerow((
                        i.hd_nr,
                        i.atext,
                        _('beleg-'+i.beleg),
                        i.provinz,
                        i.land,
                        i.fo_antik,
                        i.fo_modern,
                        i.fundstelle,
                        datierung,
                        literatur,
                        i.koordinaten1,
                        i.i_traeger_str,
                        i.i_gattung_str,
                        i.material
                    ))
                output.seek(0)    
                return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=edh.csv"})
            else:
                # default: HTML representation: Map/Table/List(=Default)
                if request.args.get('view') == 'map':
                    return render_template('inscription/search_results_map.html', title=_("Epigraphic Text Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
                if request.args.get('view') == 'table':
                    return render_template('inscription/search_results_table.html', title=_("Epigraphic Text Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
                else:
                    return render_template('inscription/search_results.html', title=_("Epigraphic Text Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=results['metadata']['number_of_hits'], form=form)
        else:
            # no results, test for redirects if query includes hd_nr parameter
            if request.args.get('hd_nr') and request.args.get('hd_nr') != "":# and request.args.get('hd_nr') in Inscription.hd_nr_redirects:
                hd_nr = request.args.get('hd_nr')
                hd_nr = re.sub(r'HD0*?', r'', hd_nr, flags=re.IGNORECASE)
                try:
                    hd_nr = "HD" + "{:06d}".format(int(hd_nr))
                except:
                    hd_nr = form['hd_nr']
                if hd_nr in Inscription.hd_nr_redirects:
                    return render_template('inscription/detail_view_redirect.html', title=_("Epigraphic Text Database"),
                               subtitle=_("Detail View"), data=(hd_nr, Inscription.hd_nr_redirects[hd_nr]))
                else:
                    return render_template('inscription/no_hits.html', title=_("Epigraphic Text Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
            else:
                return render_template('inscription/no_hits.html', title=_("Epigraphic Text Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
    else:
        return render_template('inscription/search.html', title=_("Epigraphic Text Database"), subtitle=_("Simple Search"), form=form)


@bp_inscription.route('/inschrift/erweiterteSuche', strict_slashes=False)
def extended_search():
    return render_template('inscription/extended_search.html',
                           title=_("Epigraphic Text Database"), subtitle=_("Extended Search"))


@bp_inscription.route('/edh/inschrift/<hd_nr>/xml', strict_slashes=False)
def export_xml(hd_nr):
    if hd_nr in Inscription.hd_nr_redirects:
            return render_template('inscription/detail_view_redirect.html', title=_("Epigraphic Text Database"),
                                subtitle=_("Detail View"), data=(hd_nr, Inscription.hd_nr_redirects[hd_nr]))
    inscription = Inscription.query("hd_nr:" + hd_nr)
    i = inscription['items'][0]
    return_xml = i.toXml()
    return Response(return_xml, mimetype='text/xml')
    

@bp_inscription.route('/edh/inschrift/<hd_nr>', strict_slashes=False)
def detail_view(hd_nr):
    if hd_nr in Inscription.hd_nr_redirects:
        return render_template('inscription/detail_view_redirect.html', title=_("Epigraphic Text Database"),
                               subtitle=_("Detail View"), data=(hd_nr, Inscription.hd_nr_redirects[hd_nr]))
    results = Inscription.query("hd_nr:" + hd_nr)    
    if results is None:
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database"), subtitle=_("Detail View"))
    else:
        people = Person.query("hd_nr:" + hd_nr)
        see_also_urls = Inscription.get_see_also_urls_from_tm_api(hd_nr)
        hyphened_atext = data=results['items'][0].get_hyphend_atext()
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database"),
                               data=results['items'][0], people=people, see_also_urls=see_also_urls, hyphened_atext=hyphened_atext)


@bp_inscription.route('/inschrift/ac/fo_modern', methods=['GET', 'POST'], strict_slashes=False)
@bp_inscription.route('/inschrift/ac/fo_modern/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_modern(short=None):
    """
    route for retrieving autocomplete entries for field fo_modern
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Inscription.get_autocomplete_entries("fo_modern", request.args['term'], 10))
    else:
        return json.dumps(Inscription.get_autocomplete_entries("fo_modern", request.args['term'], 20))


@bp_inscription.route('/inschrift/ac/fo_antik', methods=['GET', 'POST'], strict_slashes=False)
@bp_inscription.route('/inschrift/ac/fo_antik/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fo_antik(short=None):
    """
    route for retrieving autocomplete entries for field fo_antik
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Inscription.get_autocomplete_entries("fo_antik", request.args['term'], 10))
    else:
        return json.dumps(Inscription.get_autocomplete_entries("fo_antik", request.args['term'], 20))


@bp_inscription.route('/inschrift/ac/fundstelle', methods=['GET', 'POST'], strict_slashes=False)
@bp_inscription.route('/inschrift/ac/fundstelle/<short>', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_fundstelle(short=None):
    """
    route for retrieving autocomplete entries for field fundstelle
    :return: list of entries for autocomplete
    """
    if short:
        return json.dumps(Inscription.get_autocomplete_entries("fundstelle", request.args['term'], 10))
    else:
        return json.dumps(Inscription.get_autocomplete_entries("fundstelle", request.args['term'], 20))
