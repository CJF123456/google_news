#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:13
# @Author  : cjf
# @Site    : 
# @File    : start.py.py
# @Software: PyCharm
import sys

sys.path.append('..')
from task.cnReutersSpider import CnReutersSpider
from task.dwNewsSpider import DwNewsSpider
from task.sputnikNewsSpider import SputnikNewsSpider
from task.voachineseSpider import VoachineseSpider
from task.bbcSpider import BbcSpider
from task.cnNytimesSpider import CnNytimesSpider
from task.dwzhSpider import DwzhSpider
from task.kyodonewsSpider import KyodonewsSpider
from task.ltnSpider import LtnSpider
from task.udnSpider import UdnSpider
from task.kompasSpider import KompasSpider
from task.thejakartaSpider import ThejakartaSpider
from task.nedSpider import NedSpider
from task.smhSpider import SmhSpider
from task.inquirerSpider import InquirerSpider
from task.republikaSpider import RepublikaSpider
from task.antaranewsSpider import AntaranewsSpider
import time
from mylog.mlog import log
from utils.timeUtil import now_datetime
from task.aljazeeraSpider import AljazeeraSpider

'''
    定时
'''


def parse_it():
    pass
    # anse
    # AnsaSpider().parse()


def parse_id():
    # 安塔拉
    AntaranewsSpider().parse()
    # 印尼罗盘网 完结
    KompasSpider().parse()
    # 印尼共和报 完结
    RepublikaSpider().parse()


def parse_cn():
    # bbc中文网 完结
    BbcSpider().parse()
    # 德国之声 完结
    DwzhSpider().parse()
    # 路透中文网 完结
    CnReutersSpider().parse()
    # 俄罗斯卫星通讯社 完结
    SputnikNewsSpider().parse()
    # 多维网 完结
    DwNewsSpider().parse()
    # 美国之音 完结
    VoachineseSpider().parse()
    # 纽约中文网 完结
    CnNytimesSpider().parse()
    # 共同网 完结
    KyodonewsSpider().parse()
    # 联合新闻 完结
    UdnSpider().parse()
    # 自由时报电子报 完结
    LtnSpider().parse()


def pasrse_en():
    # 半岛电视台 完结
    AljazeeraSpider().parse()
    # 雅加达邮报 完结
    ThejakartaSpider().parse()
    # 美国国家民主基金会 完结
    NedSpider().parse()
    # 澳大利亚悉尼先驱晨报 完结
    SmhSpider().parse()
    # 菲律宾每日询问报 完结
    InquirerSpider().parse()


def parse_c():
    # 中文
    start_time = time.time()
    log.info('parse_c spider start... ')
    parse_cn()
    pasrse_en()
    parse_id()
    end_time = time.time()
    log.info('parse_c spider succ.' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))


if __name__ == '__main__':
    parse_c()
