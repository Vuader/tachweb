import email

from luxon import register
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon import GetLogger
from luxon import g
from luxon import sendmail
from luxon import db
from luxon.utils.mail import format_msg
from datetime import datetime

log = GetLogger(__name__)

g.nav_menu.add('/Admin/News Letter',
               href='/newsletter-admin', tag='newsletter_admin')


@register.resource('GET', '/newsletter-admin', tag='newsletter_admin')
def newsletter(req, resp):
    resp.content_type = TEXT_HTML
    with db() as conn:
        r = conn.execute('SELECT * FROM newsletters')
    return render_template('tachweb/newsletter_admin.html',
                           title="Newsletter Admin",
                           newsletters=r)


@register.resource('GET', '/send/{id}', tag='newsletter_admin')
def send_newsletter(req, resp, id):
    with db() as conn:
        result = conn.execute('SELECT message FROM newsletters WHERE id=?',
                              (id,))
    msg = result['message']
    msg = email.message_from_string(msg)
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%B")
    html_template = render_template('tachweb/email.html',
                                    subject=msg['Subject'],
                                    year=year,
                                    month=month)
    text_template = render_template('tachweb/email.txt',
                                    subject=msg['Subject'],
                                    year=year,
                                    month=month)
    with db() as conn:
        results = conn.execute('SELECT * FROM newslist')
        send_succeeded = False
        for rcpt in results:
            to = "%s <%s>" % (rcpt['name'], rcpt['email'],)
            new = format_msg(msg,
                             html_template=html_template,
                             text_template=text_template,
                             email_from='no-reply@tachyonic.org',
                             email_to=to,
                             multipart=True,
                             id=rcpt['id'],
                             name=rcpt['name'])
            try:
                sendmail('no-reply@tachyonic.org', to, msg=new)
                send_succeeded = True
            except Exception as e:
                log.critical('Failed to send to %s (%s)' % (rcpt, e,))

        if send_succeeded:
            sql = 'UPDATE newsletters SET last_sent=? WHERE id=?'
            conn.execute(sql,(datetime.now(),id))

    return newsletter(req,resp)


@register.resource('GET', '/view/{id}', tag='newsletter_admin')
def preview_newsletter(req, resp, id):
    resp.content_type = TEXT_HTML
    with db() as conn:
        r = conn.execute('SELECT message FROM newsletters WHERE id=?',(id,))
        msg = email.message_from_string(r['message'])
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == "text/html":
                return part.get_payload(decode=True)
