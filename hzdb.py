#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import sys, os

assert sqlite3.sqlite_version_info >= (3, 8, 2) # for WITHOUT ROWID

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
            ' exists (select 1 from HZMorph where tPhon = old.tHz'
            ' and (tPhPY is null or tPhPY = old.tPY)'
            ' and (tPhGC is null or tPhGC = old.tMGCR) limit 1); '
            'end')

if __name__ == '__main__':
    try:
        fname = sys.argv[1]
    except:
        fname = 'instance/hzlinkdb.db'
    if os.path.exists(fname) and os.stat(fname).st_size != 0:
        print 'Already initialized'
        sys.exit(1)
    db = sqlite3.connect(fname)
    create(db)
    print 'Database initialized'

# vim:ts=4:sw=4:et:ai:cc=80
