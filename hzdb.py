#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import sys, os
import string
import re
import time
_start = time.clock()
import unihan
_end = time.clock()
if __name__ == '__main__':
    print >> sys.stderr, _end - _start, 'seconds elapsed importing unihan'
_start = time.clock()
import cjkvi
_end = time.clock()
if __name__ == '__main__':
    print >> sys.stderr, _end - _start, 'seconds elapsed importing cjkvi'

assert sqlite3.sqlite_version_info >= (3, 8, 2) # for WITHOUT ROWID

try:
    import icu
    normalize_nfd = icu.Normalizer2.getInstance(None, 'nfc',
            icu.UNormalizationMode2.DECOMPOSE).normalize
except:
    import re
    _norm_sub = {}
    _py_tones = u'\u0304\u0301\u030C\u0300'
    _py_tone_xform = {
            u'a':       u'āáǎà',
            u'o':       u'ōóǒò',
            u'e':       u'ēéěè',
            u'i':       u'īíǐì',
            u'u':       u'ūúǔù',
            u'u\u0308': u'ǖǘǚǜü',
            u'e\u0302': u'?ế?ềê',
            u'm':       u'?ḿ??',
            u'n':       u'?ńňǹ',
            }
    for k, v in _py_tone_xform.iteritems():
        for i in xrange(len(v)):
            if i == len(_py_tones):
                _norm_sub[v[i]] = k
            elif v[i] != u'?':
                _norm_sub[v[i]] = k + _py_tones[i]
    _norm_pat = re.compile(u'|'.join(_norm_sub.keys()))
    _norm_repl = lambda m: _norm_sub[m.group()]
    def normalize_nfd(s):
        return _norm_pat.sub(_norm_repl, s)
_py_tones = u'\u0304\u0301\u030C\u0300'
_py_umlaut= u'\u0308'
_py_flex  = u'\u0302'
_py_char_set = set(string.ascii_lowercase + _py_tones + _py_umlaut + _py_flex)
def normalize_pinyin(s):
    if not s:
        return s
    if type(s) == str:
        s = s.decode('utf-8')
    try:
        s.encode('ascii')
        if s[-1].isdigit():
            assert u'1' <= s[-1] <= u'5'
            assert s[:-1].isalpha()
            return s
        assert s.isalpha()
        return s + u'5'
    except:
        pass
    try:
        tone = 5
        ar = []
        for c in normalize_nfd(s):
            assert c in _py_char_set
            if c.isalpha():
                ar.append(c)
            else:
                if c == _py_umlaut:
                    assert ar[-1] == u'u'
                    ar[-1] = u'v'
                elif c == _py_flex:
                    assert ar[-1] == u'e'
                    ar[-1] = u'ee'
                else:
                    assert tone == 5
                    tone = _py_tones.index(c) + 1
        ar.append(str(tone))
        return u''.join(ar)
    except:
        print >> sys.stderr, repr(s)
        raise

_py_tone_digit_pat = re.compile(ur'[1-5]')
def validate_pinyin(s):
    assert len(s.split()) == 1
    s.encode('ascii')
    assert u'1' <= s[-1] <= u'5'
    assert all([x.isalpha() for x in _py_tone_digit_pat.split(s)[:-1]])
    return True

def validate_mgcr(s):
    assert len(s.split()) == 1
    s.encode('ascii')
    assert s.isalpha()
    return True

