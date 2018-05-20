import os
import operator

from luxon import g
from luxon import GetLogger
from luxon import register
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon.utils.objects import load


log = GetLogger(__name__)

g.nav_menu.add('/Software',
               href='/software')

g.nav_menu.add('/Roadmap', href='/roadmap')
g.nav_menu.add('/Community/Contributors', href='/contributors')


def projects_docs():
    projects = g.current_request.context['projects']
    docs = {}
    for project in projects:
        docs[project] = []
        for tag in projects[project]['refs']:
            html_root = g.app.path + '/docs/%s_%s' % (project, tag,)
            if os.path.exists(html_root):
                docs[project].append(tag)

        docs[project] = docs[project]

    return docs


def projects(req):
    rst = render_template('tachweb/projects.rst', rst2html=True)
    projects = req.context['projects']
    projects_sorted = sorted(projects.keys())
    versions = {}
    docs = projects_docs()
    for project in projects:
        versions[project] = []
        for tag in projects[project]['refs']:
            versions[project].append(tag)

        versions[project] = ", ".join(versions[project])

    return render_template('tachweb/projects.html',
                           projects=projects,
                           projects_sorted=projects_sorted,
                           versions=versions,
                           docs=docs,
                           rst=rst)


def get_assignees(planning, project=None):
    assignees = []
    for a_project in planning:
        if project is None or a_project['name'] == project:
            for a_column in a_project['columns']:
                for a_card in a_column['cards']:
                    for a_assignee in a_card['assignees']:
                        if a_assignee not in assignees:
                            assignees.append(a_assignee)
    return assignees


def get_projects(planning):
    projects = []
    for a_project in planning:
        projects.append(a_project['name'])

    return projects


def get_project(planning, project=None, assignee=None):
    projects = []
    for a_project in planning:
        assigned = False
        if project is None or a_project['name'] == project:
            view_project = {}
            view_project['name'] = a_project['name']
            view_project['description'] = a_project['description']
            view_project['columns'] = []
            for a_column in a_project['columns']:
                view_columns = {}
                view_columns['name'] = a_column['name']
                view_columns['cards'] = []
                for a_card in a_column['cards']:
                    if assignee is None or assignee in a_card['assignees']:
                        view_columns['cards'].append(a_card)
                        assigned = True
                    elif a_card['title'] == 'Note':
                        view_columns['cards'].append(a_card)
                        assigned = True
                view_project['columns'].append(view_columns)

            if assigned is True:
                projects.append(view_project)

    return projects


@register.resource('GET',
                   '/contributors', cache=14400)
def contributors(req, resp):
    resp.content_type = TEXT_HTML
    return render_template('tachweb/contributors.html',
                           title="Contributors")


@register.resource('GET',
                   '/roadmap', cache=14400)
def roadmap(req, resp):
    resp.content_type = TEXT_HTML

    planning = load(g.app.path + '/planning.pickle')
    planning_as_list = []
    for project in planning:
        planning_as_list.append(planning[project])

    planning_as_list.sort(key=operator.itemgetter('name'))
    planning = planning_as_list

    assignee = req.query_params.get('assignee')
    project = req.query_params.get('project')
    return render_template('tachweb/planning.html',
                           view_projects=get_project(
                               planning,
                               project,
                               assignee),
                           assignee=assignee,
                           assignees=get_assignees(planning),
                           project=project,
                           title='Project Planning',
                           projects=get_projects(planning))


@register.resource('GET',
                   '/', cache=14400)
@register.resource('GET',
                   '/software', cache=14400)
def project(req, resp):
    resp.content_type = TEXT_HTML
    overview = render_template("tachweb/overview.rst", rst2html=True)
    opensource = render_template("tachweb/opensource.rst", rst2html=True)

    return render_template('tachweb/project.html',
                           overview=overview,
                           projects=projects(req),
                           opensource=opensource)
