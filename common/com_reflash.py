# -*- coding: UTF-8 -*-

from result import BootingResult

def reflash_result(b:BootingResult, tmp:BootingResult):
    for key in b.content.keys():
        print(key)
        if  key in tmp.content.keys():
            b.add_content_with_key(key, b.content[key])

    for key in tmp.content.keys():
        print(key)
        if key not in b.content.keys():
            b.set_content_with_key(key, tmp.content[key])

    return b