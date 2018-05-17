from luxon import register
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon import GetLogger
from luxon.exceptions import AccessDeniedError, HTTPError
from psychokinetic.github import GitHub


log = GetLogger(__name__)


def auth(username, password):
    github = GitHub((username, password,))
    teams = github.teams('TachyonicProject')
    roles = []
    for team in teams:
        id = team['id']
        role = team['name']
        members = github.team_members(id)
        for member in members:
            if member['login'] == username:
                roles.append(role)
    if len(roles) == 0:
        raise AccessDeniedError('Not member of any Tachyonic Project teams')
    return roles


@register.resource(['GET', 'POST'],
                   '/login')
def login(req, resp):
    resp.content_type = TEXT_HTML
    if req.credentials.authenticated:
        resp.redirect(req.app + '/')
        return

    username = req.get_first('username', default=None)
    password = req.get_first('password', default=None)

    error = ''
    if username is not None:
        try:
            roles = auth(username, password)
            req.credentials.new(username)
            req.credentials.roles = roles
            req.user_token = req.credentials.token
            resp.redirect(req.app + '/')
            return
        except HTTPError as e:
            error = e
        except AccessDeniedError as e:
            error = e

    return render_template('tachweb/login.html',
                           error=error, no_side=True)


@register.resource('GET',
                   '/logout')
def logout(req, resp):
    resp.content_type = TEXT_HTML
    req.session.clear()
    resp.redirect(req.app + '/')
