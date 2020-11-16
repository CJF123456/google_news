#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 16:18
# @Author  : cjf
# @Site    : redis工具类
# @File    : redisUtil.py
# @Software: PyCharm


import sys

sys.path.append('..')

import redis
from configs.dbconfig import RedisConfig

class RedisQueue(object):
    # Simple Queue with Redis Backend
    def __init__(self, name, namespace=None, **redis_kwargs):
        self.__db = redis.Redis(host=RedisConfig.HOST, port=RedisConfig.PORT, db=RedisConfig.DBID,
                                password=RedisConfig.RPASSWORD)
        if namespace == None:
            self.key = '%s' % name
        else:
            self.key = '%s:%s' % (namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def rput(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def lput(self, item):
        """Put item into the queue."""
        self.__db.lpush(self.key, item)

    def qlist(self, start, end):
        """Return a slice of the list ``name`` between  position ``start`` and ``end``"""
        return self.__db.lrange(self.key, start, end)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def lget(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def rget(self, block=True, timeout=None):

        if block:
            item = self.__db.brpop(self.key, timeout=timeout)
        else:
            item = self.__db.rpop(self.key)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)


# class RedisHashMap(object):
#     """Simple hash with Redis Backend"""
#
#     def __init__(self, name='myhash', **redis_kwargs):
#         """The default connection parameters are: host=‘localhost‘, port=6379, db=0"""
#         self.__db = redis.Redis(host=config_DB.RSHOST, port=config_DB.RSPORT, db=config_DB.RSDB,
#                                 password=config_DB.RPASSWORD)
#         self.name = '%s' % (name)
#
#     def hsize(self):
#         """Return the approximate size of the hash."""
#         return self.__db.hlen(self.name)
#
#     def set(self, key, val):
#         """Put k/v into the hash."""
#         self.__db.hset(self.name, key, val)
#
#     def get(self, name, key):
#         """get key's val from hashname  """
#         return self.__db.hget(name, key)
#
#     def exist(self, name, key):
#         """if return 0 ,not exists,otherwise 1 ,exists"""
#         return self.__db.hexists(name, key)
#
#     def hashdel(self, name, key):
#         """delete key"""
#         self.__db.hdel(name, key)
#
#     def get_keys(self, name):
#         """get all keys , return list"""
#         return self.__db.hkeys(name)
