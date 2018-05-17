from luxon import register
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon import GetLogger
from luxon import g

log = GetLogger(__name__)

g.nav_menu.add('/Admin/News Letter',
               href='/newsletter', tag='newsletter_admin')


@register.resource('GET', '/newsletter', tag='newsletter_admin')
def newsletter(req, resp):
    resp.content_type = TEXT_HTML
    return render_template('tachweb/newsletter.html',
                           title="Newsletter Admin")
