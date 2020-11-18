#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys

sys.path.append('..')
from mylog.mlog import log
from utils.timeUtil import now_datetime
from task.cron_start_task_c import parse_c
from task.cron_start_task_g import parse_g

'''
    定时
'''


# 13 12,15,17,18 * * * cd /spider/google_news/task; python3 cron_start_task.py >> /data/logs/google_news.log 2>&1




def parse():
    log.info("CSpider cate info start" + now_datetime())
    parse_c()
    parse_g()
    log.info("CSpider cate info end" + now_datetime())


if __name__ == '__main__':
    parse()
