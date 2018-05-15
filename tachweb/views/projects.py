import os
import operator
import mimetypes
import re

from luxon import register_resource
from luxon import constants as const
from luxon.exceptions import HTTPNotFound
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon.utils.html import select
from luxon import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon import g
from luxon.utils.objects import load

log = GetLogger(__name__)

g.nav_menu.add('/Project/About',
               href='/rst/tachyonic_project')
g.nav_menu.add('/Project/Projects',
               href='/projects')
g.nav_menu.add('/Project/Open Source', href='/rst/opensource')
g.nav_menu.add('/Project/Project Plan',
               href='/planning')

g.nav_menu.add('/Documentation/Tutorials',
               href='/sphinx/tutorials/latest/index.html')
g.nav_menu.add('/Documentation/Luxon',
               href='/sphinx/luxon/latest/index.html')
g.nav_menu.add('/Documentation/Psychokinetic',
               href='/sphinx/psychokinetic/latest/index.html')
g.nav_menu.add('/Documentation/InfinityStone',
               href='/sphinx/infinitystone/latest/index.html')
g.nav_menu.add('/Documentation/Netrino',
               href='/sphinx/netrino/latest/index.html')
g.nav_menu.add('/Documentation/Telepahtic',
               href='/sphinx/telepathic/latest/index.html')
g.nav_menu.add('/Documentation/Yoshii',
               href='/sphinx/yoshii/latest/index.html')
g.nav_menu.add('/Documentation/Katalog',
               href='/sphinx/katalog/latest/index.html')
g.nav_menu.add('/Documentation/Kiloquad',
               href='/sphinx/kiloquad/latest/index.html')
g.nav_menu.add('/Documentation/Photonic',
               href='/sphinx/photonic/latest/index.html')
g.nav_menu.add('/Documentation/pyipcalc', href='/rst/pyipcalc')
g.nav_menu.add('/Documentation/Blueprints',
               href='/sphinx/blueprints/latest/index.html')
g.nav_menu.add('/Documentation/DevStack',
               href='/sphinx/devstack/latest/index.html')
g.nav_menu.add('/Documentation/Lab',
               href='/sphinx/tachlab/latest/index.html')


def format_body_only(html):
    html = if_bytes_to_unicode(html)
    body_match = re.compile(r"\<!\-\-DOC\-\-\>.*\<\!\-\-DOC\-\-\>",
                            re.IGNORECASE | re.MULTILINE |
                            re.DOTALL)

    for body in body_match.findall(html):
        return body
    return "No content/body"


@register_resource(['GET', 'POST'],
                   'regex:^/sphinx.*$', cache=14400)
def sphinx(req, resp):
    app_root = g.app_root
    full_path = req.route.strip('/').split('/')[1:]

    if len(full_path) > 0 and full_path[0] in req.context.projects:
        resp.content_type = TEXT_HTML
        name = full_path[0]
        goto = req.get_first('ref')
        if goto is not None:
            return resp.redirect('/sphinx/%s/%s' % (name, goto,))

        project = req.context.projects[name]
        refs = project['refs']
        description = project['description']

        if len(refs) == 0:
            raise HTTPNotFound("Project documentation not found")

        if len(full_path) > 1:
            ref = full_path[1]
        else:
            return resp.redirect('/sphinx/%s/%s/index.html' % (name, refs[0],))

        doc_path = full_path[2:]

        html_root = app_root + '/docs/%s_%s' % (name, ref)

        if len(doc_path) == 0:
            return resp.redirect('/sphinx/%s/%s/index.html' % (name, ref,))
        else:
            path = "/".join(doc_path)

        path = html_root + '/' + path
        if os.path.isfile(path):
            sfile = open(path, 'rb').read()
            resp.content_type = const.APPLICATION_OCTET_STREAM
            mime_type = mimetypes.guess_type(path)
            if mime_type is not None:
                resp.content_type = mime_type[0]
                if mime_type[1] is not None:
                    resp.content_type += ';charset=%s' % mime_type[1]
            if mime_type[0].lower() == 'text/html':
                refs = select('ref', refs, ref, False,
                              'custom-control form-control-sm custom-select',
                              'this.form.submit()')
                sfile = format_body_only(sfile)
                git = "https://github.com/TachyonicProject/%s/tree/%s" % (name,
                                                                          ref,)
                home = '%s/sphinx/%s/%s/index.html' % (req.app, name, ref,)
                description = "%s (%s)" % (description, name,)
                return render_template('tachweb/sphinx.html', refs=refs,
                                       doc=sfile, no_news=True,
                                       project=name, title=description,
                                       description=description,
                                       git=git, home=home)
            else:
                return sfile
        else:
            raise HTTPNotFound('Documentation page not found - possibly' +
                               ' updating')

    else:
        raise HTTPNotFound("Project documentation not found")


def projects_docs():
    app_root = g.app_root
    projects = g.current_request.context.projects
    docs = {}
    for project in projects:
        docs[project] = []
        for tag in projects[project]['refs']:
            html_root = app_root + '/docs/%s_%s' % (project, tag,)
            if os.path.exists(html_root):
                docs[project].append(tag)

        docs[project] = docs[project]

    return docs


@register_resource('GET',
                   '/projects', cache=14400)
def projects(req, resp):
    resp.content_type = TEXT_HTML
    rst = render_template('tachweb/projects.rst', rst2html=True)
    projects = req.context.projects
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


@register_resource('GET',
                   '/project/{project}', cache=14400)
def project(req, resp, project):
    resp.content_type = TEXT_HTML
    project = req.context.projects[project]
    return render_template('tachweb/project.html', project=project)


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


@register_resource('GET',
                   '/planning', cache=14400)
def planning(req, resp):
    resp.content_type = TEXT_HTML

    app = g.app_root

    planning = load(app + '/planning.pickle')
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
