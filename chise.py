#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import glob
import struct
import xml.sax.saxutils
import urllib
import traceback

# Cf. xemacs-chise/lisp/mule/mule-coding.el
_coded_charset_entity_reference_alist = [
        ("mj",                  "I-MJ", 6, 10),
        ("adobe-japan1-6",      "I-AJ1-", 5, 10),
        ("mj",                  "MJ", 6, 10),
        ("adobe-japan1-6",      "AJ1-", 5, 10),
        ("mj",                  "g2-MJ", 6, 10),
        ("mj",                  "R-MJ", 6, 10),
        ("adobe-japan1-6",      "g2-AJ1-", 5, 10),
        ("adobe-japan1-6",      "R-AJ1-", 5, 10),
#       ("adobe-japan1-base",   "I-AJ1-", 5, 10),
#       ("adobe-japan1-base",   "I-AJ1-", 5, 10),
        ("hanyo-denshi/ja",     "I-HD-JA-", 4, 16),
        ("hanyo-denshi/jb",     "I-HD-JB-", 4, 16),
        ("hanyo-denshi/jc",     "I-HD-JC-", 4, 16),
        ("hanyo-denshi/jd",     "I-HD-JD-", 4, 16),
        ("hanyo-denshi/ft",     "I-HD-FT-", 4, 16),
        ("hanyo-denshi/ia",     "I-HD-IA-", 4, 16),
        ("hanyo-denshi/ib",     "I-HD-IB-", 4, 16),
        ("hanyo-denshi/hg",     "I-HD-HG-", 4, 16),
        ("hanyo-denshi/ip",     "I-HD-IP-", 4, 16),
        ("hanyo-denshi/jt",     "I-HD-JT-", 4, 16),
        ("hanyo-denshi/ks",     "I-HD-KS-", 6, 10),
        ("hanyo-denshi/ks/mf",  "I-KSMF-", 5, 10),
        ("gt",                  "I-GT-", 5, 10),
        ("jis-x0208@1990",      "I-J90-", 4, 16),
        ("jis-x0208@1983",      "I-J83-", 4, 16),
        ("jis-x0213-1@2000",    "I-JX1-", 4, 16),
        ("jis-x0213-2",         "I-JX2-", 4, 16),
        ("jis-x0213-1@2004",    "I-JX3-", 4, 16),
        ("jis-x0212",           "I-JSP-", 4, 16),
        ("jis-x0208@1978/1pr",  "I-J78-", 4, 16),
#       ("jis-x0208",           "I-J90-", 4, 16),
        ("chinese-cns11643-1",  "I-C1-", 4, 16),
        ("chinese-cns11643-2",  "I-C2-", 4, 16),
        ("chinese-cns11643-3",  "I-C3-", 4, 16),
        ("chinese-cns11643-4",  "I-C4-", 4, 16),
        ("chinese-cns11643-5",  "I-C5-", 4, 16),
        ("chinese-cns11643-6",  "I-C6-", 4, 16),
        ("chinese-cns11643-7",  "I-C7-", 4, 16),
        ("chinese-gb2312",      "I-G0-", 4, 16),
        ("iso-ir165",           "I-EGB-", 4, 16),
        ("korean-ksc5601",      "I-K0-", 4, 16),
        ("ruimoku-v6",          "I-RUI6-", 4, 16),
        ("ruimoku-v6",          "RUI6-", 4, 16),
        ("daikanwa@rev2",       "I-M-",  5, 10),
        ("gt-k",                "I-GT-K", 5, 10),
        ("cbeta",               "I-CB", 5, 10),
        ("big5-cdp",            "I-CDP-", 4, 16),
        ("hanziku-1",           "I-HZK01-", 4, 16),
        ("hanziku-2",           "I-HZK02-", 4, 16),
        ("hanziku-3",           "I-HZK03-", 4, 16),
        ("hanziku-4",           "I-HZK04-", 4, 16),
        ("hanziku-5",           "I-HZK05-", 4, 16),
        ("hanziku-6",           "I-HZK06-", 4, 16),
        ("hanziku-7",           "I-HZK07-", 4, 16),
        ("hanziku-8",           "I-HZK08-", 4, 16),
        ("hanziku-9",           "I-HZK09-", 4, 16),
        ("hanziku-10",          "I-HZK10-", 4, 16),
        ("hanziku-11",          "I-HZK11-", 4, 16),
        ("hanziku-12",          "I-HZK12-", 4, 16),
        ("latin-iso8859-1",     "I-LATIN1-", 2, 16),
        ("latin-iso8859-2",     "I-LATIN2-", 2, 16),
        ("latin-iso8859-3",     "I-LATIN3-", 2, 16),
        ("latin-iso8859-4",     "I-LATIN4-", 2, 16),
        ("cyrillic-iso8859-5",  "I-CYRILLIC-", 2, 16),
        ("greek-iso8859-7",     "I-GREEK-", 2, 16),
        ("hebrew-iso8859-8",    "I-HEBREW-", 2, 16),
        ("latin-iso8859-9",     "I-LATIN5-", 2, 16),
        ("latin-jisx0201",      "I-LATINJ-", 2, 16),
        ("katakana-jisx0201",   "I-KATAKANA-", 2, 16),
        ("latin-tcvn5712",      "I-VSCII2-", 2, 16),
        ("latin-viscii",        "I-VISCII-", 2, 16),
        ("latin-viscii-upper",  "I-MULE-VIET-U-", 2, 16),
        ("latin-viscii-lower",  "I-MULE-VIET-L-", 2, 16),
        ("thai-tis620",         "I-THAI-", 2, 16),
        ("lao",                 "I-MULE-LAO-", 2, 16),
        ("arabic-1-column",     "I-MULE-ARB1-", 2, 16),
        ("arabic-2-column",     "I-MULE-ARB2-", 2, 16),
        ("arabic-digit",        "I-MULE-ARBD-", 2, 16),
        ("ipa",                 "I-MULE-IPA-", 2, 16),
        ("china3-jef",          "I-JC3-", 4, 16),
        ("hanyo-denshi/ja",     "HD-JA-", 4, 16),
        ("hanyo-denshi/jb",     "HD-JB-", 4, 16),
        ("hanyo-denshi/jc",     "HD-JC-", 4, 16),
        ("hanyo-denshi/jd",     "HD-JD-", 4, 16),
        ("hanyo-denshi/ft",     "HD-FT-", 4, 16),
        ("hanyo-denshi/ia",     "HD-IA-", 4, 16),
        ("hanyo-denshi/ib",     "HD-IB-", 4, 16),
        ("hanyo-denshi/hg",     "HD-HG-", 4, 16),
        ("hanyo-denshi/ip",     "HD-IP-", 4, 16),
        ("hanyo-denshi/jt",     "HD-JT-", 4, 16),
        ("hanyo-denshi/ks",     "HD-KS-", 6, 10),
        ("hanyo-denshi/tk",     "HD-TK-", 8, 10),
        ("hanyo-denshi/ja",     "g2-HD-JA-", 4, 16),
        ("hanyo-denshi/jb",     "g2-HD-JB-", 4, 16),
        ("hanyo-denshi/jc",     "g2-HD-JC-", 4, 16),
        ("hanyo-denshi/jd",     "g2-HD-JD-", 4, 16),
        ("hanyo-denshi/ft",     "g2-HD-FT-", 4, 16),
        ("hanyo-denshi/ia",     "g2-HD-IA-", 4, 16),
        ("hanyo-denshi/ib",     "g2-HD-IB-", 4, 16),
        ("hanyo-denshi/hg",     "g2-HD-HG-", 4, 16),
        ("hanyo-denshi/ip",     "g2-HD-IP-", 4, 16),
        ("hanyo-denshi/jt",     "g2-HD-JT-", 4, 16),
        ("hanyo-denshi/ks",     "g2-HD-KS-", 6, 10),
        ("hanyo-denshi/tk",     "g2-HD-TK-", 8, 10),
        ("hanyo-denshi/jb",     "R-HD-JB-", 4, 16),
        ("hanyo-denshi/ft",     "R-HD-FT-", 4, 16),
        ("hanyo-denshi/ia",     "R-HD-IA-", 4, 16),
        ("hanyo-denshi/ib",     "R-HD-IB-", 4, 16),
        ("hanyo-denshi/hg",     "R-HD-HG-", 4, 16),
        ("hanyo-denshi/ip",     "R-HD-IP-", 4, 16),
        ("hanyo-denshi/jt",     "R-HD-JT-", 4, 16),
        ("hanyo-denshi/ks",     "R-HD-KS-", 6, 10),
        ("gt",                  "GT-", 5, 10),
        ("gt",                  "g2-GT-", 5, 10),
        ("gt",                  "R-GT-", 5, 10),
        ("jis-x0208@1990",      "J90-", 4, 16),
        ("jis-x0213-1@2000",    "JX1-", 4, 16),
        ("jis-x0213-2",         "JX2-", 4, 16),
        ("jis-x0213-1@2004",    "JX3-", 4, 16),
        ("jis-x0212",           "JSP-", 4, 16),
        ("jis-x0208@1990",      "g2-J90-", 4, 16),
        ("jis-x0208@1990",      "R-J90-", 4, 16),
        ("jis-x0208",           "R-J0-", 4, 16),
        ("jis-x0212",           "g2-JSP-", 4, 16),
        ("jis-x0213-1@2000",    "g2-JX1-", 4, 16),
        ("jis-x0213-2",         "g2-JX2-", 4, 16),
        ("jis-x0213-1@2004",    "g2-JX3-", 4, 16),
        ("jis-x0213-1",         "R-JX1-", 4, 16),
        ("jis-x0213-2",         "R-JX2-", 4, 16),
        ("jis-x0213-1@2004",    "R-JX3-", 4, 16),
        ("jis-x0212",           "R-JSP-", 4, 16),
        ("jis-x0213-1@2000",    "R-J00X1-", 4, 16),
        ("cns11643-1",          "C1-", 4, 16),
        ("chinese-cns11643-2",  "C2-", 4, 16),
        ("chinese-cns11643-3",  "C3-", 4, 16),
        ("chinese-cns11643-4",  "C4-", 4, 16),
        ("chinese-cns11643-5",  "C5-", 4, 16),
        ("chinese-cns11643-6",  "C6-", 4, 16),
        ("chinese-cns11643-7",  "C7-", 4, 16),
        ("gb2312",              "G0-", 4, 16),
        ("gb2312",              "g2-G0-", 4, 16),
        ("big5-cdp",            "CDP-", 4, 16),
        ("big5-cdp",            "g2-CDP-", 4, 16),
        ("big5-cdp",            "R-CDP-", 4, 16),
        ("big5-eten",           "I-B-", 4, 16),
        ("zinbun-oracle",       "ZOB-", 4, 10),
        ("daikanwa/ho",         "M-H", 4, 10),
        ("daikanwa/+p",         "M-p", 5, 10),
        ("daikanwa/+2p",        "M-2p", 5, 10),
        ("daikanwa",            "M-",  5, 10),
        ("daikanwa@rev2",       "r2M-",  5, 10),
        ("daikanwa@rev1",       "r1M-",  5, 10),
        ("daikanwa/ho",         "g2-M-H", 4, 10),
        ("daikanwa/+p",         "g2-M-p", 5, 10),
        ("daikanwa",            "g2-M-", 5, 10),
        ("daikanwa/ho",         "R-M-H", 4, 10),
        ("daikanwa/+p",         "R-M-p", 5, 10),
        ("daikanwa",            "R-M-",  5, 10),
        ("ks-x1001",            "K0-", 4, 16),
        ("ks-x1001",            "g2-K0-", 4, 16),
        ("ks-x1001",            "R-K0-", 4, 16),
        ("iso-ir165",           "EGB-", 4, 16),
        ("jis-x0208@1983",      "J83-", 4, 16),
        ("koseki",              "KOSEKI-", 6, 10),
        ("ucs-var-001",         "U-v001+", 4, 16),
        ("ucs-var-002",         "U-v002+", 4, 16),
        ("ucs-var-003",         "U-v003+", 4, 16),
        ("ucs-var-004",         "U-v004+", 4, 16),
        ("ucs-var-005",         "U-v005+", 4, 16),
        ("ucs-var-006",         "U-v006+", 4, 16),
        ("ucs-var-008",         "U-v008+", 4, 16),
        ("ucs-var-010",         "U-v010+", 4, 16),
        ("ucs-itaiji-001",      "U-i001+", 4, 16),
        ("ucs-itaiji-002",      "U-i002+", 4, 16),
        ("ucs-itaiji-003",      "U-i003+", 4, 16),
        ("ucs-itaiji-004",      "U-i004+", 4, 16),
        ("ucs-itaiji-005",      "U-i005+", 4, 16),
        ("ucs-itaiji-006",      "U-i006+", 4, 16),
        ("ucs-itaiji-007",      "U-i007+", 4, 16),
        ("ucs-itaiji-008",      "U-i008+", 4, 16),
        ("ucs-itaiji-009",      "U-i009+", 4, 16),
        ("ucs-itaiji-010",      "U-i010+", 4, 16),
        ("ucs-itaiji-011",      "U-i011+", 4, 16),
        ("ucs-itaiji-012",      "U-i012+", 4, 16),
        ("ucs-itaiji-084",      "U-i084+", 4, 16),
        ("big5-cdp-var-001",    "CDP-v001-", 4, 16),
        ("big5-cdp-var-002",    "CDP-v002-", 4, 16),
        ("big5-cdp-var-003",    "CDP-v003-", 4, 16),
        ("big5-cdp-var-004",    "CDP-v004-", 4, 16),
        ("big5-cdp-var-005",    "CDP-v005-", 4, 16),
        ("big5-cdp-itaiji-001", "CDP-i001-", 4, 16),
        ("big5-cdp-itaiji-002", "CDP-i002-", 4, 16),
        ("big5-cdp-itaiji-003", "CDP-i003-", 4, 16),
        ("jis-x0208@1978/1pr",  "J78-", 4, 16),
        ("gt-k",                "GT-K", 5, 10),
        ("jis-x0208@1983",      "g2-J83-", 4, 16),
        ("koseki",              "g2-KOSEKI-", 6, 10),
        ("ucs-var-002",         "g2-U-v002+", 4, 16),
        ("ucs-itaiji-001",      "g2-U-i001+", 4, 16),
        ("ucs-itaiji-002",      "g2-U-i002+", 4, 16),
        ("ucs-itaiji-003",      "g2-U-i003+", 4, 16),
        ("ucs-itaiji-005",      "g2-U-i005+", 4, 16),
        ("ucs-itaiji-006",      "g2-U-i006+", 4, 16),
        ("big5-cdp-itaiji-001", "g2-CDP-i001-", 4, 16),
        ("jis-x0208@1978/1pr",  "g2-J78-", 4, 16),
        ("gt-k",                "g2-GT-K", 5, 10),
        ("gt-k",                "R-GT-K", 5, 10),
        ("jis-x0208@1983",      "R-J83-", 4, 16),
        ("jis-x0208@1978",      "R-J78-", 4, 16),
        ("cbeta",               "CB", 5, 10),
        ("cbeta",               "A-CB", 5, 10),
        ("cbeta",               "g2-CB", 5, 10),
        ("cbeta",               "R-CB", 5, 10),
        ("hng-jou",             "HNG001-", 5, 10),
        ("hng-keg",             "HNG002-", 5, 10),
        ("hng-dng",             "HNG003-", 5, 10),
        ("hng-mam",             "HNG005-", 5, 10),
        ("hng-drt",             "HNG006-", 5, 10),
        ("hng-kgk",             "HNG007-", 5, 10),
        ("hng-myz",             "HNG008-", 5, 10),
        ("hng-kda",             "HNG009-", 5, 10),
        ("hng-khi",             "HNG010-", 5, 10),
        ("hng-khm",             "HNG011-", 5, 10),
        ("hng-hok",             "HNG013-", 5, 10),
        ("hng-kyd",             "HNG014-", 5, 10),
        ("hng-sok",             "HNG015-", 5, 10),
        ("hng-yhk",             "HNG016-", 5, 10),
        ("hng-kak",             "HNG017-", 5, 10),
        ("hng-kar",             "HNG018-", 5, 10),
        ("hng-kae",             "HNG019-", 5, 10),
        ("hng-sys",             "HNG022-", 5, 10),
        ("hng-tsu",             "HNG024-", 5, 10),
        ("hng-tzj",             "HNG025-", 5, 10),
        ("hng-hos",             "HNG026-", 5, 10),
        ("hng-nak",             "HNG028-", 5, 10),
        ("hng-jhk",             "HNG029-", 5, 10),
        ("hng-hod",             "HNG030-", 5, 10),
        ("hng-gok",             "HNG031-", 5, 10),
        ("hng-ink",             "HNG033-", 5, 10),
        ("hng-nto",             "HNG034-", 5, 10),
        ("hng-nkm",             "HNG036-", 5, 10),
        ("hng-k24",             "HNG037-", 5, 10),
        ("hng-nkk",             "HNG039-", 5, 10),
        ("hng-kcc",             "HNG041-", 5, 10),
        ("hng-kcj",             "HNG042-", 5, 10),
        ("hng-kbk",             "HNG043-", 5, 10),
        ("hng-sik",             "HNG044-", 5, 10),
        ("hng-skk",             "HNG046-", 5, 10),
        ("hng-kyu",             "HNG047-", 5, 10),
        ("hng-ksk",             "HNG048-", 5, 10),
        ("hng-wan",             "HNG049-", 5, 10),
        ("hng-okd",             "HNG050-", 5, 10),
        ("hng-wad",             "HNG054-", 5, 10),
        ("hng-kmi",             "HNG055-", 5, 10),
        ("hng-zkd",             "HNG056-", 5, 10),
        ("hng-doh",             "HNG057-", 5, 10),
        ("hng-jyu",             "HNG058-", 5, 10),
        ("hng-tzs",             "HNG060-", 5, 10),
        ("hng-kss",             "HNG064-", 5, 10),
        ("hng-kyo",             "HNG066-", 5, 10),
        ("hng-smk",             "HNG074-", 5, 10),
        ("hanziku-1",           "HZK01-", 4, 16),
        ("hanziku-2",           "HZK02-", 4, 16),
        ("hanziku-3",           "HZK03-", 4, 16),
        ("hanziku-4",           "HZK04-", 4, 16),
        ("hanziku-5",           "HZK05-", 4, 16),
        ("hanziku-6",           "HZK06-", 4, 16),
        ("hanziku-7",           "HZK07-", 4, 16),
        ("hanziku-8",           "HZK08-", 4, 16),
        ("hanziku-9",           "HZK09-", 4, 16),
        ("hanziku-10",          "HZK10-", 4, 16),
        ("hanziku-11",          "HZK11-", 4, 16),
        ("hanziku-12",          "HZK12-", 4, 16),
        ("hanziku-1",           "I-HZK1-", 4, 16),
        ("hanziku-1",           "HZK1-", 4, 16),
        ("hanziku-2",           "I-HZK2-", 4, 16),
        ("hanziku-2",           "HZK2-", 4, 16),
        ("hanyo-denshi/ks/mf",  "KSMF-", 5, 10),
        ("big5-cdp-var-3",      "CDP-var3-", 4, 16),
        ("big5-cdp-var-5",      "CDP-var5-", 4, 16),
        ("latin-iso8859-1",     "LATIN1-", 2, 16),
        ("latin-iso8859-2",     "LATIN2-", 2, 16),
        ("latin-iso8859-3",     "LATIN3-", 2, 16),
        ("latin-iso8859-4",     "LATIN4-", 2, 16),
        ("cyrillic-iso8859-5",  "CYRILLIC-", 2, 16),
        ("greek-iso8859-7",     "GREEK-", 2, 16),
        ("hebrew-iso8859-8",    "HEBREW-", 2, 16),
        ("latin-iso8859-9",     "LATIN5-", 2, 16),
        ("latin-jisx0201",      "LATINJ-", 2, 16),
        ("katakana-jisx0201",   "KATAKANA-", 2, 16),
        ("latin-tcvn5712",      "VSCII2-", 2, 16),
        ("latin-viscii",        "VISCII-", 2, 16),
        ("latin-viscii-upper",  "MULE-VIET-U-", 2, 16),
        ("latin-viscii-lower",  "MULE-VIET-L-", 2, 16),
        ("thai-tis620",         "THAI-", 2, 16),
        ("lao",                 "MULE-LAO-", 2, 16),
        ("ethiopic",            "MULE-ETHIO-", 4, 16),
        ("arabic-1-column",     "MULE-ARB1-", 2, 16),
        ("arabic-2-column",     "MULE-ARB2-", 2, 16),
        ("arabic-digit",        "MULE-ARBD-", 2, 16),
        ("ipa",                 "MULE-IPA-", 2, 16),
        ("jis-x0208",           "g2-J0-", 4, 16),
        ("jis-x0208",           "GI-J0-", 4, 16),
#       ("jis-x0213-1",         "g2-JX1-", 4, 16),
        ("jis-x0213-1",         "GI-JX1-", 4, 16),
        ("jis-x0213-1@2004",    "GI-JX3-", 4, 16),
        ("mj",                  "G-MJ", 6, 10),
        ("adobe-japan1",        "G-AJ1-", 5, 10),
        ("jis-x0208",           "G-J0-", 4, 16),
        ("jis-x0213-1@2000",    "G-JX1-", 4, 16),
        ("jis-x0213-2",         "G-JX2-", 4, 16),
        ("jis-x0213-1@2004",    "G-JX3-", 4, 16),
        ("hanyo-denshi/ft",     "G-HD-FT-", 4, 16),
        ("hanyo-denshi/ia",     "G-HD-IA-", 4, 16),
        ("hanyo-denshi/ib",     "G-HD-IB-", 4, 16),
        ("hanyo-denshi/jt",     "G-HD-JT-", 4, 16),
        ("hanyo-denshi/ks",     "G-HD-KS-", 4, 16),
        ("gt",                  "G-GT-", 5, 10),
        ("jis-x0208@1978",      "G-J78-", 4, 16),
        ("cns11643-4",          "G-C4-", 4, 16),
        ("big5-cdp",            "G-CDP-", 4, 16),
        ("gt-k",                "G-GT-K", 5, 10),
        ("cbeta",               "G-CB", 5, 10),
        ("jis-x0208",           "o-J0-", 4, 16),
        ("jis-x0213-1",         "o-JX1-", 4, 16),
        ("jis-x0213-2",         "o-JX2-", 4, 16),
        ("jis-x0208@1978",      "o-J78-", 4, 16),
        ("adobe-japan1",        "o-AJ1-", 5, 10),
        ("gt",                  "o-GT-", 5, 10),
        ("hanyo-denshi/ft",     "o-HD-FT-", 4, 16),
        ("hanyo-denshi/jt",     "o-HD-JT-", 4, 16),
        ("jis-x0208@1997",      "J97-", 4, 16),
        ("jis-x0208@1997",      "A-J0-", 4, 16),
        ("jis-x0213-1@2000",    "A-JX1-", 4, 16),
        ("jis-x0213-2",         "A-JX2-", 4, 16),
        ("jis-x0213-1@2004",    "A-JX3-", 4, 16),
        ("gt",                  "A-GT-", 5, 10),
        ("gt-k",                "A-GT-K", 5, 10),
        ("zinbun-oracle",       "A-ZOB-", 4, 10),
        ("ucs@bucs",            "BUCS+", 4, 16),
        ("ucs@iwds-1",          "A-IWDSU+", 4, 16),
        ("ucs@cognate",         "A-cgnU+", 4, 16),
        ("ucs@component",       "A-compU+", 4, 16),
        ("iwds-1",              "IWDS1-", 3, 10),
        ("mj",                  "A-MJ", 6, 10),
        ("ucs@hanyo-denshi",    "A-HDU+", 4, 16),
        ("ucs@hanyo-denshi",    "A-HD-UCS+", 4, 16),
        ("ucs@iso",             "A-IU+", 4, 16),
        ("ucs@unicode",         "A-UU+", 4, 16),
        ("ucs@jis",             "A-JU+", 4, 16),
        ("ucs@cns",             "A-CU+", 4, 16),
        ("ucs@ks",              "A-KU+", 4, 16),
        ("ucs@jis/2004",        "A-J04U+", 4, 16),
        ("ruimoku-v6",          "A-RUI6-", 4, 16),
        ("ucs@iso",             "o-IU+", 4, 16),
        ("ucs@unicode",         "o-UU+", 4, 16),
        ("ucs@jis",             "o-JU+", 4, 16),
        ("ucs@jis/1990",        "o-J90U+", 4, 16),
        ("ucs@cns",             "o-CU+", 4, 16),
        ("ucs@ks",              "o-KU+", 4, 16),
        ("ucs@iso",             "U-", 8, 16),
        ("ucs@unicode",         "UU+", 4, 16),
        ("ucs@unicode",         "UU-", 8, 16),
        ("ucs@iso",             "U+", 4, 16),
        ("ucs@gb",              "GU+", 4, 16),
        ("ucs@gb",              "GU-", 8, 16),
        ("ucs@jis",             "JU+", 4, 16),
        ("ucs@jis",             "JU-", 8, 16),
        ("ucs@cns",             "CU+", 4, 16),
        ("ucs@cns",             "CU-", 8, 16),
        ("ucs@ks",              "KU+", 4, 16),
        ("ucs@ks",              "KU-", 8, 16),
        ("ucs@JP",              "dJU+", 4, 16),
        ("ucs@JP/hanazono",     "hanaJU+", 4, 16),
        ("ucs@iso",             "G-IU+", 4, 16),
        ("ucs@unicode",         "G-UU+", 4, 16),
        ("ucs@jis",             "G-JU+", 4, 16),
        ("ucs@ks",              "G-KU+", 4, 16),
        ("ucs@cns",             "G-CU+", 4, 16),
        ("ucs@jis/2004",        "G-J04U+", 4, 16),
        ("ucs@jis/2000",        "G-J00U+", 4, 16),
        ("ucs@jis/1990",        "G-J90U+", 4, 16),
        ("ucs@JP",              "G-dJU+", 4, 16),
        ("ucs@iso",             "g2-IU-", 8, 16),
        ("ucs@unicode",         "g2-UU+", 4, 16),
        ("ucs@gb",              "g2-GU+", 4, 16),
        ("ucs@cns",             "g2-CU+", 4, 16),
        ("ucs@ks",              "g2-KU+", 4, 16),
        ("ucs@iso",             "R-U-", 8, 16),
        ("ucs@unicode",         "R-UU+", 4, 16),
        ("ucs@gb",              "R-GU+", 4, 16),
        ("ucs@ks",              "R-KU+", 4, 16),
        ("cns11643-1",          "g2-C1-", 4, 16),
        ("cns11643-2",          "g2-C2-", 4, 16),
        ("cns11643-3",          "g2-C3-", 4, 16),
        ("cns11643-4",          "g2-C4-", 4, 16),
        ("cns11643-5",          "g2-C5-", 4, 16),
        ("cns11643-6",          "g2-C6-", 4, 16),
        ("cns11643-7",          "g2-C7-", 4, 16),
        ("cns11643-1",          "R-C1-", 4, 16),
        ("cns11643-2",          "R-C2-", 4, 16),
        ("cns11643-3",          "R-C3-", 4, 16),
        ("cns11643-4",          "R-C4-", 4, 16),
        ("cns11643-5",          "R-C5-", 4, 16),
        ("cns11643-6",          "R-C6-", 4, 16),
        ("cns11643-7",          "R-C7-", 4, 16),
        ("ucs@JP/hanazono",     "g2-hanaJU+", 4, 16),
        ("ruimoku-v6",          "g2-RUI6-", 4, 16),
        ("ruimoku-v6",          "R-RUI6-", 4, 16),
        ("china3-jef",          "JC3-", 4, 16),
        ("jef-china3",          "g2-JC3-", 4, 16),
        ("jef-china3",          "R-JC3-", 4, 16),
        ("big5",                "B-", 4, 16),
        ("big5",                "C0-", 4, 16),
        ("big5-eten",           "BE-", 4, 16),
        ("daikanwa",            "G-M-",  5, 10),
        ("daikanwa/+p",         "G-M-p", 5, 10),
        ("daikanwa",            "A-M-", 5, 10),
        ("daikanwa/ho",         "A-M-H", 4, 10),
        ("cns11643-5",          "A-C5-", 4, 16),
        ("cns11643-7",          "A-C7-", 4, 16),
        ("big5-cdp",            "A-CDP-", 4, 16),
        ("ucs-itaiji-001",      "A-U-i001+", 4, 16),
        ("ucs-itaiji-002",      "A-U-i002+", 4, 16),
        ("ucs-itaiji-003",      "A-U-i003+", 4, 16),
        ("ucs-itaiji-004",      "A-U-i004+", 4, 16),
        ("ucs-itaiji-005",      "A-U-i005+", 4, 16),
        ("ucs-itaiji-006",      "A-U-i006+", 4, 16),
        ("ucs-itaiji-007",      "A-U-i007+", 4, 16),
        ("ucs-itaiji-009",      "A-U-i009+", 4, 16),
        ("big5-cdp-itaiji-001", "A-CDP-i001-", 4, 16),
        ("jis-x0208@1978/i1",   "J78i1-", 4, 16),
        ("shinjigen@rev",       "SJG2-", 4, 10),
        ("shinjigen@1ed",       "SJG1-", 4, 10),
        ("shinjigen@rev",       "g2-SJG2-", 4, 10),
        ("shinjigen@1ed",       "g2-SJG1-", 4, 10),
        ("ucs@iso",             "g2-IU+", 4, 16),
        ("ucs@iso",             "GI-IU+", 4, 16),
        ("ucs@unicode",         "GI-UU+", 4, 16),
        ("ucs@cns",             "GI-CU+", 4, 16),
        ("ucs@jis",             "g2-JU+", 4, 16),
        ("ucs@jis",             "GI-JU+", 4, 16),
        ("ucs@jis/2004",        "g2-J04U+", 4, 16),
        ("ucs@jis/2004",        "GI-J04U+", 4, 16),
        ("ucs@jis/1990",        "g2-J90U+", 4, 16),
        ("ucs@ks",              "GI-KU+", 4, 16),
]

