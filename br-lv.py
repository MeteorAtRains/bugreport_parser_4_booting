#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys,os,re
from typing import List, Callable, Iterable, Dict
from types import ModuleType
import argparse
import rules

from lv_input_command_parse import ParseInputCommand
# from parse_all import parseAll
from rules import *
from common.com_reflash import *
from common.com_file_name import *
from file_info_class import FileInfo
from result import BootingResult
from bugreport_class import BugreportParsedResult


def iter_rules():
    for item in dir(rules):
        if isinstance(getattr(rules, item), ModuleType):
            rule_module = __import__(f'rules.{item}', fromlist=['*'])
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
file_type = cmd_info.get_file_type()

cmd_info.set_main_device(files_list)

for ele in files_list:
    files_content.append(FileInfo(ele))

result = BootingResult(cmd_info)

if cmd_info.get_file_type() == 'bugreport':
    print(1)
    for rule_func in iter_rules():
        tmp = rule_func(cmd_info, files_content)
        result = reflash_result(result, tmp)