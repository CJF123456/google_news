#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys

sys.path.append('..')
from task.cron_start_task_c import parse_c
from task.cron_start_task_g import parse_g

if __name__ == '__main__':
    parse_c()
    parse_g()
