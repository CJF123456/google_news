#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 16:50
# @Author  : cjf
# @Site    : 时间格式转化
# @File    : timeUtil.py
# @Software: PyCharm

import sys

sys.path.append('..')

import time
from datetime import datetime, timedelta

'''
    时间转化工具类
'''


def format_time(timestr, format1, format2):
    '''
      %d/%m/%Y %H:%M >> %Y年%m月%d日
      16/06/2017 07:54
      format_time('16/06/2017 07:54','%d/%m/%Y %H:%M','%Y年%m月%d日 %H:%M')
    :param format1: original time format
    :param format2: target time format
    :param timestr: original time string
    :return:
    '''
    return time.strftime(format2, time.strptime(timestr, format1))


def now_timestamp():
    '''
    获取当前时间戳 10位
    :return:
    '''
    return int(time.time())


def timestamp_to_13():
    '''
    获取13位时间戳
    :return:
    '''
    num_ = time.time()
    time_ = int(num_ * 1000)
    return time_


def now_time():
    '''
    获取当前时间
    :return: datetime
    '''
    return time.strftime("%H:%M:%S", time.localtime(time.time()))


def now_datetime():
    '''
    获取当前时间
    :return: datetime
    '''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def now_datetime_no():
    '''
    获取当前日期
    :return:
    '''
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


def now_hour_no():
    '''
    获取当前小时
    :return: datetime
    '''
    return time.strftime("%Y-%m-%d %H", time.localtime(time.time()))


def now_month_no():
    '''
    获取当前月份含年份
    :return:
    '''
    return time.strftime("%Y-%m", time.localtime(time.time()))


def now_month():
    '''
    获取当前月份
    :return:
    '''
    return time.strftime("%m", time.localtime(time.time()))


def now_quarter():
    '''
    获取当年季度
    :return:
    '''
    global quarter
    month = int(now_month())
    if month <= 3:
        quarter = "1"
    elif 3 < month <= 6:
        quarter = "2"
    elif 6 < month <= 9:
        quarter = "3"
    elif 9 < month <= 12:
        quarter = "4"
    return quarter


def now_year_no():
    '''
    获取当前年份
    :return:
    '''
    return time.strftime("%Y", time.localtime(time.time()))


def timestamp_to_str(ctime):
    '''
    timestamp 转datetime
    :param ctime:
    :return:
    '''
    tmp_time = time.localtime(int(ctime))
    ctimeStr = time.strftime("%Y-%m-%d %H:%M:%S", tmp_time)
    return ctimeStr


def timestamp_to_date(ctime):
    '''
    timestamp 转datetime
    :param ctime:
    :return:
    '''
    tmp_time = time.localtime(int(ctime))
    ctimeStr = time.strftime("%Y-%m-%d", tmp_time)
    return ctimeStr


def get_now_strptime_8():
    '''
    当天8的时间戳
    :return:
    '''
    global timeStamp
    now_date = now_datetime_no()
    now_datetime = str(now_date) + " 08:00:00"
    timeArray = time.strptime(now_datetime, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray)) * 1000
    return timeStamp


def get_nextday_strptime_8():
    '''
    明天8的时间戳
    :return:
    '''
    global timeStamp
    now_date = get_datetime_nextday()
    now_datetime = str(now_date) + " 08:00:00"
    timeArray = time.strptime(now_datetime, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray)) * 1000
    return timeStamp


def timestr_to_timestamp(s):
    '''
    时间转化 str 转timestamp
    :param s:
    :return:
    '''
    return int(time.mktime(time.strptime(s, '%Y-%m-%d %H:%M:%S')))


def format_string_datetime(string):
    '''
    获取当天时间 datetime
    :param string:
    :return:
    '''
    return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


import datetime as dt


def str_format_datetime(format_info):
    '''
    str 格式化成datetime
    :param format_info:
    :return:
    '''
    global date_time
    info_size = format_info.lstrip().strip().__len__()
    if "-" in format_info and ":" in format_info and info_size == 19:
        date_time = dt.datetime.strptime(format_info, '%Y-%m-%d %H:%M:%S')
    elif "-" in format_info and ":" in format_info and info_size == 16:
        format_info = format_info + ":00"
        date_time = dt.datetime.strptime(format_info, '%Y-%m-%d %H:%M:%S')
    elif "-" in format_info and info_size == 13:
        format_info = format_info + ":00:00"
        date_time = dt.datetime.strptime(format_info, '%Y-%m-%d %H:%M:%S')
    elif "-" in format_info and info_size == 12:
        format_info = format_info + ":00:00"
        date_time = dt.datetime.strptime(format_info, '%Y-%m-%d %H:%M:%S')
    elif "-" in format_info and info_size == 10:
        format_info = format_info + " 00:00:00"
        date_time = dt.datetime.strptime(format_info, '%Y-%m-%d %H:%M:%S')
    else:
        pass
    return date_time


def caltime_datetime(date1, date2):
    '''
    计算两个日期相差天数，自定义函数名，和两个日期的变量名。
    :param date1:
    :param date2:
    :return:
    '''
    # %Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
    # date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    # date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = time.strptime(date1, "%Y-%m-%d")
    date2 = time.strptime(date2, "%Y-%m-%d")
    # 根据上面需要计算日期还是日期时间，来确定需要几个数组段。下标0表示年，小标1表示月，依次类推...
    # date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    # date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    date1 = dt.datetime(date1[0], date1[1], date1[2])
    date2 = dt.datetime(date2[0], date2[1], date2[2])
    # 返回两个变量相差的值，就是相差天数
    delta = date2 - date1
    interval = delta.days
    return interval


def datetime_timestamp_long(format_info):
    '''
    str 转化成时间戳
    :param format_info:
    :return:
    '''
    dtime = format_string_datetime(format_info)
    un_time = int(time.mktime(dtime.timetuple())) * 1000
    return un_time


def get_datetime_today():
    '''
    获取当天日期
    :return:
    '''
    t = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    dt = datetime.strptime(str(t), '%Y-%m-%d')  # date转str再转datetime
    return dt


def get_datetime_yesterday():
    '''
    获取前一天日期
    :return:
    '''
    today = get_datetime_today()  # datetime类型当前日期
    yesterday = today + timedelta(days=-1)  # 减去一天
    yesterday = str(yesterday).replace("00:00:00", "").strip()
    return yesterday


def get_datetime_nextday():
    '''
    获取明天日期
    :return:
    '''
    today = get_datetime_today()  # datetime类型当前日期
    nextday = today + timedelta(days=+1)  # 加一天
    nextday = str(nextday).replace("00:00:00", "").strip()
    return nextday


def get_datetime_appoint(num):
    '''
    获取未来几天日期
    :param num: 第几天
    :return:
    '''
    today = get_datetime_today()  # datetime类型当前日期
    nextday = today + timedelta(days=-int(num))  # 加一天
    nextday = str(nextday).replace("00:00:00", "").strip()
    return nextday


def get_datetime_nextday_30():
    '''
    获取20天后的日期
    :return:
    '''
    today = get_datetime_today()  # datetime类型当前日期
    nextday = today + timedelta(days=+20)  # 加一天
    nextday = str(nextday).replace("00:00:00", "").strip()
    return nextday


def format_datetime_utc(format_info):
    if len(format_info) == 24:
        UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    else:
        UTC_FORMAT = "%Y-%m-%dT%H:%M:%fZ"
    import datetime
    utc_time = datetime.datetime.strptime(format_info, UTC_FORMAT)
    local_time = utc_time + datetime.timedelta(hours=8)
    dc_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
    return dc_time


