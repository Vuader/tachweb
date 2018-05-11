from luxon import register_resource
from luxon import constants as const
from luxon.exceptions import HTTPNotFound
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon.utils.html import select
from luxon import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon import g
from luxon import js

log = GetLogger(__name__)

g.nav_menu.add('/Admin/News Letter',
               href='/newsletter', tag='newsletter_admin')


@register_resource('GET', '/newsletter', tag='newsletter_admin')
def newsletter(req, resp):
    resp.content_type = TEXT_HTML
    return render_template('tachweb/newsletter.html',
                           title="Newsletter Admin")
