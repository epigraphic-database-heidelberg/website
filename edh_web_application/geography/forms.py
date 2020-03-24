from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import Optional, Regexp
from flask_babel import lazy_gettext as _l
from ..models.Place import Place
import collections


def get_option_list_values_country():
    countries_dict = collections.OrderedDict()
    countries_dict = Place.country
    countries_list = []
    for k, v in countries_dict.items():
        countries_list.append((k, v))
    return countries_list


class GeographySearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    geo_id = StringField(_l('Geo-ID'), validators=[Optional(), Regexp('^[0-9]{1,6}$')])
    province = StringField(_l('province'))
    country = SelectField(_l('country'), choices=get_option_list_values_country())
    ancient_find_spot = StringField(_l('ancient find spot'))
    modern_find_spot = StringField(_l('modern find spot'))
    find_spot = StringField(_l('find spot'))
    region = StringField(_l('verw_bezirk'))
    comment = StringField(_l('comment'))
    pleiades_id_1 = IntegerField(_l('Pleiades ID 1'))
    pleiades_id_2 = IntegerField(_l('Pleiades ID 2'))
    geonames_id_1 = IntegerField(_l('Geonames ID 1'))
    geonames_id_2 = IntegerField(_l('Geonames ID 2'))
    tm_geo_id = IntegerField(_l('Trismegistos Geo ID'))
    sort = SelectField(_l('sort by'),
                       choices=[('geo_id', ('Geo-ID')), ('province', _l('province')), ('country', _l('country')),
                                ('ancient_find_spot', _l('ancient find spot')), ('modern_find_spot', _l('modern find spot')), ('find_spot', _l('find spot')), ('region', _l('verw_bezirk'))])
    anzahl = SelectField(_l('number of results/page'),
                         choices=[('20', '20'), ('50', '50'), ('100', '100'), ('200', '200')])
