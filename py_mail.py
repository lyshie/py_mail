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


def create_table(db='sqlite3'):
    conn = None

    if (db == 'sqlite3'):
        conn = sqlite3.connect("maildir.db")
    elif (db == 'mysql'):
        conn = MySQLdb.connect(
            'localhost', 'root', getpass.getpass('MySQL Password: '), 'maildir', charset='utf8')

    cur = conn.cursor()

    if (db == 'sqlite3'):
        cur.execute('''
            CREATE TABLE IF NOT EXISTS message
            (
                subject TEXT,
                date    TEXT,
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
                UNIQUE  (subject, date)
            )
        ''')
        warnings.resetwarnings()

    conn.commit()
    conn.close()


def open_table(db='sqlite3'):
    conn = None
    if (db == 'sqlite3'):
        conn = sqlite3.connect("maildir.db")
    elif (db == 'mysql'):
        conn = MySQLdb.connect(
            'localhost', 'root', getpass.getpass('MySQL Password: '), 'maildir', charset='utf8')

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
                REPLACE INTO message (subject, date) VALUES (?, ?)
                ''' ,  (items[0], items[1]))
        elif (db == 'mysql'):
            cur.execute('''
                REPLACE INTO message (subject, date) VALUES (%s, %s)
                ''' ,  [items[0], items[1]])


def decode_header(raw, defaults=["utf-8", "big5"]):
    # pre-process
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

    con = re.compile(r'\?==\?')

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

        insert_into_table(conn, [subject, str(t)], db='mysql')

    close_table(conn)


def load_imap():
    imap = imaplib.IMAP4(host="imap.mx.nthu.edu.tw")
    imap.login("lyshie", getpass.getpass('IMAP Password: '))

    imap.select(readonly=True)

    #typ, nums = imap.uid("SEARCH", "ALL")

    today = py_today.Today()
    yesterday = today - "days=1"
    in_two_days = today - "days=2"

    typ, nums = imap.uid("SEARCH", "SINCE", in_two_days.format_time(
        format="%d-%b-%Y"))

    con = re.compile(r"^(?:Date|Subject): ")
    lf = re.compile(r'[\n\r]+')

    msgs = {}

    count = 15000
    for i in reversed(nums[0].split()):
        if (count % 500 == 0):
            print("Count = {}".format(count))

        count = count - 1
        if (count < 0):
            break

        typ, data = imap.uid(
            "FETCH", i, '(BODY[HEADER.FIELDS (Subject)])')
        subject = con.sub("", data[0][1] or "")

        typ, data = imap.uid(
            "FETCH", i, '(BODY[HEADER.FIELDS (Date)])')
        date = lf.sub("",  con.sub("", data[0][1] or ""))

        msgs[i] = {'subject': decode_header(subject),
                   'date': date}

    imap.close()
    imap.logout()

    create_table(db='mysql')
    conn = open_table(db='mysql')

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

        insert_into_table(conn, [msgs[m]['subject'], str(t)], db='mysql')

    close_table(conn)

    print(count)


def main():
    load_imap()
    # load_maildir()

if __name__ == '__main__':
    main()
