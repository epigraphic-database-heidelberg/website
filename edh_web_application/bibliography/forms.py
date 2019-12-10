from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, Regexp
from flask_babel import lazy_gettext as _l


class BibliographySearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    b_nr = StringField(_l('B-No'), validators=[Optional(), Regexp('^B*[0-9]{1,6}$')])
    author = StringField(_l('author'))
    title = StringField(_l('title'))
    publication = StringField(_l('publication'))
    volume = StringField(_l('volume'))
    years = StringField(_l('year(s)'))
    pages = StringField(_l('pages'))
    town = StringField(_l('town'))
    ae = StringField(_l('ae'))
    cil = StringField(_l('cil'))
    on_ae = StringField(_l('on_ae'))
    other_corpora = StringField(_l('other_corpora'))
