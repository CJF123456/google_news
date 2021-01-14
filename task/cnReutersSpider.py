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
import json
import random
import re
import time
from bs4 import BeautifulSoup
from configs.dbconfig import NewsTaskSql
from lxml import etree
from utils.ossUtil import get_image, update_img
from configs import useragents
from filters.hashFilter import make_md5, hexists_md5_filter, hset_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import filter_emoji, format_info_list_str, filter_html_clear_format, \
    all_tag_replace_html, format_content_p, format_p_null
from utils.timeUtil import now_datetime, now_time, now_datetime_no


# 路透中文网 en
class CnReutersSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:cn_reuters'
        self.project_name = self.__class__.__name__
        self.web_name = "路透中文网"
        self.first_url = "https://cn.reuters.com"

    def parse(self):
        start_time = time.time()
        log.info(self.project_name + ' spider start... ')
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
                log.info(self.project_name + column_first + ' spider succ.')
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, source_id):
        if "专题" in column_first:
            if "https://cn.reuters.com/specialcoverage#china" in list_url:
                st_list, con_list = get_list_page_get(list_url, pc_headers, 'utf-8')
                if st_list:
                    html_list = etree.HTML(con_list)
                    els_list = html_list.xpath(
                        '//div[@class="gallery feature"]/h2/a')
                    for el_list in els_list:
                        try:
                            url_code_list = el_list.xpath("./@href")
                            url_code_list = "".join(url_code_list)
                        except Exception as e:
                            print(e)
                            url_code_list = ""
                        if "exclusive/specialcoverage" in url_code_list:
                            pass
                        else:
                            if url_code_list:
                                url = "https:" + url_code_list
                                st, con = get_list_page_get(url, pc_headers, 'utf-8')
                                if st:
                                    html = etree.HTML(con)
                                    els = html.xpath(
                                        '//div[@class="gallery feature"]/h2/a')
                                    for el in els:
                                        try:
                                            url_code = el.xpath("./@href")
                                            url_code = format_info_list_str(url_code)
                                        except Exception as e:
                                            print(e)
                                            url_code = ""
                                        try:
                                            title = el.xpath("./text()")
                                            title = "".join(title).strip()
                                        except Exception as e:
                                            print(e)
                                            title = ""
                                        if url_code and title:
                                            detail_url = url_code
                                            if "picture" in detail_url:
                                                pass
                                            else:
                                                md5_ = detail_url
                                                md5 = make_md5(md5_)
                                                if hexists_md5_filter(md5, self.mmd5):
                                                    pass
                                                    #log.info(self.project_name + " info data already exists!")
                                                else:
                                                    if not "video" in detail_url:
                                                        self.get_detail(title, detail_url, url_code, column_first,
                                                                        column_second, kw_site,
                                                                        pc_headers, md5, source_id)
                                                    else:
                                                        log.info("video url")
                                        else:
                                            pass
            else:
                pass
        else:
            st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
            if st:
                html = etree.HTML(con)
                els = html.xpath(
                    '//div[@class="feature"]/h3/a|//div[@class="topStory"]/h2/a|//div[@class="feature"]/h2/a|//div[@class="laundry-list gridPanel grid4"]/div/div[@class="moduleBody"]/ul/li/a')
                for el in els:
                    try:
                        url_code = el.xpath("./@href")
                        url_code = "".join(url_code)
                    except Exception as e:
                        print(e)
                        url_code = ""
                    try:
                        title = el.xpath("./text()")
                        title = "".join(title).strip()
                    except Exception as e:
                        print(e)
                        title = ""
                    if url_code and title:
                        detail_url = self.first_url + url_code
                        if "picture" in detail_url:
                            pass
                        else:
                            md5_ = detail_url
                            md5 = make_md5(md5_)
                            if hexists_md5_filter(md5, self.mmd5):
                                pass
                                #log.info(self.project_name + " info data already exists!")
                            else:
                                if not "video" in detail_url:
                                    self.get_detail(title, detail_url, url_code, column_first,
                                                    column_second, kw_site,
                                                    pc_headers, md5, source_id)
                                else:
                                    log.info("video url")
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
            format_info = format_info.replace("<p></p>", "").replace("<p>1 </p>", "").replace("<p>2 </p>", "").replace(
                "<p>3 </p>", "").replace("<p>4 </p>", "").replace("====", "").replace("\n\n", "\n").replace(
                "figcaption", "p").replace("h2", "p")
        return format_info

    def filter_REUTERS(self, caption):
        if "REUTERS" in caption:
            caption = caption.split("REUTERS")[0]
            return caption

    def get_detail(self, title, detail_url, url_code, column_first, column_second, kw_site,
                   pc_headers, md5, source_id):
        global con_html, content_text, image_text
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        cdnUrl = self.get_image_url(con)
        pub_time = self.get_pub_time(con)
        #pub_date_time = now_datetime_no()
        # if pub_time < pub_date_time:
        #     log.info("数据不是最新" + pub_time)
        #     hset_md5_filter(md5, self.mmd5)
        # else:
        if st:
            caption = self.get_caption(con)
            content = self.get_content_html(con)
            if not content:
                pass
            else:
                if caption and cdnUrl:
                    ii = get_image(cdnUrl)
                    r_i = update_img(ii)
                    img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                    content_text = img_ + content
                    content_text = self.format_repalce_space(content_text)
                    content_text = content_text.replace("<p><img", "<img")
                else:
                    content_text = content
                    content_text = self.format_repalce_space(content_text)
            content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>",
                                                                                                     "").replace(
                "<p>=</p>", "").replace("<p></p>", "")
            spider_time = now_datetime()
            # 采集时间
            body = content_text
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
                body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top,
                keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                CrawlTime,
                Hidden, file_name, file_path)
            # 入库mssql
            data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                              self.project_name)
        else:
            pass

    def get_caption(self, con):
        global image_text
        html = etree.HTML(con)
        try:
            image_text = html.xpath(
                '//article//button[@aria-label="image"]/figure//div[@role="img"][1]/@aria-label')
            caption = ''.join(image_text)
        except Exception as e:
            print(e)
            caption = ""
        return caption

    def get_pub_time(self, con):
        try:
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", con)
            pub_time = mat.groups()[0] + " " + now_time()
            # from utils.timeUtil import format_string_datetime
            # pub_time = format_string_datetime(pub_time)
        except Exception as e:
            pub_time = now_datetime()
        return pub_time

    def get_content_html(self, html):
        global content_text
        soup = BeautifulSoup(html, 'lxml')
        if 'class="ArticleBody-p-table-3vPxs"' in html:
            contents = []
            for divcon in soup.select('div.ArticleBody-p-table-3vPxs'):
                [s.extract() for s in divcon("div")]
                [s.extract() for s in divcon.find_all("div", {"class": "ArticleBody-byline-container-3H6dy"})]
                [s.extract() for s in divcon.find_all("div", {"class": "Attribution-attribution-Y5JpY"})]
                [s.extract() for s in divcon.find_all("div", {"class": "TrustBadge-trust-badge-20GM8"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = filter_html_clear_format(con)
                content_ = self.cn_replace_html(con)
                content_ = content_.replace("  ", '')
                content_ = format_content_p(content_)
                content_ = all_tag_replace_html(content_)
                contents.append(content_)
            content_text = "".join(contents)
            if "<p>相关报导" in content_text:
                content_text = content_text.split("<p>相关报导")[0]
        elif "ArticleBodyWrapper" in html:
            contents = []
            for divcon in soup.select('div.ArticleBodyWrapper'):
                [s.extract() for s in divcon("div")]
                [s.extract() for s in divcon.find_all("div", {"class": "ArticleBody-byline-container-3H6dy"})]
                [s.extract() for s in divcon.find_all("div", {"class": "Attribution-attribution-Y5JpY"})]
                [s.extract() for s in divcon.find_all("div", {"class": "TrustBadge-trust-badge-20GM8"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                con = filter_html_clear_format(con)
                content_ = self.cn_replace_html(con)
                content_ = content_.replace("  ", '')
                content_ = format_content_p(content_)
                content_ = all_tag_replace_html(content_)
                contents.append(content_)
            content_text = "".join(contents)
            if "<p>相关报导" in content_text:
                content_text = content_text.split("<p>相关报导")[0]
        else:
            content_text = ""
        content_text = format_p_null(content_text)
        return content_text

    def format_repalce_space(self, format_info):
        if "<p><p>" in format_info:
            format_info = format_info.replace("<p><p>", "<p>")
        return format_info

    def get_image_url(self, con):
        image_el = con.split('<script type="application/ld+json">')[1].split("</script>")[0]
        if image_el:
            try:
                image_json = json.loads(image_el)
                image_url = image_json.get('image')['url']
                if "https://s1.reutersmedia.net/resources_v2/images/rcom-default.png?w=800" in image_url:
                    image_url=''
            except Exception as e:
                print(e)
                image_url = ''
        else:
            image_url = ""
        return image_url


if __name__ == '__main__':
    news = CnReutersSpider()
    news.parse()
