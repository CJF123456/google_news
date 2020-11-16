#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-09-09 9:55
# @Author  : cjf
# @Version : 1.0
# @File    : newsSpider.py
# @Software: PyCharm
# @Desc    : None

import sys

sys.path.append('..')
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from configs.paramconfig import log_dir

logger_dict = {}

class logger(object):

    def __init__(self, logname):
        if logname not in logger_dict:
            log = logging.getLogger()
            formatter = logging.Formatter(
                '%(asctime)-12s level-%(levelname)-8s thread-%(thread)-8d %(message)s')  # 每行日志的前缀设置
            fileTimeHandler = TimedRotatingFileHandler(log_dir + str(logname), when="M", interval=15, backupCount=288)
            logging.basicConfig(level=logging.INFO)
            fileTimeHandler.setFormatter(formatter)
            log.addHandler(fileTimeHandler)
            logger_dict[logname] = log
        self.log = logger_dict[logname]

    def error(self, message):
        self.log.error(message)

    def debug(self, message):
        self.log.debug(message)

    def info(self, message):
        self.log.info(message)

    def warning(self, message):
        self.log.warning(message)

    def critical(self, message):
        self.log.critical(message)


project_name_ = os.path.abspath(os.path.join(os.getcwd(), ".."))
project_name = project_name_.split("\\")[-1] + ".log"
log = logger(project_name)
