from flask import render_template

from . import bp_data
from flask_babel import _


@bp_data.route('/data')
def data():
    return render_template('data/index.html', title=_("Open Data Repository"))
