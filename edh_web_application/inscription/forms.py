import collections

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, BooleanField

from ..models.Inscription import Inscription
from ..models.Place import Place


def get_option_list_values_country():
    countries_dict = collections.OrderedDict()
    countries_dict = Place.country
    countries_list = []
    for k, v in countries_dict.items():
        countries_list.append((k, v))
    return countries_list


def get_option_list_values_country_de():
    country_de_list = Place.country_de
    country_de_list_return = []
    for c in country_de_list:
        c_name = _l(str("land-"+c))
        country_de_list_return.append((c, c_name))
    return country_de_list_return


def get_option_list_values_country_en():
    country_de_list = Place.country_en
    country_de_list_return = []
    for c in country_de_list:
        c_name = _l(str("land-"+c))
        country_de_list_return.append((c, c_name))
    return country_de_list_return


def get_option_list_values_province():
    province_list = Place.province
    province_list_return = []
    for prov in province_list:
        prov_name = _l(str(prov))
        province_list_return.append((prov, prov_name))
    return province_list_return


def get_option_list_values_hist_periods():
    hist_period_list = Inscription.historic_periods
    return hist_period_list


class InscriptionSearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    hd_nr = StringField(_l('HD-No.'))
    provinz = SelectMultipleField(_l('province'), choices=get_option_list_values_province())
    fo_antik = StringField(_l('ancient find spot'))
    fo_modern = StringField(_l('modern find spot'))
    fundstelle = StringField(_l('find spot'))
    literatur = StringField(_l('literature'))
    dat_jahr_a = StringField(_l('from'))
    dat_jahr_e = StringField(_l('until'))
    dat_erweitert = BooleanField(_l('extended'))
    hist_periods = SelectField(_l('historic period'), choices=get_option_list_values_hist_periods())
    atext1 = StringField(_l('atext1'))
    atext2 = StringField(_l('atext2'))
    bool = SelectField(_l('bool'), choices=[('AND', _l('AND')), ('OR', _l('OR')), ('AND NOT', _l('AND NOT'))])

    sort = SelectField(_l('sort by'),
                       choices=[('HD-No.', _l('HD-No.')), ('provinz', _l('province')), ('land', _l('country')),
                                ('fo_antik', _l('ancient find spot')),
                                ('fo_modern', _l('modern find spot')), ('fundstelle', _l('find spot')),
                                (_l('type of inscription sort'), _l('type of inscription')),
                                (_l('type of monument sort'), _l('type of monument')),
                                (_l('material sort'), _l('material')),
                                (_l('date from sort'), _l('date from')),
                                (_l('date to sort'), _l('date to')),
                                ])
    anzahl = SelectField(_l('number of results/page'),
                         choices=[('20', '20'), ('50', '50'), ('100', '100'), ('200', '200')])


class InscriptionSearchDe(InscriptionSearch):
    land = SelectMultipleField(_l('country'), choices=get_option_list_values_country_de())


class InscriptionSearchEn(InscriptionSearch):
    land = SelectMultipleField(_l('country'), choices=get_option_list_values_country_en())
