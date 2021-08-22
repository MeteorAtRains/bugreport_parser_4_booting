# -*- coding: UTF-8 -*-

from typing import Dict

from lv_input_command_parse import ParseInputCommand

class BootingResult:
    def __init__(self, cmd:ParseInputCommand):
        self.__content = dict()
        self.__cmd = cmd

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



