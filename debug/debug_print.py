# -*- coding: UTF-8 -*-

DEBUG_ALL = True

def print_info(tag: str, flag: bool, info):
    if not DEBUG_ALL or not flag:
        return

    print(tag + ": " + info)