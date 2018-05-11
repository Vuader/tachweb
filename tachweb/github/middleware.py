import operator
from luxon.utils.objects import load
from luxon import g
from luxon.utils.timezone import utc


class GitHub(object):
    def pre(self, req, resp):
        app = g.app_root
        try:
            planning = load(app + '/planning.pickle')
            planning_as_list = []
            for project in planning:
                planning_as_list.append(planning[project])

            planning_as_list.sort(key=operator.itemgetter('name'))
            req.context.planning = planning_as_list
        except FileNotFoundError:
            req.context.planning = []

        try:
            projects = load(app + '/projects.pickle')
            events = load(app + '/events.pickle')
            req.context.projects = projects
            req.context.news = events
        except FileNotFoundError:
            req.context.projects = {}
            req.context.news = []
