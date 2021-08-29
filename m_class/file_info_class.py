# -*- coding: UTF-8 -*-

from typing import Dict, Tuple, List
import re

from m_class.bugreport_class import BugreportParsedResult
from common.com_data_struct import BOOT_STATUS
from common.com_kernel_time_reform import *
from debug.debug_print import *

################################################# 方法类说明 ###############################################
#   1.通过出入文件名构建文件类：FileInfo(<filename>)
#   2.主要功能：读取文件，解析文件
#   3.解析文件类型及存储数据：
#   -文件头用字母'c'/'d'表示测试机还是对比机
#   ------------------------------------------------------------------------------------------------------
#     文件类型 | 是否自命名/提取 |                             文件名                            | 匹配文件信息
#   ------------------------------------------------------------------------------------------------------
#   bugreport| 系统提取，284  |c-bugreport-toco_global-RKQ1.200826.002-2020-11-18-14-54-17.txt|
#   ------------------------------------------------------------------------------------------------------
##########################################################################################################

class FileInfo:
    __FI_FILE_NAME = re.compile(r'(?P<testkind>[cd]{1})-(?P<kind>([a-z]*))-(?P<other>.+)\.txt')
    __FI_FILE_NAME_OTHER_BUGREPORT = re.compile(r'(?P<name>.+)_(?P<region>.+)-(?P<version>)-(?P<time>)')
    __FI_TIME_1 = re.compile(r'(?P<year>)-(?P<month>)-(?P<day>)-(?P<hour>)-(?P<minute>)-(?P<second>)')
    __FI_BOOT_TAG = re.compile(r'boot_progress.*|.*animation_done')

    __TAG = 'FileInfo'
    __DEBUG = True

    def __print(self, msg):
        print_info(self.__TAG, self.__DEBUG, msg)    

    def __parsing_file(self):
        if self.__property['kind'] == 'bugreport':
            self.__property['parse_res'] = BugreportParsedResult(self.__property['contents'])
            # 获取开机时间信息
            # self.__property['boot_progress_time'] = paser_boot_progress_time(self.__property['parse_res'])
            # 转换kernel log的格式
            if self.__property['parse_res'].kernel_log[0][3] == 'logcat':
                self.__property['kernel2'] = kernel_time_reform(self.__property['parse_res'])
                self.__property['kernel3'] = kernel_time_reform2(self.__property['parse_res'])
            if self.__property['parse_res'].kernel_log[0][3] == 'dmesg':
                self.__property['kernel2'] = kernel_get_dmesg(self.__property['parse_res'])
                self.__property['kernel3'] = self.__property['kernel2']
            self.__print('bugreport文件解析成功')

    def __check_is_boot_normal(self, bp_map: Dict):
        if len(bp_map) == 0: # 如果bp_map里边没有任何信息，说敏此次开机没有任何开机信息。
            return  BOOT_STATUS.NO_BOOT_INFO   
        if 'wm_boot_animation_done' in bp_map.keys(): 
            for key in bp_map:
                if bp_map[key] >= 2:
                    return BOOT_STATUS.BOOT_REPEATED_AND_SUCCESS
                elif bp_map[key] == 0: #预留，等后期在map初始化中写死几个阶段再用
                    return BOOT_STATUS.BOOT_SKIP_PERIOD_AND_SUCCESS
            return BOOT_STATUS.NORMALL
        else:
            for key in bp_map:
                if bp_map[key] >= 2:
                    return BOOT_STATUS.BOOT_REPEATED_AND_FAILED
            return BOOT_STATUS.EXIT_NOT_END

    def __get_boot_progress(self, event_log) -> Tuple[list, int]:
        bp_points = list()
        ret_bp_points = str()
        bp_points_map = dict()
        ret_event = list()
        pre_bp_point = 0
        last_period = ''
        last_period_moment = 0
        for lineno, log, raw in event_log:
            if self.__FI_BOOT_TAG.match(log['tag']):
                last_period = log['tag']
                last_period_moment = log['time']
                if log['tag'] in bp_points_map.keys():
                    bp_points_map[log['tag']] += 1
                else:
                    bp_points_map[log['tag']] = 1
                bp_points.append((log['tag'], int(log['message'])))
                interval_time = int(log['message']) - pre_bp_point
                pre_bp_point = int(log['message'])
        
        boot_status = self.__check_is_boot_normal(bp_points_map)

        # bp_title =  '无开机信息' if boot_status == BOOT_STATUS.NO_BOOT_INFO else\
        #     '正常开机' if boot_status == BOOT_STATUS.NORMALL else\
        #     '完成开机，但有重复过程' if boot_status == BOOT_STATUS.BOOT_REPEATED_AND_SUCCESS else\
        #     '完成开机，但过阶段跳过' if boot_status == BOOT_STATUS.BOOT_SKIP_PERIOD_AND_SUCCESS else\
        #     '重复开机且未完成' if boot_status == BOOT_STATUS.BOOT_REPEATED_AND_FAILED else\
        #     '开机一次且未完成' if boot_status == BOOT_STATUS.EXIT_NOT_END else '未知开机情况'
        return (bp_points, boot_status)

    def __get_more_info(self):
        if self.__property['kind'] == 'bugreport':
            boot_info = self.__get_boot_progress(self.__property['parse_res'].event_log)
            self.__property['boot_progress'] = boot_info[0]
            self.__property['boot_status'] = boot_info[1]

    # to be confirmed
    def __create_new_file(self, path:str):
        if self.__property['kernel2']:
            filename = path + 'kernel2_'+self.__property['name']
            with open(filename, 'w') as f:
                for lineno, abtime, raw in self.__property['kernel2']:
                    f.writelines('['+str(abtime)+']'+' ' +raw)
        if self.__property['kernel3']:
            filename = path + 'kernel_v3_'+self.__property['name']
            with open(filename, 'w') as f:
                for lineno, abtime, raw in self.__property['kernel3']:
                    f.writelines('['+str(abtime)+']'+' ' +raw + '\n')                    
        return True


    def __read_file(self):
        with open(self.__property['name'],mode='r',errors='ignore') as f:
            self.__property['contents'] = f.readlines()

    def __init__(self, filename):
        self.__property = {
            'name'          : filename[0],
            'kind'          : filename[1],
            'kernel2'       : list(),
            'kernel3'       : list(),
            'contents'      : '',
            'parse_res'     : '',
            'path'          : '',
        }
        self.__log = {
            'kernel2' : list(),
            'kernel3' : list()
        }
        # print(self.__property)
        self.__read_file()
        self.__parsing_file()
        self.__get_more_info()
        # self.__parse_bugreport(filename[0])
        # 

    @property
    def property(self)-> Dict[str, tuple]:
        return self.__property
    #对外提供解析文件的方法
    def parse_file(self):
        self.__parse_file()

    # def parse_bugreport(self):
    #     self.__parse_bugreport()
    def create_new_file(self, path:str):
        self.__create_new_file(path)

    def name(self):
        return self.__property['name']

    def get_boot_progress(self):
        return self.__property['boot_progress']