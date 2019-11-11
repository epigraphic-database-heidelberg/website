import pysolr
import re
from flask import Markup
from flask import current_app, session


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
        results = solr.search(query_string, **{'rows': '99999'})
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
            query_string += "autor:" + form['author'] + " " + logical_operater + " "

        if 'title' in form and form['title'] != "":
            query_string += "titel:" + form['title'] + " " + logical_operater + " "

        if 'publication' in form and form['publication'] != "":
            query_string += "publikation:" + form['publication'] + " " + logical_operater + " "

        if 'volume' in form and form['volume'] != "":
            query_string += "band:" + form['volume'] + " " + logical_operater + " "

        if 'years' in form and form['years'] != "":
            query_string += "jahr:" + form['years'] + " " + logical_operater + " "

        if 'pages' in form and form['pages'] != "":
            query_string += "seiten:" + form['pages'] + " " + logical_operater + " "

        if 'town' in form and form['town'] != "":
            query_string += "ort:" + form['town'] + " " + logical_operater + " "

        if 'ae' in form and form['ae'] != "":
            query_string += "ae:" + form['ae'] + " " + logical_operater + " "

        if 'on_ae' in form and form['on_ae'] != "":
            query_string += "zu_ae:" + form['on_ae'] + " " + logical_operater + " "

        if 'cil' in form and form['cil'] != "":
            query_string += "cil:" + form['cil'] + " " + logical_operater + " "

        if 'other_corpora' in form and form['other_corpora'] != "":
            query_string += " sonstigeCorpora:" + form['other_corpora'] + " " + logical_operater + " "
        # remove last " AND"
        query_string = re.sub(" " + logical_operater,"",query_string)
        return query_string
