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
from utils.datautil import format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no, now_time
from utils.translate import cat_to_chs, translated_cn, en_con_to_cn_con
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img


# ansa 意大利语

class AnsaSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:ansa'
        self.project_name = self.__class__.__name__
        self.web_name = "ansa"
        self.first_url = "https://www.ansa.it"

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
                '//section/article[starts-with(@class,"new")]|//div/ol[@id="ultimaOra"]/li')
            for el in els:
                try:
                    url_code = el.xpath('.//h3/a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('.//h3/a/text()')
                    title = "".join(title).strip()
                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = self.first_url + url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        if detail_url and title:
                            url_idd = detail_url.split("notizie")[0]
                            if "europa" in url_idd:
                                pass
                            else:
                                self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                               pc_headers, md5, source_id)
                else:
                    pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, content_text, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            pub_time = self.get_pub_time(con)
            pub_date_time = now_datetime_no()
            if pub_time > pub_date_time:
                log.info("数据不是最新" + pub_time)
                #hset_md5_filter(md5, self.mmd5)
            else:
                log.info("新闻时间" + pub_time)
                image_url = self.get_image_url(html)
                caption = self.get_caption(html)
                contents_html = self.get_content_html(con)
                cn_title = translated_cn(title, 'it')
                if not contents_html:
                    pass
                else:
                    if caption:
                        cn_caption = translated_cn(caption, 'it')
                    else:
                        cn_caption = ""
                    cn_content_ = en_con_to_cn_con(contents_html, 'it')
                    if cn_content_ and cn_title and len(cn_content_) > len(contents_html) / 4:
                        if image_url:
                            image_url = self.first_url + image_url
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
                            "<p>  </p>", "").replace("<p>   </p>", "")
                        cn_content_text = cn_content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>",
                                                                                                               "").replace(
                            "<p>  </p>", "").replace("<p>   </p>", "")
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
                        log.info("翻译异常len(cn_content_)："+str(len(cn_content_)))

    # TODO 替换各种不用的标签
    def filter_html_clear_format(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<span>', '').replace(
                '</span>', '').replace('<button>', '').replace('</button>', ''). \
                replace('<svg>', '').replace('</svg>', '').replace('<figure>', '').replace('</figure>', '') \
                .replace('<figcaption>', '').replace('</figcaption>', '') \
                .replace('<path>', '').replace('</path>', '') \
                .strip().replace('\r', '').replace('\n', '').replace('+<!-->3+<!-->2', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>").replace("<picture>", "") \
                .replace("</picture>", "").replace("<img>", "").replace("<a>", "").replace("</a>", "") \
                .replace("<b>", "").replace("</b>", "").replace("<main>", "").replace("</main>", "") \
                .replace("<ul>", "").replace("</ul>", "").replace("<p></p>", "").replace("<i>", "").replace("</i>",
                                                                                                            '').replace(
                "<br/>", '<p>')
        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.news-txt'):
            [s.extract() for s in divcon("script")]
            [s.extract() for s in divcon("iframe")]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = self.filter_html_clear_format(con)
            con = con.replace("  ", "")
            con_html = self.cn_replace_html(con)
            con_html = "".join(cat_to_chs(con_html))
            con_html = format_content_p(con_html)
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = all_tag_replace_html(content_text)
        if "&amp;" in content_text:
            content_text = content_text.replace("&amp;", "&")
        if "<p>VIDEO</p>" in content_text:
            content_text = content_text.split("<p>VIDEO")[0]
        content_text = content_text.replace("<p><p>", "<p>"). \
            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace("<p></p>", "").replace(
            "<p>  </p>", "").replace("<p>   </p>", "")
        return content_text

    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="news-img"]/div/img/@src')[0]
            image_url = "".join(image_url)

        except Exception as e:
            print(e)
            image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//div[@class="news-caption hidden-phone"]/em/text()')[0]
            caption = "".join(caption)
            if "©" in caption:
                caption = caption.split("©")[0].strip()
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, con):
        global pub_el, pub_time_, date_
        html = etree.HTML(con)
        if "</strong><span>" in con:
            try:
                try:
                    pub_time_el = html.xpath('.//time/strong/text()')
                    pub_el = "".join(pub_time_el)
                    if " " in pub_el:
                        day_ = pub_el.split(" ")[0]
                        year_ = pub_el.split(" ")[2]
                        month_ = pub_el.split(" ")[1]
                        month = self.get_month_ydl(month_)
                        pub_time_ = year_ + "-" + str(month) + "-" + day_
                except Exception  as e:
                    print(e)
                    pub_time_ = now_datetime_no()
                try:
                    time_ = html.xpath('.//time/span/text()')
                    time_ = "".join(time_)
                except Exception as e:
                    print(e)
                    time_ = ""
                pub_time = pub_time_ + " " + time_ + ":00"
            except Exception as e:
                print(e)
                pub_time = now_datetime()
        else:
            try:
                pub_time_el = html.xpath('.//div[@class="news-date"]/time/text()')[0]
                pub_el = "".join(pub_time_el).strip().lstrip()
                if " " in pub_el:
                    day_ = pub_el.split(" ")[0]
                    year_ = pub_el.split(" ")[2]
                    month_ = pub_el.split(" ")[1]
                    month = self.get_month_ydl(month_)
                    date_ = year_ + "-" + str(month) + "-" + day_
            except Exception as e:
                print(e)
                date_ = now_datetime_no()
            try:
                pub_time_el = html.xpath('.//div[@class="news-date"]/time/span/text()')[0]
                pub_el = "".join(pub_time_el).strip().lstrip()
                time_ = pub_el.strip().lstrip()
            except Exception as e:
                print(e)
                time_ = now_time()
            pub_time = date_ + " " + time_ + ":00"
        return pub_time

    def get_month_ydl(self, month):
        if "ottobre" in month:
            month = 10
        elif "novembre" in month:
            month = 11
        elif "dicembre" in month:
            month=12
        return month


if __name__ == '__main__':
    news = AnsaSpider()
    news.parse()