#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import struct
import glob
import re
import traceback

import ids

def unichar(i):
    try:
        return unichr(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')

def _load_ids_analysis(fname):
    d = {}
    with open(fname) as f:
        for line in f.read().splitlines():
            if not line or line.startswith('#'):
                continue
            try:
                assert line.startswith('U+')
                ar = line.decode('utf-8').split('\t')
                assert len(ar) > 2
                if ar[0].count('?'):
                    continue
                code = int(ar[0][2:], 16)
                assert ar[1] == unichar(code)
                while len(ar) < 6:
                    ar.append(u'')
                if not d.has_key(code):
                    d[code] = ar[2:]
                elif d[code][0] != ar[2]:
                    for i in xrange(len(d[code])):
                        d[code][i] = u'%s / %s' % (d[code][i], ar[2 + i])
            except:
                print >> sys.stderr, ar
                raise
    for code in d.iterkeys():
        for i in xrange(len(d[code])):
            if not d[code][i].replace(u' / ', u''):
                d[code][i] = u''
    return d

_ids_analysis = _load_ids_analysis('cjkvi-ids/ids-analysis.txt')
_marks = set([u'→', u'←', u'<', u'>'])

def get_analysis(code, linker=None):
    ar = _ids_analysis.get(code)
    if ar:
        br = []
        for c in ar[0]:
            if ids.isidc(c):
                br.append(c)
            elif 0xD800 <= ord(c) < 0xDC00:
                br.append(c)
            elif 0xDC00 <= ord(c) < 0xE000:
                assert 0xD800 <= ord(br[-1]) <= 0xDC00
                br[-1] += c
                if linker:
                    br[-1] = linker(br[-1])
            elif linker and ord(c) > 0x80 and c not in _marks:
                br.append(linker(c))
            else:
                br.append(c)
        for i in (1, 3):
            if ar[i]:
                br.append(u'　')
                br.append(ar[i])
        return u''.join(br)

_variants_paren_sub = {
        u'（': u'<sub>（',
        u'）': u'）</sub>',
        }
_variants_paren_pat = re.compile(u'|'.join(_variants_paren_sub.keys()))
_variants_paren_repl = lambda m: _variants_paren_sub[m.group()]
def _variants_rename(s):
    return _variants_paren_pat.sub(_variants_paren_repl, s)
def _load_variants(directory):
    d = {}
    t = {}
    for fname in glob.glob(os.path.join(directory, '*.txt')):
        if os.path.basename(fname) == 'jp-old-style.txt':
            continue
        with open(fname) as f:
            rev = {}
            try:
                for line in f.read().splitlines():
                    if not line or line.startswith('#'):
                        continue
                    line = line.decode('utf-8')
                    ar = line.split(',')
                    rel = ar[1]
                    a, b = ar[0], ar[2]
                    if rel.startswith('<'):
                        if rel.startswith('<rev'):
                            rev[a] = b
                        elif rel == '<name>':
                            t[a] = _variants_rename(b)
                        else:
                            assert False
                    elif a == b:
                        pass
                    else:
                        if not t.has_key(rel):
                            for k, v in rev.iteritems():
                                if k == rel and t.has_key(v):
                                    t[k] = t[v]
                                    break
                                elif v == rel and t.has_key(k):
                                    t[v] = t[k]
                                    break
                            assert t.has_key(rel)
                        dd = d.setdefault(a, {})
                        tt = dd.setdefault(b, set())
                        tt.add(rel)
                        if rev.has_key(rel):
                            dd = d.setdefault(b, {})
                            tt = dd.setdefault(a, set())
                            tt.add(rev[rel])
            except:
                print >> sys.stderr, fname, line.encode('gb18030')
                raise
    return d, t

_variants, _variant_rel_name_map = _load_variants('cjkvi-variants')

def get_variants(code, linker=None):
    if type(code) == unicode:
        c = code
    else:
        c = unichar(code)
    d = _variants.get(c)
    if d:
        br = []
        for c in sorted(d.keys()):
            if br:
                br.append(u'\u3000')
            if linker:
                br.append(linker(c))
            else:
                br.append(c)
            br.append(u'<sub>')
            br.append(u' (')
            br.append(u'; '.join(map(_variant_rel_name_map.get, sorted(d[c]))))
            br.append(u')')
            br.append(u'</sub>')
        return u''.join(br)

if __name__ == '__main__':
    pass
# vim:ts=4:sw=4:et:ai:cc=80
