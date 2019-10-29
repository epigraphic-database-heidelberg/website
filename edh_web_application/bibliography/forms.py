from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, SelectMultipleField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Optional, Regexp, URL


class BibliographySearch(FlaskForm):
    reset = SubmitField('Reset...')
    submit = SubmitField('Submit...')
    b_nr = StringField('B-No', validators=[Optional(), Regexp('^B*[0-9]{1,6}$')])
    author = StringField('author')
    title = StringField('title')
    publication = StringField('publication')
    volume = StringField('volume')
    years = StringField('year(s)')
    pages = StringField('pages')
    town = StringField('town')
    ae = StringField('ae')
    cil = StringField('cil')
    on_ae = StringField('on_ae')
    other_corpora = StringField('other_corpora')
