# -*- coding: UTF-8 -*-

import re
from bugreport_class import BugreportParsedResult
from lv_input_command_parse import ParseInputCommand
from typing import Dict,List,Tuple
from result import BootingResult

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

# boot_progress_time_tag = [
#     'boot_progress_start',
#     'boot_progress_preload_start',
# ]

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



def rule_parsing_bootting_time(c:ParseInputCommand, f:list()) -> BootingResult:
    b_res = BootingResult('')
    print("in bootting time")

    for onefile in f:
        b_res.content['parsing_bootting_time'] = paser_boot_progress_time(onefile.property["parse_res"])
        # print(b_res.content['parsing_bootting_time'])

    return b_res