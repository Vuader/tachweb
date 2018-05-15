from luxon.utils.objects import load
from luxon import g


class GitHub(object):
    def pre(self, req, resp):
        app = g.app_root

        try:
            projects = load(app + '/projects.pickle')
            req.context.projects = projects
        except FileNotFoundError:
            req.context.projects = {}

        try:
            events = load(app + '/events.pickle')
            req.context.news = events
        except FileNotFoundError:
            req.context.news = []
