from flask import (
    Blueprint, render_template
)
from flask_babel import _

bp = Blueprint('data', __name__)


@bp.route('/data')
def data():
    return render_template('data/index.html', title=_("Open Data Repository"))
