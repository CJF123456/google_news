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
from utils.datautil import format_content_p, all_tag_replace_html_div, filter_emoji
from utils.timeUtil import now_datetime, now_time
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import update_img, get_image


# 纽约中文网 en

class CnNytimesSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:cnnytimes'
        self.project_name = self.__class__.__name__
        self.web_name = "纽约中文网"
        self.first_url = "https://cn.nytimes.com"

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
                log.info(self.project_name + column_first + column_second + ' spider succ.')
        else:
            pass
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div[@class="basic-list"]/ul/li|//div[@id="sectionLeadPackage"]/div')
            for el in els:
                try:
                    url_code = el.xpath(".//h3/a/@href")
                    url_code = "".join(url_code)
                    if "****" in url_code:
                        url_code = url_code.replace("****", "").lstrip().strip()
                    else:
                        url_code = url_code
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath(".//h3/a/text()")
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                try:
                    img_url = el.xpath('.//img[@class="img-lazyload"]/@data-url')
                    img_url = "".join(img_url)
                except Exception as e:
                    print(e)
                    img_url = ""
                try:
                    img_text = el.xpath(".//a/img/@alt")
                    img_text = "".join(img_text)
                except Exception as e:
                    print(e)
                    img_text = ""
                if url_code and title:
                    detail_url = self.first_url + url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                        pc_headers, md5, img_url, img_text, source_id)
                else:
                    pass

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, img_url, img_text, source_id):
        global con_, content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        pub_time = self.get_pub_time(con)
        # pub_date_time = now_datetime_no() + "00:00:00"
        # if pub_time < pub_date_time:
        #     log.info("数据不是最新" + pub_time)
        # else:
        if st:
            try:
                html = etree.HTML(con)
                column_ = html.xpath('//div[@class="col-4 section-title"]/h3/text()')
                column_first = "".join(column_)
            except Exception as e:
                print(e)
                column_first = column_first
            column_list = ["国际", "中国", "商业与经济", "观点与评论", "美国", "亚太", "商业与经济", "欧洲", "观点"]
            if column_first not in column_list:
                pass
            else:
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
                    content_text = filter_emoji(content_text)
                    spider_time = now_datetime()
                    # 采集时间
                    body = content_text
                    if "<!DOCTYPE html>" in content_text:
                        pass
                    else:
                        cn_title = title
                        create_time = spider_time
                        group_name = column_first
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
        try:
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", con)
            pub_time = mat.groups()[0] + " " + now_time()
            from utils.timeUtil import format_string_datetime
            pub_time = format_string_datetime(pub_time)
        except Exception as e:
            pub_time = now_datetime()
        return pub_time

    def get_content_html(self, html):
        global con, content_text
        try:
            soup = BeautifulSoup(html, 'lxml')
            for divcon in soup.select('section.article-body'):
                [s.extract() for s in divcon('script')]
                [s.extract() for s in divcon('figure')]
                [s.extract() for s in divcon.find_all("div", {"class": "big_ad"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = all_tag_replace_html_div(con)
                con = con.replace("\n", "").replace(" ", "")
                con = con.replace("div", "p")
                con_texts = con.split("</p><p>")
                cons = []
                for con_text in con_texts:
                    con_text = con_text.replace("<p>", "").replace("</p>", "").replace("<br/>", "")
                    if con_text:
                        cons.append(con_text)
                con_text = "</p><p>".join(cons)
                content_text = con_text.replace("（欢迎点击此处订阅NYT简报，我们将在每个工作日发送最新内容至您的邮箱。）", "")
                content_text = format_content_p(content_text)
                content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
        except Exception as e:
            print(e)
            content_text = ""
        return content_text

    def get_image_url(self, con):
        html = etree.HTML(con)
        try:
            image_url = html.xpath(
                '//article//figure[@class="article-span-photo"]/img/@src')[0]
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


if __name__ == '__main__':
    news = CnNytimesSpider()
    news.parse()
