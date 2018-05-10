#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, abort, g, request
from flask import jsonify
from sqlite3 import dbapi2 as sqlite3
import sys, os
import string
import struct
import urllib
import xml.sax.saxutils
import traceback

import time
_start = time.clock()
import unihan
_end = time.clock()
print >> sys.stderr, _end - _start, 'seconds elapsed importing unihan'
_start = time.clock()
import chise
_end = time.clock()
print >> sys.stderr, _end - _start, 'seconds elapsed importing chise'
import ids
_start = time.clock()
import cjkvi
_end = time.clock()
print >> sys.stderr, _end - _start, 'seconds elapsed importing cjkvi'
import hzdb

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

@app.cli.command()
def initdb():
    '''Create the database with initial data.'''
    db = get_db()
    _start = time.clock()
    hzdb.create(db)
    db.commit()
    hzdb.init_data(db)
    db.commit()
    _end = time.clock()
    print 'Database initialized in %g seconds' % (_end - _start,)

@app.route('/del', methods=['POST'])
def del_from_db():
    db = get_db()
    d = {}
    try:
        d.update(request.form.iteritems())
        table = d.pop('db')
        hzdb.delete_from(db, table, d)
        db.commit()
    except:
        d['error'] = traceback.format_exc()
    return jsonify(d)

@app.route('/add', methods=['POST'])
def add_to_db():
    db = get_db()
    d = {}
    try:
        d.update(request.form.iteritems())
        table = d.pop('db')
        code = d.pop('code')
        assert code.startswith(('U+', 'U-'))
        code = int(code[2:], 16)
        row = hzdb.insert_code_to(db, table, code)
        db.commit()
        d['keys'] = row.keys()
        d['values'] = map(unicode, map(row.__getitem__, row.keys()))
    except:
        d['error'] = traceback.format_exc()
    return jsonify(d)

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
    if state == 3 and ar[-1][-1] not in string.hexdigits:
        assert len(ar[-1]) == 2
        assert ar[-1][1] == c
        ar[-1] = ar[-1][0]
        ar.append(c)
    elif state == 1:
        s = ar[-1]
        del ar[-1]
        ar.extend(list(s))
    return [s for s in ar if not s.isspace()]

def url_quote(v):
    if type(v) == unicode:
        v = v.encode('utf-8')
    return urllib.quote(v)

def unicode_value(s):
    return 'U+%04X' % (ordinal(s),)

def url_quoted_unicode_value(s):
    return urllib.quote(unicode_value(s))

def _readings_linker(k, v):
    return '<a href="/l?n=readings&k=%s&v=%s">%s</a>' % (
            k,
            urllib.quote(v.encode('utf-8')),
            xml.sax.saxutils.escape(v))

def _readings_key_linker(k):
    return '<a href="/kv?n=readings&k=%s">%s</a>' % (k, k)

def _variants_key_linker(k):
    return '<a href="/kv?n=variants&k=%s">%s</a>' % (k, k)

def _tables_key_linker(k, s=None):
    if s is None:
        s = k
    return '<a href="/kv?n=tables&k=%s">%s</a>' % (k, s)

_charset = set(['kGB0', 'kGB1', 'kBigFive', 'kJis0'])

def _variants_linker(k, v):
    if k in _charset:
        return '<a href="/l?n=variants&k=%s&v=%s">%s</a>' % (k, v, v)
    vv = urllib.quote(v.encode('utf-8'))
    if k == 'kRSUnicode':
        radical = int(v[:v.index('.')].rstrip("'"), 10) - 1
        assert 0 <= radical < 214
        return '<span class="radical">%s</span>&nbsp;\
<a href="/l?n=variants&k=%s&v=%s">%s</a>' % (
            unichr(0x2F00 + radical), k, vv, v)
    elif k == 'kIICore':
        return '<a href="/l?n=variants&k=%s&v=%s">%s</a>' % (k, vv, v)
    return '<a href="/?q=%s">%s</a>&nbsp;\
<a href="/l?n=variants&k=%s&v=%s">%s</a>' % (
            vv, unichar(int(v[2:], 16)), k, vv, v)

def _tables_linker(k, v):
    return '<a href="/l?n=tables&k=%s&v=%s">%s</a>' % (
            k,
            urllib.quote(v.encode('utf-8')),
            xml.sax.saxutils.escape(v))

