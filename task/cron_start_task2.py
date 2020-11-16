#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys

sys.path.append('..')

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

from mylog.mlog import log
from utils.timeUtil import now_datetime
from task.cron_start_task_c import parse_c
from task.cron_start_task_g import parse_g

'''
    定时
'''


# 0 12 * * * python3 /spider/google_news/task/cron_start_task.py >> /data/logs/google_news.log 2>&1
# 13 4,6,8,10,12,14,16,18,20,22 * * * cd /spider/google_news/task; python3 cron_start_task.py >> /data/logs/google_news.log 2>&1

@sched.scheduled_job('cron', day_of_week='mon-sun', hour='4,6,8,10,12,14,16,18,20,22', minute=10, second=7)
def scheduled_job_hourSpider():
    log.info("CSpider cate info start" + now_datetime())
    parse_c()
    log.info("CSpider cate info end" + now_datetime())


@sched.scheduled_job('cron', day_of_week='mon-sun', hour='5,7,9,11,13,15,17,21,23', minute=57, second=15)
def scheduled_job_guoSpider():
    log.info("guoSpider cate info start" + now_datetime())
    parse_g()
    log.info("guoSpider cate info end" + now_datetime())


sched.start()