def create(db):
    cur = db.cursor()
    cur.execute('pragma page_size = 4096')
    cur.execute('drop table if exists HZGraph')
    cur.execute('create table HZGraph ('
            'tHanzi     text primary key, '
            'tParent    text, '
            'tSimp      text, '
            'tGBFB      text, '
            'tTrad      text, '
            'tB5FB      text, '
            'tJpShin    text, '
            'tJISFB     text'
            ') without rowid')
    cur.execute('create trigger HZGDefaults after insert on HZGraph '
            'when min(new.tSimp, new.tGBFB, new.tTrad, new.tB5FB,'
            ' new.tJpShin, new.tJISFB) is null '
            'begin'
            ' update HZGraph set'
            ' tSimp = ifnull(new.tSimp, new.tHanzi),'
            ' tGBFB = ifnull(new.tGBFB, new.tHanzi),'
            ' tTrad = ifnull(new.tTrad, new.tHanzi),'
            ' tB5FB = ifnull(new.tB5FB, new.tHanzi),'
            ' tJpShin = ifnull(new.tJpShin, new.tHanzi),'
            ' tJISFB = ifnull(new.tJISFB, new.tHanzi)'
            ' where tHanzi = new.tHanzi; '
            'end')
    cur.execute('create trigger HZGParChkIns before insert on HZGraph '
            'when new.tParent is not null '
            'begin'
            ' select raise(fail, "non-existent parent") where'
            ' not exists (select 1 from HZGraph where tHanzi = new.tParent); '
            'end')
    cur.execute('create trigger HZGParChk before update of tParent on HZGraph '
            'when new.tParent is not null '
            'begin'
            ' select raise(fail, "parent loop") where new.tParent = new.tHanzi;'
            ' select raise(fail, "non-existent parent") where'
            ' not exists (select 1 from HZGraph where tHanzi = new.tParent); '
            'end')
    cur.execute('create trigger HZGHzChk before update of tHanzi on HZGraph '
            'begin'
            ' select raise(fail, "parent loop") where new.tParent = new.tHanzi;'
            ' select raise(fail, "would break parent reference") where'
            ' exists (select 1 from HZGraph where tParent=old.tHanzi limit 1); '
            'end')
    cur.execute('create trigger HZGParChkDel before delete on HZGraph '
            'begin'
            ' select raise(fail, "would break parent reference") where'
            ' exists (select 1 from HZGraph where tParent=old.tHanzi limit 1); '
            'end')
    cur.execute('drop table if exists HZMorph')
    cur.execute('create table HZMorph ('
            'tHZ        text, '
            'tPY        text default "", '
            'tMGCR      text default "", '
            'nFreq      integer, '
            'bInGY      boolean, '
            'tPhon      text, '
            'tPhPY      text, '
            'tPhGC      text, '
            'bPhSP      boolean, '
            'tMsPY      text, '
            'tSndh      text, '
            'tVar1      text, '
            'tVar2      text, '
            'tVar3      text, '
            'tCogn      text, '
            'tCoin      text, '
            'tSmpl      text, '
            'tRem       text, '
            'primary key (tHZ, tPY, tMGCR)'
            ') without rowid')
    cur.execute('create trigger HZMPhChkIns before insert on HZMorph '
            'when new.tPhon is not null '
            'begin'
            ' select raise(fail, "non-existent phonetic") where'
            '  not exists (select 1 from HZMorph where tHZ = new.tPhon);'
           #' select raise(fail, "ambiguous phonetic") where'
           #'  new.tPhPY is null and'
           #'  1 < (select count(1) from HZMorph where tHZ = new.tPhon);'
            ' select raise(fail, "non-existent phonetic pinyin") where'
            '  new.tPhPY is not null and not exists (select 1 from HZMorph'
            '  where tHZ = new.tPhon and tPY = new.tPhPY); '
           #' select raise(fail, "ambiguous phonetic pinyin") where'
           #'  new.tPhPY is not null and new.tPhGC is null and 1 < (select'
           #'  count(1) from HZMorph where tHZ=new.tPhon and tPY=new.tPhPY);'
            ' select raise(fail, "non-existent phonetic MGCR") where'
            '  new.tPhPY is not null and new.tPhGC is not null and not exists'
            '  (select 1 from HZMorph where tHZ = new.tPhon and'
            '   tPY = new.tPhPY and tMGCR = new.tPhGC); '
            'end')
    cur.execute('create trigger HZMPhChk before update of '
            'tPhon, tPhPY, tPhGC on HZMorph '
            'when new.tPhon is not null '
            'begin'
            ' select raise(fail, "phonetic loop") where new.tPhon = new.tHZ;'
            ' select raise(fail, "non-existent phonetic") where'
            '  not exists (select 1 from HZMorph where tHZ = new.tPhon);'
            ' select raise(fail, "non-existent phonetic pinyin") where'
            '  new.tPhPY is not null and not exists (select 1 from HZMorph'
            '  where tHZ = new.tPhon and tPY = new.tPhPY); '
            ' select raise(fail, "non-existent phonetic MGCR") where'
            '  new.tPhPY is not null and new.tPhGC is not null and not exists'
            '  (select 1 from HZMorph where tHZ = new.tPhon and'
            '   tPY = new.tPhPY and tMGCR = new.tPhGC); '
            'end')
    cur.execute('create trigger HZMHzChk before update of tHZ on HZMorph '
            'begin'
            ' select raise(fail, "protected from updating hanzi"); '
            'end')
    cur.execute('create trigger HZMPyChk before update of tPY on HZMorph '
            'begin'
            ' select raise(fail, "would break pinyin reference") where'
            ' exists (select 1 from HZMorph where tPhon = old.tHZ and'
            ' tPhPY = old.tPY and (tPhGC = old.tMGCR or (tPhGC is null and not'
            ' exists (select 1 from HZMorph where tHZ = old.tHZ and'
            ' tPY = old.tPY and tMGCR != old.tMGCR))) limit 1); '
            'end')
    cur.execute('create trigger HZMMgcrChk before update of tMGCR on HZMorph '
            'begin'
            ' select raise(fail, "would break MGCR reference") where'
            ' exists (select 1 from HZMorph where tPhon = old.tHZ and'
            ' tPhPY = old.tPY and tPhGC = old.tMGCR limit 1); '
            'end')
    cur.execute('create trigger HZMPhChkDel before delete on HZMorph '
            'begin'
            ' select raise(fail, "would break phonetic reference") where'
            ' exists (select 1 from HZMorph where tPhon = old.tHZ'
            ' and (tPhPY is null or tPhPY = old.tPY)'
            ' and (tPhGC is null or tPhGC = old.tMGCR) limit 1); '
            'end')

