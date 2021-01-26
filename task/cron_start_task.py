#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys

sys.path.append('..')
from task.cron_start_task_c import parse_en, parse_id, parse_it, parse_cn

# from apscheduler.schedulers.blocking import BlockingScheduler
#
# sched = BlockingScheduler()

'''
    定时
'''

# 13 12,15,17,18 * * * cd /spider/google_news/task; python3 cron_start_task.py >> /data/logs/job/google_news.log 2>&1
# 13 12,15,17,18 * * * cd /spider/google_news/task; python3 cron_start_task.py >> /data/logs/google_news.log 2>&1
# */1 * * * * sleep 20 &&


# def parse():
#     log.info("CSpider cate info start" + now_datetime())
#     parse_c()
#     parse_g()
#     log.info("CSpider cate info end" + now_datetime())
#
#
# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='8,12,15,19,23', minute=11)
# def scheduled_job_parse_it():
#     log.info("parse_it  info start" + now_datetime())
#     parse_it()
#     log.info("parse_it  info end" + now_datetime())
#
#
# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='7,11,16,22', minute=50)
# def scheduled_job_parse_en():
#     log.info("parse_en info start" + now_datetime())
#     parse_en()
#     log.info("parse_en  info end" + now_datetime())
#
#
# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='8,12,15,19', minute=40)
# def scheduled_job_parse_id():
#     log.info("parse_id info start" + now_datetime())
#     parse_id()
#     log.info("parse_id info end" + now_datetime())
#
#
# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='6,10,18,23', minute=53)
# def scheduled_job_parse_cn():
#     log.info("parse_cn info start" + now_datetime())
#     parse_cn()
#     log.info("parse_cn info end" + now_datetime())
#
#
# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='7,11,14,20', minute=12)
# def scheduled_job_parse_g():
#     log.info("parse_g info start" + now_datetime())
#     parse_g()
#     log.info("parse_g info end" + now_datetime())


# @sched.scheduled_job('cron', day_of_week='mon-sun', hour='*/1', minute=9)
# def scheduled_job_AntaranewsSpider():
#     log.info("AntaranewsSpider cate info start" + now_datetime())
#     parse_it()
#     log.info("AntaranewsSpider cate info end" + now_datetime())
#


if __name__ == '__main__':
    parse_en()
    parse_cn()
    parse_id()
    parse_it()
