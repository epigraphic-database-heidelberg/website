from flask import (
    Blueprint, render_template
)

bp = Blueprint('data', __name__)

@bp.route('/data')
def data():
    return render_template('data/index.html', title="Open Data Repository")
