# -*- coding: UTF-8 -*-

from typing import List, Tuple
from debug.debug_print import *

class BOOT_STATUS :
    NORMALL = int(0)
    EXIT_NOT_END = int(1)
    BOOT_REPEATED_AND_SUCCESS = int(2)
    BOOT_REPEATED_AND_FAILED = int(3)
    BOOT_SKIP_PERIOD_AND_SUCCESS = int(4)
    NO_BOOT_INFO = int(5)

class SingleResult:
    __TAG = 'SingleResult'
    __DEBUG = True
    def __print(self, msg):
        print_info(self.__TAG, self.__DEBUG, msg)

    def __init__(self, name:str, index:str):
        self.__name = name
        self.__index = index
        self.__boot_progress = str()
        self.__res = list()

    @property
    def name(self):
        return self.__name

    def set_boot_progress(self, l:List[Tuple[str, int]]):
        for line in l:
            self.__boot_progress += \
                line[0] + ": " + str(line[1]) + "ms\n"

        self.__print(self.__boot_progress)
