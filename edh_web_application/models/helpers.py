import re


def get_fullname(name):
    """
    exchange short name with fullname of contributing researcher
    :param name: short name as string
    :return: fullname as string
    """
    fullname = {
        'Bachtal': 'Bachtaler',
        'Baeck': 'Bäck',
        'Betterma': 'Bettermann',
        'Cimarost': 'Cimarosti',
        'Daffi': 'Dafferner',
        'frgri': 'Grieshaber',
        'Geiselma': 'Geiselmann',
        'Graef': 'Gräf',
        'Hainzman': 'Hainzmann',
        'Hildebrd': 'Hildebrandt',
        'Hillebrd': 'Hillebrand',
        'Kleinhan': 'Kleinhans',
        'Marchesi': 'Marchesini',
        'Oldenhag': 'Oldenhage',
        'Osnabrue': 'Osnabrück',
        'Vanderbi': 'Vanderbilt',
    }
    if name in fullname:
        return fullname[name]
    else:
        return name


def escape_value(val):
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


def remove_number_of_hits_from_autocomplete(user_entry):
    """
    removes number of hits from entry string that has been added by autocomplete
    :param user_entry: user entry string with number of hits in parenthesis
    :return: user_entry without number of hits
    """
    user_entry = re.sub("\([0-9]*\)$", "", user_entry).strip()
    return user_entry
