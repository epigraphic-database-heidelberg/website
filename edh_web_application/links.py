from flask import (
    Blueprint, render_template
)

bp = Blueprint('links', __name__)

@bp.route('/links')
def links():
    return render_template('links/index.html', title="Links")
