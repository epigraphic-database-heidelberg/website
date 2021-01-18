import re
from datetime import datetime

import pysolr
from babel.dates import format_date
from babel.numbers import format_decimal
from flask import Markup
from flask import current_app
from flask_babel import lazy_gettext as _l


class Inscription:

    historic_periods = (
        _l('per_1'), _l('per_2'), _l('per_3'), _l('per_4'), _l('per_5'), _l('per_6'), _l('per_7'), _l('per_8'), _l('per_9'), _l('per_10'),
        _l('per_11'), _l('per_12'), _l('per_13'), _l('per_14'), _l('per_15'), _l('per_16'), _l('per_17'), _l('per_18'), _l('per_19'), _l('per_20'),
        _l('per_21'), _l('per_22'), _l('per_23'), _l('per_24'), _l('per_25'), _l('per_26')
    )

    type_of_inscription = (
        _l('titaccl'), _l('titadnun'), _l('titadsig'), _l('nota'), _l('titoppubpriv'), _l('titreiexpl'), _l('titpossfabr'), _l('brief'),
        _l('titdefix'), _l('tithon'), _l('elogium'), _l('oratio'), _l('titsep'), _l('titterm'), _l('fasti'), _l('miliarium'), _l('diplmil'), _l('titiurpub'), _l('titiurpriv'),
        _l('titsedspect'), _l('indexlaterc'), _l('titsac')
    )


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
                atext_br = result['atext']
                props['atext_br'] = Markup(re.sub("/","<br />", atext_br))
                btext_br = result['btext']
                #props['btext_br'] = Markup(re.sub("/", "<br />", btext_br))
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

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of inscription records from Solr Core edhText
        :return: number of inscription records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search("*:*")
        return format_decimal(results.hits, locale='de_DE')


    @classmethod
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhText
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhText')
        results = solr.search("*:*", sort="datum desc", rows=1)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            return format_date(dt, 'd. MMM YYYY', locale='de_DE')

    def get_title(self):
        """
        returns title for detail view of inscription
        :return: title string
        """
        title_str = ""
        if self.i_gattung and self.i_gattung != "":
            i_gatt = self.i_gattung
            if re.search("\?$", i_gatt):
                key_without_trailing_questionmark = re.sub("\?$", "", i_gatt)
                title_str = _l(key_without_trailing_questionmark) + "?"
            else:
                title_str = _l(i_gatt)
        else:
            title_str = _l("Inschrift")
        if self.fo_antik and self.fo_antik != "":
            title_str += _l(" from ") + self.fo_antik
        elif self.fo_modern:
            title_str += _l(" from ") + self.fo_modern
        else:
            provinz = self.provinz
            if re.search("\?$", provinz):
                key_without_trailing_questionmark = re.sub("\?$", "", provinz)
                title_str += _l(" from ") + _l(key_without_trailing_questionmark) + "?"
            else:
                title_str += _l(" from ") + _l(provinz)
        # uppercase first character
        return title_str[0].upper() + title_str[1:]