# Cf. est/cwiki-common.el
_coded_charset_GlyphWiki_id_alist = [
        ("adobe-japan1-0",      "aj1-",  5, 10, None),
        ("adobe-japan1-1",      "aj1-",  5, 10, None),
        ("adobe-japan1-2",      "aj1-",  5, 10, None),
        ("adobe-japan1-3",      "aj1-",  5, 10, None),
        ("adobe-japan1-4",      "aj1-",  5, 10, None),
        ("adobe-japan1-5",      "aj1-",  5, 10, None),
        ("adobe-japan1-6",      "aj1-",  5, 10, None),
        ("ucs@jis",             "u",     4, 16, None),
        ("daikanwa",            "dkw-",  5, 10, None),
        ("ucs@ks",              "u",     4, 16, "-k"),
        ("ucs-itaiji-005",      "u",     4, 16, "-itaiji-005"),
        ("ucs-var-001",         "u",     4, 16, "-var-001"),
        ("ucs-var-002",         "u",     4, 16, "-var-002"),
        ("ucs-var-003",         "u",     4, 16, "-var-003"),
        ("ucs-var-004",         "u",     4, 16, "-var-004"),
        ("ucs-itaiji-001",      "u",     4, 16, "-itaiji-001"),
        ("ucs-itaiji-002",      "u",     4, 16, "-itaiji-002"),
        ("ucs-itaiji-003",      "u",     4, 16, "-itaiji-003"),
        ("ucs-itaiji-084",      "u",     4, 16, "-itaiji-084"),
        ("ucs-itaiji-001",      "u",     4, 16, "-itaiji-001"),
        ("ucs-itaiji-006",      "u",     4, 16, "-itaiji-006"),
        ("adobe-japan1-0",      "aj1-",  5, 10, None),
        ("adobe-japan1-1",      "aj1-",  5, 10, None),
        ("adobe-japan1-2",      "aj1-",  5, 10, None),
        ("adobe-japan1-3",      "aj1-",  5, 10, None),
        ("adobe-japan1-4",      "aj1-",  5, 10, None),
        ("adobe-japan1-5",      "aj1-",  5, 10, None),
        ("adobe-japan1-6",      "aj1-",  5, 10, None),
        ("ucs@jis",             "u",     4, 16, None),
        ("ucs@iso",             "u",     4, 16, None),
        ("ucs@cns",             "u",     4, 16, "-t"),
        ("ucs@unicode",         "u",     4, 16, "-us"),
        ("daikanwa",            "dkw-",  5, 10, None),
        ("ucs@ks",              "u",     4, 16, "-k"),
        ("jis-x0208@1978",      "j78-",  4, 16, None),
        ("jis-x0208",           "j90-",  4, 16, None),
        ("jis-x0208@1990",      "j90-",  4, 16, None),
        ("jis-x0208@1983",      "j83-",  4, 16, None),
        ("cbeta",               "cbeta-", 5, 10, None),
        ("hanyo-denshi/ks",     "koseki-", 6, 10, None),
        ("jis-x0208@1978",      "j78-",  4, 16, None),
        ("big5-cdp",            "cdp-",  4, 16, None),
        ("adobe-japan1-0",      "aj1-",  5, 10, None),
        ("adobe-japan1-1",      "aj1-",  5, 10, None),
        ("adobe-japan1-2",      "aj1-",  5, 10, None),
        ("adobe-japan1-3",      "aj1-",  5, 10, None),
        ("adobe-japan1-4",      "aj1-",  5, 10, None),
        ("adobe-japan1-5",      "aj1-",  5, 10, None),
        ("adobe-japan1-6",      "aj1-",  5, 10, None),
        ("jis-x0208",           "j90-",  4, 16, None),
        ("jis-x0208@1990",      "j90-",  4, 16, None),
        ("jis-x0208@1983",      "j83-",  4, 16, None),
        ("daikanwa",            "dkw-",  5, 10, None),
        ("adobe-japan1-0",      "aj1-",  5, 10, None),
        ("adobe-japan1-1",      "aj1-",  5, 10, None),
        ("adobe-japan1-2",      "aj1-",  5, 10, None),
        ("adobe-japan1-3",      "aj1-",  5, 10, None),
        ("adobe-japan1-4",      "aj1-",  5, 10, None),
        ("adobe-japan1-5",      "aj1-",  5, 10, None),
        ("adobe-japan1-6",      "aj1-",  5, 10, None),
        ("hanyo-denshi/ks",     "koseki-", 6, 10, None),
        ("koseki",              "koseki-", 6, 10, None),
        ("ucs@jis",             "u",     4, 16, None),
        ("ucs@cns",             "u",     4, 16, "-t"),
        ("ucs@ks",              "u",     4, 16, "-k"),
        ("ucs@JP",              "u",     4, 16, None),
        ("ucs@gb",              "u",     4, 16, "-g"),
#       ("ucs@iso",             "u",     4, 16, "-u"),
        ("ucs@unicode",         "u",     4, 16, "-us"),
        ("big5-cdp",            "cdp-",  4, 16, None),
        ("big5-cdp",            "cdp-",  4, 16, None),
        ("cbeta",               "cbeta-", 5, 10, None),
        ("big5-cdp-var-3",      "cdp-",  4, 16, "-var-3"),
        ("big5-cdp-var-5",      "cdp-",  4, 16, "-var-5"),
        ("big5-cdp-itaiji-001", "cdp-", 4, 16, "-itaiji-001"),
        ("big5-cdp-itaiji-002", "cdp-", 4, 16, "-itaiji-002"),
        ("big5-cdp-itaiji-001", "cdp-", 4, 16, "-itaiji-001"),
        ("jef-china3",          "jc3-",  4, 16, None),
        ("jis-x0212",           "jsp-",  4, 16, None),
        ("jis-x0213-1@2000",    "jx1-2000-", 4, 16, None),
        ("jis-x0213-1@2004",    "jx1-2004-", 4, 16, None),
        ("jis-x0213-2",         "jx2-",  4, 16, None),
        ("gt-k",                "gt-k",  5, 10, None),
        ("jis-x0208@1978/1pr",  "j78-", 4, 16, None),
        ("jis-x0208@1978/-4pr", "j78-", 4, 16, None),
        ("jis-x0208@1978",      "j78-",  4, 16, None),
        ("jis-x0208@1978",      "j78-",  4, 16, None),
        ("jis-x0208",           "j90-",  4, 16, None),
        ("jis-x0208@1990",      "j90-",  4, 16, None),
        ("jis-x0208@1983",      "j83-",  4, 16, None),
        ("ucs",                 "u",     4, 16, None),
        ("big5",                "b-",    4, 16, None),
        ("daikanwa",            "dkw-",  5, 10, None),
        ("gt",                  "gt-",   5, 10, None),
        ("ruimoku-v6",          "rui6-", 4, 16, None),
        ("ruimoku-v6",          "rui6-", 4, 16, None),
        ("ks-x1001",            "k0-",   4, 16, None),
        ("cns11643-1",          "c1-",   4, 16, None),
        ("cns11643-2",          "c2-",   4, 16, None),
        ("cns11643-3",          "c3-",   4, 16, None),
        ("cns11643-4",          "c4-",   4, 16, None),
        ("cns11643-5",          "c5-",   4, 16, None),
        ("cns11643-6",          "c6-",   4, 16, None),
        ("cns11643-7",          "c7-",   4, 16, None),
        ("jis-x0208",           "j90-",  4, 16, None),
        ("jis-x0208@1990",      "j90-",  4, 16, None),
        ("jis-x0208@1983",      "j83-",  4, 16, None),
]

