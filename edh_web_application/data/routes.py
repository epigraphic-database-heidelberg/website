from flask import render_template, send_from_directory, send_file

from . import bp_data
from flask_babel import _


@bp_data.route('/data', strict_slashes=False)
def data():
    return render_template('data/index.html', title=_("Data"), subtitle=_("Open Data Repository"))


@bp_data.route('/data/api', strict_slashes=False)
def api():
    return render_template('data/api.html', title=_("Data"), subtitle=_("Application Programming Interface (API)"))


@bp_data.route('/data/download/<filename>', strict_slashes=False)
def download_file(filename):
    print(filename)
    return send_from_directory('data/files/',filename,
                            as_attachment=True)


@bp_data.route('/data/download', strict_slashes=False)
def download():
    return render_template('data/download.html', title=_("Data"), subtitle=_("Download Data Dumps"))
