from flask import (
    Blueprint, render_template
)

bp = Blueprint('project', __name__)


@bp.route('/projekt/konzept')
def show_project_concept_page():
    return render_template('project/project_concept.html', title="Project - Concept")


@bp.route('/projekt/geschichte')
def show_project_history_page():
    return render_template('project/project_history.html', title="Project - History")


@bp.route('/projekt/kooperationen')
def show_project_cooperations_page():
    return render_template('project/project_cooperations.html', title="Project - Cooperations")


@bp.route('/projekt/mitarbeiter')
def show_project_team_members_page():
    return render_template('project/project_team_members.html', title="Project - Research Team Members")


@bp.route('/projekt/veranstaltungen')
def show_project_presentations_page():
    return render_template('project/project_presentations.html', title="Project - Events and Presentations")

