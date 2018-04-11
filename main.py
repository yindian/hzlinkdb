#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, abort, g, request
from sqlite3 import dbapi2 as sqlite3
import sys, os
import string
import struct
import traceback

import time
_start = time.clock()
import unihan
_end = time.clock()
print >> sys.stderr, _end - _start, 'seconds elapsed importing unihan'

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.instance_path, 'hzlinkdb.db'),
    DEBUG=True,
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    if not os.path.exists(app.config['DATABASE']):
        os.makedirs(os.path.dirname(app.config['DATABASE']))
    rv = sqlite3.connect(app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def unichar(i):
    try:
        return unichr(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')

def ordinal(c):
    try:
        return ord(c)
    except TypeError:
        return struct.unpack('i', c.encode('utf-32')[4:])[0]

def query_split(s):
    ar = []
    state = 0
    for c in s:
        if state == 0:
            ar.append(c)
            if c == '&':
                state = 1
            elif c == 'U':
                state = 2
            elif 0xD800 <= ord(c) < 0xDC00:
                state = 4
        elif state == 1:
            ar[-1] += c
            if c == ';':
                state = 0
        elif state == 2:
            if c == '+' or c == '-':
                ar[-1] += c
                state = 3
            else:
                ar.append(c)
                state = 0
        elif state == 3:
            if c in string.hexdigits:
                ar[-1] += c
                if len(ar[-1]) == 10:
                    state = 0
            else:
                ar.append(c)
                state = 0
        elif state == 4:
            if 0xDC00 <= ord(c) < 0xE000:
                ar[-1] += c
            else:
                ar.append(c)
            state = 0
    return [s for s in ar if not s.isspace()]

def _readings_linker(k, v):
    return '<a href="/l?n=readings&k=%s&v=%s">%s</a>' % (k, v, v)

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    d = {}
    d['table_list'] = [
            ('zibiao2009', 'Tongyong Guifan Hanzi Biao'),
            ]
    d['result_list'] = ar = []
    query = request.args.get('q') or request.form.get('q')
    if query:
        for s in query_split(query):
            dd = {}
            ar.append(dd)
            try:
                code = None
                if s.startswith('U'):
                    code = int(s[2:], 16)
                    dd['char'] = unichar(code)
                    dd['code'] = s
                elif s.startswith('&'):
                    dd['char'] = ''
                    dd['code'] = s
                else:
                    dd['char'] = s
                    code = ordinal(s)
                    dd['code'] = 'U+%04X' % (code,)
                if code:
                    dd['readings'] = unihan.get_readings_by_code_w_link(
                            code, linker=_readings_linker)
            except:
                dd['error'] = traceback.format_exc()
                traceback.print_exc()
    return render_template('index.html', **d)

@app.route('/l', methods=['GET', 'POST'])
def link():
    db = get_db()
    d = {}
    d['result_list'] = ar = []
    name = request.args.get('n') or request.form.get('n')
    key = request.args.get('k') or request.form.get('k')
    val = request.args.get('v') or request.form.get('v')
    d['key'], d['val'] = key, val
    if name == 'readings':
        try:
            for code in unihan.get_codes_by_reading(key, val):
                ar.append(unichar(code))
        except:
            d['error'] = traceback.format_exc()
            traceback.print_exc()
    return render_template('link.html', **d)

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer

    http_server = WSGIServer(('0.0.0.0', 8080), app)
    http_server.serve_forever()
# vim:ts=4:sw=4:et:ai:cc=80
