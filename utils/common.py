#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 9:28
# @Author  : chenjianfeng
# @Site    : 
# @File    : common.py
# @Software: PyCharm
import sys

sys.path.append('..')
import io
from urllib.parse import urlparse

import requests

from configs.dbconfig import NewsTaskSql
from dbutils.sqlServerPool import MSSQL
from filters.hashFilter import hset_md5_filter
from mylog.mlog import log
from utils.datautil import sleep_long, sleep_short
from utils.timeUtil import now_datetime


def domain(url):
    '''
    获取域名
    :param url:
    :return:
    '''
    res = urlparse(url)
    return res.netloc


def download_html(url, headers=None):
    '''
    requests get请求
    :param url:
    :param headers:
    :return:
    '''
    st = 0
    try:
        r = requests.get(url, headers=headers, allow_redirects=False, timeout=(5, 60))
        if r.status_code == 200:
            st = 1
            content = r.text
        else:
            content = ''
    except Exception as e:
        content = ''
        # log.error(e, 'download html error，url:%s' % (url))
        sleep_short()
    return st, content


def get_list_page_utf(url, headers):
    '''

    :param url:
    :param headers:
    :return:
    '''
    global content
    retry = 0
    st = 0  # st  1:fail 1:success
    while not st and (retry < 5):
        st, content = download_html_utf(url, headers=headers)
        sleep_short()
    return st, content


def download_html_utf(url, headers=None):
    '''

    :param url:
    :param headers:
    :param proxies:
    :return:
    '''
    st = 0
    try:
        r = requests.get(url, headers=headers, allow_redirects=False, timeout=(5, 60))
        if r.status_code == 200:
            st = 1
            content = r.content
            content = str(content, 'utf-8')
        else:
            content = ''
    except Exception as e:
        content = ''
        log.error(e, 'download html error,because of proxy,url:%s' % (url))
    return st, content


def download_html_get_content(url, headers, charset=None):
    '''
    :name: get 请求
    :param url:
    :param headers:
    :param data:
    :return:
    '''
    global content
    st = 0
    try:
        r = requests.get(url, headers=headers, allow_redirects=False,
                         timeout=(5, 10))
        if "utf-8" in charset and r.status_code == 200:
            st = 1
            content = r.content.decode(charset)
        else:
            if r.status_code == 200:
                st = 1
                if charset:
                    content = r.content.decode(charset)
                else:
                    content = r.content
            else:
                content = ''
    except Exception as e:
        content = ''
        log.error(e, 'requests error.')
        log.error(url)
        sleep_long()

    return st, content


def download_html_get(url, headers, charset=None):
    '''
    :name: get 请求
    :param url:
    :param headers:
    :param data:
    :return:
    '''
    st = 0
    try:
        r = requests.get(url, headers=headers, allow_redirects=False,
                         timeout=(5, 10))
        if "utf-8" in charset:
            if r.status_code == 200:
                st = 1
                if charset:
                    text = r.text
                else:
                    r.encoding = 'utf-8'
                    text = r.text
            else:
                text = ''
        else:
            if r.status_code == 200:
                st = 1
                if charset:
                    text = r.content.decode(charset)
                else:
                    text = r.content
            else:
                text = ''
    except Exception as e:
        text = ''
        log.info('requests error.')
        log.info(url)
    return st, text


def get_list_page_get_content(url, headers, charset=None):
    '''
    请求
    :param url:
    :param headers:
    :return:
    '''
    global content
    retry = 0
    st = 0  # st  1:fail 1:success
    while not st and (retry < 3):
        st, content = download_html_get_content(url, headers=headers, charset=charset)
        if st == 0:
            sleep_short()
            retry = retry + 1
        else:
            pass
    return st, content


def get_list_page_get(url, headers, charset=None):
    '''
    请求
    :param url:
    :param headers:
    :return:
    '''
    global content
    retry = 0
    st = 0  # st  1:fail 1:success
    while not st and (retry < 3):
        st, content = download_html_get(url, headers=headers, charset=charset)
        if st == 0:
            sleep_short()
            retry = retry + 1
        else:
            pass
    return st, content


def get_download_html_proxies(url, headers=None, proxies=None):
    '''
    get请求携带代理IP
    :param url:
    :param headers:
    :param proxies:
    :return:
    '''
    st = 0
    try:
        r = requests.get(url, headers=headers, proxies=proxies, allow_redirects=False,
                         timeout=(5, 10), verify=False)
        if r.status_code == 200:
            st = 1
            content = r.text
        else:
            content = ''
    except Exception as e:
        content = ''
        # log.error(e, 'download html error,because of proxy,url:%s' % (url))
        print(url)
    return st, content


