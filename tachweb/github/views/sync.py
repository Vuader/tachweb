import traceback
import operator
from time import sleep

from luxon import g
from luxon import GetLogger
from luxon.utils.venv import create as create_env
from luxon.utils.objects import save, load
from luxon.utils.objects import object_name
from luxon.utils.files import exists, mkdir, joinpath
from luxon.exceptions import ExecuteError
from luxon.utils.timezone import utc, now, format_iso8601
from luxon import register
from psychokinetic.github import GitHub

from tachweb.github.version import version_order
from tachweb.github.views.utils import (build_doc,
                                        build_venv,
                                        clone,
                                        handle_error,
                                        updated)


log = GetLogger()


@register.resource('GITHUB', '/sync')
def github(req, resp):
    root_path = g.app.path
    mkdir(joinpath(root_path, 'github'))
    mkdir(joinpath(root_path, 'docs'))

    try:
        projects = load(root_path + '/projects.pickle')
    except FileNotFoundError:
        projects = {}

    username = g.app.config.get('github', 'username')
    password = g.app.config.get('github', 'password')

    tachyonic = GitHub(auth=(username, password))

    while True:
        try:
            teams = {}
            github_teams = tachyonic.teams('TachyonicProject')
            for github_team in github_teams:
                team = github_team['name']
                if team == "Author":
                    continue
                teams[team] = {}
                github_members = tachyonic.team_members(github_team['id'])
                for github_member in github_members:
                    login = github_member['login']
                    teams[team][login] = {}
                    teams[team][login]['github'] = github_member['html_url']
                    teams[team][login]['avatar'] = github_member['avatar_url']
            save(teams,
                 root_path + '/team.pickle', perms=664)

            save(tachyonic.projects('TachyonicProject'),
                 root_path + '/planning.pickle', perms=664)

            found = []
            log.info("Getting Repos")
            repos = tachyonic.repos('TachyonicProject')
            for repo in repos:
                name = repo['name']
                found.append(name)
                description = repo['description']
                if name not in projects:
                    projects[name] = {}
                log.info("Scanning Repo " + name)
                updated_at = utc(repo['updated_at'])
                created_at = utc(repo['created_at'])
                pushed_at = utc(repo['pushed_at'])

                if (('updated_at' not in projects[name]) or
                        ('updated_at' in projects[name] and
                         updated_at != projects[name]['updated_at']) or
                    ('pushed_at' not in projects[name]) or
                        ('pushed_at' in projects[name] and
                         pushed_at != projects[name]['pushed_at'])):

                    projects[name]['created_at'] = created_at
                    projects[name]['description'] = description
                    projects[name]['clone_url'] = repo['clone_url']
                    log.info("Getting Branches for %s" % name)
                    branches = tachyonic.branches('TachyonicProject', name)
                    branches = [branch['name'] for branch in branches]
                    projects[name]['branches'] = branches
                    log.info("Getting Tags for %s" % name)
                    tags = tachyonic.tags('TachyonicProject', name)
                    tags = [tag['name'] for tag in tags]
                    projects[name]['tags'] = tags
                    projects[name]['refs'] = version_order(branches + tags)
                    projects[name]['doc_refs'] = {}
                else:
                    log.info("Project %s Already up-to-date (%s)" %
                             (name,
                              updated_at,))

                projects[name]['updated_at'] = updated_at
                projects[name]['pushed_at'] = pushed_at

                if 'updated_doc' not in projects[name]:
                    projects[name]['updated_doc'] = {}

                for ref in projects[name]['refs']:
                    current_datetime = now()
                    if ref in projects[name]['updated_doc']:
                        commits = tachyonic.commits(
                            'TachyonicProject',
                            name, sha=ref,
                            since=format_iso8601(
                                projects[name]['updated_doc'][ref]
                            )
                        )
                        if len(commits) == 0:
                            log.info("Documentation" +
                                     " '%s/%s'" % (name, ref,) +
                                     " Already up-to-date (%s)" % updated_at)
                            continue

                    venv_dir = "%s/github/%s_%s" % (root_path, name, ref,)
                    doc_dir = "%s/docs/%s_%s" % (root_path, name, ref,)
                    src_path = venv_dir + '/' + name
                    log.info("Creating Virtual Environment '%s'" % venv_dir)
                    build_venv(str(venv_dir))

                    clone(projects[name]['clone_url'], src_path)

                    if (exists(src_path + '/docs/source/conf.py') and
                            exists(src_path + '/docs/Makefile')):
                        log.info("Bulding '%s/%s'" % (name, ref,))
                        projects[name]['doc_refs'][ref] = True
                        info = build_doc(root_path, venv_dir,
                                         src_path, ref,
                                         doc_dir, name)
                        updated(name, ref, info)
                    else:
                        projects[name]['doc_refs'][ref] = False
                        log.warning("No Sphinx docs found '%s/%s'" %
                                    (name, ref,))

                    projects[name]['updated_doc'][ref] = current_datetime

                save(projects, root_path + '/projects.pickle', perms=664)

            events = []
            events_ordered = []
            git_events = tachyonic.events('TachyonicProject')
            for pj in projects.copy():
                if pj not in found:
                    del projects[pj]
                else:
                    for event in git_events:
                        type = event['type']
                        payload = event['payload']
                        if type == 'PullRequestEvent':
                            pr = payload['pull_request']
                            merged = pr['merged']
                            base = pr['base']
                            ref = base['ref']
                            if merged is True:
                                merged_at = utc(pr['merged_at'])
                                events.append((merged_at,
                                               "Code Updated",
                                               "Repo " + pj + "/" + ref +
                                               ""))
            for item in sorted(events, key=operator.itemgetter(0)):
                events_ordered.append(item)
            events_ordered = list(reversed(events_ordered))
            save(events_ordered[0:10], root_path + '/events.pickle', perms=664)

            save(projects, root_path + '/projects.pickle', perms=664)
            log.info('Infinite loop sleeping 5 Minutes')
            sleep(300)

        except KeyboardInterrupt:
            print("Control-C closed / Killed")
            break
        except ExecuteError as e:
            handle_error(e.title, e.description)
        except Exception as e:
            trace = str(traceback.format_exc())
            error = '%s: %s' % (object_name(e),
                                e)
            handle_error(error, trace)
