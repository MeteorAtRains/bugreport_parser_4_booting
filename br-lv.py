#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys,os,re
from typing import List, Callable, Iterable, Dict
from types import ModuleType
import argparse
import rules

from m_class.lv_input_command_parse import ParseInputCommand
from m_class.result import BootingResult
from m_class.bugreport_class import BugreportParsedResult
from m_class.file_info_class import FileInfo
# from parse_all import parseAll
from rules.rule_parsing_bootting_time import rule_parsing_bootting_time
from common.com_reflash import *
from common.com_file_name import *
from debug.debug_print import *

_TAG = 'main'
_DEBUG = True

def print_main(info):
    print_info(_TAG, _DEBUG, str(info))

def iter_rules():
    for item in dir(rules):
        # print_main(item)
        # print_main(isinstance(getattr(rules, item), ModuleType))
        if isinstance(getattr(rules, item), ModuleType):
            rule_module = __import__(f'rules.{item}', fromlist=['*'])
            print_main(rule_module)
            rule_func_nr = len([i for i in dir(rule_module)
                                if i.startswith('rule_')])
            if rule_func_nr != 1:
                raise RuntimeError(f'规则模块 {item} 中以 rule_ 开头的函数数应为'
                                   f'一个, 实际为 {rule_func_nr}')
            yield getattr(
                rule_module,
                next(i for i in dir(rule_module) if i.startswith('rule_')),
            )

cmd_info = ParseInputCommand()
fpath = cmd_info.args['path']
fnum = cmd_info.args['num']
ftype = cmd_info.args['type']
files_list = get_file_list(fpath, ftype, fnum)
files_content = list()
file_type = cmd_info.get_files_type()

cmd_info.set_main_device(files_list)

for ele in files_list:
    files_content.append(FileInfo(ele))

result = BootingResult(cmd_info)
# result.write_bugreport_by_file(files_content)

if cmd_info.get_files_type() == 'bugreport':
    print_main('start')
    result.res['rule_parsing_bootting_time'] = rule_parsing_bootting_time(cmd_info, files_content)
    # result.res['parsing_bootting_time'] = 
    # for rule_func in iter_rules():
    #     print_main('func')
    #     tmp = rule_func(cmd_info, files_content)
    #     result = reflash_result(result, tmp)

result.write_bugreport_res(files_content, True)


