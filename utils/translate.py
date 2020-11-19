#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 9:28
# @Author  : chenjianfeng
# @Site    :
# @File    : common.py
# @Software: PyCharm

import sys

sys.path.append('..')
import json
from googletrans import Translator
from mylog.mlog import log
from utils.langconv import Converter
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models


# id 印尼 en 英文
def translated_cn_google(text, cn_info):
    global translated
    num = 0
    while True:
        try:
            translator = Translator(service_urls=['translate.google.cn'])
            translated = translator.translate(text, src=cn_info, dest='zh-cn').text.lstrip().strip()
        except Exception as e:
            # log.info(e)
            # log.info(text)
            translated = ""
        if translated:
            break
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            # log.info(text)
            break
    return translated


def en_con_to_cn_con_google(info, cn_info):
    global cn_content
    p_cons = info.split("</p><p>")
    cn_list = []
    for p_con in p_cons:
        p_con = u"" + p_con.replace("<p>", "").replace("</p>", "")
        if p_con:
            cn_con = translated_cn_google(p_con, cn_info)
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


def translated_cn(tran_str,cn_info):
    num = 0
    while True:
        try:
            cred = credential.Credential("AKIDg9dgTzJcvz70dChfVJuFK9k7F7xZh0g7", "LQE1ZqrN6ZmiOXS7Vh5C2Viju9BNI2FH")
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-hongkong", clientProfile)
            req = models.TextTranslateBatchRequest()
            tran_list = []
            tran_list.append(tran_str)
            params = {
                "SourceTextList": tran_list,
                "Source": "auto",
                "Target": "zh",
                "ProjectId": 0
            }
            req.from_json_string(json.dumps(params))
            resp = client.TextTranslateBatch(req)
            str_info = resp.to_json_string()
            dict_info = json.loads(str_info)
            translated = dict_info['TargetTextList'][0]
        except TencentCloudSDKException as err:
            print(err)
            translated = ""
        if translated:
            break
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            break
    return translated


def en_con_to_cn_con(tran_str,cn_info):
    global cn_content
    tran_str_ = tran_str.replace("</p><p>", "\n\n\n").replace("<p>", "").replace("</p>", "")
    spilt_num = len(tran_str_) // 1999
    start_num = 0
    no_cn_contents = []
    for i in range(1, spilt_num + 2):
        end_num = i * 1999
        tran_s = tran_str_[start_num:end_num]
        start_num = end_num
        no_cn_contents.append(tran_s)
    cn_contents = []
    for no_cn_content in no_cn_contents:
        cn_contents.append(translated_cn(no_cn_content))
    cn_content = "".join(cn_contents).replace("\n\n\n", "</p><p>")
    if cn_content.startswith("<p>"):
        cn_content = cn_content
    else:
        cn_content = "<p>" + cn_content
    if cn_content.endswith("</p>"):
        cn_content = cn_content
    else:
        cn_content = cn_content + "</p>"
    cn_content = cn_content.replace("\n", "")
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
