import os
import mimetypes
import re

from luxon import register
from luxon import constants as const
from luxon.exceptions import HTTPNotFound
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon import g
from luxon import db
from tachweb.models.newsletter import NewsList
log = GetLogger(__name__)

g.nav_menu.add('/Community/Newsletter', href='/newsletter')


@register.resource('GET','/newsletter')
def newsletter(req, resp):
    resp.content_type = TEXT_HTML
    return render_template('tachweb/newsletter.html')


@register.resource([ 'GET', 'POST' ],
                   '/subscribe')
def subscribe(req, resp):
    resp.content_type = TEXT_HTML
    if req.method == 'GET':
        return render_template('tachweb/subscribe.html')
    elif req.method == 'POST':
        data = req.form_dict
        if not data['email']:
            content = '<div class="alert alert-danger">'
            content += 'Email is required</div>'
            return render_template('tachweb/subscribe.html', error=content)
        data['name'] = '' if not data['name'] else data['name'];
        nl = NewsList()
        nl.update(data)
        nl.commit()
        return render_template('tachweb/subscribed.html', name=data['name'],
                                    token=nl['id'])

@register.resource('GET','/unsubscribe/{uuid}')
def unsubscribe(req, resp, uuid):
    resp.content_type = TEXT_HTML
    sql = 'DELETE FROM newslist WHERE id=?'
    with db() as cur:
        cur.execute(sql, (uuid,))
        cur.commit()
    return render_template('tachweb/unsubscribed.html')

