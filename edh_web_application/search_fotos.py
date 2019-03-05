from flask import (
    Blueprint, render_template
)

bp = Blueprint('search_fotos', __name__)

@bp.route('/foto/suche')
def foto_search():
    return render_template('search_fotos/index.html', title="Photographic Database: Search")
