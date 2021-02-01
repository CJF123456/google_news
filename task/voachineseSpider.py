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
from utils.ossUtil import get_image, update_img
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql, get_list_page_get_content
from utils.datautil import format_info_list_str, filter_html_clear_format, \
    all_tag_replace_html, format_content_p, format_p_null
from utils.timeUtil import now_datetime, now_datetime_no
from configs.dbconfig import NewsTaskSql
from utils.translate import cat_to_chs


# 美国之音 已完结
class VoachineseSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:voachinese'
        self.project_name = self.__class__.__name__
        self.web_name = "美国之音"
        self.first_url = "https://www.voachinese.com"

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
            self.project_name + ' spider succ ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        st, con = get_list_page_get_content(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div[@class="media-block-wrap"]/div[@class="row"]/ul/li')
            for el in els:
                try:
                    url_code = el.xpath('./div["media-block"]/a/@href')
                    url_code = format_info_list_str(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./div["media-block"]/a/@title')
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                try:
                    url_type = el.xpath('./div["media-block"]/a/span/@class')
                    url_type = "".join(url_type).lstrip().strip()
                except Exception as e:
                    print(e)
                    url_type = ""
                if not url_type:
                    pass
                    #log.info("video url......")
                else:
                    if url_code and title:
                        if len(url_code) <= 16:
                            # log.info("video url...")
                            pass
                        else:
                            if "https://www.voachinese.com" in url_code:
                                detail_url = url_code
                            else:
                                detail_url = self.first_url + url_code
                            md5_ = detail_url
                            md5 = make_md5(md5_)
                            if hexists_md5_filter(md5, self.mmd5):
                                pass
                                # log.info(self.project_name + " info data already exists!")
                            else:
                                if detail_url.startswith('https://www.voachinese.com/a/') and detail_url.endswith(
                                        ".html"):
                                    if "voaio" in detail_url:
                                        pass
                                    elif ".png" in detail_url:
                                        pass
                                    elif ".jpg" in detail_url:
                                        pass
                                    elif "eoa" in detail_url:
                                        pass
                                    else:
                                        self.get_detail(title, detail_url, url_code, column_first, column_second,
                                                        kw_site,
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
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        html = etree.HTML(con)
        image_url = self.get_image_url(html)
        pub_time = self.get_pub_time(html)
        caption = self.get_caption(html)
        tag_con = self.get_tag(html)
        if st:
            content = self.get_content_html(con, tag_con)
            if not content:
                pass
            else:
                if image_url:
                    ii = get_image(image_url)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + content
                else:
                    content_text = content
                content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>",
                                                                                                         "")
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
                cn_boty = ""
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
                data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                  self.project_name)

    def get_pub_time(self, html):
        try:
            pub_time_el = html.xpath('.//span[@class="date"]/time/text()')
            pub_time_ = format_info_list_str(pub_time_el).strip()
            pub_time = pub_time_.replace("年", "-").replace("月", "-").replace("日", " ").lstrip() + ":00"
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    # TODO 内容格式化
    def get_content_html(self, html, tag_con):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.wsw'):
            [s.extract() for s in divcon('script', )]
            [s.extract() for s in divcon('iframe')]
            [s.extract() for s in divcon("svg")]
            [s.extract() for s in divcon("h4")]
            [s.extract() for s in divcon("h1")]
            [s.extract() for s in divcon.find_all("div", {"class": "wsw__embed"})]
            [s.extract() for s in divcon.find_all("span", {"class": "dateline"})]
            [s.extract() for s in divcon.find_all("div", {"data-owner-ct": "Article"})]
            [s.extract() for s in
             divcon.find_all("span", {"class": "rfg5jk-0 hghSag s3n5kh1-0 gcPAtQ sc-bdVaJa iHZvIS"})]
            locu_content = divcon.prettify().lstrip().strip()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content).lstrip().strip()
            con = filter_html_clear_format(con).lstrip().strip()
            con = con.replace("  ", "").lstrip().strip()
            con_html = self.cn_replace_html(con).lstrip().strip()
            con_html = format_content_p(con_html).lstrip().strip()
            con_htmls.append(con_html)
        content_text = "".join(con_htmls).lstrip().strip()
        tag_con_ = "<p>" + tag_con + "</p><p>"
        tag_content = "<p>" + tag_con
        content_text = content_text.replace(tag_con_, tag_content).lstrip().strip()
        if "<br/><br/>" in content_text:
            content_text = content_text.replace("<br/><br/>", "</p><p>")
        else:
            content_text = content_text
        content_text = all_tag_replace_html(content_text)
        content_text = format_p_null(content_text)
        content_text_cn = "".join(cat_to_chs(content_text))
        return content_text_cn

    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="cover-media"]/figure/div[@class="img-wrap"]//img/@src')[0]
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//div[@class="cover-media"]/figure/div[@class="img-wrap"]//img/@alt')
            caption = "".join(caption).lstrip()
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_tag(self, html):
        try:
            tag_content = html.xpath('//span[@class="dateline"][1]/text()')
            tag_content = "".join(tag_content)
        except Exception as e:
            print(e)
            tag_content = ""
        return tag_content


if __name__ == '__main__':
    news = VoachineseSpider()
    news.parse()
