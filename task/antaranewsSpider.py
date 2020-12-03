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
from utils.timeUtil import now_datetime, now_datetime_no
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img
from utils.translate import translated_cn, en_con_to_cn_con


# 安塔拉新闻 id

class AntaranewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:antaranews'
        self.project_name = self.__class__.__name__
        self.web_name = "安塔拉新闻"
        self.first_url = "https://www.antaranews.com/"

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
                '//div[@class="col-md-8"]//article//h3|//div[@class="row"]/div/article//h2')
            for el in els:
                try:
                    url_code = el.xpath('./a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./a/text()')
                    title = "".join(title).strip()
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

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "").replace("<br />", "<p>")
        return format_info

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, content_text, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            pub_time = self.get_pub_time(html, column_first)
            pub_date_time = now_datetime_no()
            if pub_time < pub_date_time:
                log.info("数据不是最新" + pub_time)
                #hset_md5_filter(md5, self.mmd5)
            else:
                subhead = self.get_subhead(con)
                image_url = self.get_image_url(con)
                caption = self.get_caption(html)
                contents_html = self.get_content_html(con)
                cn_title = translated_cn(title, 'id')
                if not contents_html:
                    pass
                else:
                    contents_html = subhead + self.get_content_html(con)
                    if caption:
                        cn_caption = translated_cn(caption, 'id')
                    else:
                        cn_caption = ""
                    cn_content_ = en_con_to_cn_con(contents_html, 'id')
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
                        content_text = content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace(
                            "<p></p>",
                            "").replace(
                            "<p>  </p>", "").replace("<p>   </p>", "")
                        cn_content_text = cn_content_text.replace("<p><p>", "<p>"). \
                            replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace(
                            "<p></p>",
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
                        pass
        else:
            pass

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        content_text = ""
        if 'class="flex-caption"' in html:
            soup = BeautifulSoup(html, 'lxml')
            con_htmls = []
            for divcon in soup.select('div.single-image'):
                [s.extract() for s in divcon('img')]
                [s.extract() for s in divcon.find_all("div", {"class": "quote_old"})]
                [s.extract() for s in divcon.find_all("div", {"footer": "post-meta"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = self.filter_html_clear_format(con)
                con_html = self.cn_replace_html(con)
                con_html = con_html.replace("  ", "").replace("    ", "").strip()
                con_htmls.append(con_html)
            content_text = "".join(con_htmls)
            content_text = self.format_content_p(content_text)
            content_text = all_tag_replace_html(content_text)
            if "&amp;" in content_text:
                content_text.replace("&amp;", "&")
            content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
        elif 'class="post-content clearfix"' in html:
            soup = BeautifulSoup(html, 'lxml')
            con_htmls = []
            for divcon in soup.select('div.post-content.clearfix'):
                [s.extract() for s in divcon("ins")]
                [s.extract() for s in divcon("script")]
                [s.extract() for s in divcon.find_all("span", {"class": "baca-juga"})]
                [s.extract() for s in divcon.find_all("div", {"class": "quote_old"})]
                [s.extract() for s in divcon.find_all("div", {"footer": "post-meta"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = self.filter_html_clear_format(con)
                con_html = self.cn_replace_html(con)
                con_html = con_html.replace("  ", "").replace("    ", "").strip()
                con_htmls.append(con_html)
            content_text = "".join(con_htmls)
            content_text = self.format_content_p(content_text)
            content_text = all_tag_replace_html(content_text)
            if "&amp;" in content_text:
                content_text = content_text.replace("&amp;", "&")
            if "<p>Pewarta" in content_text:
                content_text = content_text.split("<p>Pewarta")[0]
            content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
        if content_text:
            content_text = content_text.replace("<p><p>", "<p>"). \
                replace("</p></p>", "</p>").replace("<p></p>", "").replace("<p> </p>", "").replace(
                "<p></p>",
                "").replace(
                "<p>  </p>", "").replace("<p>   </p>", "")
        else:
            content_text = ""

        return content_text

    def format_content_p(self, con_text):
        con_ = con_text.split("<p>")
        contents = []
        for con in con_:
            if con:
                if "<p>" in con:
                    con = con.replace("<p>", "").strip().lstrip()
                if "</p>" in con:
                    con = con.replace("</p>", "").strip().lstrip()
                if con.startswith("延伸阅读"):
                    pass
                elif "Baca juga" in con:
                    pass
                else:
                    contents.append(con)
            else:
                pass
        contents_p = []
        for con_p in contents:
            con_p = "<p>" + con_p + "</p>"
            contents_p.append(con_p)
        content_html = "".join(contents_p)
        return content_html

    # TODO 图片url
    def get_image_url(self, con):
        image_url = ""
        if '<figure class="image-overlay">' in con and '<source type="image/webp"' in con:
            html = etree.HTML(con)
            try:
                image_url = html.xpath('//figure[@class="image-overlay"]/picture/source/@data-srcset')[0]
                image_url = "".join(image_url)
                if ".webp" in image_url:
                    image_url = image_url.replace(".webp", "")
            except Exception as e:
                print(e)
                image_url = ""
        elif 'class="single-image"' in con:
            html = etree.HTML(con)
            try:
                image_url = html.xpath('//div[@class="single-image"]/img/@src')[0]
                image_url = "".join(image_url)
            except Exception as e:
                print(e)
                image_url = ""
        elif '<figure class="image-overlay"><img' in con:
            html = etree.HTML(con)
            try:
                image_url = html.xpath('//figure[@class="image-overlay"]/img/@src')[0]
                image_url = "".join(image_url)
            except Exception as e:
                print(e)
                image_url = ""
        return image_url

    def get_caption(self, html):
        try:
            caption = html.xpath('//p[@class="wp-caption-text"]/text()')[0]
            caption = "".join(caption)
            if "©" in caption:
                caption = caption.split("©")[0].strip()
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, html, column_first):
        global pub_el
        try:
            pub_time_el = html.xpath('//span[@class="article-date"]/text()')[0]
            pub_el = "".join(pub_time_el)
            time_list = pub_el.split(" ")
            day_ = time_list[2]
            month_ = time_list[3]
            month = str(self.get_month_ydl(month_))
            year_ = time_list[4]
            hour_mis = time_list[5]
            pub_time = year_ + "-" + month + "-" + day_ + " " + hour_mis + ":00"
        except Exception  as e:
            log.info(e)
            pub_time = now_datetime_no()
        return pub_time

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
                "<br/>", "<p>")
        if "Read Next" in format_info:
            format_info = format_info.split("Read Next")[0]
        elif "RELATED STORY" in format_info:
            format_info = format_info.split("RELATED STORY")[0]
        elif "<p>更多" in format_info:
            format_info = format_info.split("<p>更多")[0]

        return format_info

    def get_date_am_pm(self, info_):
        global num
        if ":" in info_:
            hour = info_.split(" ")[0].split(":")[0]
            mis = info_.split(" ")[0].split(":")[1]
            mp = info_.split(" ")[1]
            if "am" in mp or "AM" in mp:
                num = info_.replace("am", "").strip()
            else:
                num = int(hour) + 12
                num = str(num) + ":" + mis
        else:
            num = ""
        return num

    def get_subhead(self, con):
        if '<div class="quote_old">' in con:
            html = etree.HTML(con)
            try:
                subhead = html.xpath('//div[@class="quote_old"]/text()')[0]
                subhead = "".join(subhead).strip()
                if "©" in subhead:
                    subhead = subhead.split("©")[0].strip()
                    subhead = "<p>" + subhead + "</p>"
                else:
                    subhead = "<p>" + subhead + "</p>"
            except Exception as e:
                print(e)
                subhead = ""
        else:
            subhead = ""
        return subhead

    # 印尼月份
    def get_month_ydl(self, month):
        if "Oktober" in month:
            month = 10
        elif "November" in month:
            month = 11
        elif "Desember" in month:
            month=12
        return month


if __name__ == '__main__':
    news = AntaranewsSpider()
    news.parse()
