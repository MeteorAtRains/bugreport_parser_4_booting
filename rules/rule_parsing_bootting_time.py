# -*- coding: UTF-8 -*-

import re
from m_class.result import BootingResult
from m_class.bugreport_class import BugreportParsedResult
from m_class.lv_input_command_parse import ParseInputCommand
from m_class.file_info_class import FileInfo
from typing import Dict,List,Tuple
from debug.debug_print import *

RULE_BOOT_PROGRESS_TIME_EVENTLOG = re.compile(r'(?P<moment>(boot_progress* | *_animation_done))'
                                r': (?P<timems>)')
#RULE_BOOT_PROGRESS_TIME_EVENTLOG = re.compile(r': (?P<timems>)')
RULE_BOOT_PROGRESS_TIME_EVENTLOG_BOOTTAG = re.compile(r'boot_progress.*|.*animation_done')


RULE_BOOT_PROGRESS_TIME_RAW = re.compile(r'(?P<month>\d{2})-(?P<day>\d{2}) '
                            r'(?P<hour>\d{2}):(?P<minute>\d{2}):'
                            r'(?P<second>\d{2}).(?P<millisecond>\d{3})'
                            r'( +(?P<uid>.+?))? +(?P<pid>.+?) '
                            r'+(?P<tid>.+?) +(?P<priority>.) '
                            r'(?P<tag>.*?) *: +(?P<message>.*)')

_TAG = "rule_parsing_bootting_time"
_DEBUG = True

def _print(info:str):
    print_info(_TAG, _DEBUG, info)

def paser_boot_progress_time(r:BugreportParsedResult):
    SHOW_BOOT_PROGRESS_TIME = False
    ress = {
        'boot_progress_start' : 5817,
        'boot_progress_preload_start' : 7130,
        'boot_progress_preload_end' : 10618,
        'boot_progress_system_run' : 11108,
        'boot_progress_pms_start' : 12161,
        'boot_progress_pms_system_scan_start' : 12628,
        'boot_progress_pms_data_scan_start' : 13307,
        'boot_progress_pms_scan_end' : 0,
        'boot_progress_pms_ready' : 0,
        'boot_progress_ams_ready' : 0,
        'boot_progress_enable_screen' : 0,
        'wm_boot_animation_done' : 0,
    }
    boot_progress_time_tags = list()

    # print('------- in paser_boot_progress_time -------')
    for lineno, line_dict, line in r.event_log:
        r = RULE_BOOT_PROGRESS_TIME_EVENTLOG_BOOTTAG.match(line_dict['tag'])
        if r:
            ress[line_dict['tag']] = int(line_dict['message'])
            boot_progress_time_tags += [line_dict['tag']]

    # for tag in boot_progress_time_tags:
    #     print(tag+": "+str(ress[tag]))

    parse_ress = {
        'start_period' : 
            ress['boot_progress_start'],
        'before_preload': 
            ress['boot_progress_preload_start'] - ress['boot_progress_start'],
        'preload_period':
            ress['boot_progress_preload_end']-ress['boot_progress_preload_start'],
        'before_system_run':
            ress['boot_progress_system_run']-ress['boot_progress_preload_end'],
        'before_pms':
            ress['boot_progress_pms_start']-ress['boot_progress_system_run'],
        'pms_period':
            ress['boot_progress_pms_ready']-ress['boot_progress_pms_start'],
        'ams_start':
            ress['boot_progress_ams_ready']-ress['boot_progress_pms_ready'],
        'enable_screen':
            ress['boot_progress_enable_screen']-ress['boot_progress_ams_ready'],
        'after_enable_screen':
            ress['wm_boot_animation_done']-ress['boot_progress_enable_screen'],
        'total':
            ress['wm_boot_animation_done']
    }

    # print(parse_ress['after_enable_screen'])
    # for parse_res in parse_ress:
    #     print(parse_res+": "+str(parse_ress[parse_res]))

    if SHOW_BOOT_PROGRESS_TIME:
        for boot_progress_time_tag in boot_progress_time_tags:
            print(boot_progress_time_tag+': '+str(ress[boot_progress_time_tag]))

    resall = {
        'moment' : [ress],
        'period' : [parse_ress],
        'tags' : boot_progress_time_tags,
    }
    return resall

def _compare_two_bugreport(main_file:FileInfo, comparing_file:FileInfo):
    res = list()
    # diff_period = dict()
    # for file_info in file_info_list:
    #     if file_info.property['testkind'] == 'c':
    #         c_period = file_info.property['boot_progress_time']['period']
    #     if file_info.property['testkind'] == 'd':
    #         d_period = file_info.property['boot_progress_time']['period']

    # tag_list = [    'start_period',
    #                 'before_preload',
    #                 'preload_period',
    #                 'before_system_run',
    #                 'before_pms',
    #                 'pms_period',
    #                 'ams_start',
    #                 'enable_screen',
    #                 'after_enable_screen',
    #                 'total']

    # for tag in tag_list:
    #     diff_period[tag] = int(c_period[0][str(tag)]) - int(d_period[0][str(tag)])
    
    # for tag in tag_list:
    #     print(tag+': '+str(diff_period[tag]))

    # return diff_period
    return res

def _set_boot_progress(l:List[Tuple[str, int]]):
    res = list()
    for line in l:
        res.append(line[0] + ': ' + str(line[1]) + 'ms')

    return res

def rule_parsing_bootting_time(c:ParseInputCommand, fs:List[FileInfo]) -> list:
    _print('start')
    _print('files num - ' + str(c.get_files_num()))
    main_device = c.get_main_device()
    b_res = list()
    b_res.append('rule_parsing_bootting_time:')
    if c.get_files_num() == 2 and c.get_files_type() == 'bugreport':
        # main_file = FileInfo(Tuple['',''])
        # comparing_file = FileInfo(Tuple['',''])
        main_file = ''
        comparing_file = ''
        for f in fs:
            if f.name() == main_device:
                main_file = f
                _print('main file name - ' + main_file.name())
            else:
                comparing_file = f
                _print('comparing file name - ' + comparing_file.name())
        b_res.append('main_device - ' + main_file.name())
        b_res += _set_boot_progress(main_file.get_boot_progress())
        b_res.append('\ncomparing_file - ' + comparing_file.name())
        b_res += _set_boot_progress(comparing_file.get_boot_progress())

        # b_res += paser_boot_progress_time(main_file.get_boot_progress())
        # b_res += paser_boot_progress_time(comparing_file.get_boot_progress())
            # print(b_res.content['parsing_bootting_time'])
    
    for line in b_res:
        _print(str(line))

    return b_res