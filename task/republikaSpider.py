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
    all_tag_replace_html, get_month_en
from utils.timeUtil import now_datetime, now_datetime_no
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img
from utils.translate import translated_cn, en_con_to_cn_con


# from utils.translate import translated_cn, en_con_to_cn_con


# 印尼共和报-国际版

class RepublikaSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:republika'
        self.project_name = self.__class__.__name__
        self.web_name = "印尼共和报"
        self.first_url = "https://republika.co.id/"

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
                '//div[@class="wrap-latest"]/div[@class="conten1"]|//div[@class="headline "]')
            for el in els:
                try:
                    url_code = el.xpath('.//h2/a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('.//h2/a/text()')
                    title = "".join(title)
                except Exception as e:
                    print(e)
                    title = ""
                if url_code and title:
                    detail_url = url_code
                    md5_ = detail_url
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        pass
                        # log.info(self.project_name + " info data already exists!")
                    else:
                        if detail_url and title:
                            # https://www.republika.co.id/berita/qmr9td368/menteri-austria-mundur-tersandung-isu-plagiarisme
                            if detail_url.startswith("https://www.republika.co.id/berita/"):
                                self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                                pc_headers, md5, source_id)
                            else:
                                log.info("此文章不符合规范")
                                log.info(detail_url)
                else:
                    pass

    def cn_replace_html(self, format_info):
        if format_info:
            format_info = format_info.split("<p><em>©")[0].replace("<strong>", "").replace("</strong>", "").replace(
                "<em>", "").replace("</em>", "").replace("<p></p>", "")
        return format_info

    def get_detail(self, title__, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_, content_text, cn_content_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            title_ = self.get_title(con)
            if title_ and title__:
                if title__ in title_:
                    title = title__
                else:
                    title = title_
                pub_time = self.get_pub_time(html)
                pub_date_time = now_datetime_no()
                # if pub_time < pub_date_time:
                #     log.info("数据不是最新" + pub_time)
                #     hset_md5_filter(md5, self.mmd5)
                # else:
                image_url = self.get_image_url(html)
                caption = self.get_caption(html)
                subhead = self.get_subhead(html)
                contents_html = subhead + self.get_content_html(con)
                cn_title = translated_cn(title, 'id')
                if not contents_html:
                    pass
                else:
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
                            "<p></p>", "").replace("<p>  </p>", "").replace("<p>   </p>", "")
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
            log.info('title spider fail.')



    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html
        soup = BeautifulSoup(html, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.artikel'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon("div")]
            [s.extract() for s in divcon("iframe")]
            [s.extract() for s in divcon("blockquote")]
            [s.extract() for s in divcon("script")]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = self.filter_html_clear_format(con)
            con_html = self.cn_replace_html(con)
            con_html = con_html.replace("  ", "")
            con_htmls.append(con_html)
        content_text = "".join(con_htmls)
        content_text = format_content_p(content_text)
        content_text = all_tag_replace_html(content_text)
        if "&amp;" in content_text:
            content_text.replace("&amp;", "&")
        content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
        if "<p>. </p>" in content_text:
            content_text = content_text.replace("<p>. </p>", "")
        return content_text


    # TODO 图片url
    def get_image_url(self, html):
        try:
            image_url = html.xpath('//div[@class="img_detail"]/img/@data-original')[0]
            image_url = "".join(image_url)
        except Exception as e:
            print(e)
            image_url = ""
        return image_url


    def get_caption(self, html):
        try:
            caption = html.xpath('//div[@class="img_set_teaser_left"]/p/text()')[0]
            caption = "".join(caption)
            if "©" in caption:
                caption = caption.split("©")[0].strip()
        except Exception as e:
            print(e)
            caption = ""
        return caption


    # //div[@class="taiching"]/b/text()
    def get_subhead(self, html):
        try:
            subhead = html.xpath('//div[@class="taiching"]/b/text()')[0]
            subhead = "".join(subhead)
            subhead = "<p>" + subhead + "</p>"
        except Exception as e:
            print(e)
            subhead = ""
        return subhead


    def get_pub_time(self, html):
        global pub_el
        try:
            pub_time_el = html.xpath('//div[@class="date_detail"]/p/text()')
            pub_el = "".join(pub_time_el)
            time_list = pub_el.split(" ")
            day_ = time_list[3]
            month_ = time_list[4]
            month = get_month_en(month_)
            year_ = time_list[5]
            hour_mis = time_list[7]
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


    def get_title(self, con):
        global con_html
        soup = BeautifulSoup(con, 'lxml')
        con_htmls = []
        for divcon in soup.select('div.wrap_detail h1'):
            locu_content = divcon.prettify()
            con_locu = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con_locu_ = con_locu.replace("\n", "").strip().lstrip()
            con_locu = all_tag_replace_html(con_locu_)
            con = con_locu.replace("  ", "")
            con_htmls.append(con)
            break
        content_text = "".join(con_htmls)
        return content_text


if __name__ == '__main__':
    news = RepublikaSpider()
    news.parse()
