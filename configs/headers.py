#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 15:53
# @Author  : cjf
# @Site    : 随机配置User-Agent
# @File    : headers.py
# @Software: PyCharm
import sys
sys.path.append('..')
import random

from configs import useragents

mobile_headers = {
    'User-Agent': random.choice(useragents.mobile_agents),
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}


pc_headers = {
    'User-Agent': random.choice(useragents.pc_agents),
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

xcx_headers={
    'User-Agent': random.choice(useragents.xcx_agents),
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br',
}