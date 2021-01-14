#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 15:08
# @Author  : xiaochen
# @Site    : 数据库配置文件
# @File    : dbconfig.py
# @Software: PyCharm
import sys

sys.path.append('..')

class sqlServerConfig:
    DBHOST = '123.57.xxx.xx'
    DBPORT = 1433
    DBUSER = 'xx'
    DBPWD = 'p@xx'
    DBNAME = 'xx'
    DBCHAR = 'utf8'


# redis配置
class RedisConfig:
    ###################redis数据库库配置################################
    # redis-cli -h 120.26.90.122 -p 6379 -a v1@spider
    HOST = '47.242.xx.xx'
    PORT = 6379
    DBID = '0'
    RPASSWORD = 'xxxxxx'


class NewsTaskSql:
    t_doc_info_insert = 'insert into t_doc_info(body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name,if_top,keyword, ' \
                        'source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime, CrawlTime,Hidden,file_name, file_path) values' \
                        ' (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    image_insert = "insert into Image(ImageId, Caption, Uri, FileStream, CrawlTime, InUse) values (%s,%s,%s,%s,%s,%s)"
