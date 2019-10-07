import pysolr
import re
from flask import Markup
from flask import current_app


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
        results = solr.search(query_string, **{'rows': '20'})
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
