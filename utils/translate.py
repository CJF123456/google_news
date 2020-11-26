#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 9:28
# @Author  : chenjianfeng
# @Site    :
# @File    : common.py
# @Software: PyCharm

import sys



sys.path.append('..')
import textwrap
from googletrans import Translator
from mylog.mlog import log
from utils.langconv import Converter
from utils.tran_google import translate_zh

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


def translated_cn(context, cn_info):
    translated = translate_zh(context,cn_info)
    return translated

def en_con_to_cn_con(tran_str, cn_info):
    global cn_content
    tran_str_ = tran_str.replace("</p><p>", "\n\n\n").replace("<p>", "").replace("</p>", "")
    no_cn_contents = []
    cn_contents = []
    if len(tran_str_) < 4999:
        no_cn_contents.append(tran_str_)
    else:
        no_cn_contents = textwrap.wrap(tran_str, 4999)
    for no_cn_content in no_cn_contents:
        cn_con=translated_cn(no_cn_content, cn_info)
        if "重播重播视频" in cn_con:
            pass
        else:
            cn_contents.append(cn_con)
    cn_content = "".join(cn_contents).replace("\n\n\n", "</p><p>").replace("\n", "").strip().lstrip()
    if cn_content.startswith("<p>"):
        cn_content = cn_content.strip().lstrip()
    else:
        cn_content = "<p>" + cn_content.strip().lstrip()
    if cn_content.endswith("</p>"):
        cn_content = cn_content.strip().lstrip()
    else:
        cn_content = cn_content + "</p>"
    cn_content = cn_content.replace("\n", "").strip().lstrip()
    return cn_content


if __name__ == '__main__':
    contents_html='Centrodestra nel caos, in un giorno segnato dallo scontro frontale tra Lega e Forza Italia: Matteo Salvini accusa gli azzurri di fare \'inciuci\' con il nemico e di pensare ai "rimpasti", Silvio Berlusconi, in serata, cerca di gettare acqua sul fuoco, ma invano. Prima parla di "presunte divergenze con forze alleate", poi però picchia duro ricordando alla coalizione che senza il suo partito in Italia ci sarebbe'
    ss = en_con_to_cn_con(contents_html, 'it')
    print(ss)


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
