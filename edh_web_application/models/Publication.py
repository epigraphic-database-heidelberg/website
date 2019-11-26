import pysolr
import re
from flask import Markup
from flask import current_app, session
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime


class Publication:

    def __init__(self,
                 b_nr,
                 bearbeiter,
                 datum,
                 **kwargs):
        prop_defaults = {
            "autor": None,
            "titel": None,
            "publikation": None,
            "band": None,
            "jahr": None,
            "seiten": None,
            "ort": None,
            "ae": None,
            "zu_ae": None,
            "cil": None,
            "sonstigeCorpora": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.b_nr = b_nr
        self.bearbeiter = bearbeiter
        self.datum = datum

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :return: list of Publication instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search(query_string, **{'rows': '99999', 'sort': 'b_nr asc'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('b_nr', 'bearbeiter', 'datum'):
                        props[key] = result[key]
                publ = Publication(result['b_nr'],
                                    result['bearbeiter'],
                                    result['datum'],
                                    **props
                                    )
                query_result.append(publ)
            return query_result

    @classmethod
    def create_query_string(cls, form):
        """
        creates solr query based on user data entered into search mask
        :param form: ImmutableMultiDict of GET params
        :return: query_string
        """
        logical_operater = "AND"
        query_string = ""

        if 'b_nr' in form and form['b_nr'] != "":
            b_nr = form['b_nr']
            # check if b_nr is valid pattern
            # correct if neccessary/possible
            query_string = "b_nr:" + b_nr + " " + logical_operater + " "
        if 'author' in form and form['author'] != "":
            query_string += "autor:" + _escape_value(form['author']) + " " + logical_operater + " "

        if 'title' in form and form['title'] != "":
            query_string += "titel:" + _escape_value(form['title']) + " " + logical_operater + " "

        if 'publication' in form and form['publication'] != "":
            query_string += "publikation:" + _escape_value(form['publication']) + " " + logical_operater + " "

        if 'volume' in form and form['volume'] != "":
            query_string += "band:" + _escape_value(form['volume']) + " " + logical_operater + " "

        if 'years' in form and form['years'] != "":
            query_string += "jahr:" + _escape_value(form['years']) + " " + logical_operater + " "

        if 'pages' in form and form['pages'] != "":
            query_string += "seiten:" + _escape_value(form['pages']) + " " + logical_operater + " "

        if 'town' in form and form['town'] != "":
            query_string += "ort:" + _escape_value(form['town']) + " " + logical_operater + " "

        if 'ae' in form and form['ae'] != "":
            query_string += "ae:" + _escape_value(form['ae']) + " " + logical_operater + " "

        if 'on_ae' in form and form['on_ae'] != "":
            query_string += "zu_ae:" + _escape_value(form['on_ae']) + " " + logical_operater + " "

        if 'cil' in form and form['cil'] != "":
            query_string += "cil:" + _escape_value(form['cil']) + " " + logical_operater + " "

        if 'other_corpora' in form and form['other_corpora'] != "":
            query_string += " sonstigeCorpora:" + _escape_value(form['other_corpora']) + " " + logical_operater + " "
        # remove last " AND"
        query_string = re.sub(" " + logical_operater + " $","",query_string)
        return query_string

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of bibliographical records from Solr Core edhBiblio
        :return: number of bibliographical records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search("*:*")
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhBiblio
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search("*:*", sort="datum desc", rows=1)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            return format_date(dt, 'd. MMM YYYY', locale='de_DE')

    @classmethod
    def get_autocomplete_entries(cls, ac_field, term):
        """
        queries Splor core edhBiblio for list of entries displayed in
        autocomplete fields of Biblio form
        :param ac_field: field to facet
        :param term: querystring
        :return: list of relevant field values
        """
        params = {
            'facet': 'on',
            'facet.field': ac_field+'_ac',
            'facet.sort': 'index',
            'facet.mincount': 1,
            'facet.limit': '20',
            'rows': '0',
        }
        query = ac_field+":"+term
        query = re.sub("\s", "\ ", query)
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search(query, **params)
        return results.facets['facet_fields'][ac_field+'_ac'][::2]


def _escape_value(val):
    val = re.sub("\s", "\ ", val)
    return val