def post_download_html_proxies(url, headers=None, proxies=None, data=None):
    '''
    post 请求 带代理ip
    :param url:
    :param headers:
    :param proxies:
    :return:
    '''
    st = 0
    try:
        r = requests.post(url, data=data, headers=headers, proxies=proxies, allow_redirects=False,
                          timeout=(5, 10), verify=False)
        if r.status_code == 200:
            st = 1
            content = r.text
        else:
            content = ''
    except Exception as e:
        log.info(e)
        content = ''
    return st, content


def post_list_page_no_proxies(url, headers, data=None):
    '''
    请求
    :param url:
    :param headers:
    :return:
    '''
    global content
    retry = 0
    st = 0  # st  1:fail 1:success
    while not st and (retry < 3):
        st, content = post_download_html_post(url, headers=headers, data=data)
        if st == 0:
            sleep_short()
            retry = retry + 1
            log.info("youdao requests erro")
        else:
            pass
    return st, content


def post_download_html_no_proxies(url, headers=None, proxies=None, data=None):
    '''
    post 请求 带代理ip
    :param url:
    :param headers:
    :param proxies:
    :return:
    '''
    st = 0
    try:
        r = requests.post(url, data=data, headers=headers, proxies=proxies, allow_redirects=False,
                          timeout=(5, 10), verify=False)
        if r.status_code == 200:
            st = 1
            content = r.text
        else:
            content = ''
    except Exception as e:
        log.info(e)
        content = ''
    return st, content


def post_download_html_post(url, headers=None, data=None):
    '''
    post 请求
    :param url:
    :param headers:
    :param proxies:
    :return:
    '''
    st = 0
    try:
        r = requests.post(url, data=data, headers=headers, allow_redirects=False,
                          timeout=(5, 10))
        if r.status_code == 200:
            st = 1
            content = r.text
        else:
            content = ''
    except Exception as e:
        log.info(e)
        content = ''
    return st, content


def data_insert_mssql(info_val, sql, md5, mmd5, project_name):
    '''
    入库mysql
    :param info_val:
    :param sql:
    :param md5:
    :param mmd5:
    :param project_name:
    :return:
    '''
    if md5 == "":
        try:
            mysql = MSSQL()
            mysql.update(sql, info_val)
            hset_md5_filter(md5, mmd5)
        except Exception as e:
            erro_text = e.__str__()
            if "Violation of UNIQUE KEY" in erro_text:
                hset_md5_filter(md5, mmd5)
            else:
                txt = ' data insert fail ,please check project'
                mail_title = project_name + txt
                mail_body = mail_title + " Please check it. weather no Included."
                log.error(mail_title)
            # send_mail_to(mail_title, mail_body
    else:
        try:
            mysql = MSSQL()
            mysql.update(sql, info_val)
            hset_md5_filter(md5, mmd5)
        except Exception as e:
            erro_text = e.__str__()
            if "Violation of UNIQUE KEY" in erro_text:
                hset_md5_filter(md5, mmd5)
            else:
                txt = ' data insert fail ,please check project'
                mail_title = project_name + txt
                mail_body = mail_title + " Please check it. weather no Included."
                log.error(mail_title)
            # send_mail_to(mail_title, mail_body


def get_spider_kw_mysql(sql):
    '''
    获取采集关键词
    :return:
    '''
    mysql = MSSQL()
    tx_infos = []
    mobile_tasks = mysql.get_all(
        "SELECT url,column_first,column_second,kw_site,source_id FROM t_spider_kw WHERE on_line=3 and kw_site=N'" + sql + "\'")
    if mobile_tasks:
        for t in mobile_tasks:
            tx_info = []
            url = t[0]
            column_first = t[1]
            column_second = t[2]
            kw_site = t[3]
            source_id = t[4]
            tx_info.append(url)
            tx_info.append(column_first)
            tx_info.append(column_second)
            tx_info.append(kw_site)
            tx_info.append(source_id)
            tx_infos.append(tx_info)
    return tx_infos


# TODO 保存图片到数据库
def save_image(caption, url, ImageId, pc_headers):
    FileStream = download_image(url, pc_headers)
    Caption = caption
    Uri = url
    CrawlTime = now_datetime()
    InUse = 1
    info_val = (ImageId, Caption, Uri, FileStream, CrawlTime, InUse)
    try:
        mysql = MSSQL()
        mysql.update(NewsTaskSql.image_insert, info_val)
    except Exception as e:
        print(e)


# TODO 保存图片
def download_image(url, pc_headers):
    global image_b
    try:
        r = requests.get(url, headers=pc_headers, allow_redirects=False,
                         timeout=(5, 10))
        if r.status_code == 200:
            image_b = io.BytesIO(r.content).read()
    except Exception as e:
        log.info(e)
    return image_b
