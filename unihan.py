#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import string, re
try:
    import czipfile as zipfile
except:
    import zipfile
import xml.sax.saxutils

_unihan_zip = zipfile.ZipFile(os.path.join(os.path.dirname(__file__),
    'unihan', 'Unihan.zip'), 'r')

def _read_data(fname, fields=set(), d=None):
    f = _unihan_zip.open(fname)
    if f:
        if d is None:
            d = {}
        for line in f:
            if line.startswith('#'):
                continue
            if line == '\n':
                continue
            assert line.startswith('U+')
            ar = line.split('\t')
            assert len(ar) == 3
            if fields and not ar[1] in fields:
                continue
            code = int(ar[0][2:], 16)
            t = d.setdefault(code, {})
            t[ar[1]] = ar[2].rstrip().decode('utf-8')
        f.close()
        return d

def _get_data_by_code(d, code, keys=None):
    try:
        t = d[code]
    except:
        return
    if not keys:
        return t.copy()
    if type(keys) in (str, unicode):
        return t.get(keys)
    r = {}
    for k in keys:
        try:
            r[k] = t[k]
        except:
            pass
    return r

def _default_linker(k, v):
    return '<a href="/l?k=%s&v=%s">%s</a>' % (k, v, v)

def _get_data_by_code_w_link(d, code, keys=None, linker=None,
        splitter={}, reverse_indices={}):
    if not linker:
        linker = _default_linker
    t = _get_data_by_code(d, code, keys)
    if t:
        for k in t.keys():
            v = t[k]
            f = splitter.get(k, string.split)
            try:
                ar = f(v)
            except:
                print >> sys.stderr, f, v
                raise
            r = []
            p = 0
            for s in ar:
                try:
                    q = v.index(s, p)
                    if q > p:
                        r.append(xml.sax.saxutils.escape(v[p:q]))
                    if not reverse_indices or len(reverse_indices[k][s]) > 1:
                        r.append(linker(k, s))
                    else:
                        r.append(s)
                    p = q + len(s)
                except:
                    print >> sys.stderr, s, v[p:]
                    raise
            if p < len(v):
                r.append(xml.sax.saxutils.escape(v[p:]))
            t[k] = ''.join(r)
    return t

def _build_reverse_indices(d, splitter={}, fields=set()):
    r = {}
    for code, t in d.iteritems():
        for k, v in t.iteritems():
            if fields and not k in fields:
                continue
            try:
                dd = r[k]
            except KeyError:
                dd = r[k] = {}
            f = splitter.get(k, string.split)
            try:
                ar = f(v)
            except:
                print >> sys.stderr, f, v
                raise
            for s in ar:
                try:
                    dd[s].add(code)
                except KeyError: 
                    dd[s] = set([code])
    return r

def _lookup_reverse_indices(d, k, v):
    try:
        t = d[k]
    except:
        print >> sys.stderr, k
        raise
    try:
        return sorted(t[v])
    except:
        print >> sys.stderr, v
        raise

_readings = _read_data('Unihan_Readings.txt')
_pat_semicolon_comma_space = re.compile(r'[;,] *')
_pat_remove_paren_digits = re.compile(r'(\S+)\(\d+\)')
def _split_hanyu_pinyin(s):
    r = []
    for s in s.split():
        a, b = s.split(':')
        for x in a.split(','):
            r.append(x[:x.index('.')])
        r.extend(b.split(','))
    return r
_readings_splitter = dict(
        kDefinition = _pat_semicolon_comma_space.split,
        kHanyuPinlu = _pat_remove_paren_digits.findall,
        kHanyuPinyin = _split_hanyu_pinyin,
        kXHC1983 = _split_hanyu_pinyin,
        )
if True:
    _read_data('Unihan_DictionaryIndices.txt', set([
        'kGSR',
        ]), _readings)
    _pat_find_4_digits = re.compile(r'\d{4}')
    _readings_splitter['kGSR'] = _pat_find_4_digits.findall
    if True:
        _read_data('Unihan_DictionaryLikeData.txt', set([
            'kFenn',
            ]), _readings)
        _pat_fenn = re.compile(r'\d+|[A-KP*]')
        _readings_splitter['kFenn'] = _pat_fenn.findall
_readings_rev_idx = _build_reverse_indices(_readings, _readings_splitter)

def get_readings_by_code(code, keys=None):
    return _get_data_by_code(_readings, code, keys)

def get_readings_by_code_w_link(code, keys=None, linker=None):
    return _get_data_by_code_w_link(_readings, code, keys, linker,
            _readings_splitter, _readings_rev_idx)

def get_codes_by_reading(k, v):
    return _lookup_reverse_indices(_readings_rev_idx, k, v)

_variants = _read_data('Unihan_Variants.txt')
_read_data('Unihan_IRGSources.txt', set([
    'kCompatibilityVariant',
    'kIICore',
    'kRSUnicode',
    ]), _variants)
_pat_u_wo_less_than = re.compile(r'U\+[^< ]+')
_pat_ABC_GHJKMPT = re.compile(r'[ABCGHJKMPT]')
_variants_splitter = dict(
        kSemanticVariant = _pat_u_wo_less_than.findall,
        kSpecializedSemanticVariant = _pat_u_wo_less_than.findall,
        kZVariant = _pat_u_wo_less_than.findall,
        kIICore = _pat_ABC_GHJKMPT.findall,
        )
_variants_rev_idx = _build_reverse_indices(_variants, _variants_splitter)

def get_variants_by_code(code, keys=None):
    return _get_data_by_code(_variants, code, keys)

def get_variants_by_code_w_link(code, keys=None, linker=None):
    return _get_data_by_code_w_link(_variants, code, keys, linker,
            _variants_splitter)

def get_codes_by_variant(k, v):
    return _lookup_reverse_indices(_variants_rev_idx, k, v)

if __name__ == '__main__':
    pass
# vim:ts=4:sw=4:et:ai:cc=80
