#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import bisect
import re
import struct

_rhyme_list = u'''\
上平1東 上平2冬 上平3鍾 上平4江 上平5支 上平6脂 上平7之 上平8微 上平9魚 上平10虞
上平11模 上平12齊 上平13佳 上平14皆 上平15灰 上平16咍 上平17真 上平18諄 上平19臻
上平20文 上平21欣 上平22元 上平23䰟 上平24痕 上平25寒 上平26桓 上平27刪 上平28山
下平1先 下平2仙 下平3蕭 下平4宵 下平5肴 下平6豪 下平7歌 下平8戈 下平9麻 下平10陽
下平11唐 下平12庚 下平13耕 下平14清 下平15青 下平16蒸 下平17登 下平18尤 下平19侯
下平20幽 下平21侵 下平22覃 下平23談 下平24鹽 下平25添 下平26咸 下平27銜 下平28嚴
下平29凡 上1董 上2腫 上3講 上4紙 上5旨 上6止 上7尾 上8語 上9麌 上10姥 上11薺
上12蟹 上13駭 上14賄 上15海 上16軫 上17準 上18吻 上19隱 上20阮 上21混 上22很
上23旱 上24緩 上25潸 上26產 上27銑 上28獮 上29篠 上30小 上31巧 上32晧 上33哿
上34果 上35馬 上36養 上37蕩 上38梗 上39耿 上40靜 上41迥 上42拯 上43等 上44有
上45厚 上46黝 上47寑 上48感 上49敢 上50琰 上51忝 上52儼 上53豏 上54檻 上55范
去1送 去2宋 去3用 去4絳 去5寘 去6至 去7志 去8未 去9御 去10遇 去11暮 去12霽
去13祭 去14泰 去15卦 去16怪 去17夬 去18隊 去19代 去20廢 去21震 去22稕 去23問
去24焮 去25願 去26慁 去27恨 去28翰 去29換 去30諫 去31襉 去32霰 去33線 去34嘯
去35笑 去36效 去37号 去38箇 去39過 去40禡 去41漾 去42宕 去43映 去44諍 去45勁
去46徑 去47證 去48嶝 去49宥 去50候 去51幼 去52沁 去53勘 去54闞 去55豔 去56㮇
去57釅 去58陷 去59鑑 去60梵 入1屋 入2沃 入3燭 入4覺 入5質 入6術 入7櫛 入8物
入9迄 入10月 入11沒 入12曷 入13末 入14黠 入15鎋 入16屑 入17薛 入18藥 入19鐸
入20陌 入21麥 入22昔 入23錫 入24職 入25德 入26緝 入27合 入28盍 入29葉 入30怗
入31洽 入32狎 入33業 入34乏 
'''.split()
_rhyme_variant_map = {
        0x7B11: 0x25B07, # 去35笑 𥬇
        0x5019: 0x202EB, # 去50候 𠋫
        }
assert len(_rhyme_list) == 206

_rhyme_start_pos = []

_cjk_digits = u'〇一二三四五六七八九十'
assert len(_cjk_digits) == 11

def cjk_num(n):
    assert 0 <= n < 100
    ar = []
    if n >= 10:
        if n >= 20:
            ar.append(_cjk_digits[n / 10])
        ar.append(_cjk_digits[10])
    if n % 10 != 0 or n == 0:
        ar.append(_cjk_digits[n % 10])
    return u''.join(ar)

def _pos2int(s):
    return int(s.replace('.', ''))

def init_data(d, k):
    if len(_rhyme_start_pos) == len(_rhyme_list):
        return
    r = _rhyme_start_pos
    for code in _rhyme_variant_map.iterkeys():
        try:
            t = d[code]
            if not t.has_key(k):
                t[k] = d[_rhyme_variant_map[code]][k]
        except:
            print >> sys.stderr, code, unichr(code)
            raise
    for rhyme in _rhyme_list:
        code = ord(rhyme[-1])
        try:
            t = d[code]
            ar = map(_pos2int, t[k].split())
            if len(ar) == 1:
                v = ar[0]
            else:
                ar.sort()
                v = ar[0]
                if r:
                    i = 0
                    while r[-1] > v:
                        i += 1
                        v = ar[i]
            if r:
                assert r[-1] < v
            r.append(v)
        except:
            print >> sys.stderr, code, unichr(code)
            raise
    assert len(_rhyme_start_pos) == len(_rhyme_list)
    pat = re.compile(r'\d+')
    for i in xrange(len(_rhyme_list)):
        rhyme = _rhyme_list[i]
        s = pat.findall(rhyme)
        ar = pat.split(rhyme)
        assert len(s) == 1
        assert len(ar) == 2
        n = int(s[0])
        s = ar.pop()
        assert len(s) == 1
        ar.insert(0, u'韻')
        if len(ar[-1]) < 2:
            ar.append(u'聲')
        ar.append(cjk_num(n))
        if _rhyme_variant_map.has_key(ord(s)):
            s = struct.pack('i', _rhyme_variant_map[ord(s)]).decode('utf-32')
        ar.append(s)
        _rhyme_list[i] = u''.join(ar)

def pos2rhyme(s):
    v = _pos2int(s)
    i = bisect.bisect(_rhyme_start_pos, v)
    assert i > 0
    return _rhyme_list[i - 1]

# vim:ts=4:sw=4:et:ai:cc=80
