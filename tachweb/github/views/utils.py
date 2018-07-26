from time import sleep
from string import Template
from pkg_resources import resource_stream

from luxon import g
from luxon import sendmail
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.system import execute
from luxon.utils.files import (chmod,
                               chdir,
                               exists,
                               joinpath,
                               abspath,
                               dirname,
                               rm,)
from luxon import GetLogger


log = GetLogger(__name__)


def updated(repo, branch, info):
    email = g.app.config.get('github', 'email')
    rcpt = g.app.config.get('github', 'rcpt')
    sendmail(email, rcpt,
             subject='GitHub Docs/Project %s/%s updated' %
             (repo, branch,),
             body=info)


def handle_error(error, trace):
    email = g.app.config.get('github', 'email')
    rcpt = g.app.config.get('github', 'rcpt')

    if g.app.debug:
        log.debug(trace)
    else:
        log.error(error)

    trace = "%s\n\n%s" % (error, trace,)

    sendmail(email, rcpt,
             subject='GitHub TachWeb Error %s' % error[0:15],
             body=trace)
    log.info('Error in loop sleeping 15 minutes')
    sleep(900)


def build_venv(venv_path):
    venvsh = joinpath(abspath(dirname(__file__)), '..', 'venv.sh')
    execute([venvsh, venv_path])


def build_doc(root_path, venv_path, src_path, ref, doc_dir, name):
    chdir(src_path)
    log.info("Checkout '%s/%s'" % (name, ref,))
    execute(["git", "checkout", ref])
    metadata_py = src_path + '/' + name + '/metadata.py'
    if not exists(metadata_py):
        return None

    exec_globals = {}
    exec(open(metadata_py).read(), exec_globals, exec_globals)

    if 'package' not in exec_globals:
        return None

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

    return execute(["/usr/bin/env",
                    venv_path + "/build.sh",
                    venv_path,
                    src_path,
                    doc_dir], check=True)


def clone(clone_url, dest):
    execute(["git", "clone", clone_url, dest])
