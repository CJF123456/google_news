#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-09-09 9:55
# @Author  : cjf
# @Version : 1.0
# @File    : newsSpider.py
# @Software: PyCharm
# @Desc    : None
import sys

sys.path.append('..')
import json
import random
import re
import time
from bs4 import BeautifulSoup
from configs import useragents
from configs.headers import pc_headers
from filters.hashFilter import make_md5, hexists_md5_filter, hset_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import format_info_int_re, filter_emoji, format_content_p, \
    all_tag_replace_html_div_a, format_p_null
from utils.timeUtil import now_datetime, timestamp_to_str, now_datetime_no
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img
from utils.translate import cat_to_chs


# 多维网


class DwNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:dwnews'
        self.project_name = self.__class__.__name__
        self.site_name = "多维网"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.dwnews.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

    def parse(self):
        start_time = time.time()
        log.info(self.project_name + ' spider start... ')
        kws = get_spider_kw_mysql(self.site_name)
        if kws:
            for kw in kws:
                url = kw[0]
                column_first = kw[1]
                source_id = kw[4]
                kw_site = kw[3]
                url_code = str(format_info_int_re(url))
                url = "https://prod-site-api.dwnews.com/v2/feed/zone/" + url_code + "?offset=9999999999&language=zh-Hans&bucketId=00000"
                st, con = get_list_page_get(url, pc_headers, 'utf-8')
                if st:
                    json_data = json.loads(con)
                    items = json_data.get('items')
                    for item in items:
                        title = item.get('data')['title']
                        detail_url = item.get('data').get('canonicalUrl')
                        # 发布时间
                        publish_time = item.get('data').get('publishTime')
                        pub_time = timestamp_to_str(publish_time)
                        md5_ = detail_url
                        md5 = make_md5(md5_)
                        detail_url_code = str(format_info_int_re(detail_url))
                        if hexists_md5_filter(md5, self.mmd5):
                            pass
                            #log.info(self.project_name + " info data already exists!")
                        else:
                            main_category = item.get('data').get('mainCategory')
                            # 缩略图
                            caption, cdnUrl = self.get_caption_url(item)
                            if not "视觉" in detail_url:
                                if "https://www.dwnews.com/" in detail_url:
                                    self.get_detail(title, detail_url, main_category, pub_time,
                                                        caption, cdnUrl, md5, detail_url_code, source_id)
                            else:
                                pass
                #log.info(self.project_name + column_first + ' spider succ.')
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def get_caption_url(self, item):
        global caption, cdnUrl
        thumbnails = item.get('data').get('thumbnails')
        for thumbnail in thumbnails:
            caption = thumbnail['caption']
            cdnUrl = thumbnail['cdnUrl']
            if caption:
                caption = caption
                cdnUrl = cdnUrl
                break
        return caption, cdnUrl

    def get_detail(self, title, detail_url, main_category, pub_time, caption, cdnUrl,
                   md5, detail_url_code, source_id):
        global ImageId, img_
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            content_text = self.get_content_html(con)
            if not content_text:
                pass
            else:
                if caption and cdnUrl:
                    ii = get_image(cdnUrl)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + content_text
                    content_text = content_text.replace("<p><img", "<img")
                else:
                    content_text = content_text
                spider_time = now_datetime()
                body = content_text
                cn_title = title
                create_time = spider_time
                group_name = main_category
                title = title
                title = filter_emoji(title)
                update_time = spider_time
                website = detail_url
                Uri = detail_url
                Language = "zh"
                DocTime = pub_time
                CrawlTime = spider_time
                Hidden = 0  # 去确认
                file_name = ""
                file_path = ""
                classification = ""
                cn_boty = ""
                column_id = ''
                creator = ''
                if_top = ''
                source_id = source_id
                summary = ""
                summary = filter_emoji(summary)
                UriId = detail_url_code
                keyword = ''
                info_val = (
                    body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top,
                    keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                    CrawlTime,
                    Hidden, file_name, file_path)
                # 入库mssql
                data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                  self.project_name)

    # TODO 去掉strong
    def remove_strong(self, con_):
        if "<strong>" in con_:
            results = re.sub(r'<(strong)[^>]*>.*?</\1>|<.*? /> ', "", con_)
            content = results
            if "<p></p>" in content:
                content = content.replace("<p></p>", "").lstrip()
        else:
            content = con_
        return content

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<span>', '').replace(
                '</span>', '') \
                .strip().replace('\r', '').replace('\n', '').replace('+<!-->3+<!-->2', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>")
        if "「版權宣告" in format_info:
            format_info = format_info.split("「版權宣告")[0]
        elif "「版权声明：" in format_info:
            format_info = format_info.split("「版权声明：")[0]
        elif "推荐阅读" in format_info:
            format_info = format_info.split("推荐阅读")[0]
        return format_info

    def get_content_html(self, html):
        global content_text
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('article div.sc-bdVaJa.jLaXBp'):
            [s.extract() for s in divcon('figure')]
            #[s.extract() for s in divcon('strong')]
            [s.extract() for s in divcon.find_all("div", {"class": "s2jnsig-0 hZOstq sc-gqjmRU rgrzA"})]
            [s.extract() for s in divcon.find_all("div", {"class": "lvt1ex-0 cPcXSN sc-bdVaJa hVSRSV"})]
            [s.extract() for s in divcon.find_all("div", {"class": "sc-bwzfXH liBCIH sc-bdVaJa hjfdHC"})]
            [s.extract() for s in divcon.find_all("div", {"class": "sc-bdVaJa hVSRSV"})]
            #[s.extract() for s in divcon.find_all("strong", {"class": "s1wvug8s-0 bbEmvD"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = all_tag_replace_html_div_a(con)
            con_ = con.replace("\n", "").replace(" ", "").replace("div", "p")
            con_s = con_.split("</p><p>")
            con_texts = []
            for con_text in con_s:
                if con_text:
                    if "<a>" in con_text:
                        if len(con_text) > 13:
                            pass
                        else:
                            con_text.replace("<a>", "").replace("</a>", "").replace("<p>", "").replace("</p>", "")
                            con_texts.append(con_text)
                    else:
                        con_text.replace("<a>", "").replace("</a>", "").replace("<p>", "").replace("</p>", "")
                        con_texts.append(con_text)
            content_texts = []
            for con_ in con_texts:
                con_html_ = format_content_p(con_)
                content_texts.append(con_html_)
            content_text = "".join(cat_to_chs(content_texts))
            content_text = content_text.split("<p>推荐阅读")[0]
            content_text = content_text.replace("（点击图集浏览）", "").replace("相关阅读", "").replace("（点击浏览大图）", "").replace(
                "▼想了解更多关于以色列外交的资讯，请点击放大观看：", "").replace("↓想知道不同地方民众在疫情持续期间的生活，请点击放大观看：", "").replace("请点击放大观看：", "")
            if "「版权声明" in content_text:
                content_text=content_text.split("<p>「版权声明")[0]
            content_text = format_p_null(content_text)
        return content_text

    def cn_replace_html(self, con):
        con = con.spilt("推荐阅读")[0]
        return con


if __name__ == '__main__':
    news = DwNewsSpider()
    news.parse()
