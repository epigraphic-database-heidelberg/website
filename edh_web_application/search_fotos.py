from flask import (
    Blueprint, render_template
)
from flask_babel import _

bp = Blueprint('search_fotos', __name__)


@bp.route('/foto/suche')
def foto_search():
    return render_template('search_fotos/index.html', title=_("Photographic Database: Search"))