_coded_charset_GlyphWiki_id_alist.extend([
        ("adobe-japan1",        "aj1-",  5, 10, None),
        ("adobe-japan1-base",   "aj1-",  5, 10, None),
        ("big5-cdp-itaiji-003", "cdp-", 4, 16, "-itaiji-003"),
        ("big5-cdp-var-001",    "cdp-", 4, 16, "-var-001"),
        ("big5-cdp-var-002",    "cdp-", 4, 16, "-var-002"),
        ("big5-cdp-var-003",    "cdp-", 4, 16, "-var-003"),
        ("big5-cdp-var-004",    "cdp-", 4, 16, "-var-004"),
        ("big5-cdp-var-005",    "cdp-", 4, 16, "-var-005"),
        ("daikanwa/+2p",        "dkw-",  5, 10, None),
        ("daikanwa/+p",         "dkw-",  5, 10, None),
        ("daikanwa/ho",         "dkw-",  5, 10, None),
        ("daikanwa@rev1",       "dkw-",  5, 10, None),
        ("daikanwa@rev2",       "dkw-",  5, 10, None),
        ("gb2312",              "g0-", 4, 16, None),
        ("jis-x0208@1978/i1",   "j83-",  4, 16, None),
        ("jis-x0208@1997",      "j90-",  4, 16, None),
        ("jis-x0213-1",         "jx1-2000-", 4, 16, None),
        ("ucs-itaiji-004",      "u",     4, 16, "-itaiji-004"),
        ("ucs-itaiji-007",      "u",     4, 16, "-itaiji-007"),
        ("ucs-itaiji-008",      "u",     4, 16, "-itaiji-008"),
        ("ucs-itaiji-009",      "u",     4, 16, "-itaiji-009"),
        ("ucs-itaiji-010",      "u",     4, 16, "-itaiji-010"),
        ("ucs-itaiji-011",      "u",     4, 16, "-itaiji-011"),
        ("ucs-itaiji-012",      "u",     4, 16, "-itaiji-012"),
        ("ucs-var-005",         "u",     4, 16, "-var-005"),
        ("ucs-var-006",         "u",     4, 16, "-var-006"),
        ("ucs-var-008",         "u",     4, 16, "-var-008"),
        ("ucs-var-010",         "u",     4, 16, "-var-010"),
        ("ucs@JP/hanazono",     "u",     4, 16, None),
        ("ucs@bucs",            "u",     4, 16, None),
        ("ucs@cognate",         "u",     4, 16, None),
        ("ucs@component",       "u",     4, 16, None),
        ("ucs@hanyo-denshi",    "u",     4, 16, None),
        ("ucs@iwds-1",          "u",     4, 16, None),
        ("ucs@jis/1990",        "u",     4, 16, None),
        ("ucs@jis/2000",        "u",     4, 16, None),
        ("ucs@jis/2004",        "u",     4, 16, None),
])

