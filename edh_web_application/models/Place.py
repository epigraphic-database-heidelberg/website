import collections
import json
import math
import re
from datetime import datetime

import pysolr
from babel.dates import format_date
from babel.numbers import format_decimal
from flask import current_app
from flask import request
from flask_babel import lazy_gettext as _l

#from edh_web_application.models.Inscription import Inscription
from edh_web_application.models.helpers import remove_number_of_hits_from_autocomplete, escape_value


class Place:
    # list of countries (de)
    country_de = (
        '?', 'eg', 'al', 'dz', 'ad', 'am', 'az', 'be', 'ba', 'bg', 'dk', 'de', 'fr', 'ge', 'gi', 'gr',
        'gb', 'iq', 'il', 'it', 'ye', 'jo', 'kz', 'kg', 'hr', 'lb', 'ly', 'li', 'lu', 'mt', 'ma', 'mk', 'md', 'mc',
        'me', 'nl', 'at', 'pl', 'pt', 'ro', 'ru', 'sm', 'se', 'ch', 'rs', 'sk', 'si', 'es', 'sd', 'sy', 'tj', 'cz',
        'tn', 'tr', 'ua', 'hu', 'uz', 'va', 'cy'
    )
    country_en = (
        '?', 'al', 'dz', 'ad', 'am', 'at', 'az', 'be', 'ba', 'bg', 'hr', 'cy', 'cz', 'dk', 'eg', 'fr', 'ge',
        'de', 'gi', 'gr', 'hu', 'iq', 'il', 'it', 'jo', 'kz', 'kg', 'lb', 'ly', 'li', 'lu', 'mk', 'mt', 'md',
        'mc', 'me', 'ma', 'nl', 'pl', 'pt', 'ro', 'ru', 'sa', 'rs', 'sk', 'si', 'es', 'sd', 'se', 'ch', 'sy',
        'tj', 'tn', 'tr', 'ua', 'gb', 'uz', 'va', 'ye'
    )

    # dict of localized country names
    country = collections.OrderedDict()
    country = {
        "?": _l("land-?"),
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
        "sa": _l("land-sa"),
        "sy": _l("land-sy"),
        "tj": _l("land-tj"),
        "tn": _l("land-tn"),
        "tr": _l("land-tr"),
        "ua": _l("land-ua"),
        "uz": _l("land-uz"),
        "va": _l("land-va"),
        "ye": _l("land-ye"),
        "rks": _l("land-rks")
    }

    # list of province short names
    province = (
        'Inc', 'Ach', 'Aeg', 'Aem', 'Afr', 'AlC', 'AlG', 'AlM', 'AlP', 'ApC',
        'Aqu', 'Ara', 'Arm', 'Asi', 'Ass', 'Bae', 'Bar', 'Bel', 'BiP', 'BrL',
        'Bri', 'Cap', 'Cil', 'Cor', 'Cre', 'Cyp', 'Cyr', 'Dac', 'Dal', 'Epi',
        'Etr', 'Gal', 'GeI', 'GeS', 'HiC', 'Iud', 'LaC', 'Lig', 'Lug', 'Lus',
        'LyP', 'Mak', 'MaC', 'MaT', 'Mes', 'MoI', 'MoS', 'Nar', 'Nor', 'Num',
        'PaI', 'PaS', 'Pic', 'Rae', 'ReB', 'Rom', 'Sam', 'Sar', 'Sic', 'Syr',
        'Thr', 'Tra', 'Umb', 'VeH')

    province_dict = {
        "Inc": _l("Inc"),
        "Ach": _l("Ach"),
        "Aeg": _l("Aeg"),
        "Aem": _l("Aem"),
        "Afr": _l("Afr"),
        "AlC": _l("AlC"),
        "AlG": _l("AlG"),
        "AlM": _l("AlM"),
        "AlP": _l("AlP"),
        "ApC": _l("ApC"),
        "Aqu": _l("Aqu"),
        "Ara": _l("Ara"),
        "Arm": _l("Arm"),
        "Asi": _l("Asi"),
        "Ass": _l("Ass"),
        "Bae": _l("Bae"),
        "Bar": _l("Bar"),
        "Bel": _l("Bel"),
        "BiP": _l("BiP"),
        "BrL": _l("BrL"),
        "Bri": _l("Bri"),
        "Cap": _l("Cap"),
        "Cil": _l("Cil"),
        "Cor": _l("Cor"),
        "Cre": _l("Cre"),
        "Cyp": _l("Cyp"),
        "Cyr": _l("Cyr"),
        "Dac": _l("Dac"),
        "Dal": _l("Dal"),
        "Epi": _l("Epi"),
        "Etr": _l("Etr"),
        "Gal": _l("Gal"),
        "GeI": _l("GeI"),
        "GeS": _l("GeS"),
        "HiC": _l("HiC"),
        "Iud": _l("Iud"),
        "LaC": _l("LaC"),
        "Lig": _l("Lig"),
        "Lug": _l("Lug"),
        "Lus": _l("Lus"),
        "LyP": _l("LyP"),
        "Mak": _l("Mak"),
        "MaC": _l("MaC"),
        "MaE": _l("MaE"),
        "MaT": _l("MaT"),
        "Mes": _l("Mes"),
        "MoI": _l("MoI"),
        "MoS": _l("MoS"),
        "Nar": _l("Nar"),
        "Nor": _l("Nor"),
        "Num": _l("Num"),
        "PaI": _l("PaI"),
        "PaS": _l("PaS"),
        "Pic": _l("Pic"),
        "Rae": _l("Rae"),
        "ReB": _l("ReB"),
        "Rom": _l("Rom"),
        "Sam": _l("Sam"),
        "Sar": _l("Sar"),
        "Sic": _l("Sic"),
        "Syr": _l("Syr"),
        "Thr": _l("Thr"),
        "Tra": _l("Tra"),
        "Tri": _l("Tri"),
        "TuU": _l("TuU"),
        "Umb": _l("Umb"),
        "Val": _l("Val"),
        "VeH": _l("VeH"),
    }

    province_id_dict = {
        "900000": "Ach",
        "900001": "AlP",
        "900002": "AlG",
        "900003": "Umb",
        "900004": "Pic",
        "900005": "Sam",
        "900006": "LaC",
        "900007": "Etr",
        "900008": "Tra",
        "900009": "Lig",
        "900010": "Aem",
        "900011": "AlC",
        "900012": "AlM",
        "900013": "VeH",
        "900014": "BrL",
        "900015": "Sic",
        "900016": "Sar",
        "900017": "Cor",
        "900018": "ApC",
        "900019": "Asi",
        "900020": "Bri",
        "900021": "Cre",
        "900022": "Cyp",
        "900023": "GeS",
        "900024": "Bel",
        "900025": "Nar",
        "900026": "Aqu",
        "900027": "Lug",
        "900028": "GeI",
        "900029": "Lus",
        "900030": "Bae",
        "900031": "Ass",
        "900032": "Arm",
        "900033": "LyP",
        "900034": "BiP",
        "900035": "Mes",
        "900036": "Gal",
        "900037": "Cap",
        "900038": "Cil",
        "900039": "Mak",
        "900040": "Epi",
        "900041": "HiC",
        "900042": "Nor",
        "900043": "PaI",
        "900044": "PaS",
        "900045": "Cyr",
        "900046": "Aeg",
        "900047": "MaC",
        "900048": "Num",
        "900049": "Afr",
        "900050": "MaT",
        "900051": "Rae",
        "900052": "Thr",
        "900053": "Ara",
        "900054": "Syr",
        "900055": "Iud",
        "900056": "MoI",
        "900057": "MoS",
        "900058": "Dac",
        "900059": "Dal",
        "900060": "Rom",
        "900061": "Bar",
    }

    province_pleiades_dict = {
        "Ach": "https://pleiades.stoa.org/places/981502",
        "Aeg": "https://pleiades.stoa.org/places/766",
        "Aem": "https://pleiades.stoa.org/places/393372",
        "Afr": "https://pleiades.stoa.org/places/981504",
        "AlC": "https://pleiades.stoa.org/places/982257",
        "AlG": "https://pleiades.stoa.org/places/167637",
        "AlM": "https://pleiades.stoa.org/places/982259",
        "AlP": "",
        "ApC": "https://pleiades.stoa.org/places/991359",
        "Aqu": "https://pleiades.stoa.org/places/981505",
        "Ara": "https://pleiades.stoa.org/places/29475",
        "Arm": "https://pleiades.stoa.org/places/981507",
        "Asi": "https://pleiades.stoa.org/places/981509",
        "Ass": "https://pleiades.stoa.org/places/29492",
        "Bae": "https://pleiades.stoa.org/places/862",
        "Bel": "https://pleiades.stoa.org/places/981511",
        "BiP": "https://pleiades.stoa.org/places/981512",
        "Bri": "https://pleiades.stoa.org/places/981513",
        "BrL": "https://pleiades.stoa.org/places/991362",
        "Cap": "https://pleiades.stoa.org/places/628949",
        "Cil": "https://pleiades.stoa.org/places/981514",
        "Cor": "https://pleiades.stoa.org/places/991339",
        "Cre": "https://pleiades.stoa.org/places/991373",
        "Cyp": "https://pleiades.stoa.org/places/981516",
        "Cyr": "https://pleiades.stoa.org/places/981517",
        "Dal": "https://pleiades.stoa.org/places/981522",
        "Dac": "https://pleiades.stoa.org/places/981518",
        "Epi": "https://pleiades.stoa.org/places/991364",
        "Etr": "https://pleiades.stoa.org/places/413122",
        "Gal": "https://pleiades.stoa.org/places/619161",
        "GeI": "https://pleiades.stoa.org/places/981524",
        "GeS": "https://pleiades.stoa.org/places/1000",
        "HiC": "https://pleiades.stoa.org/places/1027",
        "Iud": "https://pleiades.stoa.org/places/981527",
        "LaC": "",
        "Lig": "https://pleiades.stoa.org/places/383698",
        "Lug": "https://pleiades.stoa.org/places/981528",
        "Lus": "https://pleiades.stoa.org/places/1101",
        "LyP": "https://pleiades.stoa.org/places/981530",
        "Mak": "https://pleiades.stoa.org/places/981531",
        "MaC": "https://pleiades.stoa.org/places/285482",
        "MaT": "https://pleiades.stoa.org/places/981533",
        "Mes": "https://pleiades.stoa.org/places/874602",
        "MoI": "https://pleiades.stoa.org/places/981535",
        "MoS": "https://pleiades.stoa.org/places/981536",
        "Nar": "https://pleiades.stoa.org/places/981537",
        "Nor": "https://pleiades.stoa.org/places/187490",
        "Num": "https://pleiades.stoa.org/places/981539",
        "PaI": "https://pleiades.stoa.org/places/981540",
        "PaS": "https://pleiades.stoa.org/places/981541",
        "Pic": "https://pleiades.stoa.org/places/413253",
        "Rae": "https://pleiades.stoa.org/places/981547",
        "Rom": "",
        "Sam": "https://pleiades.stoa.org/places/433078",
        "Sar": "https://pleiades.stoa.org/places/991344",
        "Sic": "https://pleiades.stoa.org/places/981549",
        "Syr": "https://pleiades.stoa.org/places/981550",
        "Thr": "https://pleiades.stoa.org/places/981552",
        "Tra": "https://pleiades.stoa.org/places/383801",
        "Umb": "https://pleiades.stoa.org/places/413360",
        "VeH": "https://pleiades.stoa.org/places/991349",
        "Bar": "https://pleiades.stoa.org/places/20468/barbaricum",
    }

    province_wikidata_dict = {
        "Ach": "https://www.wikidata.org/entity/Q204772",
        "Aeg": "https://www.wikidata.org/entity/Q202311",
        "Aem": "https://www.wikidata.org/entity/Q1135779",
        "Afr": "https://www.wikidata.org/entity/Q181238",
        "AlC": "https://www.wikidata.org/entity/Q623322",
        "AlG": "https://www.wikidata.org/entity/Q360922",
        "AlM": "https://www.wikidata.org/entity/Q309270",
        "AlP": "https://www.wikidata.org/entity/Q660100",
        "ApC": "https://www.wikidata.org/entity/Q623322",
        "Aqu": "https://www.wikidata.org/entity/Q715376",
        "Ara": "https://www.wikidata.org/entity/Q221353",
        "Arm": "https://www.wikidata.org/entity/Q1254480",
        "Asi": "https://www.wikidata.org/entity/Q210718",
        "Ass": "https://www.wikidata.org/entity/Q40169",
        "Bae": "https://www.wikidata.org/entity/Q219415",
        "Bel": "https://www.wikidata.org/entity/Q206443",
        "BiP": "https://www.wikidata.org/entity/Q913382",
        "Bri": "https://www.wikidata.org/entity/Q185103",
        "BrL": "https://www.wikidata.org/entity/Q3931879",
        "Cap": "https://www.wikidata.org/entity/Q33490",
        "Cil": "https://www.wikidata.org/entity/Q4819648",
        "Cor": "https://www.wikidata.org/entity/Q281345",
        "Cre": "https://www.wikidata.org/entity/Q24049878",
        "Cyp": "https://www.wikidata.org/entity/Q2967757",
        "Cyr": "https://www.wikidata.org/entity/Q692775",
        "Dal": "https://www.wikidata.org/entity/Q1330965",
        "Dac": "https://www.wikidata.org/entity/Q971609",
        "Epi": "https://www.wikidata.org/entity/Q1820754",
        "Etr": "https://www.wikidata.org/entity/Q206730",
        "Gal": "https://www.wikidata.org/entity/Q1249412",
        "GeI": "https://www.wikidata.org/entity/Q152136",
        "GeS": "https://www.wikidata.org/entity/Q153553",
        "HiC": "https://www.wikidata.org/entity/Q1126678",
        "Iud": "https://www.wikidata.org/entity/Q1003997",
        "LaC": "",
        "Lig": "https://www.wikidata.org/entity/Q1256",
        "Lug": "https://www.wikidata.org/entity/Q10971",
        "Lus": "https://www.wikidata.org/entity/Q188650",
        "LyP": "https://www.wikidata.org/entity/Q1246140",
        "Mak": "https://www.wikidata.org/entity/Q207497",
        "MaC": "https://www.wikidata.org/entity/Q734505",
        "MaT": "https://www.wikidata.org/entity/Q1244742",
        "Mes": "https://www.wikidata.org/entity/Q765845",
        "MoI": "https://www.wikidata.org/entity/Q1227719",
        "MoS": "https://www.wikidata.org/entity/Q670837",
        "Nar": "https://www.wikidata.org/entity/Q26897",
        "Nor": "https://www.wikidata.org/entity/Q131434",
        "Num": "https://www.wikidata.org/entity/Q12901244",
        "PaI": "https://www.wikidata.org/entity/Q1247297",
        "PaS": "https://www.wikidata.org/entity/Q642188",
        "Pic": "https://www.wikidata.org/entity/Q510990",
        "Rae": "https://www.wikidata.org/entity/Q156789",
        "Rom": "",
        "Sam": "https://www.wikidata.org/entity/Q463459",
        "Sar": "https://www.wikidata.org/entity/Q281345",
        "Sic": "https://www.wikidata.org/entity/Q691321",
        "Syr": "https://www.wikidata.org/entity/Q207118",
        "Thr": "https://www.wikidata.org/entity/Q635058",
        "Tra": "https://www.wikidata.org/entity/Q635058",
        "Umb": "https://www.wikidata.org/entity/Q1247527",
        "VeH": "https://www.wikidata.org/entity/Q649505",
        "Bar": "",
    }

    province_tm_dict = {
        "Ach": "https://www.trismegistos.org/place/30282",
        "Aeg": "https://www.trismegistos.org/place/49",
        "Aem": "https://www.trismegistos.org/place/33158",
        "Afr": "https://www.trismegistos.org/place/15771",
        "AlC": "https://www.trismegistos.org/place/22433",
        "AlG": "https://www.trismegistos.org/place/22459",
        "AlM": "https://www.trismegistos.org/place/22359",
        "AlP": "https://www.trismegistos.org/place/22472",
        "ApC": "https://www.trismegistos.org/place/30938",
        "Aqu": "https://www.trismegistos.org/place/3924",
        "Ara": "https://www.trismegistos.org/place/281",
        "Arm": "https://www.trismegistos.org/place/2614",
        "Asi": "https://www.trismegistos.org/place/344",
        "Ass": "https://www.trismegistos.org/place/5181",
        "Bae": "https://www.trismegistos.org/place/25443",
        "Bel": "https://www.trismegistos.org/place/23540",
        "BiP": "https://www.trismegistos.org/place/16280",
        "Bri": "https://www.trismegistos.org/place/3232",
        "BrL": "https://www.trismegistos.org/place/33153",
        "Cap": "https://www.trismegistos.org/place/482",
        "Cil": "https://www.trismegistos.org/place/526",
        "Cor": "https://www.trismegistos.org/place/22055",
        "Cre": "https://www.trismegistos.org/place/527",
        "Cyp": "https://www.trismegistos.org/place/528",
        "Cyr": "https://www.trismegistos.org/place/1201",
        "Dal": "https://www.trismegistos.org/place/11624",
        "Dac": "https://www.trismegistos.org/place/12834",
        "Epi": "https://www.trismegistos.org/place/655",
        "Etr": "https://www.trismegistos.org/place/13603",
        "Gal": "https://www.trismegistos.org/place/691",
        "GeI": "https://www.trismegistos.org/place/16530",
        "GeS": "https://www.trismegistos.org/place/16528",
        "HiC": "https://www.trismegistos.org/place/16933",
        "Iud": "https://www.trismegistos.org/place/936",
        "LaC": "https://www.trismegistos.org/place/33152",
        "Lig": "https://www.trismegistos.org/place/33157",
        "Lug": "https://www.trismegistos.org/place/19858",
        "Lus": "https://www.trismegistos.org/place/5531",
        "LyP": "https://www.trismegistos.org/place/16417",
        "Mak": "https://www.trismegistos.org/place/1279",
        "MaC": "https://www.trismegistos.org/place/36807",
        "MaT": "https://www.trismegistos.org/place/14002",
        "Mes": "https://www.trismegistos.org/place/1363",
        "MoI": "https://www.trismegistos.org/place/29480",
        "MoS": "https://www.trismegistos.org/place/29481",
        "Nar": "https://www.trismegistos.org/place/19860",
        "Nor": "https://www.trismegistos.org/place/11329",
        "Num": "https://www.trismegistos.org/place/6054",
        "PaI": "https://www.trismegistos.org/place/16529",
        "PaS": "https://www.trismegistos.org/place/16532",
        "Pic": "https://www.trismegistos.org/place/14405",
        "Rae": "https://www.trismegistos.org/place/3319",
        "Rom": "https://www.trismegistos.org/place/2058",
        "Sam": "https://www.trismegistos.org/place/14346",
        "Sar": "https://www.trismegistos.org/place/3310",
        "Sic": "https://www.trismegistos.org/place/2132",
        "Syr": "https://www.trismegistos.org/place/2211",
        "Thr": "https://www.trismegistos.org/place/2414",
        "Tra": "https://www.trismegistos.org/place/33156",
        "Umb": "https://www.trismegistos.org/place/13620",
        "VeH": "https://www.trismegistos.org/place/33155",
        "Bar": "",
    }

    # dict of localized sort paramter values
    sort_param_values = {
        "geo_id": _l('geo_id'),
        "country": _l('land'),
        "province": _l('provinz'),
        "ancient_find_spot": _l('fo_antik'),
        "modern_find_spot": _l('fo_modern'),
        "find_spot": _l('fundstelle'),
        "region": _l('region'),
        "pleiades_id_1": _l('pleiades_id_1'),
        "pleiades_id_2": _l('pleiades_id_2'),
        "geonames_id_1": _l('geonames_id_1'),
        "geonames_id_2": _l('geonames_id_2'),
        "tm_geo_id": _l('tm_geo_id'),
    }

    # defines current EDH working status of province:
    # 0: EDH provisional
    # 1: EDH fully entered
    # 2: EDH under progress
    # 3: responsible: EDR
    # 4: responsible HEplOnl
    #
    province_status_dict = {
        "Ach": _l("provStatus-1"),
        "AlP": _l("provStatus-1"),
        "AlG": _l("provStatus-1"),
        "Umb": _l("provStatus-3"),
        "Pic": _l("provStatus-3"),
        "Sam": _l("provStatus-3"),
        "LaC": _l("provStatus-3"),
        "Etr": _l("provStatus-3"),
        "Tra": _l("provStatus-3"),
        "Lig": _l("provStatus-3"),
        "Aem": _l("provStatus-3"),
        "AlC": _l("provStatus-1"),
        "AlM": _l("provStatus-1"),
        "VeH": _l("provStatus-3"),
        "BrL": _l("provStatus-3"),
        "Sic": _l("provStatus-3"),
        "Sar": _l("provStatus-3"),
        "Cor": _l("provStatus-3"),
        "ApC": _l("provStatus-3"),
        "Asi": _l("provStatus-0"),
        "Bri": _l("provStatus-1"),
        "Cre": _l("provStatus-0"),
        "Cyp": _l("provStatus-0"),
        "GeS": _l("provStatus-2"),
        "Bel": _l("provStatus-2"),
        "Nar": _l("provStatus-0"),
        "Aqu": _l("provStatus-0"),
        "Lug": _l("provStatus-0"),
        "GeI": _l("provStatus-2"),
        "Lus": _l("provStatus-4"),
        "Bae": _l("provStatus-4"),
        "Ass": _l("provStatus-0"),
        "Arm": _l("provStatus-0"),
        "LyP": _l("provStatus-0"),
        "BiP": _l("provStatus-0"),
        "Mes": _l("provStatus-0"),
        "Gal": _l("provStatus-0"),
        "Cap": _l("provStatus-0"),
        "Cil": _l("provStatus-0"),
        "Mak": _l("provStatus-1"),
        "Epi": _l("provStatus-1"),
        "HiC": _l("provStatus-4"),
        "Nor": _l("provStatus-1"),
        "PaI": _l("provStatus-1"),
        "PaS": _l("provStatus-1"),
        "Cyr": _l("provStatus-0"),
        "Aeg": _l("provStatus-0"),
        "Mac": _l("provStatus-0"),
        "Num": _l("provStatus-0"),
        "Afr": _l("provStatus-0"),
        "MaT": _l("provStatus-0"),
        "Rae": _l("provStatus-1"),
        "Thr": _l("provStatus-1"),
        "Ara": _l("provStatus-0"),
        "Syr": _l("provStatus-0"),
        "Iud": _l("provStatus-0"),
        "MoI": _l("provStatus-1"),
        "MoS": _l("provStatus-1"),
        "Dac": _l("provStatus-1"),
        "Dal": _l("provStatus-1"),
        "Rom": _l("provStatus-3"),
        "MaC": _l("provStatus-0"),
        "Bar": _l("provStatus-0"),
    }

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
            "geonames_id_1": None,
            "geonames_id_2": None,
            "koordinaten_1": None,
            "koordinaten_2": None,
            "provinz": None,
            "provinz_id": None,
            "name": None,
            "land": None,
            "trismegistos_geo_id": None,
            "bearbeitet": None,
            "kommentar": None,
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.id = id
        self.datum = datum
        self.bearbeiter = bearbeiter

    @classmethod
    def create_query_string(cls, form):
        """
        creates solr query based on user data entered into search mask
        :param form: ImmutableMultiDict of GET params
        :return: query_string
        """
        logical_operater = "AND"
        query_string = ""

        if 'geo_id' in form and form['geo_id'] != "":
            geo_id = form['geo_id']
            geo_id = re.sub(r'G0*?', r'', geo_id, flags=re.IGNORECASE)
            try:
                geo_id = "G" + "{:06d}".format(int(geo_id))
            except:
                geo_id = form['geo_id']
            query_string = "id:" + geo_id + " " + logical_operater + " "
        else:
            query_string = "id:* " + logical_operater + " "

        if 'pleiades_id' in form and form['pleiades_id'] != "":
            query_string += "(pleiades_id_1:" + escape_value(form['pleiades_id']) + " OR " + " pleiades_id_2:" + escape_value(form['pleiades_id']) + ") " + logical_operater + " "

        if 'geonames_id' in form and form['geonames_id'] != "":
            query_string += "(geonames_id_1:" + escape_value(form['geonames_id']) + " OR "  + " geonames_id_2:" + escape_value(form['geonames_id']) + ") "  + logical_operater + " "

        if 'geonames_id_2' in form and form['geonames_id_2'] != "":
            query_string += "geonames_id_2:" + escape_value(form['geonames_id_2']) + " " + logical_operater + " "

        if 'tm_geo_id' in form and form['tm_geo_id'] != "":
            query_string += "trismegistos_geo_id:" + escape_value(form['tm_geo_id']) + " " + logical_operater + " "

        if 'provinz' in form and form['provinz'] != "":
            # province is a multi value field
            query_string += "("
            for prov in form.getlist('provinz'):
                if prov != "":
                    query_string += "provinz:" + prov + "* OR "
            # remove trailing OR
            query_string = re.sub(" OR $", "", query_string)
            query_string += ") " + logical_operater + " "

        if 'land' in form and form['land'] != "":
            # country is a multi value field
            query_string += "("
            for c in form.getlist('land'):
                if c != "":
                    query_string += "land:" + c + "* OR "
            # remove trailing OR
            query_string = re.sub(" OR $", "", query_string)
            query_string += ") " + logical_operater + " "

        if 'region' in form and form['region'] != "":
            if re.search("\([0-9]*\)$", form['region']):
                query_string += 'verw_bezirk_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['region'])) + '" ' + logical_operater + ' '
            else:
                query_string += "verw_bezirk_ci:*" + escape_value(form['region']) + "* " + logical_operater + " "

        if 'fo_antik' in form and form['fo_antik'] != "":
            if re.search("\([0-9]*\)$", form['fo_antik']):
                query_string += 'fo_antik_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['fo_antik'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fo_antik_ci:*" + escape_value(form['fo_antik']) + "* " + logical_operater + " "

        if 'fo_modern' in form and form['fo_modern'] != "":
            if re.search("\([0-9]*\)$", form['fo_modern']):
                query_string += 'fo_modern_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['fo_modern'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fo_modern_ci:*" + escape_value(form['fo_modern']) + "* " + logical_operater + " "

        if 'fundstelle' in form and form['fundstelle'] != "":
            if re.search("\([0-9]*\)$", form['fundstelle']):
                query_string += 'fundstelle_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['fundstelle'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fundstelle_ci:*" + escape_value(form['fundstelle']) + "* " + logical_operater + " "

        if 'kommentar' in form and form['kommentar'] != "":
            query_string += "kommentar:*" + escape_value(form['kommentar']) + "* " + logical_operater + " "

        if 'bearbeitet_abgeschlossen' in form and 'bearbeitet_provisorisch' not in form:
            query_string += "bearbeitet:true" + logical_operater + " "
        elif 'bearbeitet_abgeschlossen' not in form and 'bearbeitet_provisorisch' in form:
            query_string += "-bearbeitet:* " + logical_operater + " "

        if 'bearbeiter' in form and form['bearbeiter'] != "":
            query_string += "bearbeiter:" + escape_value(form['bearbeiter']) + " " + logical_operater + " "

        # remove last " AND"
        query_string = re.sub(" " + logical_operater + " $", "", query_string)
        return query_string

    @classmethod
    def query(cls, query_string, *args, **kwargs):
        """
        queries Solr core
        :param query_string: Solr query string
        :return: list of Place instances
        """
        hits = kwargs.get('hits', None)
        start = 0  # index number of first record to retrieve
        rows = 20  # number of receords to retrieve
        sort = "id asc"  # default
        if request.args.get('start'):
            start = request.args.get('start')
        if request.args.get('anzahl'):
            rows = int(request.args.get('anzahl'))
            # if user changes number of hits/page in result page
            # show all hits on one page if start < rows
            if int(start) < rows:
                start = 0
        if hits:
            rows = hits
        if request.args.get('sort') in ['fo_antik', 'fo_modern', 'verw_bezirk']:
            sort = request.args.get('sort') + "_str asc"
        elif request.args.get('sort') == "provinz":
            sort = "provinz asc"
        elif request.args.get('sort') == "fundstelle":
            sort = "fundstelle_sort asc"
        elif request.args.get('sort') == "land":
            from flask import session
            if session.get('lang'):
                sort = "land_sort_" + session.get('lang') + " asc"
            else:
                sort = "land_sort_en asc"
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search(query_string, **{'rows': rows, 'start': start, 'sort': sort})
        if len(results) == 0:
            # no hits, return query params
            query_params = _get_query_params(request.args)

            return {'metadata': {"number_of_hits": 0,
                                 "url_without_pagination_parameters": _get_url_without_pagination_parameters(
                                     request.url), "url_without_sort_parameter": _get_url_without_sort_parameter(
                    request.url), "url_without_view_parameter": _get_url_without_view_parameter(
                    request.url), "query_params": query_params}}
        else:
            number_of_hits = results.hits
            query_params = _get_query_params(request.args)
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('id', 'bearbeiter', 'datum', 'land', 'provinz', 'name'):
                        props[key] = result[key]
                    if key == 'land':
                        if re.search(".+\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = Place.country[key_without_trailing_questionmark] + "?"
                        else:
                            props[key] = Place.country[result[key]]
                    elif key == 'provinz':
                        if re.search("\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = _l(key_without_trailing_questionmark) + "?"
                        else:
                            props[key] = _l(result[key])
                        props['provinz_id'] = Place.get_province_id_from_code(re.sub("\?$", "", result[key]))
                fo_antik = ""
                fo_modern = ""
                fundstelle = ""
                if 'fundstelle' in result:
                    fundstelle = re.sub("[\{\}]", "", result['fundstelle'])
                if 'fo_antik' in result:
                    fo_antik = result['fo_antik']
                if 'fo_modern' in result:
                    fo_modern = result['fo_modern']
                props['name'] = Place.get_find_spot_name(fo_antik, fo_modern, fundstelle)
                if 'kommentar' in props:
                    props['kommentar'] = _encode_string_with_links(props['kommentar'])
                    props['kommentar'] = props['kommentar'].replace("\n", "<br />")
                pl = Place(result['id'],
                           result['datum'],
                           result['bearbeiter'],
                           **props
                           )
                query_result.append(pl)
            return {"metadata": {"start": start, "rows": rows, "number_of_hits": number_of_hits,
                                 "url_without_pagination_parameters": _get_url_without_pagination_parameters(
                                     request.url), "url_without_sort_parameter": _get_url_without_sort_parameter(
                    request.url), "url_without_view_parameter": _get_url_without_view_parameter(
                    request.url), "query_params": query_params},
                    "items": query_result}

    @classmethod
    def get_find_spot_name(cls, fo_antik, fo_modern, fundstelle):
        """
        returns a placename for findspot detail views,
        will be displayed as h1
        param fo_antik: ancient find spot string
        param fo_modern: modern find spot string
        param fundstelle: find spot string
        return: name string
        """
        name = ""
        if fo_antik != "" and fo_modern != "":
            name = fo_antik + " &ndash; " + fo_modern
        elif fo_antik != "":
            name = fo_antik
        else:
            name = fo_modern
        if fundstelle == "":
            return name
        if name != "":
            name += " (" + fundstelle + ")"
        else:
            name = fundstelle
        return name

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

    @classmethod
    def last_updates(cls):
        """
        return last 50 entries that have been updated
        :return: list of 50 entries
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search("*:*", sort="datum desc", rows=50)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            res['datum'] = format_date(dt, 'd. MMM YYYY', locale='de_DE')
            fragezeichen = ""
            land = res['land']
            if res['land'][-1] == "?":
                fragezeichen = "?"
                land = re.sub("\\?", "", res['land'])
            res['land'] = Place.country[land] + fragezeichen
            fragezeichen = ""
            provinz = res['provinz']
            if res['provinz'][-1] == "?":
                fragezeichen = "?"
                provinz = re.sub("\\?", "", res['provinz'])
            res['provinz'] = Place.province_dict[provinz] + fragezeichen
            res['provinz_id'] = Place.get_province_id_from_code(res['provinz'])
            if 'fundstelle' in res:
                res['fundstelle'] = re.sub("[\{\}]", "", res['fundstelle'])
        return results

    @classmethod
    def group_results_by_date(cls, results):
        """
        groups last 50 entries in geographic database by date
        :param results: list of geographic entries
        :return: orderedDict with date as keys, and list of entries as values
        """
        last_date = ""
        grouped_result = collections.OrderedDict()
        for res in results:
            current_date = res['datum']
            if current_date != last_date:
                grouped_result[current_date] = []
                last_date = current_date
            grouped_result[current_date].append(res)
        return grouped_result

    @classmethod
    def get_autocomplete_entries(cls, ac_field, term, hits):
        """
        queries Solr core edhGeo for list of entries displayed in
        autocomplete fields of Geo form
        :param ac_field: field to facet
        :param term: querystring
        :return: list of relevant field values
        """
        if re.match("[a-zA-Z]+", term):
            params = {
                'facet': 'on',
                'facet.field': ac_field + '_str',
                'facet.sort': 'count',
                'facet.mincount': 1,
                'facet.limit': hits,
                'rows': '0',
            }
            query = ac_field + '_ac:"' + term + '"'
            solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
            results = solr.search(query, **params)
            # concat results and counts as string
            return_list = []
            is_first_element = True
            first_item = ""
            for entry in results.facets['facet_fields'][ac_field + "_str"]:
                if is_first_element:
                    first_item = entry
                    is_first_element = False
                    continue
                else:
                    is_first_element = True
                    return_list.append(re.sub("[\{\}]*", '', first_item) + " (" + str(entry) + ")")
            return return_list

    @classmethod
    def get_findspots_for_province(cls, province):
        """
        returns all findspots for given province
        param: province short code
        return: list of Place instances (findspots of given province)
        """
        query = "provinz:" + province + "*"
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        params = {
            'rows': 10000,
            'fl': "id, datum, bearbeiter, fo_antik, fo_modern, fundstelle, verw_bezirk, land",
        }
        results = solr.search(query, **params)
        query_result = []
        for result in results:
            props = {}
            for key in result:
                if key not in ('land', 'fundstelle'):
                    props[key] = result[key]
                if key == 'land':
                    if re.search(".+\?$", result[key]):
                        key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                        props[key] = Place.country[key_without_trailing_questionmark] + "?"
                    else:
                        props[key] = Place.country[result[key]]
                elif key == 'fundstelle':
                    props[key] = re.sub("[\{\}]", "", result[key])
            pl = Place(**props)
            query_result.append(pl)
        return query_result

    @classmethod
    def get_province_id_from_code(cls, code):
        """
        returns numeric key for given province
        param code: province code like 'GeS'
        return: province key
        """
        for key in Place.province_id_dict:
            if Place.province_id_dict[key] == code:
                return key

    @classmethod
    def get_polygon_for_province(cls, province):
        # province data in geojson format in sub folder province
        with open("./edh_web_application/models/province/" + province.lower() + ".json") as file:
            data = file.read()
        return data

    @classmethod
    def get_center_of_polygon(cls, geojson):
        """
        returns geographic center of given province polygon
        param geojson: province geojson
        return: coordinate string
        """
        geojson_coordinates = str(json.loads(geojson)['geometry']['coordinates'])
        geojson_coordinates = re.sub("\s*", "", geojson_coordinates)
        geojson_coordinates = re.sub("\n", "", geojson_coordinates)
        coordinates_list = re.findall('\[.*?\]', geojson_coordinates)
        num_coords = len(coordinates_list)
        x = 0.0
        y = 0.0
        z = 0.0
        if num_coords > 1:
            for coord_str in coordinates_list:
                coord_str = re.sub("[\[\]]*", "", coord_str)
                (lat, lon) = coord_str.split(",")
                lat = float(lat) * math.pi / 180
                lon = float(lon) * math.pi / 180
                a = math.cos(lat) * math.cos(lon)
                b = math.cos(lat) * math.sin(lon)
                c = math.sin(lat)
                x = x + a
                y = y + b
                z = z + c
            x = x / num_coords
            y = y / num_coords
            z = z / num_coords
            clon = math.atan2(y, x)
            hyp = math.sqrt(x * x + y * y)
            clat = math.atan2(z, hyp)
            return str((clon * 180 / math.pi)) + ", " + str((clat * 180 / math.pi))
        else:
            return "47, 11"

    @classmethod
    def get_inscriptions_from_place(cls, geo_id):
        """
        returns list of HD-Nos of inscriptions from given place
        param geo_id: ID of place
        return: list of HD-Nos
        """
        from edh_web_application.models.Inscription import Inscription
        inscription_list = []
        # only numeric value is needed
        geo_id = re.sub("G0*", "", geo_id)
        places = Inscription.query("gdb_id:" + geo_id)
        if places['metadata']['number_of_hits'] > 0:
            for place in places['items']:
                inscription_list.append({"hd_nr":place.hd_nr, "titel":place.titel})
        return inscription_list

    @classmethod
    def get_json_for_geo_record(cls, geo_id):
        """
        return record as json
        :param geo_id: No. of record
        """
        record = Place.query("id:" + geo_id)
        if len(record) > 0 and 'items' in record:
            for item in record['items']:
                item_dict = {'id': geo_id,
                             'uri': current_app.config['HOST'] + "/edh/geographie/" + geo_id,
                             'last_update': item.datum,
                             'responsible_individual': item.bearbeiter,
                             }
                if item.fo_antik:
                    item_dict['findspot_ancient'] = item.fo_antik
                if item.fo_antik:
                    item_dict['findspot_modern'] = item.fo_modern
                if item.fundstelle:
                    item_dict['findspot'] = item.fundstelle
                if item.provinz:
                    item_dict['province'] = item.provinz
                if item.land:
                    item_dict['country'] = item.land
                if item.verw_bezirk:
                    item_dict['modern_region'] = item.verw_bezirk
                if item.pleiades_id_1:
                    item_dict['pleiades_uri_1'] = "https://pleiades.stoa.org/places/" + item.pleiades_id_1
                if item.pleiades_id_2:
                    item_dict['pleiades_uri_2'] = "https://pleiades.stoa.org/places/" + item.pleiades_id_2
                if item.geonames_id_1:
                    item_dict['geonames_uri_1'] = "https://geonames.org/" + item.geonames_id_1
                if item.pleiades_id_2:
                    item_dict['geonames_uri_2'] = "https://geonames.org/" + item.geonames_id_2
                if item.koordinaten_1:
                    item_dict['coordinates_1'] = item.koordinaten_1
                if item.koordinaten_2:
                    item_dict['coordinates_2'] = item.koordinaten_2
                if item.trismegistos_geo_id:
                    item_dict['tm_geo_uri'] = "https://trismegistos.org/place/" + item.trismegistos_geo_id
                if item.bearbeitet:
                    item_dict['work_status'] = _l('completed')
                else:
                    item_dict['work_status'] = 'provisional'
                if item.kommentar:
                    item_dict['commentary'] = item.kommentar
            pub_dict = {'items': item_dict, 'limit': 20, 'total': 1}
            return pub_dict


def _get_url_without_pagination_parameters(url):
    """
    removes URL parameters anzahl and start; these get added later in the template again
    with values for pagination
    :param url: current URL as string
    :return: shortened URL as string
    """
    url = re.sub("start=[0-9]*&*", "", url)
    url = re.sub("anzahl=[0-9]*&*", "", url)
    url = re.sub("&{2,}", "&", url)
    url = re.sub(request.url_root, "", url)
    return "/" + url


def _get_url_without_sort_parameter(url):
    """
    removes URL parameter sort; these get added later in the template again
    in dialog "sort by"
    :param url: current URL as string
    :return: shortened URL as string
    """
    url = re.sub("sort=.*&*", "", url)
    url = re.sub("&{2,}", "&", url)
    url = re.sub(request.url_root, "", url)
    return "/" + url


def _get_url_without_view_parameter(url):
    """
    removes URL parameter view; these get added later in the template again
    in dialog "view"
    :param url: current URL as string
    :return: shortened URL as string
    """
    url = re.sub("view=.*?&*", "", url)
    url = re.sub("&{2,}", "&", url)
    url = re.sub(request.url_root, "", url)
    return "/" + url


def _get_query_params(args):
    """
    creates dictionary of search params for displaying on
    search result page
    :param args: request.args
    :return: dictionary with all params of query
    """
    result_dict = {}
    for key in args:
        if key == 'provinz' and args['provinz'] != "":
            # multidict
            result_dict['provinz'] = ""
            params_list = args.getlist('provinz')
            for prov in params_list:
                result_dict['provinz'] = result_dict['provinz'] + _l(prov) + ", "
        elif key == 'land' and args['land'] != "":
            # multidict
            result_dict['land'] = ""
            params_list = args.getlist('land')
            for c in params_list:
                result_dict['land'] = result_dict['land'] + Place.country[c] + ", "
        elif key == 'bearbeitet_abgeschlossen' and 'bearbeitet_provisorisch' not in args:
            # only completed records
            result_dict[_l('Work Status')] = _l('completed')
        elif key == 'bearbeitet_provisorisch' and 'bearbeitet_abgeschlossen' not in args:
            # only provisional records
            result_dict[_l('Work Status')] = _l('provisional')
        elif key == 'bearbeiter' and args['bearbeiter'] != "":
            result_dict[_l('responsible individual')] = args['bearbeiter']
        elif key not in ('anzahl', 'sort', 'start', 'view', 'bearbeitet_abgeschlossen', 'bearbeitet_provisorisch') and args[key] != "":
            result_dict[key] = args[key]
    if 'provinz' in result_dict:
        result_dict['provinz'] = re.sub(", $", "", result_dict['provinz'])
    if 'land' in result_dict:
        result_dict['land'] = re.sub(", $", "", result_dict['land'])
    if len(result_dict) == 0:
        result_dict['Geo-ID'] = '*'
    return result_dict


def _encode_string_with_links(unencoded_string):
    """
    returns string with encode url links
    param unencoded_string: string which contains URLs
    return: string with encoded URLs
    """
    URL_REGEX = re.compile(r'''((http://|https://)[^ <>'"{}|\\^`[\]]*)''')
    return URL_REGEX.sub(r'<a href="\1">\1</a>', unencoded_string)
