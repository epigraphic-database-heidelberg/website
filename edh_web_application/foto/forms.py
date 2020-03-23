from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import Optional, Regexp
from flask_babel import lazy_gettext as _l
from ..models.Foto import Foto
import collections


def get_option_list_values_country():
    countries_dict = collections.OrderedDict()
    countries_dict = Foto.country
    countries_list = []
    for k, v in countries_dict.items():
        countries_list.append((k, v))
    return countries_list


class FotoSearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    f_id = StringField(_l('F-number'), validators=[Optional(), Regexp('^[0-9]{1,6}$')])
    province = StringField(_l('province'))
    country = SelectField(_l('country'), choices=get_option_list_values_country())
    ancient_find_spot = StringField(_l('ancient find spot'))
    modern_find_spot = StringField(_l('modern find spot'))
    present_location = StringField(_l('present location'))
    original_image = StringField(_l('original image'))
    date_of_photograph = StringField(_l('date of photograph'))
    quality = IntegerField(_l('quality'))
    cil = IntegerField(_l('cil'))
    ae = IntegerField(_l('ae'))
    other_literature = IntegerField(_l('other literature'))
    commentary = IntegerField(_l('commentary'))
    hd_nr = IntegerField(_l('HD-No.'))
