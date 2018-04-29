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

_table_list = (
        ('zibiao2013', 'Tongyong Guifan Hanzi Biao'),
        )
_table_name_map = dict(_table_list)

def get_table_list():
    return _table_list

def get_table_name(table):
    return _table_name_map[table]

def _load_tables(directory):
    d = {}
    for n in _table_name_map.iterkeys():
        d[n] = eval('_load_' + n)(directory, n)
    return d

_sup_digits = set(u'¹²³\u2074\u2075\u2076\u2077\u2078\u2079\u2070')

def _load_zibiao2013(directory, name=None):
    name = 'zibiao2009'
    n = 0
    ar = []
    for i in (1, 2, 3):
        fname = os.path.join(directory, '%s-%d.txt' % (name, i))
        with open(fname) as f:
            for line in f.read().splitlines():
                if not (line and 0x30 <= ord(line[0]) < 0x40):
                    continue
                line = line.decode('utf-8')
                assert line[4] == u'\u3000'
                n += 1
                assert int(line[:4]) == n
                s = line[5:]
                while s[-1] in _sup_digits:
                    s = s[:-1]
                assert s
                ar.append(s)
    assert len(ar) == n == 8300
    # patch table for zibiao2013
    # Cf. https://zh.wikisource.org/wiki/通用规范汉字表
    for pos, old, new, insert in (
            (1431, u'査',       u'查', False),
            (2956, u'毀',       u'毁', False),
            (3612, u'氽',       None,  False),
            (3622, u'汕',       u'饧', True ),
            (3652, u'扽',       None,  False),
            (3658, u'芫',       u'㧐', True ),
            (3839, u'拈',       u'坫', True ),
            (3848, u'坨',       u'㧟', True ),
            (3971, u'舠',       None,  False),
            (4004, u'⿰火区',   u'𬉼', False),
            (4051, u'祊',       None,  False),
            (4103, u'挢',       None,  False),
            (4138, u'柰',       u'荮', True ),
            (4336, u'浈',       None,  False),
            (4444, u'䓖',       None,  False),
            (4546, u'铎',       u'䥽', True ),
            (4853, u'啜',       u'唰', True ),
            (5177, u'铻',       u'赕', True ),
            (5364, u'搦',       u'毂', True ),
            (5472, u'嗨',       u'嗍', True ),
            (5590, u'慄',       None,  False),
            (5642, u'毂',       None,  False),
            (5693, u'睽',       u'䁖', True ),
            (5792, u'粼',       u'粿', True ),
            (5801, u'漤',       None,  False),
            (6005, u'潽',       None,  False),
            (6072, u'磺',       None,  False),
            (6502, u'彳',       u'尢', True ),
            (6504, u'邒',       None,  False),
            (6514, u'𨙮',       u'冮', False),
            (6517, u'𣱼',       None,  False),
            (6520, u'⿰讠于',   u'𬣙', False),
            (6522, u'玐',       None,  False),
            (6522, u'㺩',       None,  False),
            (6529, u'𨙶',       None,  False),
            (6538, u'㲻',       None,  False),
            (6545, u'㡯',       None,  False),
            (6547, u'闬',       None,  False),
            (6547, u'⿰氵万',   u'𬇕', False),
            (6549, u'𢖳',       None,  False),
            (6551, u'⿰讠㝉',   u'𬣞', False),
            (6553, u'𨸝',       None,  False),
            (6553, u'㚤',       None,  False),
            (6553, u'⿰纟川',   u'𬘓', False),
            (6555, u'玗',       None,  False),
            (6556, u'玔',       None,  False),
            (6558, u'㺭',       None,  False),
            (6559, u'⿰土区',   u'刬', True ),
            (6560, u'⿰土区',   u'𫭟', False),
            (6563, u'⿰土仑',   u'扽', True ),
            (6564, u'⿰土仑',   u'𫭢', False),
            (6569, u'耴',       None,  False),
            (6574, u'䒜',       None,  False),
            (6581, u'杋',       None,  False),
            (6589, u'𠧚',       None,  False),
            (6594, u'⿰山历',   u'𫵷', False),
            (6605, u'佁',       u'伲', True ),
            (6607, u'肜',       None,  False),
            (6609, u'𨚔',       None,  False),
            (6609, u'疕',       None,  False),
            (6615, u'⿰氵专',   None,  False),
            (6616, u'⿰氵贝',   u'𬇙', False),
            (6619, u'沕',       None,  False),
            (6623, u'⿰讠戋',   u'𬣡', False),
            (6630, u'⿰弓区',   u'𫸩', False),
            (6631, u'𨚓',       None,  False),
            (6635, u'妌',       None,  False),
            (6636, u'⿰女韦',   None,  False),
            (6637, u'姂',       None,  False),
            (6642, u'⿰纟冘',   u'𬘘', False),
            (6647, u'𫞥',       None,  False),
            (6647, u'𪻐',       None,  False),
            (6647, u'玪',       None,  False),
            (6651, u'坫',       None,  False),
            (6659, u'苼',       None,  False),
            (6667, u'厔',       None,  False),
            (6670, u'⿰车氏',   u'𬨂', False),
            (6671, u'⿰日韦',   u'𬀩', False),
            (6672, u'⿰日见',   u'𬀪', False),
            (6678, u'甽',       None,  False),
            (6688, u'⿰钅弋',   u'𬬩', False),
            (6692, u'䢾',       None,  False),
            (6704, u'𫝈',       None,  False),
            (6704, u'㑎',       None,  False),
            (6705, u'郐',       u'舠', True ),
            (6707, u'𦔯',       None,  False),
            (6714, u'㹣',       None,  False),
            (6714, u'⿺风韦',   None,  False),
            (6717, u'並',       None,  False),
            (6729, u'𫍣',       u'祊', True ),
            (6731, u'⿰讠艮',   u'𬣳', False),
            (6732, u'⿰寻阝',   u'𬩽', False),
            (6737, u'⿰阝岂',   u'𬮿', False),
            (6739, u'⿰阝齐',   u'𬯀', False),
            (6742, u'㚰',       None,  False),
            (6742, u'㚴',       None,  False),
            (6743, u'𡛟',       None,  False),
            (6743, u'妰',       None,  False),
            (6744, u'𪥰',       None,  False),
            (6744, u'妼',       None,  False),
            (6744, u'⿰女𢀖',   u'𫰛', False),
            (6747, u'⿰马丕',   u'𬳵', False),
            (6749, u'𩧬',       None,  False),
            (6749, u'⿰马冋',   u'𬳶', False),
            (6758, u'玵',       None,  False),
            (6758, u'𤤒',       None,  False),
            (6759, u'⿰王卢',   None,  False),
            (6761, u'珃',       None,  False),
            (6761, u'⿰王乐',   u'𬍛', False),
            (6762, u'玽',       None,  False),
            (6763, u'玸',       None,  False),
            (6766, u'㺹',       None,  False),
            (6771, u'㧥',       None,  False),
            (6774, u'⿰土夅',   u'鿍', False),
            (6780, u'垏',       u'垵', True ),
            (6791, u'⿱艹问',   u'𬜬', False),
            (6804, u'郙',       None,  False),
            (6808, u'䣅',       None,  False),
            (6810, u'𥐰',       None,  False),
            (6815, u'𠡠',       None,  False),
            (6837, u'峏',       u'耑', False),
            (6838, u'峢',       u'峛', False),
            (6839, u'𡷫',       None,  False),
            (6842, u'帲',       u'帡', False),
            (6845, u'⿰钅韦',   None,  False),
            (6846, u'⿰钅长',   u'𬬮', False),
            (6847, u'⿰钅斤',   u'𬬱', False),
            (6848, u'⿰钅仑',   u'𬬭', False),
            (6861, u'㣝',       None,  False),
            (6871, u'胐',       u'朏', False),
            (6873, u'𫠈',       None,  False),
            (6883, u'洏',       None,  False),
            (6886, u'浉',       u'浈', True ),
            (6903, u'⿰讠连',   None,  False),
            (6913, u'娍',       None,  False),
            (6913, u'姯',       None,  False),
            (6913, u'⿰女华',   None,  False),
            (6919, u'⿰纟因',   u'𬘡', False),
            (6920, u'⿰马先',   u'𬳽', False),
            (6921, u'⿰纟廷',   u'𬘩', False),
            (6927, u'珬',       None,  False),
            (6929, u'玼',       u'琊', True ),
            (6932, u'𤤺',       None,  False),
            (6932, u'珚',       None,  False),
            (6935, u'珘',       None,  False),
            (6935, u'珨',       None,  False),
            (6935, u'𤤸',       None,  False),
            (6937, u'⿰王寻',   u'𬍤', False),
            (6941, u'⿰土劳',   u'𫭼', False),
            (6951, u'⿱艹两',   u'𬜯', False),
            (6953, u'𦯬',       None,  False),
            (6955, u'䓂',       u'䓖', False),
            (6959, u'⿰木夹',   u'𬂩', False),
            (6965, u'栘',       None,  False),
            (6979, u'⿰牙合',   u'𬌗', False),
            (6998, u'峬',       None,  False),
            (7004, u'⿰钅术',   u'𬬸', False),
            (7006, u'⿰钅卢',   u'𬬻', False),
            (7007, u'⿰钅申',   u'𬬹', False),
            (7008, u'⿰钅召',   u'𬬿', False),
            (7009, u'⿰钅母',   u'𬭁', False),
            (7012, u'𤙔',       None,  False),
            (7019, u'⿰亻单',   u'𫢸', False),
            (7022, u'𨈓',       None,  False),
            (7028, u'𨛭',       None,  False),
            (7031, u'脁',       u'朓', False),
            (7045, u'䍨',       None,  False),
            (7045, u'䍩',       None,  False),
            (7053, u'烅',       None,  False),
            (7053, u'烑',       None,  False),
            (7053, u'⿰火寻',   u'𬊈', False),
            (7056, u'浬',       u'浭', True ),
            (7066, u'浵',       None,  False),
            (7066, u'浫',       None,  False),
            (7070, u'⿳⺍冖石', u'𬒈', False),
            (7079, u'袚',       u'袯', False),
            (7086, u'䧑',       None,  False),
            (7087, u'娪',       None,  False),
            (7087, u'㛒',       None,  False),
            (7087, u'娏',       None,  False),
            (7087, u'𫝫',       None,  False),
            (7087, u'𡝐',       None,  False),
            (7087, u'⿰女佥',   None,  False),
            (7093, u'⿰马余',   u'𬳿', False),
            (7097, u'⿰纟完',   u'𬘫', False),
            (7098, u'⿰马良',   None,  False),
            (7101, u'㻉',       None,  False),
            (7103, u'㻌',       None,  False),
            (7105, u'琂',       None,  False),
            (7105, u'珶',       None,  False),
            (7106, u'⿱规女',   None,  False),
            (7114, u'⿰土单',   u'𫮃', False),
            (7146, u'⿰石达',   u'鿎', False),
            (7148, u'硃',       None,  False),
            (7152, u'龁',       u'䴕', True ),
            (7154, u'祡',       None,  False),
            (7154, u'砦',       None,  False),
            (7156, u'𣆳',       u'啫', False),
            (7157, u'晘',       None,  False),
            (7159, u'𣆲',       None,  False),
            (7161, u'⿰由页',   u'𬱖', False),
            (7166, u'⿰虫东',   u'𬟽', False),
            (7170, u'𡹇',       None,  False),
            (7186, u'铦',       None,  False),
            (7190, u'䇞',       None,  False),
            (7191, u'笣',       None,  False),
            (7192, u'偡',       u'偰', True ),
            (7198, u'鄅',       u'㿠', True ),
            (7201, u'𢔁',       None,  False),
            (7219, u'⿰贸阝',   u'𠅤', False), #𬪍 in 2009
            (7227, u'羝',       u'阌', True ),
            (7230, u'⿰火寿',   None,  False),
            (7231, u'烿',       None,  False),
            (7233, u'煐',       None,  False),
            (7234, u'⿰氵国',   u'𬇹', False),
            (7241, u'⿱汤玉',   u'𬍡', False),
            (7249, u'⿰讠垔',   u'𬤇', False),
            (7254, u'⿰讠是',   u'𬤊', False),
            (7260, u'⿰阝贵',   u'𬯎', False),
            (7262, u'⿰女责',   None,  False),
            (7269, u'婋',       None,  False),
            (7270, u'婩',       None,  False),
            (7270, u'㛥',       None,  False),
            (7270, u'婇',       None,  False),
            (7273, u'娽',       None,  False),
            (7273, u'娺',       None,  False),
            (7273, u'⿰纟青',   u'𬘬', False),
            (7274, u'⿰纟林',   u'𬘭', False),
            (7275, u'⿰马非',   u'𬴂', False),
            (7279, u'⿰纟享',   u'𬘯', False),
            (7284, u'㻓',       None,  False),
            (7284, u'𪻨',       None,  False),
            (7286, u'㻒',       None,  False),
            (7286, u'㻔',       None,  False),
            (7286, u'㻑',       None,  False),
            (7287, u'𤥿',       None,  False),
            (7287, u'琗',       None,  False),
            (7287, u'𤥽',       None,  False),
            (7295, u'揾',       None,  False),
            (7297, u'𢯺',       None,  False),
            (7301, u'堟',       None,  False),
            (7316, u'葹',       None,  False),
            (7325, u'𣓉',       None,  False),
            (7325, u'椢',       None,  False),
            (7326, u'⿰木质',   u'𬃊', False),
            (7334, u'盚',       None,  False),
            (7334, u'⿰甫鸟',   u'𬷕', False),
            (7336, u'䣓',       None,  False),
            (7347, u'⿰齿介',   u'𬹼', False),
            (7351, u'𥆧',       None,  False),
            (7351, u'⿰目间',   None,  False),
            (7361, u'⿰山带',   u'𫶇', False),
            (7370, u'䞍',       None,  False),
            (7373, u'⿰钅麦',   u'鿏', False),
            (7375, u'⿰钅杜',   u'𬭊', False),
            (7382, u'⿰钅宏',   u'𬭎', False),
            (7387, u'䅋',       None,  False),
            (7399, u'殽',       None,  False),
            (7403, u'䏽',       None,  False),
            (7405, u'⿰危页',   u'𬱟', False),
            (7406, u'⿰鱼介',   None,  False),
            (7414, u'⿸广钦',   u'𫷷', False),
            (7421, u'⿵门垔',   u'𬮱', False),
            (7423, u'⿰火单',   u'𬊤', False),
            (7429, u'渱',       None,  False),
            (7433, u'湙',       None,  False),
            (7447, u'隞',       None,  False),
            (7448, u'媙',       None,  False),
            (7448, u'媔',       None,  False),
            (7450, u'㛱',       None,  False),
            (7454, u'媥',       None,  False),
            (7454, u'媃',       None,  False),
            (7456, u'⿰马砉',   u'𬴃', False),
            (7462, u'㻡',       None,  False),
            (7463, u'㻟',       None,  False),
            (7472, u'㻠',       None,  False),
            (7472, u'瑏',       None,  False),
            (7474, u'瑈',       None,  False),
            (7476, u'䪞',       None,  False),
            (7503, u'⿰酉农',   u'𬪩', False),
            (7506, u'⿰石肯',   u'𬒔', False),
            (7510, u'𩐁',       None,  False),
            (7512, u'⿰车酋',   u'𬨎', False),
            (7516, u'𨝘',       None,  False),
            (7519, u'⿰口恶',   u'𫫇', False),
            (7520, u'㬈',       None,  False),
            (7523, u'⿰𧾷夹',   None,  False),
            (7526, u'㡗',       None,  False),
            (7533, u'⿰钅朋',   None,  False),
            (7534, u'⿰钅享',   u'𬭚', False),
            (7537, u'⿰钅波',   u'𬭛', False),
            (7541, u'⿱竹贡',   u'𬕂', False),
            (7545, u'筤',       u'筦', True ),
            (7561, u'⿰鱼句',   u'𬶋', False),
            (7562, u'⿰鱼它',   u'𬶍', False),
            (7582, u'𫞡',       None,  False),
            (7604, u'𧛑',       u'禋', False),
            (7612, u'嫃',       None,  False),
            (7619, u'耤',       u'缞', True ),
            (7625, u'𫞨',       None,  False),
            (7629, u'墈',       u'墕', True ),
            (7653, u'樋',       None,  False),
            (7654, u'⿰匽鸟',   u'𬸘', False),
            (7661, u'⿰石览',   u'𬒗', False),
            (7668, u'夥',       u'䴗', True ),
            (7682, u'⿰钅泉',   None,  False),
            (7682, u'⿰钅侯',   u'𬭤', False),
            (7689, u'箨',       u'鹙', True ),
            (7693, u'𥮾',       None,  False),
            (7696, u'躴',       None,  False),
            (7699, u'⿰月⿱龹贝',None, False),
            (7703, u'鲘',       u'鲗', True ),
            (7706, u'⿰鱼兆',   u'𬶐', False),
            (7707, u'⿰鱼危',   u'𬶏', False),
            (7712, u'⿱狱鸟',   u'𬸚', False),
            (7719, u'𣄎',       u'鲝', False),
            (7723, u'潆',       u'漖', True ),
            (7725, u'潩',       u'漤', True ),
            (7737, u'⿰讠惠',   u'𬤝', False),
            (7742, u'嫤',       None,  False),
            (7746, u'⿰纟寅',   u'𬙂', False),
            (7767, u'暳',       None,  False),
            (7770, u'曏',       None,  False),
            (7789, u'⿰钅翁',   u'𬭩', False),
            (7792, u'篊',       None,  False),
            (7795, u'艎',       u'䴘', True ),
            (7816, u'澛',       u'澂', True ),
            (7819, u'潾',       u'潽', True ),
            (7824, u'⿱𡨄鸟',   u'𬸣', False),
            (7828, u'𥛚',       None,  False),
            (7829, u'㜤',       None,  False),
            (7830, u'㜣',       None,  False),
            (7830, u'嬁',       None,  False),
            (7831, u'⿰马粦',   u'𬴊', False),
            (7832, u'𤩲',       None,  False),
            (7833, u'㻸',       None,  False),
            (7833, u'⿰王阑',   None,  False),
            (7834, u'㻵',       None,  False),
            (7834, u'𤩄',       None,  False),
            (7841, u'⿱艹频',   u'𬞟', False),
            (7842, u'𨞼',       None,  False),
            (7843, u'薐',       None,  False),
            (7849, u'瑿',       None,  False),
            (7855, u'⿰齿奇',   u'𬺈', False),
            (7860, u'曔',       None,  False),
            (7860, u'暻',       None,  False),
            (7867, u'𧎥',       None,  False),
           #(7870, u'𪩘',       u'𪩘', False),
            (7872, u'⿰钅彗',   u'𬭬', False),
            (7874, u'⿰钅敝',   u'𬭯', False),
            (7878, u'䈪',       None,  False),
            (7894, u'⿱族鸟',   u'𬸦', False),
            (7903, u'濛',       None,  False),
            (7909, u'𢣏',       None,  False),
            (7914, u'嬚',       None,  False),
            (7918, u'瓁',       None,  False),
           #(7918, u'𤩽',       u'𤩽', False),
            (7919, u'㻿',       None,  False),
            (7923, u'盩',       None,  False),
            (7937, u'⿰钅喜',   u'𬭳', False),
            (7939, u'⿰钅黑',   u'𬭶', False),
            (7943, u'⿰钅粦',   u'𬭸', False),
            (7945, u'⿰钅遂',   u'𬭼', False),
            (7958, u'⿰番鸟',   u'𬸪', False),
            (7960, u'臁',       u'䲠', False),
            (7961, u'⿰鱼剌',   u'𬶟', False),
            (7963, u'⿰鱼柬',   u'𬶠', False),
            (7964, u'鳁',       u'鲿', True ),
            (7967, u'𫠑',       None,  False),
            (7970, u'䚦',       None,  False),
            (7974, u'⿱既鱼',   u'𬶨', False),
            (7981, u'𤪌',       None,  False),
            (7982, u'瓋',       None,  False),
            (7982, u'瓍',       None,  False),
            (7982, u'璻',       None,  False),
            (7984, u'䰂',       None,  False),
            (7987, u'⿱艹鹝',   u'𬟁', False),
            (7992, u'檽',       None,  False),
            (7997, u'㬤',       None,  False),
            (8003, u'𩪁',       None,  False),
            (8010, u'𥳘',       None,  False),
            (8029, u'㜴',       u'䴙', False),
            (8030, u'⿰纟墨',   u'𬙊', False),
            (8031, u'瓃',       None,  False),
            (8031, u'𣂐',       None,  False),
            (8032, u'酄',       None,  False),
            (8036, u'𧒽',       None,  False),
            (8042, u'⿰鱼祭',   u'𬶭', False),
            (8049, u'爅',       None,  False),
            (8051, u'瓌',       None,  False),
            (8052, u'蘶',       None,  False),
            (8062, u'⿰鱼喜',   u'𬶮', False),
            (8063, u'黁',       None,  False),
            (8068, u'灢',       u'瀼', False),
            (8072, u'⿰马雚',   None,  False),
            (8073, u'⿰纟襄',   u'𬙋', False),
            (8079, u'礳',       None,  False),
            (8079, u'⿰齿楚',   u'𬺓', False),
            (8080, u'𣌓',       None,  False),
            (8084, u'爟',       u'鳣', True ),
            (8087, u'爙',       None,  False),
            (8093, u'㬬',       None,  False),
            (8098, u'䂂',       None,  False),
            ):
        pos -= 1
        assert ar[pos] == old
        if not new:
            del ar[pos]
        elif insert:
            ar.insert(pos, new)
        else:
            ar[pos] = new
    assert len(ar) == 8105
    return ar

_table_data = _load_tables('cjkvi-tables')

def get_table_data_by_name(name):
    return _table_data.get(name)

if __name__ == '__main__':
    print u'\n'.join(get_table_data_by_name('zibiao2013')).encode('utf-8')
# vim:ts=4:sw=4:et:ai:cc=80
