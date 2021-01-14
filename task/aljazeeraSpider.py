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
from utils.translate import translated_cn, en_con_to_cn_con
from utils.ossUtil import get_image, update_img
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import filter_html_clear_format, format_content_p, \
    all_tag_replace_html, get_month_en, format_p_null
from utils.timeUtil import now_datetime, now_time, now_datetime_no
from configs.dbconfig import NewsTaskSql


# 半岛电视台 已完结


class AljazeeraSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:aljazeera'
        self.project_name = self.__class__.__name__
        self.web_name = "半岛电视台"
        self.first_url = "https://www.aljazeera.com"

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
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div/article/div//h3[@class="gc__title"]')
            for el in els:
                try:
                    url_code = el.xpath('.//a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                if url_code:
                    detail_url = self.first_url + url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        if "program" in detail_url:
                            pass
                        elif "interactive" in detail_url:
                            pass
                        else:
                            self.get_detail(detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, source_id)
                else:
                    pass

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

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "").replace("h2", "p")
        return format_info

    def get_detail(self, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, cn_boty, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            pub_time = self.pub_time_html(html)
            pub_date_time = now_datetime_no()
            # if pub_time < pub_date_time:
            #     log.info("数据不是最新" + pub_time)
            #     hset_md5_filter(md5, self.mmd5)
            # else:
            image_url = self.get_image_url(html)
            title = self.get_title_html(html)
            cn_title = translated_cn(title, 'en')
            subhead = self.get_subhead_text(html)
            caption = self.get_caption_html(html)
            if caption:
                cn_caption = translated_cn(caption, 'en')
            else:
                cn_caption = ""
            content_ = subhead + self.get_content_html(con)
            if not content_:
                pass
            else:
                cn_content_ = en_con_to_cn_con(content_, 'en')
                if cn_content_ and cn_title and len(cn_content_) > len(content_) / 4:
                    if image_url:
                        image_url = self.first_url + image_url
                        ii = get_image(image_url)
                        r_i = update_img(ii)
                        img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                        content_text = img_ + content_
                        cn_img_ = '<img src="' + r_i + '"/><p>' + cn_caption + '</p>'
                        cn_content_text = cn_img_ + cn_content_
                    else:
                        content_text = content_
                        cn_content_text = cn_content_
                    content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace(
                        "<p></p>",
                        "")
                    cn_content_text = cn_content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace(
                        "<p></p>", "")
                    spider_time = now_datetime()
                    # 采集时间
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
                else:
                    pass

        else:
            pass


    def format_repalce_space(self, format_info):
        if "</ p> <p>" in format_info:
            format_info = format_info.replace("</ p> <p>", "</p><p>")
        if "<p> </ p>" in format_info:
            format_info = format_info.replace("<p> </ p>", "<p></p>")
        if "<p></p>" in format_info:
            format_info = format_info.replace("<p></p>", "")
        if " / p> <p>" in format_info:
            format_info = format_info.replace(" / p> <p>", "</p><p>")
        return format_info


    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.wysiwyg.wysiwyg--all-content'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon("div")]
            [s.extract() for s in divcon("iframe")]
            [s.extract() for s in divcon("blockquote")]
            [s.extract() for s in divcon.find_all("div", {"class": "twitter-tweet twitter-tweet-rendered"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = filter_html_clear_format(con)
            con_html = self.cn_replace_html(con)
            con_html = con_html.replace("  ", "")
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = format_content_p(content_text)
        content_text = all_tag_replace_html(content_text)
        if "&amp;" in content_text:
            content_text.replace("&amp;", "&")
        content_text =format_p_null(content_text)
        return content_text


    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//figure[@class="article-featured-image"]/div[@class="responsive-image"]/img/@src')
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


    def get_title_html(self, html):
        try:
            title_el = html.xpath(
                '//header/h1/text()')
            title = "".join(title_el)
        except Exception as e:
            print(e)
            title = ""
        return title


    def get_caption_html(self, html):
        try:
            img_text = html.xpath('//figure[@class="article-featured-image"]/figcaption/text()')
            img_text = "".join(img_text)
        except Exception as e:
            print(e)
            img_text = ""
        return img_text


    def get_subhead_text(self, html):
        try:
            subhead = html.xpath('//p[@class="article__subhead"]/text()')
            subhead_text = "".join(subhead)
        except Exception as e:
            print(e)
            subhead_text = ""
        if subhead_text:
            subhead_text = "<p>" + subhead_text + "</p>"
        else:
            subhead_text = ""
        return subhead_text


    def pub_time_html(self, html):
        try:
            pub_time_ = html.xpath('//div[@class="article-dates"]/div[@class="date-simple"]/text()')
            pub_time_ = "".join(pub_time_)
            pub_time_ = pub_time_.split(" ")
            day = pub_time_[0]
            month_ = pub_time_[1]
            month_ = get_month_en(month_)
            year = pub_time_[2]
            pub_time_txt = year + "-" + month_ + "-" + day
        except Exception as e:
            print(e)
            pub_time_txt = now_datetime_no()
        if pub_time_txt:
            pub_time = pub_time_txt + " " + now_time()
        else:
            pub_time = now_datetime()
        return pub_time


if __name__ == '__main__':
    news = AljazeeraSpider()
    news.parse()
