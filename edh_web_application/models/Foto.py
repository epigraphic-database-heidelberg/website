import pysolr
import re
from flask import Markup
from flask import current_app


class Foto:

    def __init__(self,
                 f_nr,
                 bearbeiter,
                 datum,
                 **kwargs):
        prop_defaults = {
            "f_nr": None,
            "provinz": None,
            "land": None,
            "land_sort_de": None,
            "land_sort_en": None,
            "fo_antik": None,
            "fo_modern": None,
            "aufbewahrung": None,
            "neg_nr": None,
            "aufnahme_jahr": None,
            "qualitaet": None,
            "cil": None,
            "ae": None,
            "internet": None,
            "andere": None,
            "kommentar": None,
            "hd_nr": None,
            "bearbeiter": None,
            "datum": None,
            "aufschrift": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.f_nr = f_nr
        self.bearbeiter = bearbeiter
        self.datum = datum

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :return: list of Foto instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
        results = solr.search(query_string, **{'rows': '20'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('f_nr', 'bearbeiter', 'datum'):
                        props[key] = result[key]
                publ = Foto(result['f_nr'],
                                   result['bearbeiter'],
                                   result['datum'],
                                   **props
                                   )
                query_result.append(publ)
            return query_result
