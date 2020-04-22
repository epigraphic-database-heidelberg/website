from flask import render_template

from . import bp_project
from flask_babel import _


@bp_project.route('/projekt/konzept')
def show_project_concept_page():
    return render_template('project/project_concept.html', title=_("Project"), subtitle=_("concept"))


@bp_project.route('/projekt/geschichte')
def show_project_history_page():
    return render_template('project/project_history.html', title=_("Project"), subtitle=_("history"))


@bp_project.route('/projekt/kooperationen')
def show_project_cooperations_page():
    return render_template('project/project_cooperations.html', title=_("Project"), subtitle=_("cooperations"))


@bp_project.route('/projekt/mitarbeiter')
def show_project_team_members_page():
    return render_template('project/project_team_members.html', title=_("Project"), subtitle=_("research team members"))


@bp_project.route('/projekt/veranstaltungen')
def show_project_presentations_page():
    return render_template('project/project_presentations.html', title=_("Project"), subtitle=_("presentations"))


@bp_project.route('/projekt/kontakt')
def show_project_contact_page():
    return render_template('project/project_contact.html', title=_("Project"), subtitle=_("contact"))


@bp_project.route('/projekt/provinzen')
def show_project_provinces_page():
    return render_template('project/project_provinces.html', title=_("Project"), subtitle=_("provinces"))


@bp_project.route('/links')
def links():
    return render_template('project/links.html', title=_("Links"))

