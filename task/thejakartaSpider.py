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
    all_tag_replace_html, get_month_en
from utils.timeUtil import now_datetime, now_datetime_no
from utils.translate import cat_to_chs, en_con_to_cn_con, translated_cn
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import update_img, get_image


# 雅加达邮报
class ThejakartaSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:thejakarta'
        self.project_name = self.__class__.__name__
        self.web_name = "雅加达邮报"

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
                '//div[@class="containerLeft col-xs-12"]/div/div[@class="listNews whtPD columns"]/div[@class="columnsNews columns"]')
            for el in els:
                try:
                    url_code = el.xpath('.//div[@class="newsWord"]/a[last()]/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./div[@class="newsWord"]/a[last()]/h2/text()')
                    title = "".join(title).replace("\n", "").strip()
                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        pass
                        #log.info(self.project_name + " info data already exists!")
                    else:
                        if detail_url and title:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, source_id)
                else:
                    pass
            els2 = html.xpath(
                '//ul[@class="slides"]/li//a[2]')
            for el2 in els2:
                try:
                    url_code2 = el2.xpath('./@href')
                    url_code2 = "".join(url_code2)
                except Exception as e:
                    print(e)
                    url_code2 = ""
                try:
                    title2 = el2.xpath('./h5/text()')
                    title2 = "".join(title2).replace("\n", "").strip()
                except Exception as e:
                    print(e)
                    title2 = ""
                if url_code2 and title2:
                    detail_url2 = url_code2
                    md5_2 = detail_url2
                    md52 = make_md5(md5_2)
                    if hexists_md5_filter(md52, self.mmd5):
                        pass
                        #log.info(self.project_name + " info data already exists!")
                    else:
                        if detail_url2 and title2:
                            self.get_detail(title2, detail_url2, url_code2, column_first, column_second, kw_site,
                                            pc_headers, md52, source_id)
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
            log_in = self.get_login(html)
            if log_in:
                pass
            else:
                pub_time = self.get_pub_time(html)
                # pub_date_time = now_datetime_no()
                # if pub_time < pub_date_time:
                #     log.info("数据不是最新" + pub_time)
                #     hset_md5_filter(md5, self.mmd5)
                # else:
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
                    if cn_content_ and cn_title and len(cn_content_) > len(contents_html) / 4:
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
                        cn_content_text = cn_content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace(
                            "<p></p>",
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
                    else:
                        pass


    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.col-md-10.col-xs-12.detailNews'):
            [s.extract() for s in divcon("script")]
            [s.extract() for s in divcon("div")]
            [s.extract() for s in divcon.find_all("span", {"class": "readalso"})]
            [s.extract() for s in divcon.find_all("span", {"class": "created"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = con.replace("\n", "").replace("  ", "").strip()
            con = filter_html_clear_format(con)
            con = con.replace("  ", "")
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
            "<p>  </p>", "").replace("<p>   </p>", "").replace("\n", "").strip()
        return content_text


    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="row"]/img/@src')[0]
            image_url = "".join(image_url).replace("\n", "").strip()
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


    def get_caption(self, html):
        try:
            caption = html.xpath('//span[@class="created"]/text()')[0]
            caption = "".join(caption).replace("\n", "").strip()
        except Exception as e:
            print(e)
            caption = ""
        return caption


    def get_pub_time(self, html):
        try:
            try:
                day_el = html.xpath('.//span[@class="day"]/text()')
                day_time = "".join(day_el).replace("\n", "").strip()
                month = day_time.split(" ")[1]
                month = get_month_en(month)
                day = day_time.split(" ")[2].replace(",", "")
                year = day_time.split(" ")[3].replace("/", "")
                day_time = year + "-" + month + "-" + day
            except Exception as e:
                print(e)
                day_time = now_datetime_no()
            try:
                pub_time_el = html.xpath('.//span[@class="time"]/text()')
                now_time = "".join(pub_time_el).replace("\n", "").replace("/   ", "").strip()
                now_time = self.get_hour_mis(now_time) + ":00"
            except Exception as e:
                print(e)
                now_time = time.strftime("%H:%M:%S", time.localtime(time.time()))
            pub_time = day_time + " " + now_time
        except Exception as e:
            print(e)
            pub_time = now_datetime()

        return pub_time


    def get_hour_mis(self, info_):
        global num
        if ":" in info_:
            hour = info_.split(" ")[0].split(":")[0]
            mis = info_.split(" ")[0].split(":")[1]
            mp = info_.split(" ")[1]
            if "am" in mp:
                num = info_.replace("am", "").strip()
            else:
                if "08" in hour:
                    num = "20"
                elif "07" in hour:
                    num = "19"
                elif "06" in hour:
                    num = "18"
                elif "05" in hour:
                    num = "17"
                elif "04" in hour:
                    num = "16"
                elif "03" in hour:
                    num = "15"
                elif "02" in hour:
                    num = "14"
                elif "01" in hour:
                    num = "13"
                elif "09" in hour:
                    num = "21"
                elif "10" in hour:
                    num = "22"
                elif "11" in hour:
                    num = "23"
                else:
                    pass
                num = num + ":" + mis
        else:
            num = ""
        return num


    def get_login(self, html):
        try:
            login_text = html.xpath('//div[@class="col-md-10 col-xs-12 detailNews"]//h1/text()')
            login_text = "".join(login_text)
        except Exception as e:
            print(e)
            login_text = ""
        return login_text


if __name__ == '__main__':
    news = ThejakartaSpider()
    news.parse()
