from flask import render_template

from . import bp_data
from flask_babel import _


@bp_data.route('/data')
def data():
    return render_template('data/index.html', title=_("Data"), subtitle=_("Open Data Repository"))


@bp_data.route('/data/api')
def api():
    return render_template('data/api.html', title=_("Data"), subtitle=_("Application Programming Interface (API)"))
