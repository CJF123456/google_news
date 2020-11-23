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
from configs import useragents
from filters.hashFilter import make_md5, hexists_md5_filter, hset_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import filter_html_clear_format, all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no
from utils.translate import cat_to_chs, en_con_to_cn_con, translated_cn
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img


# 印尼罗盘网
class KompasSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:kompas'
        self.project_name = self.__class__.__name__
        self.web_name = "印尼罗盘报"
        self.first_url = "https://www.kompas.com/"

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
                '//div[@class="trenLatest"]//div[@class="trenLatest__box"]')
            for el in els:
                try:
                    url_code = el.xpath('./h3/a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./h3/a/text()')
                    title = "".join(title).strip()

                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = url_code + "?page=all"
                    md5_ = title+kw_site
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        if detail_url and title:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, source_id)
                else:
                    pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "").replace("h2", "p")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, content_text, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            pub_time = self.get_pub_time(html)
            pub_date_time = now_datetime_no()
            if pub_time < pub_date_time:
                log.info("数据不是最新" + pub_time)
                hset_md5_filter(md5, self.mmd5)
            else:
                image_url = self.get_image_url(html)
                caption = self.get_caption(html)
                contents_html = self.get_content_html(con)
                cn_title = translated_cn(title, 'id')
                if not contents_html:
                    pass
                else:
                    if caption:
                        cn_caption = translated_cn(caption, 'id')
                    else:
                        cn_caption = ""
                    cn_content_ = en_con_to_cn_con(contents_html, 'id')
                    cn_content_ = cn_content_.replace("<p><p>", "<p>"). \
                        replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>",
                                                                                                           "").replace(
                        "<p>  </p>", "").replace("<p>   </p>", "").replace("</p></p>", "</p>")
                    if cn_content_:
                        if image_url:
                            ii = get_image(image_url)
                            r_i = update_img(ii)
                            img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                            content_text = img_ + contents_html
                            cn_img_ = '<img src="' + r_i + '"/><p>' + cn_caption + '</p>'
                            cn_content_text = cn_img_ + cn_content_
                        else:
                            content_text = contents_html
                            cn_content_text = cn_content_
                        content_text = content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>",
                                                                                                               "").replace(
                            "<p>  </p>", "").replace("<p>   </p>", "").replace("\n", "").strip()
                        cn_content_text = cn_content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>",
                                                                                                               "").replace(
                            "<p>  </p>", "").replace("<p>   </p>", "").replace("\n", "").strip()
                        spider_time = now_datetime()
                        body = content_text
                        cn_title = cn_title
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
                        cn_boty = cn_content_text
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

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.read__content'):
            [s.extract() for s in divcon("script")]
            [s.extract() for s in divcon("div")]
            [s.extract() for s in divcon("blockquote")]  # 外链
            [s.extract() for s in divcon.find_all("strong", {"class": "photo__caption"})]
            locu_content = divcon.prettify()
            con_ = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con_ = filter_html_clear_format(con_)
            con = con_.replace("  ", "")
            con_html = self.cn_replace_html(con)
            con_html = "".join(cat_to_chs(con_html))
            con_html = self.format_content_p(con_html)
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = all_tag_replace_html(content_text)
        if "&amp;" in content_text:
            content_text = content_text.replace("&amp;", "&")
        content_text = content_text.replace("<p><p>", "<p>"). \
            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>", "").replace(
            "<p>  </p>", "").replace("<p>   </p>", "").replace("</p></p>", "</p>")
        return content_text

    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="photo"]/img/@src')[0]
            image_url = "".join(image_url)

        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//div[@class="photo"]/img/@alt')[0]
            caption = "".join(caption)
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, html):
        try:
            pub_time_el = html.xpath('.//div[@class="read__time"]/text()')
            pub_el = "".join(pub_time_el)
            time_ = pub_el.split("-")[1]
            time_ = time_.split("/")
            day_ = time_[0].strip()
            month_ = time_[1].strip()
            year_ = time_[2].split(",")[0].strip()
            mis = pub_el.split(",")[1].replace("WIB", "").strip()
            pub_time = year_ + "-" + month_ + "-" + day_ + " " + mis + ":00"
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    def format_content_p(self, con_text):
        con_ = con_text.split("<p>")
        contents = []
        for con in con_:
            if con:
                if "<p>" in con:
                    con = con.replace("<p>", "").lstrip().strip()
                if "</p>" in con:
                    con = con.replace("</p>", "").lstrip().strip()
                if con.startswith("延伸阅读"):
                    pass
                else:
                    contents.append(con)
            else:
                pass
        contents_p = []
        for con_p in contents:
            con_p = "<p>" + con_p + "</p>"
            if "Baca juga" in con_p:
                pass
            else:
                contents_p.append(con_p)
        content_html = "".join(contents_p)
        return content_html


if __name__ == '__main__':
    news = KompasSpider()
    news.parse()
