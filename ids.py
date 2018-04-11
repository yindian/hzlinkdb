#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import traceback

try:
    import icu
    def isidc(c):
        return operands(c) > 0
    def operands(c):
        if not c:
            return 0
        try:
            if type(c) != unicode:
                c = unichr(c)
            if icu.Char.hasBinaryProperty(c, icu.UProperty.IDS_BINARY_OPERATOR):
                return 2
            elif icu.Char.hasBinaryProperty(c, icu.UProperty.IDS_TRINARY_OPERATOR):
                return 3
            return 0
        except:
            traceback.print_exc()
            return 0
except:
    traceback.print_exc()
    def isidc(c):
        try:
            if type(c) == unicode:
                c = ord(c)
            return 0x2FF0 <= c < 0x3000
        except:
            #traceback.print_exc()
            return False
    def operands(c):
        try:
            if type(c) == unicode:
                c = ord(c)
            if 0x2FF0 <= c < 0x2FFE:
                if c in (0x2FF2, 0x2FF3):
                    return 3
                else:
                    return 2
            elif 0x2FFE <= c < 0x3000: # L2018-012
                return 1
            else:
                return 0
        except:
            traceback.print_exc()
            return 0

if __name__ == '__main__':
    pass
# vim:ts=4:sw=4:et:ai:cc=80
