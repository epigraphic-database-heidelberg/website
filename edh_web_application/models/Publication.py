import pysolr
import re
from flask import current_app
from flask import request
from babel.numbers import format_decimal
from babel.dates import format_date
from datetime import datetime
import collections


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
    def query(cls, query_string, *args, **kwargs):
        """
        queries Solr core
        :return: list of Publication instances
        """
        start = 0  # index number of first record to retrieve
        rows = 20  # number of records to retrieve
        sort = "b_nr asc"  # default
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
        if request.args.get('sort') in ['autor', 'publikation', 'jahr']:
            sort = request.args.get('sort') + "_sort asc"
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search(query_string, **{'rows': rows, 'start': start, 'sort': sort, 'defType': 'edismax'})
        if len(results) == 0:
            return None
        else:
            number_of_hits = results.hits
            query_params = _get_query_params(request.args)
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

        if 'b_nr' in form and form['b_nr'] != "":
            b_nr = form['b_nr']
            # check if b_nr is valid pattern
            # correct if necessary/possible
            b_nr = Publication.format_b_nr(b_nr)
            query_string = "b_nr:" + b_nr + " " + logical_operater + " "

        if 'autor' in form and form['autor'] != "":
            if re.search("\([0-9]*\)$", form['autor']):
                query_string += "autor_ac:" + _escape_value(
                    _remove_number_of_hits_from_autocomplete(form['autor'])) + " " + logical_operater + " "
            else:
                query_string += "autor_ac:*" + _escape_value(form['autor']) + "* " + logical_operater + " "

        if 'titel' in form and form['titel'] != "":
            query_string += "titel_str_ci:*" + re.sub(" ","\ ",form['titel']) + "* " + logical_operater + " "

        if 'publikation' in form and form['publikation'] != "":
            query_string += "publikation_str_ci:*" + _escape_value(_remove_number_of_hits_from_autocomplete(form['publikation'])) + "* " + logical_operater + " "

        if 'band' in form and form['band'] != "":
            query_string += "band:" + _escape_value(form['band']) + " " + logical_operater + " "

        if 'jahr' in form and form['jahr'] != "":
            query_string += "jahr:" + _escape_value(form['jahr']) + " " + logical_operater + " "

        if 'seiten' in form and form['seiten'] != "":
            query_string += "seiten:" + _escape_value(form['seiten']) + " " + logical_operater + " "

        if 'ort' in form and form['ort'] != "":
            query_string += "ort:*" + re.sub(" ", "\ ", form['ort']) + "* " + logical_operater + " "

        if 'ae' in form and form['ae'] != "":
            query_string += "ae:*" + _escape_value(form['ae']) + "* " + logical_operater + " "

        if 'zu_ae' in form and form['zu_ae'] != "":
            query_string += "zu_ae:*" + _escape_value(form['zu_ae']) + "* " + logical_operater + " "

        if 'cil' in form and form['cil'] != "":
            query_string += "cil:*" + _escape_value(form['cil']) + "* " + logical_operater + " "

        if 'sonstige' in form and form['sonstige'] != "":
            query_string += "sonstigeCorpora:*" + _escape_value(form['sonstige']) + "* " + logical_operater + " "
        # remove last " AND"
        query_string = re.sub(" " + logical_operater + " $", "", query_string)
        return query_string

    @classmethod
    def get_number_of_records(cls):
        """
        returns number of bibliographical records from Solr Core edhBiblio
        :return: number of bibliographical records (str)
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search("*:*")
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_number_of_hits_for_query(cls, query_string):
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search(query_string)
        return format_decimal(results.hits, locale='de_DE')

    @classmethod
    def get_date_of_last_update(cls):
        """
        returns date of latest update to Solr Core edhBiblio
        :return: date of latest update
        """
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
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
        solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
        results = solr.search("*:*", sort="datum desc", rows=50)
        for res in results:
            dt = datetime.strptime(res['datum'], '%Y-%m-%d').date()
            res['datum'] = format_date(dt, 'd. MMM YYYY', locale='de_DE')
        return results

    @classmethod
    def group_results_by_date(cls, results):
        """
        groups last 50 entries in bibliographic database by date
        :param results: list of bibliographic entries
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
        queries Splor core edhBiblio for list of entries displayed in
        autocomplete fields of Biblio form
        :param ac_field: field to facet
        :param term: querystring
        :return: list of relevant field values
        """
        if re.match("[a-zA-Z]+",term):
            params = {
                'facet': 'on',
                'facet.field': ac_field + '_ac',
                'facet.sort': 'count',
                'facet.mincount': 1,
                'facet.limit': '20',
                'rows': '0',
            }
            query = ac_field + ":" + term
            solr = pysolr.Solr(current_app.config['SOLR_BASE_URL'] + 'edhBiblio')
            results = solr.search(query, **params)
            # concat results and counts as string
            return_list = []
            is_first_element = True
            first_item = ""
            for entry in results.facets['facet_fields'][ac_field + "_ac"]:
                if is_first_element:
                    first_item = entry
                    is_first_element = False
                    continue
                else:
                    is_first_element = True
                    return_list.append(first_item + " (" + str(entry) + ")")
            return return_list

    @classmethod
    def format_b_nr(cls, b_nr):
        """
        formats user entered b_nr string into valid B-No like 'B004711'
        :param b_nr: user entered string of B-No
        :return: string of valid B-No, like 'B004711'
        """
        b_no_pattern = re.compile(r"^B\d{6}$")
        if b_no_pattern.match(b_nr):
            return b_nr
        b_nr = re.sub("^[Bb]", "", b_nr, re.IGNORECASE)
        b_nr = b_nr.lstrip("0")
        b_nr = b_nr.zfill(6)
        return "B" + b_nr


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
    val = re.sub("\.", "\.", val)
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
    url = re.sub(request.url_root, "", url)
    return "/" + url


def _remove_number_of_hits_from_autocomplete(user_entry):
    """
    removes number of hits from entry string that has been added by autocomplete
    :param user_entry: user entry string with number of hits in parenthesis
    :return: user_entry without number of hits
    """
    user_entry = re.sub("\([0-9]*\)$", "", user_entry).strip()
    return user_entry


def _get_query_params(args):
    """
    creates dictionary of search params for displaying on
    search result page
    :param args: request.args
    :return: dictionary with all params of query
    """
    result_dict = {}
    for key in args:
        if key not in ('anzahl', 'sort', 'start', 'view') and args[key] != "":
            result_dict[key] = args[key]
    return result_dict


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
