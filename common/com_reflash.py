# -*- coding: UTF-8 -*-

from m_class.result import BootingResult

def reflash_result(b:BootingResult, tmp:BootingResult):
    for key in b.content.keys():
        if  key in tmp.content.keys():
            b.add_content_with_key(key, b.content[key])

    for key in tmp.content.keys():
        if key not in b.content.keys():
            b.set_content_with_key(key, tmp.content[key])

    return b

def reflash_result_4bugreport(b:BootingResult, tmp:BootingResult):

    return b