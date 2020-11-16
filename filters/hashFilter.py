#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 16:50
# @Author  : cjf
# @Site    : 时间格式转化
# @File    : timeUtil.py
# @Software: PyCharm
import sys

sys.path.append('..')
import hashlib
from dbutils.redisPool import RedisCache
from utils.timeUtil import now_datetime


def md5_filter(vmd5, vmd5name):
    videoHash = RedisCache(vmd5name)
    if videoHash.hexists(vmd5):
        return 1
    else:
        videoHash.hset(vmd5, now_datetime())
        return 0


def make_md5(data):
    tmp = hashlib.md5()
    tmp.update(data.encode("utf8"))
    fmd5 = tmp.hexdigest()
    return fmd5


def make_md5_eu(data):
    tmp = hashlib.md5()
    tmp.update(data)
    fmd5 = tmp.hexdigest()
    return fmd5


# hexists md5
def hexists_md5_filter(vmd5, vmdname):
    videoHash = RedisCache(vmdname)
    if videoHash.hexists(vmd5):
        return 1
    else:
        # videoHash.hset(vmd5, now_datetime())
        return 0


# hset md5
def hset_md5_filter(vmd5, vmdname):
    videoHash = RedisCache(vmdname)
    if videoHash:
        videoHash.hset(vmd5, now_datetime())
        return 1
    else:
        return 0

def hdel_md5_filter(vmd5, vmdname):
    videoHash = RedisCache(vmdname)
    if videoHash:
        videoHash.hdel(vmd5)
        return 1
    else:
        return 0