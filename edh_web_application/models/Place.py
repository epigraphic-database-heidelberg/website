import pysolr
import re
from flask import Markup
from flask import current_app
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime


class Place:
    def __init__(self,
                 id,
                 datum,
                 bearbeiter,
                 **kwargs):
        prop_defaults = {
            "fo_modern": None,
            "fo_antik": None,
            "fundstelle": None,
            "verw_bezirk": None,
            "pleiades_id_1": None,
            "pleiades_id_2": None,
            "koordinaten_1": None,
            "koordinaten_2": None,
            "provinz": None,
            "land": None,
            "trismegistos_geo_id": None,
            "bearbeitet": None,
            "kommentar": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.id = id
        self.bearbeiter = bearbeiter
        self.datum = datum

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :param query_string: Solr query string
        :return: list of Place instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search(query_string, **{'rows': '99999', 'sort': 'id asc'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('id', 'bearbeiter', 'datum'):
                        props[key] = result[key]
                publ = Place(result['id'],
                                   result['bearbeiter'],
                                   result['datum'],
                                   **props
                                   )
                query_result.append(publ)
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
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhGeo
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search("*:*", sort="datum desc", rows=1)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            return format_date(dt, 'd. MMM YYYY', locale='de_DE')

