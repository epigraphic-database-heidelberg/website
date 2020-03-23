import pysolr
import re
from flask import Markup
from flask import current_app
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime
import collections
from flask_babel import lazy_gettext as _l


class Foto:
    # dict of localized country names
    country = collections.OrderedDict()
    country = {
        "": "",
        "ad": _l("land-ad"),
        "al": _l("land-al"),
        "am": _l("land-am"),
        "at": _l("land-at"),
        "az": _l("land-az"),
        "ba": _l("land-ba"),
        "be": _l("land-be"),
        "bg": _l("land-bg"),
        "ch": _l("land-ch"),
        "cy": _l("land-cy"),
        "cz": _l("land-cz"),
        "de": _l("land-de"),
        "dk": _l("land-dk"),
        "dz": _l("land-dz"),
        "eg": _l("land-eg"),
        "es": _l("land-es"),
        "fr": _l("land-fr"),
        "gb": _l("land-gb"),
        "ge": _l("land-ge"),
        "gi": _l("land-gi"),
        "gr": _l("land-gr"),
        "hr": _l("land-hr"),
        "hu": _l("land-hu"),
        "il": _l("land-il"),
        "iq": _l("land-iq"),
        "it": _l("land-it"),
        "jo": _l("land-jo"),
        "kg": _l("land-kg"),
        "kz": _l("land-kz"),
        "lb": _l("land-lb"),
        "li": _l("land-li"),
        "lu": _l("land-lu"),
        "ly": _l("land-ly"),
        "ma": _l("land-ma"),
        "mc": _l("land-mc"),
        "md": _l("land-md"),
        "me": _l("land-me"),
        "mk": _l("land-mk"),
        "mt": _l("land-mt"),
        "nl": _l("land-nl"),
        "pl": _l("land-pl"),
        "pt": _l("land-pt"),
        "ro": _l("land-ro"),
        "rs": _l("land-rs"),
        "ru": _l("land-ru"),
        "sd": _l("land-sd"),
        "se": _l("land-se"),
        "si": _l("land-si"),
        "sk": _l("land-sk"),
        "sm": _l("land-sm"),
        "sa": _l("land-sa"),
        "sy": _l("land-sy"),
        "tj": _l("land-tj"),
        "tn": _l("land-tn"),
        "tr": _l("land-tr"),
        "ua": _l("land-ua"),
        "?": _l("land-?"),
        "uz": _l("land-uz"),
        "va": _l("land-va"),
        "ye": _l("land-ye"),
        "rks": _l("land-rks")
    }
    # dict of province names
    province = {
        "Ach": "Achaia",
        "Aeg": "Aegyptus",
        "Aem": "Aemilia (Regio VIII)",
        "Afr": "Africa Proconsularis",
        "AlC": "Alpes Cottiae",
        "AlG": "Alpes Graiae",
        "AlM": "Alpes Maritimae",
        "AlP": "Alpes Poeninae",
        "ApC": "Apulia et Calabria (Regio II)",
        "Aqu": "Aquitania",
        "Ara": "Arabia",
        "Arm": "Armenia",
        "Asi": "Asia",
        "Ass": "Assyria",
        "Bae": "Baetica",
        "Bar": "Barbaricum",
        "Bel": "Belgica",
        "BiP": "Bithynia et Pontus",
        "BrL": "Bruttium et Lucania (Regio III)",
        "Bri": "Britannia",
        "Cap": "Cappadocia",
        "Cil": "Cilicia",
        "Cor": "Corsica",
        "Cre": "Creta",
        "Cyp": "Cyprus",
        "Cyr": "Cyrene",
        "Dac": "Dacia",
        "Dal": "Dalmatia",
        "Epi": "Epirus",
        "Etr": "Etruria (Regio VII)",
        "Gal": "Galatia",
        "GeI": "Germania inferior",
        "GeS": "Germania superior",
        "HiC": "Hispania citerior",
        "Inc": _l("unknown"),
        "Iud": "Iudaea",
        "LaC": "Latium et Campania (Regio I)",
        "Lig": "Liguria (Regio IX)",
        "Lug": "Lugdunensis",
        "Lus": "Lusitania",
        "LyP": "Lycia et Pamphylia",
        "Mak": "Macedonia",
        "MaC": "Mauretania Caesariensis",
        "MaE": "Macedonia, Epirus",
        "MaT": "Mauretania Tingitana",
        "Mes": "Mesopotamia",
        "MoI": "Moesia inferior",
        "MoS": "Moesia superior",
        "Nar": "Narbonensis",
        "Nor": "Noricum",
        "Num": "Numidia",
        "PaI": "Pannonia inferior",
        "PaS": "Pannonia superior",
        "Pic": "Picenum (Regio V)",
        "Rae": "Raetia",
        "ReB": "Regnum Bospori",
        "Rom": "Roma",
        "Sam": "Samnium (Regio IV)",
        "Sar": "Sardinia",
        "Sic": "Sicilia, Melita",
        "Syr": "Syria",
        "Thr": "Thracia",
        "Tra": "Transpadana (Regio XI)",
        "Tri": "Tripolitania",
        "TuU": "Tuscia et Umbria",
        "Umb": "Umbria (Regio VI)",
        "Val": "Valeria",
        "VeH": "Venetia et Histria (Regio X)",
    }
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

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of fotographic records from Solr Core edhBiblio
        :return: number of fotographic records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
        results = solr.search("*:*")
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhFoto
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
        results = solr.search("*:*", sort="datum desc", rows=1)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            return format_date(dt, 'd. MMM YYYY', locale='de_DE')