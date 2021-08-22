# -*- coding: UTF-8 -*-

from typing import List
import re, os
from lv_input_command_parse import ParseInputCommand

def get_file_list(f_path, f_type, f_num) -> List[dict]:
    ret = list()
    path = os.path.abspath(f_path)
    parsing_match_type = re.compile(f_type + r'-.*')
    if f_num == 0:
        for root,dirs,files in os.walk(path):
            for one in files:
                if parsing_match_type.match(one):
                    ret.append((one,c.args['type']))
    elif f_num == 1:
        for root,dirs,files in os.walk(path):
            for one in files:
                if parsing_match_type.match(one):
                    ret.append((one,f_type))
                    break
    elif f_num == 2:
        for root,dirs,files in os.walk(path):
            count = 0
            for one in files:
                if parsing_match_type.match(one):
                    count += 1
                    ret.append((one,f_type))
                if count == f_num:
                    break
    
    return ret

