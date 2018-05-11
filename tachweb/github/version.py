
import re

version_re = re.compile(r'[\d.]+')


def version_order(tags):
    tags = list(tags)
    versions = []

    if 'latest' in tags:
        tags.remove('latest')
        versions.append('latest')

    if 'current' in tags:
        tags.remove('current')
        versions.append('current')

    if 'master' in tags:
        tags.remove('master')
        versions.append('master')

    num_versions = []
    for item in list(tags):
        if version_re.match(item):
            num_versions.append(item)
            tags.remove(item)

    num_versions = sorted(num_versions)
    num_versions.reverse()
    versions += num_versions

    for item in tags:
        versions.append(item)

    return versions
