from luxon.utils.objects import load
from luxon import g


class GitHub(object):
    def pre(self, req, resp):
        try:
            projects = load(g.app.path + '/projects.pickle')
            req.context['projects'] = projects
        except FileNotFoundError:
            req.context['projects'] = {}

        try:
            events = load(g.app.path + '/events.pickle')
            req.context['news'] = events
        except FileNotFoundError:
            req.context['news'] = []
