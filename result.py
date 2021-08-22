# -*- coding: UTF-8 -*-

from typing import List, Dict

from lv_input_command_parse import ParseInputCommand
from debug.debug_print import *
from file_info_class import FileInfo
from common.com_data_struct import SingleResult

class BootingResult:
    __TAG = 'BootingResult'
    __DEBUG = True

    def __print(self, msg):
        print_info(self.__TAG, self.__DEBUG, msg)

    def __set_cmds(self, c: ParseInputCommand):
        self.__content['path'] = c.args['result']
        self.__content['type'] = c.args['type']

    def __init__(self, cmd: ParseInputCommand):
        self.__content = {
            'path' : '',
        }
        self.__cmds = dict()
        self.__main_file = {
            'common'    : list(),
            'sp'        : List[SingleResult],
            'file_name' : list(),
        }
        self.__dispersing_files = dict()

        self.__set_cmds(cmd)
        # self.__init_result_args()

    @property
    def content(self):
        return self.__content

    # @property
    # def content_with_key(self, key):
    #     return self.__content[key]

    def set_content_with_key(self, key, value):
        self.__content[key] = value

    def add_content_with_key(self, key, value):
        self.__content[key] += value
    
    def write_bugreport_by_file(self, l:List[FileInfo]):
        if self.__content['type'] == 'bugreport':
            for f in l:
                if f.name() not in self.__main_file['file_name']:
                    self.__main_file['file_name'].append(f.name())
                    sf = SingleResult(f.name())
                    sf.set_boot_progress(f.get_boot_progress())
        return



