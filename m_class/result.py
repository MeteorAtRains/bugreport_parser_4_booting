# -*- coding: UTF-8 -*-

from typing import List, Dict
import os
from m_class.lv_input_command_parse import ParseInputCommand
from m_class.file_info_class import FileInfo
from debug.debug_print import *
from common.com_data_struct import SingleResult

class BootingResult:
    __TAG = 'BootingResult'
    __DEBUG = False

    def __print(self, msg):
        print_info(self.__TAG, self.__DEBUG, msg)

    def __set_cmds(self, c: ParseInputCommand):
        self.__content['path'] = c.args['result']
        self.__content['type'] = c.args['type']
        self.__print(self.__content['path'])

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
        self.__res_bugreport = {
            'com'   : list(),
        }
        self.__res = dict()
        self.__dispersing_files = dict()

        self.__set_cmds(cmd)
        # self.__init_result_args()

    @property
    def content(self):
        return self.__content
    @property
    def res(self):
        return self.__res
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
                    sf = SingleResult(f.name(),'')
                    sf.set_boot_progress(f.get_boot_progress())
        return

    def init_diff_res_depending_on_bugreport(self, num:int, name:str):
        count = 1
        for i in num:
            index = 'device' + str(i)
            self.__res_bugreport[index] = SingleResult(name, index)
        
        return

    def write_bugreport_res(self, fs_in:List[FileInfo], flag:bool):
        if self.__content['type'] == 'bugreport':
            if not os.path.exists(self.__content['path']):
                os.makedirs(self.__content['path'])            
            filename = 'common'
            with open(filename, mode = 'w') as f_out:
                for key in self.__res.keys():
                    for line in self.__res[key]:
                        f_out.writelines(line + '\n')

            if flag == True:
                for f_in in fs_in:
                    f_in.create_new_file(self.__content['path'])

        return


