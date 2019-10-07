import pysolr
import re
from flask import Markup
from flask import current_app


class Inscription:

    def __init__(self,
                 hd_nr,
                 provinz,
                 land,
                 bearbeiter,
                 datum,
                 beleg,
                 **kwargs):
        prop_defaults = {
            "fo_modern": None,
            "fo_antik": None,
            "fundstelle": None,
            "verw_bezirk": None,
            "fundjahr": None,
            "aufbewahrung": None,
            "i_gattung": None,
            "i_traeger": None,
            "material": None,
            "hoehe": None,
            "breite": None,
            "tiefe": None,
            "if_h": None,
            "if_b": None,
            "bh": None,
            "tm_nr": None,
            "gdb_id": None,
            "sprache": None,
            "metrik": None,
            "dekor": None,
            "schreibtechnik": None,
            "interpunktion": None,
            "dat_jahr_a": None,
            "dat_jahr_e": None,
            "dat_monat": None,
            "dat_tag": None,
            "religion": None,
            "militaer": None,
            "geographie": None,
            "sowire": None,
            "literatur": None,
            "kommentar": None,
            "atext": None,
            "atext_br": None,
            "btext": None,
            "btext_br": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.hd_nr = hd_nr
        self.provinz = provinz
        self.land = land
        self.bearbeiter = bearbeiter
        self.datum = datum
        self.beleg = beleg

    @classmethod
    def query(cls, query_string):
        """
        queries Solr core
        :return: list of Inscription instances
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search(query_string, **{'rows': '20'})
        if len(results) == 0:
            return None
        else:
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('hd_nr', 'provinz', 'land', 'bearbeiter', 'datum', 'beleg'):
                        props[key] = result[key]
                        print(key + " => " + result[key])
                atext_br = result['atext']
                props['atext_br'] = Markup(re.sub("/","<br />", atext_br))
                btext_br = result['btext']
                props['btext_br'] = Markup(re.sub("/", "<br />", btext_br))
                inscr = Inscription(result['hd_nr'],
                                    result['provinz'],
                                    result['land'],
                                    result['bearbeiter'],
                                    result['datum'],
                                    result['beleg'],
                                    **props
                                    )
                query_result.append(inscr)
            return query_result
