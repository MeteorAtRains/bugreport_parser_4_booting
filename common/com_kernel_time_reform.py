# -*- coding: UTF-8 -*-

import re
from m_class.bugreport_class import BugreportParsedResult

def kernel_time_reform(r:BugreportParsedResult):
    if r.kernel_log[0][3] != 'logcat':
        return False
    else:
        ref_time = r.kernel_log[0][1]['time']

    kernel_newlog = list()

    for lineno, info, raw, _ in r.kernel_log:
        rela_time = format(relative_time(info['time'], ref_time), '.3f')
        # print(rela_time)
        if float(rela_time) > 100000:
            ref_time = info['time']
            rela_time = '0.000'

        kernel_newlog.append((lineno, rela_time, raw))
        # print((lineno, rela_time, raw))
    return kernel_newlog

def kernel_time_reform2(r:BugreportParsedResult):
    if r.kernel_log[0][3] != 'logcat':
        return False
    else:
        ref_time = r.kernel_log[0][1]['time']

    kernel_newlog = list()

    for lineno, info, raw, _ in r.kernel_log:
        rela_time = format(relative_time(info['time'], ref_time), '.3f')
        # print(rela_time)
        if float(rela_time) > 100000:
            ref_time = info['time']
            rela_time = '0.000'

        kernel_newlog.append((lineno, rela_time, info['priority'] + ': '+ info['message']))
        # print((lineno, rela_time, raw))
    return kernel_newlog

def kernel_get_dmesg(r:BugreportParsedResult):
    if r.kernel_log[0][3] != 'dmesg':
        return False

    kernel_newlog = list()

    for lineno, info, raw, _ in r.kernel_log:
        kernel_newlog.append((lineno, 0, raw))
        # print((lineno, rela_time, raw))
    return kernel_newlog

def relative_time(in_time, ref_time):
    # print(in_time.microsecond)
    # print(ref_time.microsecond)
    # print(in_time.microsecond - ref_time.microsecond)
    res_time =  float(in_time.microsecond - ref_time.microsecond) * 0.000001\
                +float(in_time.second - ref_time.second) * 1.0\
                +float(in_time.minute - ref_time.minute) * 60.0\
                +float(in_time.hour - ref_time.hour) * 60.0 * 60.0\
                +float(in_time.day - ref_time.day) * 60.0 * 60.0 * 24.0\
                +float(in_time.month - ref_time.month) * 60.0 * 60.0 * 24.0 * 12.0\
                +float(in_time.year - ref_time.year) * 60.0 * 60.0 * 24.0 * 12.0 * 365.0 

    return res_time