unichar = cjkvi.unichar
ordinal = cjkvi.ordinal

def ishanzi(s):
    assert ordinal(s) >= 0x2E80
    return True

def get_graph_by_code(db, code):
    cur = db.cursor()
    cur.execute('select * from HZGraph where tHanzi = ?', (unichar(code),))
    return cur.fetchone()

def get_morph_by_code(db, code):
    cur = db.cursor()
    cur.execute('select * from HZMorph where tHZ = ?'
            ' order by nFreq desc, tPY'
            , (unichar(code),))
    return cur.fetchall()

def delete_from(db, table, d):
    assert d
    sql = 'delete from %s where %s' % (
            table,
            ' and '.join(['%s = ?' % (s,) for s in d.iterkeys()]),
            )
    try:
        db.execute(sql, d.values())
    except:
        print >> sys.stderr, sql, d
        raise

def _chk(cond):
    if not cond:
        raise AssertionError
    return True

_check_graph_func = dict(
        tHanzi     = lambda s: s,
        tParent    = lambda s: s is None or ishanzi(s),
        tSimp      = lambda s: _chk(map(ishanzi, s.split())),
        tGBFB      = lambda s: _chk(len(s.split()) == 1) and s.encode('gb2312'),
        tTrad      = lambda s: _chk(map(ishanzi, s.split())),
        tB5FB      = lambda s: _chk(len(s.split()) == 1) and s.encode('big5'),
        tJpShin    = lambda s: _chk(map(ishanzi, s.split())),
        tJISFB     = lambda s: _chk(len(s.split()) == 1) and s.encode('euc-jp'),
        )
_check_morph_func = dict(
        tHZ   = lambda s, z: s,
        tPY   = lambda s, z: validate_pinyin(s),
        tMGCR = lambda s, z: validate_mgcr(s),
        nFreq = lambda s, z: s is None or int(s),
        bInGY = lambda s, z: s is None or _chk(int(s) in (0, 1)),
        tPhon = lambda s, z: s is None or ishanzi(s),
        tPhPY = lambda s, z: s is None or validate_pinyin(s),
        tPhGC = lambda s, z: s is None or validate_mgcr(s),
        bPhSP = lambda s, z: s is None or _chk(int(s) in (0, 1)),
        tMsPY = lambda s, z: s is None or map(validate_pinyin, s.split()),
        tSndh = lambda s, z: s is None or map(validate_pinyin, s.split()),
        tVar1 = lambda s, z: s is None or _chk(map(ishanzi, s.split())),
        tVar2 = lambda s, z: s is None or _chk(map(ishanzi, s.split())),
        tVar3 = lambda s, z: s is None or _chk(map(ishanzi, s.split())),
        tCogn = lambda s, z: s is None or _chk(map(ishanzi, s.split())),
        tCoin = lambda s, z: s is None or _chk(map(ishanzi, s.replace(' ',''))),
        tSmpl = lambda s, z: s is None or _chk([x.index(z) for x in s.split()]),
        tRem  = lambda s, z: s,
        )
