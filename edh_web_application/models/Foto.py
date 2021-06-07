import collections
import re
from datetime import datetime

import pysolr
from babel.dates import format_date
from babel.numbers import format_decimal
from flask import current_app
from flask import request
from flask_babel import lazy_gettext as _l

from edh_web_application.models.Place import Place
from edh_web_application.models.helpers import get_fullname, escape_value, remove_number_of_hits_from_autocomplete


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

    # dict of localized sort paramter values
    sort_param_values = {
        "f_nr": _l('f_nr'),
        "provinz": _l('provinz'),
        "land": _l('land'),
        "fo_antik": _l('fo_antik'),
        "fo_modern": _l('fo_modern'),
        "aufbewahrung": _l('aufbewahrung'),
        "hd_nr": _l('hd_nr'),
        "cil": _l('cil'),
        "ae": _l('ae'),
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
            "inschriften_fotos": None
        }
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        self.f_nr = f_nr
        self.bearbeiter = get_fullname(bearbeiter)
        self.datum = datum

    @classmethod
    def query(cls, query_string, *args, **kwargs):
        """
        queries Solr core
        :return: list of Foto instances
        """
        start = 0  # index number of first record to retrieve
        rows = 20  # number of records to retrieve
        sort = "f_nr asc"  # default
        hits = kwargs.get('hits', None)
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
        if request.args.get('sort') in ['cil', 'ae']:
            sort = request.args.get('sort') + "_sort asc"
        elif request.args.get('sort') in ['fo_antik', 'fo_modern', 'aufbewahrung']:
            sort = request.args.get('sort') + "_str asc"
        elif request.args.get('sort') == "provinz":
            sort = "provinz asc"
        elif request.args.get('sort') == "land":
            from flask import session
            if session.get('lang'):
                sort = "land_sort_" + session.get('lang') + " asc"
            else:
                sort = "land_sort_en asc"
        elif request.args.get('sort') == "hd_nr":
            sort = request.args.get('sort') + " asc"
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
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
                    if key not in ('f_nr', 'bearbeiter', 'datum'):
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
                    elif key == 'bearbeiter':
                        bearbeiter = get_fullname(result['bearbeiter'].lower().capitalize())
                    elif key == 'hd_nr':
                        props['inschriften_fotos'] = _get_fotos_of_inscription(result['hd_nr'], result['f_nr'])
                publ = Foto(result['f_nr'],
                                   bearbeiter,
                                   result['datum'],
                                   **props
                                   )
                query_result.append(publ)
            return {"metadata": {"start": start, "rows": rows, "number_of_hits": number_of_hits,
                                 "url_without_pagination_parameters": _get_url_without_pagination_parameters(
                                     request.url), "url_without_sort_parameter": _get_url_without_sort_parameter(
                    request.url), "url_without_view_parameter": _get_url_without_view_parameter(
                    request.url), "query_params": query_params},
                    "items": query_result}

    @classmethod
    def create_query_string(cls, form):
        """
        creates solr query based on user data entered into search mask
        :param form: ImmutableMultiDict of GET params
        :return: query_string
        """
        logical_operater = "AND"
        query_string = ""
        if 'f_nr' in form and form['f_nr'] != "":
            f_nr = form['f_nr']
            f_nr = re.sub(r'F0*?', r'', f_nr, flags=re.IGNORECASE)
            if re.match(r'^\d*$', f_nr):
                f_nr = "F" + "{:06d}".format(int(f_nr))
            query_string = "f_nr:" + f_nr + " " + logical_operater + " "
        else:
            query_string = "f_nr:* " + logical_operater + " "

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

        if 'aufbewahrung' in form and form['aufbewahrung'] != "":
            if re.search("\([0-9]*\)$", form['aufbewahrung']):
                query_string += 'aufbewahrung_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['aufbewahrung'])) + '" ' + logical_operater + ' '
            else:
                query_string += "aufbewahrung_ci:*" + escape_value(form['aufbewahrung']) + "* " + logical_operater + " "

        if 'vorlage' in form and form['vorlage'] != "":
            if re.search("\([0-9]*\)$", form['vorlage']):
                query_string += 'neg_nr_ci:"' + escape_value(
                    remove_number_of_hits_from_autocomplete(form['vorlage'])) + '" ' + logical_operater + ' '
            else:
                query_string += "neg_nr_ci:" + escape_value(form['vorlage']) + " " + logical_operater + " "

        if 'aufnahme_jahr' in form and form['aufnahme_jahr'] != "":
            query_string += "aufnahme_jahr:" + escape_value(form['aufnahme_jahr']) + " " + logical_operater + " "

        if 'qualitaet' in form and form['qualitaet'] != "":
            if form['qualitaet'].isnumeric():
                query_string += "qualitaet:" + escape_value(form['qualitaet']) + " " + logical_operater + " "

        if 'ae' in form and form['ae'] != "":
            query_string += "ae_ci:*" + escape_value(form['ae']) + "* " + logical_operater + " "

        if 'cil' in form and form['cil'] != "":
            query_string += "cil_ci:*" + escape_value(form['cil']) + "* " + logical_operater + " "

        if 'andere' in form and form['andere'] != "":
            query_string += "andere_ci:*" + escape_value(form['andere']) + "* " + logical_operater + " "

        if 'kommentar' in form and form['kommentar'] != "":
            query_string += "kommentar_ci:*" + escape_value(form['kommentar']) + "* " + logical_operater + " "

        if 'hd_nr' in form and form['hd_nr'] != "":
            hd_nr = form['hd_nr']
            hd_nr = re.sub(r'HD0*?', r'', hd_nr, flags=re.IGNORECASE)
            if re.match(r'^\d*$', hd_nr):
                hd_nr = "HD" + "{:06d}".format(int(hd_nr))
            query_string += "hd_nr:" + hd_nr + " " + logical_operater + " "

        # remove last " AND"
        query_string = re.sub(" " + logical_operater + " $", "", query_string)
        return query_string

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of fotographic records from Solr Core edhFoto
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

    @classmethod
    def get_number_of_hits_for_query(cls, query_string):
        """
        returns number of hits for given query
        :param query_string: Solr query string
        :return:
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
        results = solr.search(query_string)
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_autocomplete_entries(cls, ac_field, term, hits):
        """
        queries Solr core edhFoto for list of entries displayed in
        autocomplete fields of form
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
            solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
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
    def last_updates(cls):
        """
        return last 50 entries that have been updated
        :return: list of 50 entries
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
        results = solr.search("*:*", sort="datum desc", rows=50)
        for res in results:
            fragezeichen = ""
            land = res['land']
            if land == '??':
                land = '?'
                fragezeichen = '?'
            elif res['land'][-1] == "?":
                fragezeichen = "?"
                land = re.sub("\\?", "", res['land'])
            res['land'] = Place.country[land] + fragezeichen
            fragezeichen = ""
            provinz = res['provinz']
            if res['provinz'][-1] == "?":
                fragezeichen = "?"
                provinz = re.sub("\\?", "", res['provinz'])
            res['provinz'] = Place.province_dict[provinz] + fragezeichen
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            res['datum'] = format_date(dt, 'd. MMM YYYY', locale='de_DE')
        return results

    @classmethod
    def group_results_by_date(cls, results):
        """
        groups last 50 entries in foto database by date
        :param results: list of foto entries
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
    def get_json_for_foto_record(cls, f_nr):
        record = Foto.query("f_nr:" + f_nr)
        if len(record) > 0 and 'items' in record:
            for item in record['items']:
                item_dict = {'id': f_nr,
                             'uri': current_app.config['HOST'] + "/edh/foto/" + f_nr,
                             'iiif_manifest_uri': current_app.config['HOST'] + "/iiif/edh/" + f_nr + ".manifest.json",
                             'last_update': item.datum,
                             'responsible_individual': item.bearbeiter,
                             }
                if item.fo_antik:
                    item_dict['findspot_ancient'] = item.fo_antik
                if item.fo_modern:
                    item_dict['findspot_modern'] = item.fo_modern
                if item.provinz:
                    item_dict['province'] = item.provinz
                if item.land:
                    item_dict['country'] = item.land
                if item.aufbewahrung:
                    item_dict['present_location'] = item.aufbewahrung
                if item.aufnahme_jahr:
                    item_dict['year_of_foto'] = item.aufnahme_jahr
                if item.cil:
                    item_dict['cil'] = item.cil
                if item.ae:
                    item_dict['ae'] = item.ae
                if item.andere:
                    item_dict['other_literature'] = item.andere
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
    url = re.sub("&&", "&", url)
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
    removes URL parameter view & start; these get added later in the template again
    in dialog "view"
    :param url: current URL as string
    :return: shortened URL as string
    """
    url = re.sub("view=table|list", "", url)
    url = re.sub("view=.*?&*", "", url)
    url = re.sub("start=.*?&", "", url)
    url = re.sub("&{2,}", "&", url)
    url = re.sub(request.url_root, "", url)
    return "/" + url


def _get_fotos_of_inscription(hd_nr, f_nr):
    """
    returns list of other fotos of given inscription + F-No combination
    :param hd_nr: HD-No of inscription
    :param f_nr: F-No of image to exclude from list of images
    :return: list of F-Nos of inscription
    """
    list_of_fotos = []
    solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhFoto')
    results = solr.search("hd_nr:"+hd_nr+" AND NOT f_nr:" + f_nr)
    for res in results:
        list_of_fotos.append(res['f_nr'])
    return list_of_fotos


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
        elif key == 'vorlage' and args['vorlage'] != "":
            result_dict['original image'] = args[key]
        elif key == 'aufnahme_jahr' and args['aufnahme_jahr'] != "":
            result_dict['date of photograph'] = args[key]
        elif key == 'qualitaet' and args['qualitaet'] != "":
            result_dict['quality'] = args[key]
        elif key == 'andere' and args['andere'] != "":
            result_dict['other literature'] = args[key]
        elif key == 'kommentar' and args['kommentar'] != "":
            result_dict['commentary'] = args[key]
        elif key not in ('anzahl', 'sort', 'start', 'view', 'bearbeitet_abgeschlossen', 'bearbeitet_provisorisch') and args[key] != "":
            result_dict[key] = re.sub("\([0-9]+\)", "", args[key])
    if 'provinz' in result_dict:
        result_dict['provinz'] = re.sub(", $", "", result_dict['provinz'])
    if 'land' in result_dict:
        result_dict['land'] = re.sub(", $", "", result_dict['land'])
    if len(result_dict) == 0:
        result_dict['F-Nr'] = '*'
    return result_dict
