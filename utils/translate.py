#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 9:28
# @Author  : chenjianfeng
# @Site    :
# @File    : common.py
# @Software: PyCharm
import sys
sys.path.append('..')
from googletrans import Translator
from mylog.mlog import log
from utils.langconv import Converter


# id 印尼 en 英文
def translated_cn(text, cn_info):
    global translated
    num = 0
    while True:
        try:
            translator = Translator(service_urls=['translate.google.cn'])
            translated = translator.translate(text, src=cn_info, dest='zh-cn').text.lstrip().strip()
        except Exception as e:
            #log.info(e)
            #log.info(text)
            translated = ""
        if translated:
            break
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            #log.info(text)
            break
    return translated


def en_con_to_cn_con(info, cn_info):
    global cn_content
    p_cons = info.split("</p><p>")
    cn_list = []
    for p_con in p_cons:
        p_con = u"" + p_con.replace("<p>", "").replace("</p>", "")
        if p_con:
            cn_con = translated_cn(p_con, cn_info)
            if cn_con:
                cn_list.append(cn_con)
            else:
                cn_content = ""
                break
    cn_content = "</p><p>".join(cn_list)
    if cn_content.startswith("<p>"):
        cn_content = cn_content
    else:
        cn_content = "<p>" + cn_content
    if cn_content.endswith("</p>"):
        cn_content = cn_content
    else:
        cn_content = cn_content + "</p>"
    return cn_content


def cat_to_chs(sentence):  # 传入参数为列表
    """
    将繁体转换成简体
    :param line:
    :return:
    """
    sentence = ",".join(sentence)
    sentence = Converter('zh-hans').convert(sentence)
    sentence.encode('utf-8')
    return sentence.split(",")