def _build_entity_map(_from, _to):
    d = {}
    for aname, entity, digits, base in _from:
        try:
            if d.has_key(entity):
                assert d[entity] == (aname, digits, base)
            else:
                d[entity] = (aname, digits, base)
                assert len(entity) > 1
        except:
            print >> sys.stderr, aname, entity, digits, base, d.get(entity)
            raise
    t = {}
    for aname, prefix, digits, base, suffix in _to:
        try:
            if t.has_key(aname):
                assert t[aname] == (prefix, digits, base, suffix, aname)
            else:
                t[aname] = (prefix, digits, base, suffix, aname)
        except:
            print >> sys.stderr, aname, prefix, digits, base, suffix, t[aname]
            raise
    r = {}
    for s in set([entity[:2] for entity in d.iterkeys()]):
        r[s] = {}
    for entity, (aname, digits, base) in d.iteritems():
        if t.has_key(aname):
            assert digits, base == t[aname][1:3]
            r[entity[:2]][entity] = t[aname]
        else:
            r[entity[:2]][entity] = (None, digits, base, None, aname)
    return r

_entity_map = _build_entity_map(
        _coded_charset_entity_reference_alist,
        _coded_charset_GlyphWiki_id_alist)

def unichar(i):
    try:
        return unichr(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')

def _load_ids_ucs(directory):
    d = {}
    t = {}
    for fname in glob.glob(os.path.join(directory, 'IDS-UCS*')):
        with open(fname) as f:
            try:
                for line in f.read().splitlines():
                    if not line or line.startswith(';'):
                        continue
                    line = line.decode('utf-8')
                    #assert line.startswith(('U+', 'U-'))
                    ar = line.split('\t')
                    #assert len(ar) >= 3
                    code = int(ar[0][2:], 16)
                    #assert not d.has_key(code)
                    if ar[1].startswith('&'):
                        #assert ar[1].endswith(';')
                        #assert not t.has_key(ar[1])
                        t[ar[1]] = unichar(code)
                    else:
                        #assert ar[1] == unichar(code)
                        pass
                    d[code] = ar[2]
            except:
                print >> sys.stderr, fname, line.encode('gb18030')
                raise
    return d, t

_ids_ucs, _ucs_entity_map = _load_ids_ucs('ids')

def ids_find_by_code(code):
    return _ids_ucs.get(code)

def _load_ids_non_ucs(directory):
    d = {}
    for fname in glob.glob(os.path.join(directory, 'IDS*.txt')):
        if os.path.basename(fname).startswith('IDS-UCS'):
            continue
        with open(fname) as f:
            try:
                for line in f.read().splitlines():
                    if not line or line.startswith(';'):
                        continue
                    line = line.decode('utf-8')
                    ar = line.split('\t')
                    if len(ar) < 3:
                        continue
                    if ar[1].startswith('&'):
                        #assert ar[1].endswith(';')
                        if not d.has_key(ar[1]) or d[ar[1]] == ar[1]:
                            d[ar[1]] = ar[2]
                        elif d[ar[1]].count('&') > ar[2].count('&'):
                            d[ar[1]] = ar[2]
                        else:
                            #assert d[ar[1]] == ar[2]
                            pass
                    else:
                        if not d.has_key(ar[1]) or d[ar[1]] == ar[1]:
                            d[ar[1]] = ar[2]
                        else:
                            #assert d[ar[1]] == ar[2]
                            pass
            except:
                print >> sys.stderr, fname, line.encode('gb18030')
                raise
    return d

_ids_non_ucs = _load_ids_non_ucs('ids')

def ids_find_by_entity(entity):
    return _ids_non_ucs.get(entity)

import re
_idc_pat = re.compile(ur'[\u2FF0-\u2FFF]')

def _build_reverse_indices(d, t):
    r = {}
    for k, v in d.iteritems():
        #assert type(k) == int
        s = r.setdefault(v, set())
        k = unichar(k)
        s.add(k)
        r.setdefault(_idc_pat.sub(u'', v), set()).add(k)
    for k, v in t.iteritems():
        #assert type(k) == unicode
        s = r.setdefault(v, set())
        s.add(k)
        r.setdefault(_idc_pat.sub(u'', v), set()).add(k)
    return r

_ids_rev = _build_reverse_indices(_ids_ucs, _ids_non_ucs)

def ids_reverse_lookup(s):
    return _ids_rev.get(s)

def imgref(entity):
    assert entity.startswith('&')
    assert entity.endswith(';')
    s = _ucs_entity_map.get(entity)
    if s:
        return s
    d = _entity_map.get(entity[1:3])
    if not d:
        return xml.sax.saxutils.escape(entity)
    key = None
    keylen = 0
    for k in d.iterkeys():
        if entity.startswith(k, 1):
            if len(k) > keylen:
                key = k
                keylen = len(k)
    if not key or d[key][0] is None:
        return xml.sax.saxutils.escape(entity)
    prefix, digits, base, suffix, aname = d[key]
    n = int(entity[1 + keylen:-1], base)
    s = '%s%%0%d%s%s'% (prefix, digits, base == 10 and 'd' or 'x', suffix or '')
    s = s % (n,)
    t = ('<img alt="%s" src="http://glyphwiki.org/glyph/%s.svg" style="'
            'vertical-align: -0.1em; width: 1em;"/>'
            ) % (xml.sax.saxutils.escape(entity), s)
    return '<a target="_blank" href="http://glyphwiki.org/wiki/%s">%s</a>' % (
            s, t)

def repurl(entity):
    assert entity.startswith('&')
    assert entity.endswith(';')
    d = _entity_map.get(entity[1:3])
    if not d:
        return
    key = None
    keylen = 0
    for k in d.iterkeys():
        if entity.startswith(k, 1):
            if len(k) > keylen:
                key = k
                keylen = len(k)
    if not key:
        return
    prefix, digits, base, suffix, aname = d[key]
    n = int(entity[1 + keylen:-1], base)
    return 'http://www.chise.org/est/view/character/rep.%s:%s' % (
            aname, base == 10 and str(n) or hex(n))

def ids_find_url(s):
    if type(s) != str:
        if type(s) == unicode:
            s = s.encode('utf-8')
        else:
            s = unichar(s).encode('utf-8')
    return 'http://www.chise.org/ids-find?components=' + urllib.quote(s)

if __name__ == '__main__':
    a = set([x[0] for x in _coded_charset_entity_reference_alist])
    b = set([x[0] for x in _coded_charset_GlyphWiki_id_alist])
    print '\t'.join(sorted(a.difference(b)))
# vim:ts=4:sw=4:et:ai:cc=80
