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
from utils.datautil import filter_html_clear_format, format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no
from utils.translate import cat_to_chs
from utils.ossUtil import get_image, update_img
from configs.dbconfig import NewsTaskSql

# 自由时报电子报

class LtnSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:ltn'
        self.project_name = self.__class__.__name__
        self.web_name = "自由时报电子报"
        self.first_url = "https://talk.ltn.com.tw"

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
        if "https://news.ltn.com.tw" in list_url:
            st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
            if st:
                html = etree.HTML(con)
                els = html.xpath(
                    '//ul[@class="list"]/li')
                for el in els:
                    try:
                        url_code = el.xpath('./a[1]/@href')
                        url_code = "".join(url_code)
                    except Exception as e:
                        print(e)
                        url_code = ""
                    try:
                        title = el.xpath('./a[1]/@title')
                        title = "".join(title).strip()
                        title = "".join(cat_to_chs(title))
                    except Exception as e:
                        print(e)
                        title = ""
                    if url_code and title:
                        detail_url = url_code
                        md5_ = detail_url
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            if detail_url and title:
                                self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                                pc_headers, md5, source_id)
                    else:
                        pass
        elif "https://talk.ltn.com.tw" in list_url:
            st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
            if st:
                html = etree.HTML(con)
                els = html.xpath(
                    '//div[@data-desc="列表"]/ul/li')
                for el in els:
                    try:
                        url_code = el.xpath('./a[1]/@href')
                        url_code = "".join(url_code)
                    except Exception as e:
                        print(e)
                        url_code = ""
                    try:
                        title = el.xpath('./a[@class="titlist"]/p/text()')
                        title = "".join(title).strip()
                        title = "".join(cat_to_chs(title))
                    except Exception as e:
                        print(e)
                        title = ""
                    if url_code and title:
                        detail_url = "https://talk.ltn.com.tw/" + url_code
                        md5_ = detail_url
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            if detail_url and title:
                                self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                                pc_headers, md5, source_id)
                    else:
                        pass
        else:
            pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_
        if "https://news.ltn.com.tw/news" in detail_url:
            st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
            html = etree.HTML(con)
            pub_time = self.get_pub_time(html)
            pub_date_time = now_datetime_no()
            if pub_time < pub_date_time:
                log.info("数据不是最新" + pub_time)
                hset_md5_filter(md5, self.mmd5)
            else:
                image_url = self.get_image_url(html)
                if not image_url:
                    pass
                else:
                    caption = self.get_caption(html)
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
                            content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace(
                                "<p></p>",
                                "")
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
                                body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name,
                                if_top,
                                keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                                CrawlTime,
                                Hidden, file_name, file_path)
                            # 入库mssql
                            data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                             self.project_name)

        if "https://talk.ltn.com.tw/article" in detail_url:
            st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
            html = etree.HTML(con)
            pub_time = self.get_pub_time(html)
            pub_date_time = now_datetime_no()
            if pub_time < pub_date_time:
                log.info("数据不是最新" + pub_time)
                hset_md5_filter(md5, self.mmd5)
            else:
                image_url = self.get_image_url_2(html)
                caption = self.get_caption_2(html)
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
                        content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace(
                            "<p></p>",
                            "")
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
        if not 'title="作者圖片"' in html:
            soup = BeautifulSoup(html, 'lxml')
            con_htmls = []
            for divcon in soup.select('div.text.boxTitle.boxText'):
                [s.extract() for s in divcon("div")]
                [s.extract() for s in divcon("script")]
                [s.extract() for s in divcon("b")]
                [s.extract() for s in divcon("iframe")]
                [s.extract() for s in divcon("blockquote")]
                [s.extract() for s in divcon("h4")]
                [s.extract() for s in divcon.find_all("p", {"class": "before_ir"})]
                [s.extract() for s in divcon.find_all("article", {"role": "article"})]
                [s.extract() for s in divcon.find_all("p", {"class": "appE1121"})]
                [s.extract() for s in divcon.find_all("span", {"class": "time"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = filter_html_clear_format(con)
                con = con.replace("  ", "")
                con_html = self.cn_replace_html(con)
                con_html = "".join(cat_to_chs(con_html))
                con_html = format_content_p(con_html)
                con_htmls.append(con_html)
            content_text = "".join(con_htmls)
            content_text = all_tag_replace_html(content_text)
            content_text = content_text.replace("     ", "")
            content_text = content_text.replace("<p>  </p>", "")
            content_text = content_text.replace("<p>   </p>", "")
        else:
            soup = BeautifulSoup(html, 'lxml')
            con_htmls = []
            for divcon in soup.select('div.text'):
                [s.extract() for s in divcon("div")]
                [s.extract() for s in divcon("script")]
                [s.extract() for s in divcon("b")]
                [s.extract() for s in divcon("iframe")]
                [s.extract() for s in divcon("blockquote")]
                [s.extract() for s in divcon.find_all("span", {"class": "ph_b ph_d1"})]
                [s.extract() for s in divcon.find_all("span", {"class": "time"})]
                [s.extract() for s in divcon.find_all("p", {"class": "before_ir"})]
                [s.extract() for s in divcon.find_all("p", {"class": "appE1121"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = filter_html_clear_format(con)
                con = con.replace("  ", "")
                con_html = self.cn_replace_html(con)
                con_html = "".join(cat_to_chs(con_html))
                con_html = format_content_p(con_html)
                con_htmls.append(con_html)
            content_text = "".join(con_htmls)
            content_text = all_tag_replace_html(content_text)
            content_text = content_text.replace("     ", "")
            content_text = content_text.replace("<p>  </p>", "")
            content_text = content_text.replace("<p>   </p>", "")

        return content_text

    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="photo boxTitle"]/a/img/@src')[0]
            image_url = "".join(image_url)
            if "assets/images/default" in image_url:
                image_url = ""
        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//div[@class="photo boxTitle"]/a/img/@title')[0]
            caption = "".join(caption)
            caption = "".join(cat_to_chs(caption))
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, html):
        try:
            pub_time_el = html.xpath('.//span[@class="time"][1]/text()')
            pub_el = "".join(pub_time_el)
            pub_el = pub_el.replace("/", "-").strip()
            pub_time = pub_el + ":00"
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    def get_image_url_2(self, html):
        try:
            image_url = html.xpath('//span[@class="ph_b ph_d1"]/span[@class="ph_i"]//img/@data-original')[0]
            image_url = "".join(image_url)
            if "assets/images/default" in image_url:
                image_url = ""
        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption_2(self, html):
        try:
            caption = html.xpath('//span[@class="ph_b ph_d1"]/span[@class="ph_d"]/text()')[0]
            caption = "".join(caption)
            caption = "".join(cat_to_chs(caption))
        except Exception as e:
            print(e)
            caption = ""
        return caption


if __name__ == '__main__':
    news = LtnSpider()
    news.parse()
