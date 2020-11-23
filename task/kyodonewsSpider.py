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

from bs4 import BeautifulSoup
from lxml import etree
from utils.ossUtil import get_image, update_img
from configs import useragents
from configs.dbconfig import NewsTaskSql
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import filter_html_clear_format, format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no


# 共同网
class KyodonewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:kyodonews'
        self.project_name = self.__class__.__name__
        self.web_name = "共同网"
        self.first_url = "https://china.kyodonews.net"

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
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                }
                column_second = kw[2]
                kw_site = kw[3]
                column_first = kw[1]
                source_id = kw[4]
                self.parse_info(column_first, column_second, kw_site, list_url, pc_headers, source_id)
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//ul[@id="js-postListItems"]/li')
            for el in els:
                try:
                    url_code = el.xpath('./a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./a/h3/text()')
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                pub_time = self.get_pub_time(el)
                pub_date_time = now_datetime_no()
                if pub_time < pub_date_time:
                    log.info("数据不是最新" + pub_time)
                else:
                    if url_code and title:
                        detail_url = self.first_url + url_code
                        md5_ = title+kw_site
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, pub_time, source_id)
                    else:
                        pass

    def get_pub_time(self, el):
        try:
            pub_time_el = el.xpath('./p[@class="time"]/text()')
            pub_el = "".join(pub_time_el)
            pub_date_ = pub_el.replace("|", "").split("-")[0].replace(" ", "").replace("\n", "")
            pub_date_ = pub_date_.replace("年", "-").replace("月", "-").replace("日", "")
            pub_time_ = pub_el.replace("|", "").replace(" ", "").replace("\n", "").split("-")[1] + ":00"
            pub_time = pub_date_.strip() + " " + pub_time_.strip()
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, pub_time, source_id):
        global con_
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        image_url = self.get_image_url(con)
        caption = ""
        if st:
            contents_html = self.get_content_html(con)
            if not contents_html:
                pass
            else:
                if image_url:
                    ii = get_image(image_url)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + contents_html

                else:
                    content_text = contents_html
                content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
                spider_time = now_datetime()
                body = content_text
                cn_title = title
                create_time = spider_time
                group_name = column_first
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
                cn_boty = ''
                column_id = ''
                creator = 0
                if_top = 0
                source_id = source_id
                summary = ''
                UriId = ''
                keyword = ''
                info_val = (
                    body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top,
                    keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                    CrawlTime,
                    Hidden, file_name, file_path)
                # 入库mssql
                data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                  self.project_name)

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.article-body'):
            [s.extract() for s in divcon('script', )]
            [s.extract() for s in divcon('iframe')]
            [s.extract() for s in divcon("svg")]
            [s.extract() for s in divcon("h4")]
            [s.extract() for s in divcon("h1")]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = filter_html_clear_format(con)
            con = con.replace(" ", "")
            con_html = self.cn_replace_html(con)
            con_html = format_content_p(con_html)
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = all_tag_replace_html(content_text)
        content_text = content_text.replace("&lt;", "").replace("&gt;", "")
        return content_text

    # TODO 图片url
    def get_image_url(self, con):
        html = etree.HTML(con)
        try:
            image_url = html.xpath('//div[@class="mainpic"]/img/@data-src')[0]
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


if __name__ == '__main__':
    news = KyodonewsSpider()
    news.parse()
