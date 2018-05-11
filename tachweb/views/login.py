import pam

from luxon import register_resource
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon import GetLogger
from luxon.utils.system import get_login_groups

log = GetLogger(__name__)

pam_auth = pam.pam()


@register_resource(['GET', 'POST'],
                   '/login')
def login(req, resp):
    resp.content_type = TEXT_HTML
    if req.credentials.authenticated:
        resp.redirect('/')
        return

    username = req.get_first('username', default=None)
    password = req.get_first('password', default=None)

    error = ''
    if username is not None:
        if pam.authenticate(username, password):
            req.credentials.new(username)
            req.credentials.roles = get_login_groups(username)
            req.user_token = req.credentials.token
            resp.redirect('/')
            return
        else:
            error = "Bad credentials"

    return render_template('tachweb/login.html',
                           error=error)


@register_resource('GET',
                   '/logout')
def logout(req, resp):
    resp.content_type = TEXT_HTML
    req.session.clear()
    resp.redirect('/')
