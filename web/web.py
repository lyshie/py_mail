#!/usr/bin/env python
# -*- coding: utf-8 -*-

#=========================================================================
#
#         FILE: web.py
#
#        USAGE: ./web.py
#
#  DESCRIPTION: Simple RESTful API
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: SHIE, Li-Yi (lyshie), lyshie@mx.nthu.edu.tw
# ORGANIZATION:
#      VERSION: 1.0
#      CREATED: 2014-10-27 16:39:30
#     REVISION: ---
#=========================================================================

import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
import getpass
import ConfigParser


def get_default_config(filename=""):
    path = os.path.dirname(os.path.realpath(__file__))

    # default config filename 'web.py' => 'web.conf'
    if (not filename):
        basename = os.path.basename(os.path.realpath(__file__))
        basename, a = basename.split(".", 1)
        filename = basename + ".conf"

    return os.path.join(path, filename)


def get_config(filename=get_default_config()):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    params = {'mysql_username': 'root',
              'mysql_password': None,
              'mysql_table': 'maildir',
              'mysql_host': 'localhost',
              }

    for sec in ['mysql']:
        if (config.has_section(sec)):
            for k in config.options(sec):
                if (config.has_option(sec, k)):
                    params["{}_{}".format(sec, k)] = config.get(sec, k)

    return params

app = Flask(__name__)
params = get_config()
password = params['mysql_password'] or getpass.getpass("MySQL Password: ")
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_table}".format(**params)
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255))
    s_from = db.Column(db.String(255))
    date = db.Column(db.Integer)

    db.UniqueConstraint('subject', 'date')

    def __getitem__(self, key):
        if (key in self.__table__.columns):
            return getattr(self, key)

    def as_dict(self):
        return {'id': self.id,
                'subject': self.subject,
                's_from': self.s_from,
                'date': self.date}


@app.route("/mail")
def get_mail_info():
    count = Message.query.count()
    columns = [{'name': c.name, 'type': repr(c.type)}
               for c in Message.__table__.columns]

    return jsonify(count=count, columns=columns)


@app.route("/mail/<int:row>/<int:count>")
@app.route("/mail/<int:row>/<int:count>/<column>")
def get_row_count(row, column=None, count=1):
    sorted = request.args.get('sorted')
    keyword = request.args.get('keyword')
    query = Message.query
    keywords = []
    result = []

    if (keyword):
        keywords = [k.strip() for k in keyword.split(",")]

    if (keywords):
        for k in keywords:
            if (k):
                query = query.filter(Message.subject.contains(k))

    if (sorted):
        if (column):
            records = query.order_by(Message.date.desc()).limit(
                count).offset(row).with_entities(getattr(Message, column))
        else:
            records = query.order_by(
                Message.date.desc()).limit(count).offset(row)
    else:
        if (column):
            records = query.limit(count).offset(
                row).with_entities(getattr(Message, column))
        else:
            records = query.limit(count).offset(row)

    if (column):
        # tuple
        for r in records:
            result.append({column: r[0]})
    else:
        for r in records:
            result.append(r.as_dict())

    return jsonify(result=result)


@app.route("/mail/<int:row>")
@app.route("/mail/<int:row>/<column>")
def get_row(row, column=None):
    sorted = request.args.get('sorted')
    record = None
    error = "not found"

    if (sorted):
        records = Message.query.order_by(
            Message.date.desc()).limit(1).offset(row)
        try:
            record = records[0]
        except IndexError, e:
            error = repr(e)
    else:
        record = Message.query.get(row)

    if (record):
        if (column):
            c = {column: record[column]}
            return jsonify(**c)
        else:
            return jsonify(result=[record.as_dict()])
    else:
        return jsonify(error=error)


@app.route("/")
def index():
    return render_template('index.html')


def main():
    app.run(host="0.0.0.0", debug=True)

if __name__ == '__main__':
    main()
