from luxon.utils.objects import load
from luxon import g


class GitHub(object):
    def pre(self, req, resp):
        try:
            req.context['projects'] = load(g.app.path +
                                           '/projects.pickle')
        except FileNotFoundError:
            req.context['projects'] = {}

        try:
            req.context['news'] = load(g.app.path +
                                       '/events.pickle')
        except FileNotFoundError:
            req.context['news'] = []

        try:
            req.context['team'] = load(g.app.path +
                                       '/team.pickle')
        except FileNotFoundError:
            req.context['team'] = {}
