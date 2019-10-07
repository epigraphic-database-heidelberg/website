from flask import (
    Blueprint, render_template
)
from flask_babel import _
from edh_web_application.models.Publication import Publication

bp = Blueprint('search_bibliography', __name__)


@bp.route('/bibliographie/suche')
def search_bibliography():
    return render_template('search_bibliography/index.html', title=_("Bibliographic Database: Search"))


@bp.route('/edh/bibliographie/<b_nr>')
def detail_view(b_nr):
    results = Publication.query("b_nr:" + b_nr)
    if results is None:
        return render_template('search_bibliography/detail_view.html', title=_("Epigraphic Bibliography Database: Detail View"))
    else:
        return render_template('search_bibliography/detail_view.html', title=_("Epigraphic Bibliography Database: Detail View"),
                               data=results[0])
