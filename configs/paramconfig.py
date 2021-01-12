#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 15:53
# @Author  : cjf
# @Site    : User-Agent集合
# @File    : headers.py
# @Software: PyCharm
import sys
sys.path.append('..')

import sys


def get_log_dir():
    os_name = sys.platform
    if "darwin" in os_name:
        log_dir = '/Users/chengjianfeng/Documents/logs/'
    elif "win32" in os_name:
        log_dir = 'D:/logs/'
    elif "linux" in os_name:
        log_dir = '/data/logs/'
    else:
        log_dir = '/data/logs/'
    return log_dir
