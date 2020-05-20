from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Optional, Regexp
from flask_babel import lazy_gettext as _l


class BibliographySearch(FlaskForm):
    reset = SubmitField(_l('Reset...'))
    submit = SubmitField(_l('Submit...'))
    b_nr = StringField(_l('B-No'), validators=[Optional(), Regexp('^B*[0-9]{1,6}$')])
    autor = StringField(_l('author'))
    titel = StringField(_l('title'))
    publikation = StringField(_l('publication'))
    band = StringField(_l('volume'))
    jahr = StringField(_l('year(s)'))
    seiten = StringField(_l('pages'))
    ort = StringField(_l('town'))
    ae = StringField(_l('ae'))
    cil = StringField(_l('cil'))
    zu_ae = StringField(_l('on_ae'))
    sonstige = StringField(_l('other_corpora'))
    sort = SelectField(_l('sort by'),
                       choices=[('b_nr', _l('B-No')), ('author', _l('author')), ('publication', _l('publication')),
                                ('years', _l('year(s)'))])
    anzahl = SelectField(_l('number of results/page'),
                       choices=[('20', '20'), ('50', '50'), ('100', '100'), ('200', '200')])