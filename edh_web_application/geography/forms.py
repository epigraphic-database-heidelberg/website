from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import Optional, Regexp

from ..models.Place import Place


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


class GeographySearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    geo_id = StringField(_l('Geo-ID'), validators=[Optional(), Regexp('^[0-9]{1,6}$')])
    provinz = SelectMultipleField(_l('province'), choices=get_option_list_values_province())
    fo_antik = StringField(_l('ancient find spot'))
    fo_modern = StringField(_l('modern find spot'))
    fundstelle = StringField(_l('find spot'))
    region = StringField(_l('verw_bezirk'))
    kommentar = StringField(_l('comment'))
    pleiades_id = IntegerField('Pleiades ID')
    pleiades_id_1 = IntegerField(_l('Pleiades ID 1'))
    pleiades_id_2 = IntegerField(_l('Pleiades ID 2'))
    geonames_id = IntegerField('Geonames ID')
    geonames_id_1 = IntegerField(_l('Geonames ID 1'))
    geonames_id_2 = IntegerField(_l('Geonames ID 2'))
    tm_geo_id = IntegerField(_l('Trismegistos Geo ID'))
    bearbeitet_abgeschlossen = BooleanField(_l('completed'))
    bearbeitet_provisorisch = BooleanField(_l('provisional'))
    bearbeiter = StringField(_l('responsible individual'))
    sort = SelectField(_l('sort by'),
                       choices=[('Geo-ID', ('Geo-ID')), ('provinz', _l('province')), ('land', _l('country')),
                                ('fo_antik', _l('ancient find spot')),
                                ('fo_modern', _l('modern find spot')), ('fundstelle', _l('find spot')),
                                ('verw_bezirk', _l('verw_bezirk'))])
    anzahl = SelectField(_l('number of results/page'),
                         choices=[('20', '20'), ('50', '50'), ('100', '100'), ('200', '200')])


class GeographySearchDe(GeographySearch):
    land = SelectMultipleField(_l('country'), choices=get_option_list_values_country_de())


class GeographySearchEn(GeographySearch):
    land = SelectMultipleField(_l('country'), choices=get_option_list_values_country_en())
