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
from filters.hashFilter import make_md5, hexists_md5_filter, hset_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import format_info_list_str, filter_html_clear_format, format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, format_string_datetime, now_datetime_no


# 俄罗斯卫星通讯社 已完结
class SputnikNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:sputniknews'
        self.project_name = self.__class__.__name__
        self.web_name = "俄罗斯卫星通讯社"
        self.first_url = "http://sputniknews.cn"

    def parse(self):
        start_time = time.time()
        log.info(self.project_name + ' spider start... ')
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
                log.info(self.project_name + column_first + ' spider succ...')
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div/ul[@class="b-stories__list"]/li|//div[@class="b-main-news__first-content"]/div[last()-1]')
            for el in els:
                try:
                    url_code = el.xpath('.//div[@class="b-stories__title"]/h2/a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('.//div[@class="b-stories__title"]/h2/a/text()')
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = self.first_url + url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        pass
                       # log.info(self.project_name + " info data already exists!")
                    else:
                        url_code = detail_url.replace("http://sputniknews.cn/", "").split("/")[0]
                        url_limit_code = ["society", "politics", "military", "economics", "russia_china_relations",
                                          "covid-2019", "china", "russia"]
                        if url_code in url_limit_code:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, source_id)
                        else:
                            pass
                else:
                    pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.replace("路透新闻部", "").replace("分钟阅读", "")
            format_info = format_info.replace("<p></p>", "").replace("<p>1 </p>", "").replace("<p>2 </p>", "").replace(
                "<p>3 </p>", "").replace("<p>4 </p>", "").replace("====", "").replace("\n\n", "\n").replace(
                "/ Touch Of Light", "").replace("©", "").replace("<br/>", "</p><p>").replace("blockquote", "p").replace(
                "<p></p>", "")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global pub_time
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        image_url = self.get_image_url(con)
        content = self.get_content_html(con)
        if st:
            html = etree.HTML(con)
            pub_time = self.get_pub_time(html)
            pub_date_time = now_datetime_no()
            # if pub_time < pub_date_time:
            #     log.info("数据不是最新" + pub_time)
            #     hset_md5_filter(md5, self.mmd5)
            # else:
            if not content:
                pass
            else:
                if image_url:
                    caption = ""
                    ii = get_image(image_url)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + content.lstrip().strip()
                    content_text = content_text.replace("<p><img", "<img")
                else:
                    content_text = content
                content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
                spider_time = now_datetime()
                # 采集时间
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
        else:
            pass

    def get_pub_time(self, html):
        global pub_time
        try:
            pub_time_el = html.xpath('//div[@class="b-article__refs-credits"]/time[1]/@datetime')
            pub_time_ = format_info_list_str(pub_time_el)
            date_ = pub_time_.split("T")[0]
            time_ = pub_time_.split("T")[1]
            pub_time = date_ + " " + time_ + ":00"
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.b-article__lead'):
            [s.extract() for s in divcon('script', )]
            [s.extract() for s in divcon('iframe')]
            [s.extract() for s in divcon("svg")]
            [s.extract() for s in divcon("cite")]
            [s.extract() for s in divcon.find_all("div", {"class": "b-article__header-copy"})]
            [s.extract() for s in divcon.find_all("div", {"class": "b-inject__copy"})]
            [s.extract() for s in divcon.find_all("div", {"class": "b-inject m-inject-min"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = filter_html_clear_format(con)
            con = con.replace(" ", "")
            con = self.cn_replace_html(con)
            con = format_content_p(con)
            con_htmls.append(con)
        for divcon in soup.select('div.b-article__text'):
            [s.extract() for s in divcon('script', )]
            [s.extract() for s in divcon('iframe')]
            [s.extract() for s in divcon("svg")]
            [s.extract() for s in divcon("cite")]
            [s.extract() for s in divcon.find_all("div", {"class": "b-article__header-copy"})]
            [s.extract() for s in divcon.find_all("div", {"class": "b-inject__copy"})]
            [s.extract() for s in divcon.find_all("div", {"class": "b-inject m-inject-min"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = filter_html_clear_format(con)
            con = con.replace("  ", "")
            con = self.cn_replace_html(con)
            con = format_content_p(con)
            con_htmls.append(con)
        content_html = "".join(con_htmls)
        content_text = all_tag_replace_html(content_html)
        return content_text

    # TODO 图片url
    def get_image_url(self, con):
        html = etree.HTML(con)
        try:
            image_url = html.xpath(
                '//div[@class="b-article__header"]/img/@src')[0]
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


if __name__ == '__main__':
    news = SputnikNewsSpider()
    news.parse()
