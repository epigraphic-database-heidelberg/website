from flask import render_template, request
from flask_babel import _

from . import bp_inscription
from .forms import InscriptionSearchDe, InscriptionSearchEn
from ..models.Inscription import Inscription
from ..models.Person import Person


@bp_inscription.route('/inschrift/lastUpdates', methods=['GET', 'POST'])
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


@bp_inscription.route('/inschrift/suche')
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
        return render_template('inscription/search_results.html', title=_("Epigraphic Text Database"),
                               subtitle=_("Search results"), data=results,
                                   number_of_hits=number_of_hits, form=form)


    else:
        return render_template('inscription/search.html', title=_("Epigraphic Text Database"), subtitle=_("Simple Search"), form=form)


@bp_inscription.route('/inschrift/erweiterteSuche')
def extended_search():
    return render_template('inscription/extended_search.html',
                           title=_("Epigraphic Text Database"), subtitle=_("Extended Search"))


@bp_inscription.route('/edh/inschrift/<hd_nr>')
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
