from flask import (
    Blueprint, render_template
)
from flask_babel import _

bp = Blueprint('links', __name__)


@bp.route('/links')
def links():
    return render_template('links/index.html', title=_("Links"))
