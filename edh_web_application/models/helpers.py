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
