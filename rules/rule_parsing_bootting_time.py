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
    res.append('\n 各阶段差距:')
    m_bp = main_file.get_boot_progress()
    c_bp = comparing_file.get_boot_progress()

    m = dict()
    c = dict()
    for m_it in m_bp:
        if m_it[0] not in m.keys():
            m[m_it[0]] = (m_it[1], 1)
        else:
            m[m_it[0] + str(m[m_it[0]][1])] = (m_it[1], 1)
            m[m_it[0]][1] += 1

    for c_it in c_bp:
        if c_it[0] not in c.keys():
            c[c_it[0]] = (c_it[1], 1)
        else:
            c[c_it[0] + str(c[c_it[0]][1])] = (c_it[1], 1)
            c[c_it[0]][1] += 1
    
    _print(str(m))
    key_ref = [
        'boot_progress_start',
        'boot_progress_preload_start',
        'boot_progress_preload_end',
        'boot_progress_system_run',
        'boot_progress_pms_start',
        'boot_progress_pms_system_scan_start',
        'boot_progress_pms_data_scan_start',
        'boot_progress_pms_scan_end',
        'boot_progress_pms_ready',
        'boot_progress_ams_ready',
        'boot_progress_enable_screen',
        'wm_boot_animation_done',
    ]
    pre_m = 0
    pre_c = 0
    for key in key_ref:
        if key not in m.keys() and not key in c.keys():
            continue

        diff = 0
        if key in m.keys() and key not in c.keys():
            c[key][0] = pre_c
        elif key not in m.keys() and key in c.keys():
            m[key][0] = pre_m
        
        diff = m[key][0] - pre_m - (c[key][0] - pre_c)
        pre_m = m[key][0]
        pre_c = c[key][0]
        tail = ' [*]' if diff > 500 else ''
        res.append('diff_' + key + ': ' + str(diff) + tail)
        
    return res

def _set_boot_progress(l:List[Tuple[str, int]]):
    res = list()
    pre_time = 0
    for line in l:
        gap = line[1] - pre_time
        pre_time = line[1]
        res.append(line[0] + ': ' + str(line[1]) + 'ms [' + str(gap) + ']')

    return res

def rule_parsing_bootting_time(c:ParseInputCommand, fs:List[FileInfo]) -> list:
    _print('start')
    _print('files num - ' + str(c.get_files_num()))
    main_device = c.get_main_device()
    b_res = list()
    b_res.append('[rule_parsing_bootting_time]')
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
        b_res += _compare_two_bugreport(main_file, comparing_file)

        # b_res += paser_boot_progress_time(main_file.get_boot_progress())
        # b_res += paser_boot_progress_time(comparing_file.get_boot_progress())
            # print(b_res.content['parsing_bootting_time'])
    
    for line in b_res:
        _print(str(line))

    return b_res