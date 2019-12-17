import pysolr
from flask import current_app
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime
import collections
from flask_babel import lazy_gettext as _l
import re


class Person:

    def __init__(self,
                 id,
                 hd_nr,
                 pers_no,
                 **kwargs):
        prop_defaults = {
            "name": None,
            "praenomen": None,
            "cognomen": None,
            "nomen": None,
            "supernomen": None,
            "origo": None,
            "filiation": None,
            "tribus": None,
            "besonderheit": None,
            "geschlecht": None,
            "verwandt": None,
            "status": None,
            "funktion": None,
            "beruf": None,
            "l_jahre": None,
            "l_monate": None,
            "l_tage": None,
            "l_stunden": None,
            "uri": None,
            "pir": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.id = id
        self.hd_nr = hd_nr
        self.pers_no = pers_no

    @classmethod
    def create_query_string(cls, form):
        """
        creates solr query based on user data entered into search mask
        :param form: ImmutableMultiDict of GET params
        :return: query_string
        """
        logical_operater = "AND"
        query_string = ""



        # remove last " AND"
        query_string = re.sub(" " + logical_operater + " $", "", query_string)
        return query_string

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :param query_string: Solr query string
        :return: list of Place instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhPers')
        results = solr.search(query_string, **{'rows': '99999', 'sort': 'id asc'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('id'):
                        props[key] = result[key]
                pers = Person(result['id'],
                                   **props
                                   )
                query_result.append(pers)
            return query_result

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of geographical records from Solr Core edhGeo
        :return: number of geographical records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search("*:*")
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_number_of_hits_for_query(cls, query_string):
        """
        returns number of hits for given query
        :param query_string: Solr query string
        :return:
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search(query_string)
        return format_decimal(results.hits, locale='de_DE')


    @classmethod
    def get_autocomplete_entries(cls, ac_field, term):
        """
        queries Splor core edhPers for list of entries displayed in
        autocomplete fields of Pers form
        :param ac_field: field to facet
        :param term: querystring
        :return: list of relevant field values
        """
        params = {
            'facet': 'on',
            'facet.field': ac_field + '_ac',
            'facet.sort': 'index',
            'facet.mincount': 1,
            'facet.limit': '20',
            'rows': '0',
        }
        query = ac_field + ":" + term
        query = re.sub("\s", "\ ", query)
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search(query, **params)
        result_list = results.facets['facet_fields'][ac_field + '_ac'][::2]
        return_list = []
        # remove curley brackets from field 'fundstelle
        for res in result_list:
            res = re.sub(r'[\{\}]','',res)
            return_list.append(res)
        return return_list


def _escape_value(val):
    """
    escape user entered value for solr query
    :param val: string value entered by user to be escaped
    :return: escaped string ready for solr query
    """
    val = re.sub("\s", "\ ", val)
    val = re.sub(":", "\:", val)
    val = re.sub("\(", "\(", val)
    val = re.sub("\)", "\)", val)
    val = re.sub("\]", "\]", val)
    val = re.sub("\[", "\[", val)
    val = re.sub("\{", "\{", val)
    val = re.sub("\}", "\}", val)
    val = re.sub("/", "\/", val)
    val = re.sub("\?", "\?", val)
    return val
