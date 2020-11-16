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
import random
import time
import oss2
import requests

from retrying import retry


@retry(stop_max_attempt_number=5)
def update_img(image_content, access_key_id='LTAI4G2xT21jFFiUeiaAAi5N',
               access_key_secret='owUjZqX0vLsvFi6hWoPjadXWiC6BeQ',
               endpoint='oss-cn-beijing.aliyuncs.com', bucket_name='apposs2020'):
    m = hashlib.md5()
    now_time = str(int(time.time() * 1000) + random.randint(10000, 9999999))
    m.update(now_time.encode())
    file_name = m.hexdigest()
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    g = bucket.put_object(f'{file_name}.png', image_content)
    return g.resp.response.url


@retry(stop_max_attempt_number=10)
def get_image(url):
    response = requests.get(url, timeout=(10, 10))
    return response.content
