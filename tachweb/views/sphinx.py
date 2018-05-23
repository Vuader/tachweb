import os
import mimetypes
import re

from luxon import register
from luxon import constants as const
from luxon.exceptions import HTTPNotFound
from luxon import render_template
from luxon.constants import TEXT_HTML
from luxon.utils.html5 import select
from luxon import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon import g

log = GetLogger(__name__)


g.nav_menu.add('/Documentation/Tutorials',
               href='/sphinx/tutorials/latest/index.html')
g.nav_menu.add('/Documentation/Luxon',
               href='/sphinx/luxon/latest/index.html')
g.nav_menu.add('/Documentation/Psychokinetic',
               href='/sphinx/psychokinetic/latest/index.html')
g.nav_menu.add('/Documentation/InfinityStone',
               href='/sphinx/infinitystone/latest/index.html')
g.nav_menu.add('/Documentation/Netrino',
               href='/sphinx/netrino/latest/index.html')
g.nav_menu.add('/Documentation/Yoshii',
               href='/sphinx/yoshii/latest/index.html')
g.nav_menu.add('/Documentation/Katalog',
               href='/sphinx/katalog/latest/index.html')
g.nav_menu.add('/Documentation/Kiloquad',
               href='/sphinx/kiloquad/latest/index.html')
g.nav_menu.add('/Documentation/Photonic',
               href='/sphinx/photonic/latest/index.html')
g.nav_menu.add('/Documentation/pyipcalc', href='/rst/pyipcalc')
g.nav_menu.add('/Documentation/Blueprints',
               href='/sphinx/blueprints/latest/index.html')
g.nav_menu.add('/Documentation/DevStack',
               href='/sphinx/devstack/latest/index.html')
g.nav_menu.add('/Documentation/Lab',
               href='/sphinx/tachlab/latest/index.html')


def format_body_only(html):
    html = if_bytes_to_unicode(html)
    body_match = re.compile(r"\<!\-\-DOC\-\-\>.*\<\!\-\-DOC\-\-\>",
                            re.IGNORECASE | re.MULTILINE |
                            re.DOTALL)

    for body in body_match.findall(html):
        return body
    return "No content/body"


@register.resource(['GET', 'POST'],
                   'regex:^/sphinx.*$', cache=14400)
def sphinx(req, resp):
    full_path = req.route.strip('/').split('/')[1:]

    if len(full_path) > 0 and full_path[0] in req.context['projects']:
        resp.content_type = TEXT_HTML
        name = full_path[0]
        goto = req.get_first('ref')
        if goto is not None:
            return resp.redirect('%s/sphinx/%s/%s' %
                                 (g.current_request.app, name, goto,))

        project = req.context['projects'][name]
        refs = project['refs']
        description = project['description']

        if len(refs) == 0:
            raise HTTPNotFound("Project documentation not found")

        if len(full_path) > 1:
            ref = full_path[1]
        else:
            return resp.redirect('%s/sphinx/%s/%s/index.html' %
                                 (g.current_request.app, name, refs[0],))

        doc_path = full_path[2:]

        html_root = g.app.path + '/docs/%s_%s' % (name, ref)

        if len(doc_path) == 0:
            return resp.redirect('%s/sphinx/%s/%s/index.html' %
                                 (g.current_request.app, name, ref,))
        else:
            path = "/".join(doc_path)

        path = html_root + '/' + path
        if os.path.isfile(path):
            sfile = open(path, 'rb').read()
            resp.content_type = const.APPLICATION_OCTET_STREAM
            mime_type = mimetypes.guess_type(path)
            if mime_type is not None:
                resp.content_type = mime_type[0]
                if mime_type[1] is not None:
                    resp.content_type += ';charset=%s' % mime_type[1]
            if mime_type[0].lower() == 'text/html':
                refs = select('ref', refs, ref, False,
                              'custom-control form-control-sm custom-select',
                              'this.form.submit()')
                sfile = format_body_only(sfile)
                git = "https://github.com/TachyonicProject/%s/tree/%s" % (name,
                                                                          ref,)
                home = '%s/sphinx/%s/%s/index.html' % (req.app, name, ref,)
                description = "%s (%s)" % (description, name,)
                return render_template('tachweb/sphinx.html', refs=refs,
                                       doc=sfile,
                                       no_side=True,
                                       project=name, title=description,
                                       description=description,
                                       git=git, home=home)
            else:
                return sfile
        else:
            raise HTTPNotFound('Documentation page not found - possibly' +
                               ' updating')

    else:
        raise HTTPNotFound("Project documentation not found")
