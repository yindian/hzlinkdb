#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import string, re
try:
    import czipfile as zipfile
except:
    import zipfile
import xml.sax.saxutils
import struct

def unichar(i):
    try:
        return unichr(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')

_unihan_zip = zipfile.ZipFile(os.path.join(os.path.dirname(__file__),
    'unihan', 'Unihan.zip'), 'r')

def _read_data(fname, fields=set(), d=None):
    f = _unihan_zip.open(fname)
    if f:
        if d is None:
            d = {}
        if 1 <= len(fields) <= 3:
            s = list(fields)[0]
            t = '\t' + s + '\t'
            tl = len(t)
            buf = f.read()
            p = buf.find(t)
            q = 0
            while p > 0:
                q = buf.rindex('\n', q, p)
                assert buf.startswith('U+', q + 1)
                code = int(buf[q+3:p], 16)
                p += tl
                q = buf.find('\n', p)
                d.setdefault(code, {})[s] = buf[p:q].decode('utf-8')
                p = buf.find(t, q)
            f.close()
            if len(fields) == 1:
                return d
        if 2 <= len(fields) <= 3:
            s = list(fields)[1]
            t = '\t' + s + '\t'
            tl = len(t)
            p = buf.find(t)
            q = 0
            while p > 0:
                q = buf.rindex('\n', q, p)
                assert buf.startswith('U+', q + 1)
                code = int(buf[q+3:p], 16)
                p += tl
                q = buf.find('\n', p)
                d.setdefault(code, {})[s] = buf[p:q].decode('utf-8')
                p = buf.find(t, q)
            if len(fields) == 2:
                return d
        if len(fields) == 3:
            s = list(fields)[2]
            t = '\t' + s + '\t'
            tl = len(t)
            p = buf.find(t)
            q = 0
            while p > 0:
                q = buf.rindex('\n', q, p)
                assert buf.startswith('U+', q + 1)
                code = int(buf[q+3:p], 16)
                p += tl
                q = buf.find('\n', p)
                d.setdefault(code, {})[s] = buf[p:q].decode('utf-8')
                p = buf.find(t, q)
            return d
        for line in f.read().splitlines():
            if line.startswith('#'):
                continue
            if not line:
                continue
            assert line.startswith('U+')
            ar = line.split('\t')
            assert len(ar) == 3
            if fields and not ar[1] in fields:
                continue
            code = int(ar[0][2:], 16)
            t = d.setdefault(code, {})
            t[ar[1]] = ar[2].decode('utf-8')
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
        splitter={}, reverse_indices={}, transformer={}):
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
                    if reverse_indices and transformer.has_key(k):
                        f = transformer[k]
                        r.append(linker(k, f(s)))
                        r.append('&nbsp;')
                        r.append(s)
                    elif not reverse_indices or len(reverse_indices[k][s]) > 1:
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

def _build_reverse_indices(d, splitter={}, fields=set(), transformer={}):
    assert type(fields) == set
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
            if transformer.has_key(k):
                f = transformer[k]
            else:
                f = None
            for s in ar:
                if f:
                    try:
                        s = f(s)
                        assert s
                    except:
                        print >> sys.stderr, k, f, s
                        raise
                try:
                    dd[s].add(code)
                except KeyError: 
                    dd[s] = set([code])
    return r

def _lookup_reverse_indices(d, k, v, idx={}, sort_key_factory={}):
    try:
        t = d[k]
    except:
        print >> sys.stderr, k
        raise
    try:
        if sort_key_factory.has_key(k):
            return sorted(t[v], key=sort_key_factory[k](idx, k, v))
        return sorted(t[v])
    except:
        print >> sys.stderr, v
        raise

def _list_reverse_indices_values(d, k, sort_key={}):
    try:
        t = d[k]
        return sorted(t.keys(), key=sort_key.get(k))
    except:
        print >> sys.stderr, k
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
_readings_transformer = {}
_readings_value_sort_key = {}
_readings_code_sort_key_factory = {}
try:
    import icu
    loc_zh = icu.Locale.getChina()
    col_zh = icu.Collator.createInstance(loc_zh)
    loc_vi = icu.Locale('vi')
    col_vi = icu.Collator.createInstance(loc_vi)
    _readings_value_sort_key.update(dict(
        kHanyuPinlu = col_zh.getSortKey,
        kHanyuPinyin = col_zh.getSortKey,
        kMandarin = col_zh.getSortKey,
        kTang = col_zh.getSortKey,
        kVietnamese = col_vi.getSortKey,
        kXHC1983 = col_zh.getSortKey,
        ))
    loc_zh_strk = icu.Locale.createFromName('zh@collation=stroke')
    col_zh_strk = icu.Collator.createInstance(loc_zh_strk)
    def _get_strokes_sort_key_by_code(code):
        return col_zh_strk.getSortKey(unichar(code))
    def _sort_code_by_strokes_factory(d, k, v):
        return _get_strokes_sort_key_by_code
    def _hanyu_pinlu_sort_key_factory(d, k, v):
        v += '('
        def _sort_key(code):
            for s in d[code][k].split():
                if s.startswith(v):
                    return -int(s[len(v):-1])
            assert False
        return _sort_key
    def _hanyu_pinyin_sort_key_factory(d, k, v):
        if v.isdigit():
            v += '.'
            def _sort_key(code):
                for s in d[code][k].split():
                    for t in s[:s.index(':')].split(','):
                        if t.startswith(v):
                            return t
                assert False
            return _sort_key
        def _sort_key(code):
            for s in d[code][k].split():
                a, b = s.split(':')
                for t in b.split(','):
                    if t == v:
                        return a.split(',')[0]
            assert False
        return _sort_key
    _readings_code_sort_key_factory.update(dict(
        kHanyuPinlu = _hanyu_pinlu_sort_key_factory,
        kHanyuPinyin= _hanyu_pinyin_sort_key_factory,
        kXHC1983    = _hanyu_pinyin_sort_key_factory,
        ))
