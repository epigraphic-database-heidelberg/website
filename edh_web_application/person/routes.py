from flask import render_template
from flask_babel import _
from ..models.Person import Person
from . import bp_people


@bp_people.route('/edh/person/<hd_nr>/<pers_id>', strict_slashes=False)
def detail_view(hd_nr, pers_id):
    """
    route for displaying detail view of person record
    :param hd_nr: HD-No of person record
    :param pers_id: identifier of person record
    :return: html template
    """
    results = Person.query("id:" + hd_nr + "\/" + pers_id)
    if results is None:
        return render_template('person/no_hits.html',
                               title=_("Epigraphic People Database: Detail View"))
    else:
        return render_template('person/detail_view.html',
                               title=_("Epigraphic Person Database: Detail View"),
                               data=results[0])
