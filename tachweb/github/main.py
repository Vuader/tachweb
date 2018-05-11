#!/usr/bin/env /usr/bin/python3
import sys
import argparse
import traceback
import operator
from time import sleep
from string import Template
from pkg_resources import resource_stream

from luxon import g
from luxon import GetLogger
from luxon import send_email
from luxon.utils.app import init
from luxon.utils.daemon import Daemon
from luxon.utils.python import create_env
from luxon.utils.objects import save, load
from luxon.utils.objects import object_name
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.system import execute
from luxon.utils.files import (chmod,
                               chdir,
                               exists,
                               rm,
                               abspath,)
from luxon.exceptions import ExecuteError
from luxon.utils.timezone import utc
from psychokinetic.github import GitHub

from tachweb.github.version import version_order

log = GetLogger()


def handle_error(error, trace):
    email = g.config.get('github', 'email')
    rcpt = g.config.get('github', 'rcpt')

    if g.debug:
        log.debug(trace)
    else:
        log.error(error)

    send_email(email, rcpt,
               subject='GitHub TachWeb Error %s' % error,
               body=trace)
    log.info('Error in loop sleeping 15 minutes')
    sleep(900)


def build_doc(root_path, venv_path, src_path, ref, doc_dir, name):
    chdir(src_path)
    log.info("Checkout '%s/%s'" % (name, ref,))
    execute(["git", "checkout", ref])
    metadata_py = src_path + '/' + name + '/metadata.py'
    exec_globals = {}
    exec(open(metadata_py).read(), exec_globals, exec_globals)

    confpy = venv_path + '/conf.py'
    if exists(confpy):
        rm(confpy)
    with resource_stream('tachweb', 'github/conf.py.tpl') as tpl_file:
        template = Template(if_bytes_to_unicode(tpl_file.read()))
    with open(confpy, 'w') as real_file:
        real_file.write(template.safe_substitute(
            **exec_globals))

    buildsh = venv_path + '/build.sh'
    if exists(buildsh):
        rm(buildsh)
    with resource_stream('tachweb', 'github/build.sh.tpl') as tpl_file:
        template = Template(if_bytes_to_unicode(tpl_file.read()))
    with open(buildsh, 'w') as real_file:
        real_file.write(template.safe_substitute(
            virtualenv=venv_path,
            src_path=src_path,
            doc_dir=doc_dir))

    chmod(buildsh, 700)

    execute(["/usr/bin/env",
            venv_path + "/build.sh",
            venv_path,
            src_path,
            doc_dir], check=True)


def clone(clone_url, dest):
    execute(["git", "clone", clone_url, dest])


def daemon(root_path):
    try:
        projects = load(root_path + '/projects.pickle')
    except FileNotFoundError:
        projects = {}

    username = g.config.get('github', 'username')
    password = g.config.get('github', 'password')

    tachyonic = GitHub('https://api.github.com',
                       auth=(username, password))

    while True:
        try:
            save(tachyonic.projects('TachyonicProject'),
                 root_path + '/planning.pickle')
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
                updated_at = repo['updated_at']
                created_at = repo['updated_at']

                # NOTE(cfrademan): This does not work for tags/branches
                # updating.
                if (('updated_at' not in projects[name]) or
                        ('updated_at' in projects[name] and
                         updated_at != projects[name]['updated_at'])):

                    projects[name]['description'] = description
                    projects[name]['created_at'] = created_at
                    projects[name]['clone_url'] = repo['clone_url']
                    projects[name]['events'] = tachyonic.events(
                        'TachyonicProject',
                        name
                    )
                    log.info("Getting Branches for %s" % name)
                    branches = tachyonic.branches('TachyonicProject', name)
                    projects[name]['branches'] = branches
                    log.info("Getting Tags for %s" % name)
                    tags = tachyonic.tags('TachyonicProject', name)
                    projects[name]['tags'] = tags
                    projects[name]['refs'] = version_order(branches + tags)
                    projects[name]['doc_refs'] = {}
                else:
                    log.info("Project %s Already up-to-date (%s)" %
                             (name,
                              updated_at,))

                projects[name]['updated_at'] = updated_at

                if 'updated_doc' not in projects[name]:
                    projects[name]['updated_doc'] = {}

                for ref in projects[name]['refs']:
                    if (ref in projects[name]['updated_doc'] and
                            updated_at == projects[name]['updated_doc'][ref]):
                        log.info("Documentation" +
                                 " '%s/%s'" % (name, ref,) +
                                 " Already up-to-date (%s)" % updated_at)
                        continue

                    venv_dir = "%s/github/%s_%s" % (root_path, name, ref,)
                    doc_dir = "%s/docs/%s_%s" % (root_path, name, ref,)
                    src_path = venv_dir + '/' + name
                    log.info("Creating Virtual Environment '%s'" % venv_dir)
                    create_env(str(venv_dir), wipe=True, site_packages=True)

                    clone(projects[name]['clone_url'], src_path)

                    if (exists(src_path + '/docs/source/conf.py') and
                            exists(src_path + '/docs/Makefile')):
                        log.info("Bulding '%s/%s'" % (name, ref,))
                        projects[name]['doc_refs'][ref] = True
                        build_doc(root_path, venv_dir,
                                  src_path, ref,
                                  doc_dir, name)
                    else:
                        projects[name]['doc_refs'][ref] = False
                        log.warning("No Sphinx docs found '%s/%s'" %
                                    (name, ref,))

                    projects[name]['updated_doc'][ref] = updated_at

                save(projects, root_path + '/projects.pickle')

            events = []
            events_ordered = []
            for pj in projects:
                if pj not in found:
                    del projects[pj]
                else:
                    for event in projects[pj]['events']:
                        type = event['type']
                        # created_at = event['created_at']
                        payload = event['payload']
                        if type == 'PullRequestEvent':
                            pr = payload['pull_request']
                            merged = pr['merged']
                            # status = pr['state']
                            # head = pr['head']
                            base = pr['base']
                            ref = base['ref']
                            # title = pr['title']
                            if merged is True:
                                merged_at = utc(pr['merged_at'])
                                events.append((merged_at,
                                               "Code Updated",
                                               "Repo " + pj + "/" + ref +
                                               ""))
            for item in sorted(events, key=operator.itemgetter(0)):
                events_ordered.append(item)
            events_ordered = list(reversed(events_ordered))
            save(events_ordered, root_path + '/events.pickle')

            save(projects, root_path + '/projects.pickle')
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


def main(argv):
    try:
        parser = argparse.ArgumentParser()
        action = parser.add_mutually_exclusive_group()
        parser.add_argument('path',
                            help='Tachyonic Web Location')
        action.add_argument('-s', '--start',
                            action='store_true',
                            help='Fork Process')
        parser.add_argument('-f', '--fork',
                            action='store_true',
                            help='Fork Process')
        action.add_argument('-k', '--kill',
                            action='store_true',
                            help='Stop/Kill Process')
        action.add_argument('-r', '--restart',
                            action='store_true',
                            help='Restart Process')

        args = parser.parse_args()
        root_path = abspath(args.path)
        init('github', root_path)
        pid_file = root_path + '/github.pid'

        def proc():
            daemon(root_path)

        fork = Daemon(pid_file, run=proc)

        if args.start:
            if args.fork is True:
                fork.start()
            else:
                fork.start(fork=False)
        else:
            if args.kill is True:
                fork.stop()
            if args.restart is True:
                fork.restart()

    except KeyboardInterrupt:
        print("Control-C closed / Killed")


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
