#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 16:37
# @Author  : cjf
# @Site    : 
# @File    : redisPool.py
# @Software: PyCharm

import sys

sys.path.append('..')
import redis
from configs.dbconfig import RedisConfig


def operator_status(func):
    '''get operatoration status
    '''

    def gen_status(*args, **kwargs):
        error, result = None, None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error = str(e)

        return {'result': result, 'error': error}

    return gen_status


class RedisCache(object):
    def __init__(self, key):
        if not hasattr(RedisCache, 'pool'):
            RedisCache.create_pool()
        self.__db = redis.Redis(connection_pool=RedisCache.pool)
        self.key = key

    @staticmethod
    def create_pool():
        RedisCache.pool = redis.ConnectionPool(
            host=RedisConfig.HOST,
            port=RedisConfig.PORT,
            db=RedisConfig.DBID,
            password=RedisConfig.RPASSWORD
        )

    # @operator_status
    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    # @operator_status
    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    # @operator_status
    def qput(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    # @operator_status
    def qget(self, block=True, timeout=None):
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

    # @operator_status
    def qlist(self, start, end):
        """Return a slice of the list ``name`` between  position ``start`` and ``end``"""
        return self.__db.lrange(self.key, start, end)

    # @operator_status
    def qltrim(self, start, end):
        """ Return a trim list between position start to end """
        return self.__db.ltrim(self.key, start, end)

    # @operator_status
    def hsize(self):
        """Return the approximate size of the hash."""
        return self.__db.hlen(self.key)

    def delete(self):
        """ delete key"""
        return self.__db.delete(self.key)

    # @operator_status
    def hset(self, k, v):
        """Put k/v into the hash."""
        self.__db.hset(self.key, k, v)

    # @operator_status
    def hget(self, k):
        """get k's value from hash  """
        return self.__db.hget(self.key, k)

    # @operator_status
    def hexists(self, k):
        """
        if return 0 ,not exists
        otherwise 1 ,exists
        """
        return self.__db.hexists(self.key, k)

        # @operator_status

    def lpush(self, k):

        return self.__db.lpush(self.key, k)

    def lpop(self):

        return self.__db.lpop(self.key)

    def llen(self):
        return self.__db.llen(self.key)

    # @operator_status
    def hdel(self, k):
        """delete k"""
        self.__db.hdel(self.key, k)

    # @operator_status
    def hkeys(self):
        """get all keys , return list"""
        return self.__db.hkeys(self.key)

    def set(self, v):
        return self.__db.set(self.key, v)

    def get(self, name):
        return self.__db.get(name)

    def expire(self, t):
        return self.__db.expire(self.key, t)

    def keys(self, pattern):
        return self.__db.keys(pattern)

# r = RedisCache('hello')
# r.set('hellowprd')
# r.expire(10)
# import time
# print(r.get('hello'))
# time.sleep(12)
# print(r.get('hello'))

# print(r.hget('name'))

# print(r.hdel('name'))

# r.delete()
