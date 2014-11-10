#!/usr/bin/env python
# -*- coding: utf-8 -*-

#=========================================================================
#
#         FILE: py_mail.py
#
#        USAGE: ./py_mail.py
#
#  DESCRIPTION: Fetch mails from IMAP server into database (SQLite/MySQL)
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: SHIE, Li-Yi (lyshie), lyshie@mx.nthu.edu.tw
# ORGANIZATION:
#      VERSION: 1.0
#      CREATED: 2014-10-14 15:08:39
#     REVISION: ---
#=========================================================================

import mailbox
import email.errors
import email.header
import email.utils
import re
import sqlite3
import MySQLdb
import warnings
import imaplib
import getpass
import py_today
import rfc822
import os
import ConfigParser
import sched
import time
import logging
import argparse
import gettext

_ = gettext.gettext


class I18N(object):

    @classmethod
    def bind(self):
        basename = os.path.basename(os.path.realpath(__file__))
        path = os.path.dirname(os.path.realpath(__file__))

        domain, ext = os.path.splitext(basename)
        localedir = os.path.join(path, "I18N")

        gettext.bindtextdomain(domain, localedir)
        gettext.textdomain(domain)


class Argument(object):
    args = None

    def __init__(self):
        if (not Argument.args):
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-s", "--since", default="days=2", help=_("Time format: 1second, 2days, week=2"))
            Argument.args = parser.parse_args()

    @classmethod
    def get_since(self, since="days=2"):
        re_value = re.compile(r"(\d+)")
        re_unit = re.compile(r"(second|minute|hour|day|week)")

        value = None
        unit = None

        m = re_value.search(since)
        if (m):
            value = m.group(1)

        m = re_unit.search(since)
        if (m):
            unit = m.group(1)

        since = "days=2"
        if (value and unit):
            since = "{}s={}".format(unit, value)
        else:
            debug(_("WARN: failed to parse time string."))

        debug(_("Since '{}'").format(since))

        return since