def _query_linker(s):
    return '<a href="/?q=%s">%s</a>' % (url_quote(s), s)

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    d = {}
    d['table_list'] = [
            ]
    d['table_list'].extend(cjkvi.get_table_list())
    d['result_list'] = ar = []
    query = request.args.get('q') or request.form.get('q')
    if query:
        d['query'] = query
        qs = query_split(query)
        for i in xrange(len(qs)):
            s = qs[i]
            dd = {}
            dd['q'] = s
            ar.append(dd)
            try:
                code = None
                if s.startswith(('U+', 'U-')):
                    code = int(s[2:], 16)
                    dd['char'] = unichar(code)
                    dd['code'] = s
                elif s.startswith('&') and len(s) > 1:
                    try:
                        dd['char'] = chise.imgref(s)
                    except:
                        traceback.print_exc()
                        dd['char'] = s
                    t = chise.repurl(s)
                    if t:
                        dd['code'] = '<a target="_blank" href="%s">%s</a>' % (
                                t, xml.sax.saxutils.escape(s))
                    else:
                        dd['code'] = xml.sax.saxutils.escape(s)
                else:
                    dd['char'] = s
                    code = ordinal(s)
                    dd['code'] = 'U+%04X' % (code,)
                if ids.isidc(code):
                    stk = [ids.operands(code)]
                    j = i + 1
                    while stk:
                        try:
                            t = qs[j]
                        except IndexError:
                            break
                        stk[-1] -= 1
                        if not stk[-1]:
                            del stk[-1]
                        if ids.isidc(t):
                            stk.append(ids.operands(t))
                        j += 1
                    dd['ids'] = j
                    t = None
                elif code:
                    dd['readings'] = unihan.get_readings_by_code_w_link(
                            code, linker=_readings_linker)
                    dd['variants'] = unihan.get_variants_by_code_w_link(
                            code, linker=_variants_linker)
                    t = cjkvi.get_analysis(code, _query_linker)
                    if t:
                        dd['cjkvi_analysis'] = t
                    t = cjkvi.get_variants(code, _query_linker)
                    if t:
                        dd['cjkvi_variants'] = t
                    t = cjkvi.get_tables_by_code_w_link(code, _tables_linker)
                    if t:
                        dd['tables'] = t
                    t = chise.ids_find_by_code(code)
                    if not t:
                        t = chise.ids_find_by_entity(s)
                    if t:
                        dd['chise_ids_find'] = chise.ids_find_url(code)
                    dd['hz_graph'] = hzdb.get_graph_by_code(db, code)
                    dd['hz_morph'] = hzdb.get_morph_by_code(db, code)
                else:
                    t = chise.ids_find_by_entity(s)
                if t is not None:
                    if t:
                        br = query_split(t)
                        for j in xrange(len(br)):
                            if ids.isidc(br[j]):
                                stk = [ids.operands(br[j])]
                                k = j + 1
                                while stk:
                                    try:
                                        t = br[k]
                                    except IndexError:
                                        break
                                    stk[-1] -= 1
                                    if not stk[-1]:
                                        del stk[-1]
                                    if ids.isidc(t):
                                        stk.append(ids.operands(t))
                                    k += 1
                                br[j] = '<a href="/?q=%s">%s</a>' % (
                                        url_quote(
                                            ''.join(br[j:k])),
                                        br[j])
                            else:
                                t = xml.sax.saxutils.escape(br[j])
                                br[j] = '<a href="/?q=%s">%s</a>' % (
                                        url_quote(br[j]), t)
                        dd['chise_ids'] = ''.join(br)
            except:
                dd['error'] = traceback.format_exc()
                traceback.print_exc()
        has_ids = False
        for i in xrange(len(qs)):
            dd = ar[i]
            if dd.has_key('ids'):
                j = dd['ids']
                dd['char'] = ''.join([x['char'] for x in ar[i:j]])
                dd['code'] = ','.join([x['code'] for x in ar[i:j]])
                s = ''.join([x['q'] for x in ar[i:j]])
                t = chise.ids_reverse_lookup(s)
                if t and not dd.has_key('chise_ids'):
                    dd['chise_ids'] = ' '.join(map(_query_linker, sorted(t)))
                has_ids = True
        if not has_ids and len(qs) > 1:
            s = ''.join(qs)
            t = chise.ids_reverse_lookup(s)
            if t:
                dd = {}
                dd['char'] = ''.join([x['char'] for x in ar])
                dd['code'] = ','.join([x['code'] for x in ar])
                dd['chise_ids'] = ' '.join(map(_query_linker, sorted(t)))
                dd['chise_ids_find'] = chise.ids_find_url(s)
                ar.insert(0, dd)
    d['readings_key_linker'] = _readings_key_linker
    d['variants_key_linker'] = _variants_key_linker
    d['tables_key_linker']   = _tables_key_linker
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
    d['klnk'] = str
    n = 0
    if name == 'readings':
        repo = unihan.get_codes_by_reading(key, val)
        d['klnk'] = _readings_key_linker
    elif name == 'variants':
        repo = unihan.get_codes_by_variant(key, val)
        d['klnk'] = _variants_key_linker
    elif name == 'tables':
        repo = cjkvi.get_codes_by_table(key, val)
        d['klnk'] = _tables_key_linker
    if True:
        try:
            for code in repo:
                ar.append(unichar(code))
                n += 1
        except:
            d['error'] = traceback.format_exc()
            traceback.print_exc()
    d['cnt'] = n
    return render_template('link.html', **d)

@app.route('/kv', methods=['GET', 'POST'])
def keyvalues():
    db = get_db()
    d = {}
    d['result_list'] = ar = []
    name = request.args.get('n') or request.form.get('n')
    key = request.args.get('k') or request.form.get('k')
    d['name'] = name
    d['key'] = key
    d['quote'] = url_quote
    n = 0
    try:
        if name == 'readings':
            values = unihan.get_values_of_reading(key)
        elif name == 'variants':
            values = unihan.get_values_of_variant(key)
            if key.endswith('Variant'):
                values = [unichar(int(v[2:], 16)) for v in values]
                d['quote'] = url_quoted_unicode_value
        elif name == 'tables':
            values = cjkvi.get_values_of_table(key)
        for s in values:
            ar.append(s)
            n += 1
    except:
        d['error'] = traceback.format_exc()
        traceback.print_exc()
    d['cnt'] = n
    return render_template('keyvalues.html', **d)

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer

    http_server = WSGIServer(('0.0.0.0', 8080), app)
    http_server.serve_forever()
# vim:ts=4:sw=4:et:ai:cc=80
