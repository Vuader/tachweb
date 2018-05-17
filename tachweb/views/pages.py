from luxon import g
from luxon import GetLogger
from luxon import render_template
from luxon import register
from luxon.constants import TEXT_HTML

log = GetLogger(__name__)

g.nav_menu.add('/Community/Sponsors', href='/rst/project_sponsors')
g.nav_menu.add('/Community/Get involved', href='/rst/get_involved')
g.nav_menu.add('/Media', href='/rst/media')


def view_rst(rst):
    content = render_template("tachweb/%s.rst" % (rst,), rst2html=True)
    title = rst.replace('_', ' ').title()
    return render_template('tachweb/pages.html', title=title, content=content)


@register.resource('GET', '/pyipcalc', cache=14400)
def pyipcalc(req, resp):
    resp.redirect('/rst/pyipcalc')


@register.resource('GET', '/rst/{page}', cache=14400)
def pages(req, resp, page):
    resp.content_type = TEXT_HTML
    return view_rst(page)


@register.resource('GET', '/', cache=14400)
def home(req, resp):
    resp.content_type = TEXT_HTML
    return view_rst('tachyonic_project')
