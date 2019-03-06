from flask import (
    Blueprint, render_template
)
from flask_babel import _

bp = Blueprint('search_bibliography', __name__)


@bp.route('/bibliographie/suche')
def search_bibliography():
    return render_template('search_bibliography/index.html', title=_("Bibliographic Database: Search"))
