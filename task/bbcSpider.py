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
import random
import re
import time
from utils.ossUtil import get_image, update_img
from bs4 import BeautifulSoup
from lxml import etree
from mylog.mlog import log
from configs import useragents
from configs.dbconfig import NewsTaskSql
from filters.hashFilter import make_md5, hexists_md5_filter
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import filter_html_clear_format, format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, now_time


# bbc中文网 en

class BbcSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:bbc'
        self.project_name = self.__class__.__name__
        self.web_name = "BBC中文网"
        self.first_url = "https://www.bbc.com"

    def parse(self):
        log.info(self.project_name + ' spider start... ')
        start_time = time.time()
        kws = get_spider_kw_mysql(self.web_name)
        if kws:
            for kw in kws:
                list_url = kw[0]
                pc_headers = {
                    'User-Agent': random.choice(useragents.pc_agents),
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'referer': list_url
                }
                column_second = kw[2]
                kw_site = kw[3]
                column_first = kw[1]
                source_id = kw[4]
                self.parse_info(column_first, column_second, kw_site, list_url, pc_headers, source_id)
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div[@id="lx-stream"]//ol/li')
            for el in els:
                try:
                    url_code = el.xpath(".//div/h3/a/@href")
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath(".//div/h3/a/span/text()")
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = self.first_url + url_code
                    md5_ = title + kw_site
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        url_code = detail_url.replace("https://www.bbc.com/zhongwen/simp/", "").split("-")[0]
                        url_limit_code = ["business", "world", "chinese"]
                        if url_code in url_limit_code:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, source_id)
                        else:
                            pass
                else:
                    pass

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        pub_time = self.get_pub_time(con)
        # pub_date_time = now_datetime_no()
        # if pub_time < pub_date_time:
        #     log.info("数据不是最新" + pub_time)
        # else:
        if st:
            html = etree.HTML(con)
            try:
                img_url = html.xpath('//figure[1]//img[1]/@src')[0]
                img_url = "".join(img_url)
            except Exception as e:
                print(e)
                img_url = ""
            try:
                img_text = html.xpath('//main/div[3]/figure//p/text()')
                img_text = "".join(img_text)
            except Exception as e:
                print(e)
                img_text = ""
            caption = img_text
            contents_html = self.get_content_html(con)
            if not contents_html:
                pass
            else:
                if img_url:
                    ii = get_image(img_url)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + contents_html
                    content_text = content_text.replace("<p><img", "<img")
                else:
                    content_text = contents_html
            if "html" in content_text:
                print("获取内容失败")
            else:
                spider_time = now_datetime()
                content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>",
                                                                                                         "").replace(
                    "<p>.</p>", "")
                body = content_text
                if "<!DOCTYPE html>" in content_text:
                    pass
                else:
                    cn_title = title
                    create_time = spider_time
                    group_name = column_first
                    title = title
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
                    creator = 0
                    if_top = 0
                    source_id = source_id
                    summary = ''
                    UriId = ''
                    keyword = ''
                    info_val = (
                        body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name,
                        if_top,
                        keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                        CrawlTime,
                        Hidden, file_name, file_path)
                    # 入库mssql
                    data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                      self.project_name)
        else:
            pass

    def get_pub_time(self, con):
        global pub_time
        try:
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", con)
            pub_time = mat.groups()[0] + " " + now_time()
            from utils.timeUtil import format_string_datetime
            pub_time = format_string_datetime(pub_time)
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    def get_content_html(self, html):
        global con, content_text
        try:
            soup = BeautifulSoup(html, 'lxml')
            for divcon in soup.select('main'):
                [s.extract() for s in divcon('script')]
                [s.extract() for s in divcon('style')]
                [s.extract() for s in divcon('iframe')]
                [s.extract() for s in divcon("svg")]
                [s.extract() for s in divcon("cite")]
                [s.extract() for s in divcon("h1")]
                [s.extract() for s in divcon("figure")]
                [s.extract() for s in divcon("time")]
                [s.extract() for s in divcon("time")]
                [s.extract() for s in divcon("section")]
                [s.extract() for s in divcon.find_all("div", {"class": "Wrapper-sc-19u4gna-0 iSPrWK"})]
                [s.extract() for s in divcon.find_all("ul", {"role": "list"})]
                [s.extract() for s in divcon.find_all("li", {"role": "listitem"})]
                [s.extract() for s in divcon.find_all("div", {"class": "Include-sc-1ugtlik-1 hOrCaV"})]
                [s.extract() for s in divcon.find_all("h2", {"id": "相关内容"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = filter_html_clear_format(con)
                con = con.replace(" ", "")
                con = self.cn_replace_html(con)
                content_text = format_content_p(con)
                content_text = all_tag_replace_html(content_text)
        except Exception as e:
            print(e)
            content_text = ""
        return content_text

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.replace("路透新闻部", "").replace("分钟阅读", "")
            format_info = format_info.replace("<p></p>", "").replace("<p>1 </p>", "").replace("<p>2 </p>", "").replace(
                "<p>3 </p>", "").replace("<p>4 </p>", "").replace("====", "").replace("\n\n", "\n").replace(
                "/ Touch Of Light", "").replace("©", "").replace("li", "p").replace("h2", "p").replace("strong",
                                                                                                       "p").replace(
                "点击以下链接阅读全文：", "")
        return format_info


if __name__ == '__main__':
    news = BbcSpider()
    news.parse()
