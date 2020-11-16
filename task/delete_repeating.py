#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-11-09 10:13
# @Author  : cjf
# @Version : 1.0
# @File    : delete_repeating.py
# @Software: PyCharm
# @Desc    : None
import sys

sys.path.append('..')
from utils.timeUtil import now_datetime
from dbutils.sqlServerPool import MSSQL
from mylog.mlog import log



def get_spider_kw_mysql(sql):
    mysql = MSSQL()
    mobile_tasks = mysql.update(sql)
    log.info(now_datetime()+":"+str(mobile_tasks))
    return mobile_tasks


if __name__ == '__main__':
    sql = "delete from t_doc_info where title in (select title from t_doc_info group by title having count(title) > 1) and  id not in (select max(id) from t_doc_info group by title  having count(title)>1)"
    get_spider_kw_mysql(sql)
