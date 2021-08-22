from bugreport_class import BugreportParsedResult
from file_info_class import FileInfo
# from bugreport_v2_class import BugreportParsedPerf
from rules.get_boot_progress_time import *

import os,re
from typing import List

def parseAll(lv_cmd):
    lv_files = list()
    file_contents = list()
    bugreport_ress = list()
    boot_progress_time = list()
    allfiles = list()
    
    file_path = lv_cmd.property['abspath']
    for root,dirs,files in os.walk(file_path):
        for tmpfile in files:
            # 创建文件对象，获取文件信息
            onefile = FileInfo(tmpfile)
            # 对文件的解析同做
            onefile.parse_bugreport()
            onefile.parse_file()
            if lv_cmd.property['create_new_files']:
                onefile.create_new_file()
            # 生成文件链表
            allfiles += [onefile]

    if lv_cmd.property['filekind'] == 'bugreport':
        if lv_cmd.property['files_num'] == 2:
            print('########## show diff ##########')
            compare_two_bugreport(allfiles)
        if lv_cmd.property['files_num'] == 1:
            for onefile in allfiles:
                if onefile.property['testkind'] == lv_cmd.property['parse_file_testkind']:
                    print("############ show in one file ##############")
                    parse_one_bugreport(onefile.property)
                    return True
        if lv_cmd.property['files_num'] == 0:
            for onefile in allfiles:
                parse_one_bugreport(onefile.property)

    return True

def compare_two_bugreport(file_info_list):
    diff_period = dict()
    for file_info in file_info_list:
        if file_info.property['testkind'] == 'c':
            c_period = file_info.property['boot_progress_time']['period']
        if file_info.property['testkind'] == 'd':
            d_period = file_info.property['boot_progress_time']['period']

    tag_list = [    'start_period',
                    'before_preload',
                    'preload_period',
                    'before_system_run',
                    'before_pms',
                    'pms_period',
                    'ams_start',
                    'enable_screen',
                    'after_enable_screen',
                    'total']

    for tag in tag_list:
        diff_period[tag] = int(c_period[0][str(tag)]) - int(d_period[0][str(tag)])
    
    for tag in tag_list:
        print(tag+': '+str(diff_period[tag]))

    return diff_period

def parse_one_bugreport(onefile_info):
    print(onefile_info['kind'])
    if onefile_info['kind'] == 'unknown':
        return False
    if onefile_info['testkind'] == 'c':
        print("############## 测试机 #############")
    else:
        print("############## 对比机 #############")
    print("时间点：")
    for otag in onefile_info['boot_progress_time']['tags']:
        print(otag+': '+str(onefile_info['boot_progress_time']['moment'][0][otag]))
    tag_list = ['start_period',
                'before_preload',
                'preload_period',
                'before_system_run',
                'before_pms',
                'pms_period',
                'ams_start',
                'enable_screen',
                'after_enable_screen',
                'total']
    print("\n各阶段时间：")
    for otag in tag_list:
        print(otag+': '+str(onefile_info['boot_progress_time']['period'][0][otag]))