except:
    traceback.print_exc()
    def _sort_code_by_strokes_factory(d, k, v):
        return lambda code: code
    pass
def _numeric_sort(s):
    try:
        return int(s)
    except:
        return s
_pat_number = re.compile(r'[+-]?\d+')
def _multi_numeric_sort(s):
    try:
        return map(int, _pat_number.findall(s)) + _pat_number.split(s)
    except:
        return [s]
def _unicode_point_sort(s):
    try:
        return int(s[2:], 16)
    except:
        return s
if True:
    _read_data('Unihan_DictionaryIndices.txt', set([
        'kGSR',
        'kSBGY',
        ]), _readings)
    _pat_find_4_digits = re.compile(r'\d{4}')
    _readings_splitter['kGSR'] = _pat_find_4_digits.findall
    def _gsr_sort_key_factory(d, k, v):
        def _sort_key(code):
            for s in d[code][k].split():
                if s.startswith(v):
                    n = string.ascii_lowercase.index(s[4])
                    if len(s) > 5:
                        n += 26
                    return n
            assert False
        return _sort_key
    _readings_code_sort_key_factory['kGSR'] = _gsr_sort_key_factory
    import sbgy
    sbgy.init_data(_readings, 'kSBGY')
    _readings_transformer['kSBGY'] = sbgy.pos2rhyme
    _readings_value_sort_key['kSBGY'] = sbgy.rhyme_index
    _readings_code_sort_key_factory['kSBGY'] = sbgy.code_sort_key_factory
    if True:
        _read_data('Unihan_DictionaryLikeData.txt', set([
            'kFenn',
            ]), _readings)
        _pat_fenn = re.compile(r'\d+|[A-KP*]')
        _readings_splitter['kFenn'] = _pat_fenn.findall
        _readings_value_sort_key['kFenn'] = _numeric_sort
        _readings_code_sort_key_factory['kFenn'] = _sort_code_by_strokes_factory
_readings_rev_idx = _build_reverse_indices(_readings, _readings_splitter,
        transformer=_readings_transformer)

def get_readings_by_code(code, keys=None):
    return _get_data_by_code(_readings, code, keys)

def get_readings_by_code_w_link(code, keys=None, linker=None):
    return _get_data_by_code_w_link(_readings, code, keys, linker,
            _readings_splitter, _readings_rev_idx, _readings_transformer)

def get_codes_by_reading(k, v):
    return _lookup_reverse_indices(_readings_rev_idx, k, v,
            _readings, _readings_code_sort_key_factory)

def get_values_of_reading(k):
    return _list_reverse_indices_values(_readings_rev_idx,
            k, _readings_value_sort_key)

_variants = _read_data('Unihan_Variants.txt')
_read_data('Unihan_IRGSources.txt', set([
    'kCompatibilityVariant',
    'kIICore',
    'kRSUnicode',
    ]), _variants)
_read_data('Unihan_OtherMappings.txt', set([
    'kGB0',
    'kGB1',
    'kBigFive',
    'kJis0',
    ]), _variants)
_pat_u_wo_less_than = re.compile(r'U\+[^< ]+')
_pat_ABC_GHJKMPT = re.compile(r'[ABCGHJKMPT]')
_pat_quwei_qu = re.compile(r'([0-9A-F]{2})[0-9A-F]{2}')
_variants_splitter = dict(
        kSemanticVariant = _pat_u_wo_less_than.findall,
        kSpecializedSemanticVariant = _pat_u_wo_less_than.findall,
        kZVariant = _pat_u_wo_less_than.findall,
        kIICore = _pat_ABC_GHJKMPT.findall,
        kGB0 = _pat_quwei_qu.findall,
        kGB1 = _pat_quwei_qu.findall,
        kBigFive = _pat_quwei_qu.findall,
        kJis0 = _pat_quwei_qu.findall,
        )
_variants_value_sort_key = dict(
        kRSUnicode = _multi_numeric_sort,
        kCompatibilityVariant = _unicode_point_sort,
        kSemanticVariant = _unicode_point_sort,
        kSimplifiedVariant = _unicode_point_sort,
        kSpecializedSemanticVariant = _unicode_point_sort,
        kTraditionalVariant = _unicode_point_sort,
        kZVariant = _unicode_point_sort,
        )
_variants_code_sort_key_factory = {}
def _iicore_sort_key_factory(d, k, v):
    def _sort_key(code):
        for s in d[code][k].split():
            if s.find(v) >= 0:
                n = string.ascii_uppercase.index(s[0]) * 10
                n -= len(s)
                return (n, code)
        assert False
    return _sort_key
_variants_code_sort_key_factory['kIICore'] = _iicore_sort_key_factory
_variants_rev_idx = _build_reverse_indices(_variants, _variants_splitter)

def get_variants_by_code(code, keys=None):
    return _get_data_by_code(_variants, code, keys)

def get_variants_by_code_w_link(code, keys=None, linker=None):
    return _get_data_by_code_w_link(_variants, code, keys, linker,
            _variants_splitter)

def get_codes_by_variant(k, v):
    return _lookup_reverse_indices(_variants_rev_idx, k, v,
            _variants, _variants_code_sort_key_factory)

def get_values_of_variant(k):
    return _list_reverse_indices_values(_variants_rev_idx,
            k, _variants_value_sort_key)

if __name__ == '__main__':
    pass
# vim:ts=4:sw=4:et:ai:cc=80
