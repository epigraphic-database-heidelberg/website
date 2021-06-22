from flask import render_template, request, jsonify, Response
from flask_babel import _
from ..models.Publication import Publication
from . import bp_bibliography
from .forms import BibliographySearch
import json
import io
import csv


@bp_bibliography.route('/bibliographie/suche', methods=['GET', 'POST'], strict_slashes=False)
def search_bibliography():
    """
    route for bibliographical search mask
    :return: html template of bibliographical search mask
    """
    form = BibliographySearch()
    form.autor.data = request.args.get('autor')
    form.titel.data = request.args.get('titel')
    form.publikation.data = request.args.get('publikation')
    form.band.data = request.args.get('band')
    form.jahr.data = request.args.get('jahr')
    form.ae.data = request.args.get('ae')
    form.cil.data = request.args.get('cil')
    form.zu_ae.data = request.args.get('zu_ae')
    form.sonstige.data = request.args.get('sonstige')

    if len(request.args) > 0:
        # create query string
        query_string = Publication.create_query_string(request.args)
        if request.args.get('view') == 'table':
            results = Publication.query(query_string, hits=10000)
        else:
            results = Publication.query(query_string)
        # return results to client
        if results['metadata']['number_of_hits'] > 0:
            # CSV export of results
            if request.args.get('export') and request.args.get('export') == 'csv':
                results = Publication.query(query_string, number_of_results=100000, start=0)
                output = io.StringIO()
                writer = csv.writer(output)
                first_row = ['b-no.', 'author', 'title', 'publication', 
                            'volume', 'pages', 'place', 'ae', 'about ae', 'cil', 'other literature' ]
                writer.writerow(first_row)
                for i in results['items']:
                    writer.writerow((
                        i.b_nr,
                        i.autor,
                        i.titel,
                        i.publikation,
                        i.band,
                        i.seiten,
                        i.ort,
                        i.ae,
                        i.zu_ae,
                        i.cil,
                        i.sonstigeCorpora
                    ))
                output.seek(0)    
                return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=edh_bibliography.csv"})
            else:
                if request.args.get('view') == 'table':
                    return render_template('bibliography/search_results_table.html', title=_("Bibliographic Database"),
                                    subtitle=_("Search results"), data=results,
                                    number_of_hits=results['metadata']['number_of_hits'], form=form)
                else:
                    return render_template('bibliography/search_results.html',
                                    title=_("Bibliographic Database"),
                                    subtitle=_("Search results"),
                                    form=form,
                                    data=results,
                                    number_of_hits=results['metadata']['number_of_hits'])
        else:
            return render_template('bibliography/no_hits.html', title=_("Bibliographic Database"),
                                   subtitle=_("Search results"), data=results,
                                   number_of_hits=results['metadata']['number_of_hits'], form=form)
    else:
        return render_template('bibliography/search.html', title=_("Bibliographic Database"), subtitle=_("Search"), form=form)


@bp_bibliography.route('/edh/bibliographie/<b_nr>', strict_slashes=False)
@bp_bibliography.route('/edh/bibliographie/<b_nr>/<conv_format>', strict_slashes=False)
def detail_view(b_nr, conv_format=''):
    """
    route for displaying detail view of bibliographical record
    :param b_nr: identifier of bibliographical record
    :param conv_format: conversion format (json)
    :return: html template (default) or json
    """
    b_nr = Publication.format_b_nr(b_nr)
    results = Publication.query("b_nr:" + b_nr)
    if results['metadata']['number_of_hits'] == 0:
        results['metadata']['query_params'] = {'b_nr': b_nr}
        return render_template('bibliography/no_hits.html',
                               title=_("Bibliographic Database"), subtitle=_("Search results"), data=results)
    else:
        if conv_format == '':
            return render_template('bibliography/detail_view.html',
                               title=_("Bibliographic Database"), subtitle=_("Detail View"),
                               data=results['items'][0])
        else:
            return_dict = Publication.get_json_for_bib_record(b_nr)
            return_dict_json = jsonify(return_dict)
            return_dict_json.headers.add('Access-Control-Allow-Origin', '*')
            return return_dict_json


@bp_bibliography.route('/bibliographie/lastUpdates', methods=['GET', 'POST'], strict_slashes=False)
def last_updates():
    """
    route for displaying last updates in bibliographic database
    :return: orderedDictionary of bibliographic entries grouped by date
    """
    results = Publication.last_updates()
    results_grouped_by_date = Publication.group_results_by_date(results)
    return render_template('bibliography/last_updates.html',
                           title=_("Bibliography Database"),
                           subtitle=_("Last Updates"),
                           data=results_grouped_by_date)


@bp_bibliography.route('/bibliographie/ac/autor', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_autor():
    """
    route for retrieving autocomplete entries for field autor
    :return: list of entries for autocomplete
    """
    return json.dumps(Publication.get_autocomplete_entries("autor", request.args['term']))


@bp_bibliography.route('/bibliographie/ac/publikation', methods=['GET', 'POST'], strict_slashes=False)
def autocomplete_publikation():
    """
    route for retrieving autocomplete entries for field publikation
    :return: list of entries for autocomplete
    """
    return json.dumps(Publication.get_autocomplete_entries("publikation", request.args['term']))
