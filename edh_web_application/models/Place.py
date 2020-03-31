import pysolr
from flask import current_app
from flask import request
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime
import collections
from flask_babel import lazy_gettext as _l
import re


class Place:
    # list of countries (de)
    country_de = (
        'eg', 'al', 'dz', 'ad', 'am', 'az', 'be', 'ba', 'bg', 'dk', 'de', 'fr', 'ge', 'gi', 'gr',
        'gb', 'iq', 'il', 'it', 'ye', 'jo', 'kz', 'kg', 'hr', 'lb', 'ly', 'li', 'lu', 'mt', 'ma', 'mk', 'md', 'mc',
        'me', 'nl', 'at', 'pl', 'pt', 'ro', 'ru', 'sm', 'se', 'ch', 'rs', 'sk', 'si', 'es', 'sd', 'sy', 'tj', 'cz',
        'tn', 'tr', 'ua', '?', 'hu', 'uz', 'va', 'cy'
    )
    country_en = (
        'al', 'dz', 'ad', 'am', 'at', 'az', 'be', 'ba', 'bg', 'hr', 'cy', 'cz', 'dk', 'eg', 'fr', 'ge',
        'de', 'gi', 'gr', 'va', 'hu', 'iq', 'il', 'it', 'jo', 'kz', 'kg', 'lb', 'ly', 'li', 'lu', 'mk', 'mt', 'md',
        'mc', 'me', 'ma', 'nl', 'pl', 'pt', 'ro', 'ru', 'sm', 'sa', 'rs', 'sk', 'si', 'es', 'sd', 'se', 'ch', 'sy',
        'tj', 'tn', 'tr', 'ua', 'gb', '?', 'uz', 'ye'
    )

    # dict of localized country names
    country = collections.OrderedDict()
    country = {
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
    # list of province names
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
        "Inc": _l("unknown"),
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
            # check if b_nr is valid pattern
            # correct if neccessary/possible
            query_string = "id:" + geo_id + " " + logical_operater + " "

        if 'pleiades_id_1' in form and form['pleiades_id_1'] != "":
            query_string += "pleiades_id_1:" + _escape_value(form['pleiades_id_1']) + " " + logical_operater + " "

        if 'pleiades_id_2' in form and form['pleiades_id_2'] != "":
            query_string += "pleiades_id_2:" + _escape_value(form['pleiades_id_2']) + " " + logical_operater + " "

        if 'geonames_id_1' in form and form['geonames_id_1'] != "":
            query_string += "geonames_id_1:" + _escape_value(form['geonames_id_1']) + " " + logical_operater + " "

        if 'geonames_id_2' in form and form['geonames_id_2'] != "":
            query_string += "geonames_id_2:" + _escape_value(form['geonames_id_2']) + " " + logical_operater + " "

        if 'tm_geo_id' in form and form['tm_geo_id'] != "":
            query_string += "trismegistos_geo_id:" + _escape_value(form['tm_geo_id']) + " " + logical_operater + " "

        if 'province' in form and form['province'] != "":
            # province is a multi value field
            query_string += "("
            for prov in form.getlist('province'):
                if prov != "":
                    query_string += "provinz:" + prov + "* OR "
            # remove trailing OR
            query_string = re.sub(" OR $", "", query_string)
            query_string += ") " + logical_operater + " "

        if 'country' in form and form['country'] != "":
            # country is a multi value field
            query_string += "("
            for c in form.getlist('country'):
                if c != "":
                    query_string += "land:" + c + "* OR "
            # remove trailing OR
            query_string = re.sub(" OR $", "", query_string)
            query_string += ") " + logical_operater + " "

        if 'region' in form and form['region'] != "":
            if re.search("\([0-9]*\)$", form['region']):
                query_string += 'verw_bezirk_ci:"' + _escape_value(
                    _remove_number_of_hits_from_autocomplete(form['region'])) + '" ' + logical_operater + ' '
            else:
                query_string += "verw_bezirk_ci:*" + re.sub(" ","\ ",form['region']) + "* " + logical_operater + " "

        if 'ancient_find_spot' in form and form['ancient_find_spot'] != "":
            if re.search("\([0-9]*\)$", form['ancient_find_spot']):
                query_string += 'fo_antik_ci:"' + _escape_value(
                    _remove_number_of_hits_from_autocomplete(form['ancient_find_spot'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fo_antik_ci:*" + re.sub(" ","\ ",form['ancient_find_spot']) + "* " + logical_operater + " "

        if 'modern_find_spot' in form and form['modern_find_spot'] != "":
            query_string += "fo_modern:" + _escape_value(form['modern_find_spot']) + " " + logical_operater + " "
            if re.search("\([0-9]*\)$", form['modern_find_spot']):
                query_string += 'fo_modern_ci:"' + _escape_value(
                    _remove_number_of_hits_from_autocomplete(form['modern_find_spot'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fo_modern_ci:*" + re.sub(" ","\ ",form['modern_find_spot']) + "* " + logical_operater + " "

        if 'find_spot' in form and form['find_spot'] != "":
            if re.search("\([0-9]*\)$", form['find_spot']):
                query_string += 'fundstelle_ci:"' + _escape_value(
                    _remove_number_of_hits_from_autocomplete(form['find_spot'])) + '" ' + logical_operater + ' '
            else:
                query_string += "fundstelle_ci:*" + re.sub(" ","\ ",form['find_spot']) + "* " + logical_operater + " "

        if 'comment' in form and form['comment'] != "":
            query_string += "kommentar:*" + re.sub(" ", "\ ", form['comment']) + "* " + logical_operater + " "

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
        start = 0  # index number of first record to retrieve
        rows = 20  # number of receords to retrieve
        if request.args.get('start'):
            start = request.args.get('start')
        if request.args.get('anzahl'):
            rows = int(request.args.get('anzahl'))
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhGeo')
        results = solr.search(query_string, **{'rows': rows, 'start': start, 'sort': 'id asc'})
        if len(results) == 0:
            return None
        else:
            number_of_hits = results.hits
            query_result = []
            for result in results:
                props = {}
                for key in result:
                    if key not in ('id', 'bearbeiter', 'datum', 'land', 'provinz'):
                        props[key] = result[key]
                    if key == 'land':
                        if re.search("\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = Place.country[key_without_trailing_questionmark] + "?"
                        else:
                            props[key] = Place.country[result[key]]
                    if key == 'provinz':
                        if re.search("\?$", result[key]):
                            key_without_trailing_questionmark = re.sub("\?$", "", result[key])
                            props[key] = _l(key_without_trailing_questionmark) + "?"
                        else:
                            props[key] = _l(result[key])

                pl = Place(result['id'],
                           result['datum'],
                           result['bearbeiter'],
                           **props
                           )
                query_result.append(pl)
            return {"metadata": {"start": start, "rows": rows, "number_of_hits": number_of_hits,
                                 "url_without_pagination_parameters": _get_url_without_pagination_parameters(
                                     request.url)},
                    "items": query_result}

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
            res['land'] = Place.country[res['land']]
            res['provinz'] = Place.province[res['provinz']]
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
    def get_autocomplete_entries(cls, ac_field, term):
        """
        queries Splor core edhGeo for list of entries displayed in
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
                'facet.limit': '20',
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


def _get_url_without_pagination_parameters(url):
    """
    removes URL parameters anzahl and start; these get added later in the template again
    with values for pagination
    :param url: current URL as string
    :return: shortened URL as string
    """
    url = re.sub("start=[0-9]*&*", "", url)
    url = re.sub("anzahl=[0-9]*&*", "", url)
    url = re.sub("&&", "&", url)
    return url


def _remove_number_of_hits_from_autocomplete(user_entry):
    """
    removes number of hits from entry string that has been added by autocomplete
    :param user_entry: user entry string with number of hits in parenthesis
    :return: user_entry without number of hits
    """
    user_entry = re.sub("\([0-9]*\)$", "", user_entry).strip()
    return user_entry
