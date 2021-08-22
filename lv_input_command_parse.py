# -*- coding: UTF-8 -*-

import re,os
import argparse
from typing import List, Tuple

class ParseInputCommand:
    __CMD_FILE_PATH = re.compile(r'dir=(?P<file_path>.*)')
    __CMD_FILE_NUM = re.compile(r'num=(?P<num>[0-9]+)')
    __CMD_SHORT = re.compile(r'-(?P<cmd>[a-z]+)')
    __CMD_TEST = re.compile(r'(?P<test>.*)')

    __ARG_TYPE_1 = re.compile(r'(?P<name>.*)=(?P<value>.*)')
    __ARG_TYPE_2 = re.compile(r'-(?P<value>[a-z,A-Z]+)')

    def __get_files_num(self):
        self.__args['num'] = self.__parser.parse_args().num
        print(self.__args['num'])

    def __get_files(self):
        path = os.path.abspath(self.__parser.parse_args().path)
        parsing_match_type = re.compile(self.__args['type'] + r'-.*')
        if self.__args['num'] == 0:
            self.__args['range'] = 'all'
            for root,dirs,files in os.walk(path):
                for one in files:
                    if parsing_match_type.match(one):
                        self.__args['file_list'].append((one,self.__args['type']))
        elif self.__args['num'] == 1:
            self.__args['range'] = 'single'
            for root,dirs,files in os.walk(path):
                for one in files:
                    if parsing_match_type.match(one):
                        self.__args['file_list'].append((one,self.__args['type']))
                        break
        elif self.__args['num'] == 2:
            self.__args['range'] = 'double'
            for root,dirs,files in os.walk(path):
                count = 0
                for one in files:
                    if parsing_match_type.match(one):
                        count += 1
                        self.__args['file_list'].append((one,self.__args['type']))
                    if count == self.__args['num']:
                        break

    def __get_parsing_type(self):
        self.__args['type'] = self.__parser.parse_args().type
        print(self.__args['type'])

    def __get_result_path(self):
        self.__args['result'] = self.__parser.parse_args().reuslt
        print(self.__args['result'])

    def __config_flags(self):
        self.__args['ignore-mark'] = self.__parser.parse_args().ignore
        print(self.__args['ignore-mark'])

    def __loading_args(self):
        self.__parser.add_argument('-p',    '--path',   default='.')
        self.__parser.add_argument('-n',    '--num',    type=int,   default=2)
        self.__parser.add_argument('-b',    '--base_num', type=int, default=0)
        self.__parser.add_argument('-t',    '--type',   default='bugreport')
        self.__parser.add_argument('-d',    action='store_true',    default=False)
        self.__parser.add_argument('-o',    default='./result/')
        self.__parser.add_argument('--order',   action='store_true',    default=True)
        self.__parser.add_argument('--ignore',  action='store_true',    default=True)
        self.__parser.add_argument('--base',    default='')
        self.__args['path'] = self.__parser.parse_args().path


    def __parse_args(self):
        self.__get_parsing_type()
        self.__config_flags()
        self.__get_files_num()
        self.__get_files()

    def __init__(self):
        self.__parser = argparse.ArgumentParser(description='开关机问题分析工具')
        # self._raw_args = dict()
        self.__args = {
            'path'          : '.',
            'files_num'     : 0,
            'type'          : 'bugreport',
            'file_list'     : list(),
            'range'         : '',
            'main_device'   : '',
        }

        self.__loading_args()
        self.__parse_args()

        # print(self.__parser)
        print(self.__args)

    @property
    def args(self):
        return self.__args

    def get_file_list(self):
        return self.__args['file_list']
    
    def get_file_type(self):
        return self.__args['type']
    
    def set_main_device(self, l: List[Tuple[str, str]]):
        n = self.__parser.parse_args().base_num
        print('length ' + str(n))
        if n > 0 and n < len(l):
            self.__args['main_device'] = l[n-1][0]
            print('main device')
            print(self.__args['main_device'])
        if self.__parser.parse_args().base != '':
            for ele in l:
                if self.__parser.parse_args().base == ele[0]:
                    self.__args['main_device'] = ele[0]
                    return
        self.__args['main_device'] = l[0][0]
        print('main device')
        print(self.__args['main_device'])
