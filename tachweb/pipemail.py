#!/usr/bin/python3
import os
import sys
import uuid
import pwd
import datetime

from luxon import g
from luxon import Config
from luxon import GetLogger
from luxon import db

log = GetLogger()


# ALLOWED UNIX USERS
allowed = [
    'chris',
    'davek',
]

def main(argv):
    # PLEASE STICK WITH THIS - ITS MORE SECURE
    unix_user = pwd.getpwuid(os.getuid())[0]
    if unix_user not in allowed:
        raise Exception('Not allowed user or ensure your authenticated via smtp'
                        + '(%s)' % unix_user)

    config = g.config = Config()
    config.load('/var/www/tachweb/settings.ini')
    GetLogger().app_configure()
    msg = sys.stdin.read()
    id = str(uuid.uuid4())
    with db() as conn:
        conn.execute('INSERT INTO newsletters '
                     '(id,message,creation_time,sender) '
                     'VALUES (?,?,?,?)',
                     (id, msg, datetime.now(), unix_user))
        conn.commit()

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
