# coding=utf-8
# !/usr/bin/env python
# -------------------------------------------------------------------------------
# Name: pymssqlTest.py
# Purpose: 测试 pymssql库，该库到这里下载：http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql
#
# Author: scott
#
# Created: 04/02/2012
# -------------------------------------------------------------------------------

import pymssql

from configs.dbconfig import sqlServerConfig


class MSSQL(object):
    """
    对pymssql的简单封装
    pymssql库，该库到这里下载：http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql
    使用该库时，需要在Sql Server Configuration Manager里面将TCP/IP协议开启

    用法：

    """

    __pool = None

    def __init__(self):
        """
        数据库构造函数，从连接池中取出连接，并生成操作游标
        """

        self._conn = MSSQL.__get_conn()

    @staticmethod
    def __get_conn():
        # def __GetConnect(self):
        # def __GetConnect(self):
        """
        得到连接信息
        返回: conn.cursor()
        """
        global __pool, cur
        if MSSQL.__pool is None:
            __pool = pymssql.connect(host=sqlServerConfig.DBHOST, user=sqlServerConfig.DBUSER,
                                     password=sqlServerConfig.DBPWD, database=sqlServerConfig.DBNAME, charset="utf8",autocommit=True)
            cur = __pool.cursor()
        if not cur:
            raise (NameError, "连接数据库失败")
        else:
            return cur

    def get_all(self, sql):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        try:
            self._conn.execute(sql)
            result = self._conn.fetchall()
            return result
        except Exception as e:
            print(e)

    def update(self, sql, param=None):
        if param is None:
            self._conn.execute(sql)
        else:
            self._conn.execute(sql, param)