def _check_field(table, field, val, d):
    if table == 'HZGraph':
        _check_graph_func[field](val)
    else:
        assert table == 'HZMorph'
        _check_morph_func[field](val, d['tHZ'])

def update_field(db, table, d, field, val):
    assert d
    if type(val) == unicode:
        val = val.strip()
        if field in ('tPY', 'tPhPY'):
            val = normalize_pinyin(val)
    _check_field(table, field, val, d)
    sql = 'update %s set %s = ? where %s' % (
            table,
            field,
            ' and '.join(['%s = ?' % (s,) for s in d.iterkeys()]),
            )
    try:
        db.execute(sql, [val] + d.values())
    except:
        print >> sys.stderr, sql, d
        raise
    if d.has_key(field):
        d[field] = val
    cur = db.cursor()
    sql = 'select * from %s where %s' % (
            table,
            ' and '.join(['%s = ?' % (s,) for s in d.iterkeys()]),
            )
    try:
        cur.execute(sql, d.values())
    except:
        print >> sys.stderr, sql, d
        raise
    return cur.fetchone()

def _insert_db(db, table, d):
    assert d
    sql = 'insert into %s (%s) values (%s)' % (
            table,
            ', '.join(d.keys()),
            ', '.join([type(s) == unicode and '"%s"' % s or str(s)
                for s in d.itervalues()]),
            )
    try:
        db.execute(sql)
    except:
        print >> sys.stderr, sql
        raise

def insert_code_to(db, table, code):
    d = {}
    c = unichar(code)
    if table == 'HZGraph':
        d['tHanzi'] = c
    elif table == 'HZMorph':
        d['tHZ'] = c
        d['tPY'] = u''
        d['tMGCR'] = u''
    _insert_db(db, table, d)
    cur = db.cursor()
    sql = 'select * from %s where %s' % (
            table,
            ' and '.join(['%s = ?' % (s,) for s in d.iterkeys()]),
            )
    try:
        cur.execute(sql, d.values())
    except:
        print >> sys.stderr, sql, d
        raise
    return cur.fetchone()

def insert_graph(db, *args, **kwargs):
    d = {}
    if args:
        d['tHanzi'] = args[0]
        assert len(args) <= 1
    d.update(**kwargs)
    return _insert_db(db, 'HZGraph', d)

def insert_morph(db, *args, **kwargs):
    d = {}
    if args:
        d['tHZ'] = args[0]
        if len(args) > 1:
            d['tPY'] = args[1]
            if len(args) > 2:
                d['tMGCR'] = args[2]
                assert len(args) <= 3
    d.update(**kwargs)
    if d.has_key('tPY'):
        d['tPY'] = normalize_pinyin(d['tPY'])
    if d.has_key('tPhPY'):
        d['tPhPY'] = normalize_pinyin(d['tPhPY'])
    return _insert_db(db, 'HZMorph', d)

