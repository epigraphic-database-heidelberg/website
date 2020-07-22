import collections

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import Optional, Regexp

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


class FotoSearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    f_nr = StringField(_l('F-number'), validators=[Optional(), Regexp('^[0-9]{1,6}$')])
    provinz = SelectMultipleField(_l('province'), choices=get_option_list_values_province())
    land = SelectMultipleField(_l('country'), choices=get_option_list_values_country_de())
    fo_antik = StringField(_l('ancient find spot'))
    fo_modern = StringField(_l('modern find spot'))
    aufbewahrung = StringField(_l('present location'))
    vorlage = StringField(_l('original image'))
    aufnahme_jahr = StringField(_l('date of photograph'))
    qualitaet = IntegerField(_l('quality'))
    cil = IntegerField(_l('cil'))
    ae = IntegerField(_l('ae'))
    andere = IntegerField(_l('other literature'))
    kommentar = IntegerField(_l('commentary'))
    hd_nr = IntegerField(_l('HD-No.'))
    datum = StringField(_l('Date'))
    bearbeiter = StringField(_l('responsible individual'))
    aufschrift = StringField(_l('Label'))
    sort = SelectField(_l('sort by'),
                       choices=[('f_nr', _l('F-number')),
                                ('provinz', _l('province')),
                                ('land', _l('country')),
                                ('fo_antik', _l('ancient find spot')),
                                ('fo_modern', _l('modern find spot')),
                                ('aufbewahrung', _l('present location')),
                                ('hd_nr', _l('HD-No.')),
                                ('CIL', ('CIL')),
                                ('AE', 'AE')])
    anzahl = SelectField(_l('number of results/page'),
                         choices=[('20', '20'), ('50', '50'), ('100', '100'), ('200', '200')])
