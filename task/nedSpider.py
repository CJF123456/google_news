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
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import all_tag_replace_html, format_content_p, get_month_en
from utils.timeUtil import now_datetime, now_datetime_no, now_time
from utils.translate import cat_to_chs, translated_cn, en_con_to_cn_con
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img



# 美国国家民主基金会

class NedSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:ned'
        self.project_name = self.__class__.__name__
        self.web_name = "美国国家民主基金会"

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
                '//div[@class="events-page"]/div[starts-with(@class,"large-container")]//div[@class="detail-block"]')
            for el in els:
                try:
                    url_code = el.xpath('.//a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./h3/text()|./h2/text()')
                    title = "".join(title).replace("\n", "").strip()
                except Exception as e:
                    print(e)
                    title = ""
                pub_time = self.get_pub_time(el,column_first)
                pub_date_time = now_datetime_no()
                if pub_time < pub_date_time:
                    log.info("数据不是最新" + pub_time)
                else:
                    if url_code:
                        detail_url = url_code
                        md5_ = title + kw_site
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            if detail_url:
                                self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                                pc_headers, md5, source_id,pub_time)
                    else:
                        pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id,pub_time):
        global con_, content_text, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            image_url = self.get_image_url(html)
            caption = self.get_caption(html)
            contents_html = self.get_content_html(con)
            cn_title = translated_cn(title, 'en')
            if not contents_html:
                pass
            else:
                if caption:
                    cn_caption = translated_cn(caption, 'en')
                else:
                    cn_caption = ""
                cn_content_ = en_con_to_cn_con(contents_html, 'en')
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
                        replace("</p></p>", "</p>").replace("<p></p>", ""). \
                        replace("<p> </p>", "").replace("<p></p>", "").replace(
                        "<p>  </p>", "").replace("<p>   </p>", "").replace("<p></p>", "")
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
                else:
                    pass

    # TODO 替换各种不用的标签
    def filter_html_clear_format(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<span>', '').replace(
                '</span>', '').replace('<button>', '').replace('</button>', ''). \
                replace('<svg>', '').replace('</svg>', '').replace('<figure>', '').replace('</figure>', '') \
                .replace('<figcaption>', '').replace('</figcaption>', '') \
                .replace('<path>', '').replace('</path>', '') \
                .replace('\r', '').replace('\n', '').replace('+<!-->3+<!-->2', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>").replace("<picture>", "") \
                .replace("</picture>", "").replace("<img>", "").replace("<a>", "").replace("</a>", " ") \
                .replace("<b>", "").replace("</b>", "").replace("<main>", "").replace("</main>", "") \
                .replace("<ul>", "").replace("</ul>", "").replace("<p></p>", "").replace("<i>", "").replace("</i>", '')
        if "「版權宣告" in format_info:
            format_info = format_info.split("「版權宣告")[0]
        elif "「版权声明：" in format_info:
            format_info = format_info.split("「版权声明：")[0]
        elif "<p>推荐阅读" in format_info:
            format_info = format_info.split("推荐阅读")[0]
        elif "<p>推荐阅读" in format_info:
            format_info = format_info.split("推荐阅读")[0]
        elif "<p>记者" in format_info:
            format_info = format_info.split("<p>记者")[0]
        elif "<p>编译" in format_info:
            format_info = format_info.split("<p>编译")[0]
        elif "<p>审校" in format_info:
            format_info = format_info.split("<p>审校")[0]
        elif "<p>更多" in format_info:
            format_info = format_info.split("<p>更多")[0]

        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.entry-content'):
            [s.extract() for s in divcon("script")]
            [s.extract() for s in divcon("h1")]
            [s.extract() for s in divcon("figure")]
            [s.extract() for s in divcon("h3")]
            [s.extract() for s in divcon("div")]
            locu_content = divcon.prettify()
            con_ = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con_ = self.filter_html_clear_format(con_)
            con = con_.replace("  ", "")
            con_html = self.cn_replace_html(con)
            con_html = "".join(cat_to_chs(con_html))
            con_html = format_content_p(con_html)
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = all_tag_replace_html(content_text)
        if "&amp;" in content_text:
            content_text = content_text.replace("&amp;", "&")
        content_text = content_text.replace("<p><p>", "<p>"). \
            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>", "").replace(
            "<p>  </p>", "").replace("<p>   </p>", "").replace("<p></p>", "").replace("   ", "").replace("  ", "")
        return content_text

    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="entry-content"]//img/@data-src')[0]
            image_url = "".join(image_url).replace("\n", "").strip()
        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//figure[1]/figcaption[@class="wp-caption-text"]/text()')
            caption = "".join(caption).replace("\n", "").strip()
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, html,column_first):
        if "events" in column_first:
            pub_time=now_datetime()
        else:
            try:
                pub_time_ = html.xpath('.//div[@class="event-date"]/text()')
                pub_time_ = "".join(pub_time_).strip()
                month_ = pub_time_.split(" ")[0]
                month = get_month_en(month_)
                day_ = pub_time_.split(" ")[1].replace(",", "")
                year_ = pub_time_.split(" ")[2]
                pub_time = year_ + "-" + month + "-" + day_ +" " +now_time()
            except Exception as e:
                print(e)
                pub_time = now_datetime()
        return pub_time


if __name__ == '__main__':
    news = NedSpider()
    news.parse()
