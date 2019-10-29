from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, SelectMultipleField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Optional, Regexp, URL


class FotoSearch(FlaskForm):
    reset = SubmitField('Reset...')
    submit = SubmitField('Submit...')
    