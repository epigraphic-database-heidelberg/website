from flask import render_template, request, Response
from flask_babel import _
import io
import csv
import re

from . import bp_inscription
from .forms import InscriptionSearchDe, InscriptionSearchEn
from ..models.Inscription import Inscription
from ..models.Person import Person


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

    if len(request.args) > 0:
        # create query string
        query_string = Inscription.create_query_string(request.args)
        results = Inscription.query(query_string)
        number_of_hits = Inscription.get_number_of_hits_for_query(query_string)
        # return results to client
        if results['metadata']['number_of_hits'] > 0:
            # CSV export of results
            if request.args.get('export') and request.args.get('export') == 'csv':
                results = Inscription.query(query_string, number_of_results=100000, no_highlighting=True, start=0)
                output = io.StringIO()
                writer = csv.writer(output)
                first_row = ['HD-No.', 'transcription', 'work status', 'province / Italic region', 'country', 'ancient find spot', 
                            'modern find spot', 'find spot (village, street, etc.)', 'chronological data', 'literature', 'coordinates (lat,lng)', 'type of monument', 'type of inscription', 'material']
                writer.writerow(first_row)
                for i in results['items']:
                    writer.writerow((
                        i.hd_nr,
                        i.atext,
                        _('beleg-'+i.beleg),
                        i.provinz,
                        i.land,
                        i.fo_antik,
                        i.fo_modern,
                        i.fundstelle,
                        i.datierung.replace("&ndash;", "-"),
                        i.literatur.replace("#", ""),
                        i.koordinaten1,
                        i.i_traeger_str,
                        i.i_gattung_str,
                        i.material
                    ))
                output.seek(0)    
                return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=edh.csv"})
            else:
                # default: HTML representation
                return render_template('inscription/search_results.html', title=_("Epigraphic Text Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=number_of_hits, form=form)
        else:
            return render_template('inscription/no_hits.html', title=_("Epigraphic Text Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=number_of_hits, form=form)
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
        people = Person.query("id:" + hd_nr)
        return render_template('inscription/detail_view.html', title=_("Epigraphic Text Database"),
                               data=results['items'][0], people=Person.query("hd_nr:" + hd_nr ))
