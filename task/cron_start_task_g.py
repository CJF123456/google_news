#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys
sys.path.append('..')

from mylog.mlog import log
from utils.timeUtil import now_datetime
#from task.g_appledailyNewsSpider import g_AppledailyNewsSpider
#from task.g_beijingNewsSpider import g_BeijingNewsSpider
#from task.g_bj_peopleNewsSpider import g_Bj_peopleNewsSpider
from task.g_chinaaidNewsSpider import g_ChinaaidNewsSpider
from task.g_chinatimeNewsSpider import g_ChinatimeNewsSpider
#from task.g_cpcNewsSpider import g_CpcNewsSpider
from task.g_idemocracyNewsSpider import g_IdemocracyNewsSpider
# from task.g_rfaNewsSpider import g_RfaNewsSpider
# from task.g_udnbkkNewsSpider import g_UdnbkkNewsSpider
from task.g_ynaNewsSpider import g_YnaNewsSpider
from task.g_efeNewsSpider import g_EfeNewsSpider
from task.g_manilatimesNewsSpider import g_ManilatimesNewsSpider
from task.g_philstarNewsSpider import g_PhilstarNewsSpider
'''
    定时
'''


def parse_g():
    log.info("guoSpider cate info start" + now_datetime())
    # 苹果即时 完结  10379
    # g_AppledailyNewsSpider().parse()
    # 人民网-北京  完结 10365 10366
    #g_Bj_peopleNewsSpider().parse()
    # 对华援助新闻网  完结 10351
    g_ChinaaidNewsSpider().parse()
    # 中时电子报  完结
    g_ChinatimeNewsSpider().parse()
    # 中国共产党网  完结  10372
    #g_CpcNewsSpider().parse()
    # 华人民主书院   完结  10353
    g_IdemocracyNewsSpider().parse()
    # 自由亚洲电台  完结  10352
    # g_RfaNewsSpider().parse()
    # 世界日报--泰国  完结  10374
    # g_UdnbkkNewsSpider().parse()
    # 韩联社  完结  10362
    g_YnaNewsSpider().parse()
    # 首都之窗 本地跑不了
    # g_BeijingNewsSpider().parse()
    #西班牙埃菲社（EFE） 完结
    g_EfeNewsSpider().parse()
    # 马尼拉时报  完结
    g_ManilatimesNewsSpider().parse()
    # 菲律宾星报 完结
    g_PhilstarNewsSpider().parse()
    log.info("guoSpider cate info end" + now_datetime())

if __name__ == '__main__':
    parse_g()