def debug(msg, *args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.debug(msg, *args, **kwargs)


def get_default_config(filename=""):
    path = os.path.dirname(os.path.realpath(__file__))

    # default config filename 'web.py' => 'web.conf'
    if (not filename):
        basename = os.path.basename(os.path.realpath(__file__))
        basename, ext = os.path.splitext(basename)
        filename = basename + ".conf"

    return os.path.join(path, filename)


def get_config(filename=get_default_config()):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    params = {'mysql_username': 'root',
              'mysql_password': None,
              'mysql_table': 'maildir',
              'mysql_host': 'localhost',
              'imap_username': 'lyshie',
              'imap_password': None,
              'imap_host': 'imap.mx.nthu.edu.tw',
              'sqlite3_database': 'maildir.db',
              }

    for sec in ['imap', 'mysql']:
        if (config.has_section(sec)):
            for k in config.options(sec):
                if (config.has_option(sec, k)):
                    params["{}_{}".format(sec, k)] = config.get(sec, k)

    return params


def create_table(db='sqlite3', params=None):
    conn = None

    if (db == 'sqlite3'):
        conn = sqlite3.connect(params['sqlite3_database'])
    elif (db == 'mysql'):
        conn = MySQLdb.connect(
            params['mysql_host'], params['mysql_username'], params['mysql_password'] or getpass.getpass('MySQL Password: '), params['mysql_table'],  charset='utf8')

    cur = conn.cursor()

    if (db == 'sqlite3'):
        cur.execute('''
            CREATE TABLE IF NOT EXISTS message
            (
                subject TEXT,
                date    TEXT,
                s_from  TEXT,
                UNIQUE  (subject, date)
            )
        ''')
    elif (db == 'mysql'):
        warnings.simplefilter('ignore', category=MySQLdb.Warning)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS message
            (
                subject VARCHAR(255),
                date    VARCHAR(255),
                s_from  VARCHAR(255),
                UNIQUE  (subject, date)
            )
        ''')
        warnings.resetwarnings()

    conn.commit()
    conn.close()


def open_table(db='sqlite3', params=None):
    conn = None
    if (db == 'sqlite3'):
        conn = sqlite3.connect(params['sqlite3_database'])
    elif (db == 'mysql'):
        conn = MySQLdb.connect(
            params['mysql_host'], params['mysql_username'], params['mysql_password'] or getpass.getpass('MySQL Password: '), params['mysql_table'], charset='utf8')

    conn.text_factory = str

    return conn


def close_table(conn):
    if (conn):
        conn.commit()
        conn.close()


def insert_into_table(conn, items, db='sqlite3'):
    if (conn):
        cur = conn.cursor()

        if (db == 'sqlite3'):
            cur.execute('''
                REPLACE INTO message (subject, date, s_from) VALUES (?, ?, ?)
                ''' ,  (items[0], items[1], items[2]))
        elif (db == 'mysql'):
            cur.execute('''
                REPLACE INTO message (subject, date, s_from) VALUES (%s, %s, %s)
                ''' ,  [items[0], items[1], items[2]])


def decode_header(raw, defaults=["utf-8", "big5"]):
    # pre-process
    raw = raw.replace("?gb2312?", "?gbk?")

    lf = re.compile(r'[\n\r]+')
    raw = lf.sub("", raw)

    con = re.compile(r'\?==\?')
    raw = con.sub('?= =?', raw)

    result = u""

    try:
        pairs = email.header.decode_header(raw)
    except email.errors.HeaderParseError:
        for enc in defaults:
            try:
                result = raw.decode(enc, errors="strict")
                break
            except:
                continue

        return result

    for i, (decoded, charset) in enumerate(pairs):
        if (charset):
            pairs[i] = decoded.decode(charset, errors="replace")
        else:
            for enc in defaults:
                try:
                    pairs[i] = decoded.decode(enc, errors="strict")
                    break
                except:
                    continue

    return u"".join(pairs)


def load_maildir():
    md = mailbox.Maildir("~/Maildir")

    keys = md.keys()
    keys.sort(cmp=lambda x, y: cmp(x, y))

    create_table(db='mysql')
    conn = open_table(db='mysql')

    for k in keys:
        try:
            msg = md.get(k)
        except email.errors.MessageParseError:
            continue

        raw = msg.get("subject")
        subject = decode_header(raw)
        print(subject)

        date = msg.get("date")
        dt = email.utils.parsedate_tz(date)
        t = 0
        if (dt):
            t = email.utils.mktime_tz(dt)
        else:
            t = 0

        s_from = msg.get("from")
        s_from = decode_header(s_from)
        r, e = rfc822.parseaddr(s_from)
        if (e):
            s_from = e

        insert_into_table(conn, [subject, str(t), s_from], db='mysql')

    close_table(conn)


def load_imap(params=None):
    imap = imaplib.IMAP4(host=params['imap_host'])
    imap.login(params['imap_username'], params[
               'imap_password'] or getpass.getpass('IMAP Password: '))

    imap.select(readonly=True)

    #typ, nums = imap.uid("SEARCH", "ALL")

    today = py_today.Today()
    #yesterday = today - "days=1"
    since = today - Argument.get_since(Argument.args.since)

    typ, nums = imap.uid("SEARCH", "SINCE", since.format_time(
        format="%d-%b-%Y"))

    msgs = {}

    count = 15000
    for i in reversed(nums[0].split()):
        if (count % 500 == 0):
            debug(_("Current = {}").format(count))

        count = count - 1
        if (count < 0):
            break

        typ, data = imap.uid(
            "FETCH", i, '(BODY[HEADER.FIELDS (Subject Date From)])')

        header = email.message_from_string(data[0][1] or "")

        subject = header['Subject'] or ""
        date = header['Date'] or ""
        s_from = header['From'] or ""
        r, e = rfc822.parseaddr(s_from)
        if (e):
            s_from = e

        msgs[i] = {'subject': decode_header(subject),
                   'date': date,
                   'from': decode_header(s_from)}

    imap.close()
    imap.logout()

    create_table(db='mysql', params=params)
    conn = open_table(db='mysql', params=params)

    count = 0
    for m in reversed(sorted(msgs.keys())):
        count = count + 1
        dt = None
        if (msgs[m]['date']):
            dt = email.utils.parsedate_tz(msgs[m]['date'])

        if (dt):
            t = email.utils.mktime_tz(dt)
        else:
            t = 0

        insert_into_table(
            conn, [msgs[m]['subject'], str(t), msgs[m]['from']], db='mysql')

    close_table(conn)

    debug(_("Total = {}").format(count))


def fetch_mail(params=None, sch=None):
    debug(_("Fetch mail and store ({})...").format(time.strftime("%F %T")))

    # every 180 seconds
    sch.enter(180, 1, fetch_mail, (params, sch))

    load_imap(params=params)
    # load_maildir()


def main():
    I18N().bind()
    Argument()

    params = get_config()

    logging.basicConfig(level=logging.DEBUG)
    sch = sched.scheduler(time.time, time.sleep)
    sch.enter(0, 1, fetch_mail, (params, sch))
    sch.run()

if __name__ == '__main__':
    main()