def init_data(db):
    name = 'zibiao2013'
    levels = cjkvi.get_values_of_table(name)
    assert len(levels) == 3
    done = set()
    def _process_code(code, freq):
        c = unichar(code)
        # pinyin readings
        ar = []
        def add_ar(k, v):
            ar.append(v)
            return ''
        unihan.get_readings_by_code_w_link_all(code, 'kHanyuPinlu', add_ar)
        if freq & 1 == 0: # not in zibiao2013
            ar = []
        if ar:
            br = unihan.get_readings_by_code(code, 'kHanyuPinlu').split()
            assert len(ar) == len(br)
            for i in xrange(len(ar)):
                assert br[i].startswith(ar[i] + '(')
                assert br[i].endswith(')')
                n = int(br[i][len(ar[i])+1:-1])
                assert n > 7
                insert_morph(db, c, tPY=ar[i], nFreq=n)
            n = 1
        else:
            n = freq
        br = []
        def add_br(k, v):
            if v not in ar and not v.isdigit():
                br.append(v)
            return ''
        unihan.get_readings_by_code_w_link_all(code, 'kXHC1983', add_br)
        for s in br:
            insert_morph(db, c, tPY=s, nFreq=n)
            n = 1
        if not ar and not br:
            unihan.get_readings_by_code_w_link_all(code,
                    'kHanyuPinyin', add_br)
            cr = set()
            for s in br:
                if s in cr:
                    continue
                cr.add(s)
                insert_morph(db, c, tPY=s, nFreq=n)
                n = 1
            if not br:
                unihan.get_readings_by_code_w_link_all(code,
                        'kMandarin', add_ar)
                n = 0
                for s in ar:
                    insert_morph(db, c, tPY=s, nFreq=n)
        # variant forms
        d = {}
        cr = []
        def add_cr(k, v):
            cr.append(unichar(int(v[2:], 16)))
            return ''
        unihan.get_variants_by_code_w_link(code,
                'kSimplifiedVariant', add_cr)
        if cr:
            d['tSimp'] = ' '.join(cr)
            cr = []
        unihan.get_variants_by_code_w_link(code,
                'kTraditionalVariant', add_cr)
        if cr:
            d['tTrad'] = ' '.join(cr)
            cr = []
        unihan.get_variants_by_code_w_link(code,
                'kZVariant', add_cr)
        if cr:
            d['tJpShin'] = ' '.join(cr)
            cr = []
        try:
            c.encode('gb2312')
        except UnicodeEncodeError:
            try:
                d['tGBFB'] = d['tSimp'].split()[0]
                d['tGBFB'].encode('gb2312')
            except:
                d['tGBFB'] = u'？'
        try:
            c.encode('big5')
        except UnicodeEncodeError:
            unihan.get_variants_by_code_w_link(code,
                    'kSemanticVariant', add_cr)
            if not d.has_key('tTrad') and not d.has_key('tGBFB') and cr:
                d['tTrad'] = ' '.join(cr)
            try:
                d['tB5FB'] = d['tTrad'].split()[0]
                d['tB5FB'].encode('big5')
            except:
                d['tB5FB'] = u'？'
        try:
            c.encode('euc-jp')
        except UnicodeEncodeError:
            try:
                d['tJISFB'] = d['tJpShin'].split()[0]
                d['tJISFB'].encode('euc-jp')
            except:
                try:
                    d['tJISFB'] = d['tTrad'].split()[0]
                    d['tJISFB'].encode('euc-jp')
                except:
                    d['tJISFB'] = u'？'
        if not d.has_key('tJpShin') and d.get('tJISFB') not in (None, u'？'):
            d['tJpShin'] = d['tJISFB']
        if d.get('tB5FB') == u'？' and d.get('tJISFB') not in (None, u'？'):
            try:
                d['tJISFB'].encode('big5')
                d['tB5FB'] = d['tJISFB']
            except:
                pass
        if d.get('tGBFB') == u'？' and d.get('tJISFB') not in (None, u'？'):
            try:
                d['tJISFB'].encode('gb2312')
                d['tGBFB'] = d['tJISFB']
            except:
                pass
        insert_graph(db, c, **d)
        done.add(code)
    freq = 7
    for lvl in levels:
        for code in cjkvi.get_codes_by_table(name, lvl):
            _process_code(code, freq)
        freq -= 2
    name = 'kIICore'
    levels = unihan.get_values_of_variant(name)
    levels = levels[:levels.index('G')]
    assert len(levels) == 3
    freq = 6
    for lvl in levels:
        for code in unihan.get_codes_by_variant(name, lvl):
            if code not in done:
                _process_code(code, freq)
        freq -= 2

if __name__ == '__main__':
    try:
        fname = sys.argv[1]
    except:
        fname = 'instance/hzlinkdb.db'
    if os.path.exists(fname) and os.stat(fname).st_size != 0:
        print 'Already initialized'
        sys.exit(1)
    db = sqlite3.connect(fname)
    _start = time.clock()
    create(db)
    db.commit()
    _end = time.clock()
    print >> sys.stderr, _end - _start, 'seconds elapsed creating db'
    _start = time.clock()
    init_data(db)
    db.commit()
    _end = time.clock()
    print >> sys.stderr, _end - _start, 'seconds elapsed filling data in db'
    print 'Database initialized'

# vim:ts=4:sw=4:et:ai:cc=80
