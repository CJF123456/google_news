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
from lxml import etree
from configs import useragents
from bs4 import BeautifulSoup
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, get_spider_kw_mysql, data_insert_mssql
from utils.datautil import format_content_p, \
    all_tag_replace_html
from utils.timeUtil import now_datetime, now_time, format_string_datetime, now_datetime_no
from configs.dbconfig import NewsTaskSql
from utils.ossUtil import get_image, update_img


# 德国之声 已完结
class DwzhSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'google:dwzh'
        self.image_mmd5 = 'google:image:dwzh'
        self.project_name = self.__class__.__name__
        self.web_name = "德国之声"
        self.first_url = "https://www.dw.com"

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
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                }
                column_second = kw[2]
                kw_site = kw[3]
                column_first = kw[1]
                soucre_id = kw[4]
                self.parse_info(column_first, column_second, kw_site, list_url, pc_headers, soucre_id)
                log.info(self.project_name + column_first + ' spider succ...')
        end_time = time.time()
        log.info(
            self.project_name + ' spider succ' + now_datetime() + '.time consuming :%.2f' % (end_time - start_time))

    def parse_info(self, column_first, column_second, kw_site, list_url, pc_headers, soucre_id):
        st, con = get_list_page_get(list_url, pc_headers, 'utf-8')
        if st:
            html = etree.HTML(con)
            els = html.xpath(
                '//div[starts-with(@class,"news")]')
            for el in els:
                try:
                    url_code = el.xpath('./a/@href')
                    url_code = "".join(url_code)
                except Exception as e:
                    print(e)
                    url_code = ""
                try:
                    title = el.xpath('./a/h2/text()')
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
                        if "zh/" in detail_url and "/a-" in detail_url:
                            self.get_detail(title, detail_url, url_code, column_first, column_second, kw_site,
                                            pc_headers, md5, soucre_id)
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
                   pc_headers, md5, soucre_id):
        global pub_time
        st, con = get_list_page_get(detail_url, pc_headers, 'utf-8')
        image_url = self.get_image_url(con)
        if st:
            html = etree.HTML(con)
            pub_time=self.get_pub_time(html)
            pub_date_time = now_datetime_no()
            if pub_time < pub_date_time:
                log.info("数据不是最新" + pub_time)
            else:
                try:
                    img_text = html.xpath('//div[@class="picBox full"]/p/text()')
                    caption = "".join(img_text)
                except Exception as e:
                    print(e)
                    caption = ""
                content = self.get_content_html(con)
                if not content:
                    pass
                else:
                    if image_url and caption:
                        ii = get_image(image_url)
                        r_i = update_img(ii)
                        img_ = '<img src="' + r_i + '"/><p>' + caption + '</p>'
                        content_text = img_ + content
                        content_text = content_text.replace("<p><img", "<img")
                    else:
                        content_text = content
                    content_text = content_text.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>",
                                                                                                             "").replace(
                        "<p><p>", "<p>").replace("</p></p>", "</p>")
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
                    cn_boty = ""
                    column_id = ''
                    creator = 0
                    if_top = 0
                    source_id = soucre_id
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

    def get_pub_time(self, html):
        global pub_time
        try:
            pub_time_el = html.xpath('//ul[@class="smallList"]/li[1]/text()')[1]
            pub_el = "".join(pub_time_el)
            pub_year_ = pub_el.split(".")[2]
            pub_date_ = pub_el.split(".")[1]
            pub_time_ = pub_el.split(".")[0]
            pub_time = pub_year_ + "-" + pub_date_ + "-" + pub_time_ + " " + now_time()
            if "\n" in pub_time:
                pub_time = pub_time.replace("\n", "")
            pub_time = format_string_datetime(pub_time)
        except Exception as e:
            print(e)
            pub_time = now_datetime()
        return pub_time

    # TODO 内容格式化
    def get_content_html(self, html):
        global con, con_html, con_text, content_, content_texts, content_text, content
        soup = BeautifulSoup(html, 'lxml')
        content_s = []
        for divcon in soup.select('div#bodyContent div.col3'):
            [s.extract() for s in divcon('script')]
            [s.extract() for s in divcon('iframe')]
            [s.extract() for s in divcon("svg")]
            [s.extract() for s in divcon("h4")]
            [s.extract() for s in divcon("h1")]
            [s.extract() for s in divcon("ul")]
            [s.extract() for s in divcon.find_all("div", {"class": "col1"})]
            [s.extract() for s in divcon.find_all("div", {"class": "col3"})]
            [s.extract() for s in divcon.find_all("div", {"class": "col1 dim"})]
            [s.extract() for s in divcon.find_all("div", {"style": "clear:both;"})]
            [s.extract() for s in divcon.find_all("div", {"class": "standaloneWrap"})]
            [s.extract() for s in divcon.find_all("div", {"class": "picBox"})]
            [s.extract() for s in divcon.find_all("div", {"class": "col3 relatedContent"})]
            [s.extract() for s in divcon.find_all("div", {"class": "linkList intern"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            con = self.all_tag_replace_html(con)
            con_ = con.replace("\n", "").replace(" ", "").replace("<br/>", "</p><p>").replace("h2", "p")
            con_s = con_.split("</p><p>")
            content_texts = []
            for con_text in con_s:
                if con_text:
                    con_text.replace("<p>", "").replace("</p>", "")
                    con_text = format_content_p(con_text)
                    content_ = all_tag_replace_html(con_text)
                    content_texts.append(content_)
                else:
                    pass
            for con in content_texts:
                content_s.append(con)
            content = "".join(content_s)
            if "延伸阅读：" in content:
                content = content.split("延伸阅读：")[0]
            if "系列报道说明：" in content:
                content = content.split("系列报道说明：")[0]
            content = format_content_p(content)
            content = content.replace("<p><p>", "<p>").replace("</p></p>", "</p>").replace("<p></p>", "")
        return content


    # TODO 图片url
    def get_image_url(self, con):
        html = etree.HTML(con)
        try:
            image_url = html.xpath('//div[@class="picBox full"]/a/img/@src')[0]
            image_url = "".join(image_url)
            if "https://static.dw.com/" in image_url:
                image_url = image_url
        except Exception as e:
            # print(e)
            image_url = ""
        return image_url


    def all_tag_replace_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<!DOCTYPE>', '').replace('<div>', '').replace('</div>', '').replace(
                '<html>', '').replace('<title>', '').replace(
                '<body>', '').replace('<hr>', '').replace('<!--...-->',
                                                          '').replace('<abbr>',
                                                                      '').replace(
                '<address>', '').replace('<b>', '').replace('<bdi>', '').replace('<bdo>', '').replace('<blockquote>',
                                                                                                      '').replace(
                '<cite>', '').replace('<code>', '').replace('<del>', '').replace('<dfn>', '').replace('<em>',
                                                                                                      '').replace(
                '<i>',
                '').replace(
                '<ins>', '').replace('<kbd>', '').replace('<mark>', '').replace('<meter>', '').replace('<pre>',
                                                                                                       '').replace(
                '<progress>', '').replace('<q>', '').replace('<rp>', '').replace('<rt>', '').replace('<ruby>',
                                                                                                     '').replace(
                '<s>',
                '').replace(
                '<samp>', '').replace('<small>', '').replace('<strong>', '').replace('<sub>', '').replace('<sup>',
                                                                                                          '').replace(
                '<time>', '').replace('<u>', '').replace('<var>', '').replace('<wbr>', '').replace('<form>',
                                                                                                   '').replace(
                '<input>',
                '').replace(
                '<textarea>', '').replace('<button>', '').replace('<select>', '').replace('<optgroup>', '').replace(
                '<option>',
                '').replace(
                '<label>', '').replace('<fieldset>', '').replace('<legend>', '').replace('<datalist>', '').replace(
                '<output>',
                '').replace(
                '<iframe>', '').replace('<img>', '').replace('<map>', '').replace('<area>', '').replace('<canvas>',
                                                                                                        '').replace(
                '<figcaption>', '').replace('<figure>', '').replace('<audio>', '').replace('<source>', '').replace(
                '<track>',
                '').replace(
                '<video>', '').replace('<a>', '').replace('<link>', '').replace('<nav>', '').replace('<ul>',
                                                                                                     '').replace(
                '<ol>',
                '').replace(
                '<li>', '').replace('<dl>', '').replace('<dt>', '').replace('<dd>', '').replace('<menu>', '').replace(
                '<commend>',
                '').replace(
                '<table>', '').replace('<caption>', '').replace('<th>', '').replace('<tr>', '').replace('<td>',
                                                                                                        '').replace(
                '<thead>', '').replace('<tbody>', '').replace('<tfoot>', '').replace('<col>', '').replace('<colgroup>',
                                                                                                          '').replace(
                '<style>', '').replace('<span>', '').replace('<header>', '').replace('<footer>',
                                                                                     '').replace(
                '<section>', '').replace('<article>', '').replace('<aside>', '').replace('<details>', '').replace(
                '<dialog>',
                '').replace(
                '<summary>', '').replace('<head>', '').replace('<meta>', '').replace('<base>', '').replace('<script>',
                                                                                                           '').replace(
                '<noscript>', '').replace('<embed>', '').replace('<object>', '').replace('<param>', '').replace(
                '<main>',
                '').replace(
                '</html>', '').replace('</title>', '').replace('</body>', '').replace(
                '</br>', '').replace('</hr>', '').replace('</!--...-->', '').replace('</abbr>', '').replace(
                '</address>',
                '').replace(
                '</b>',
                '').replace(
                '</bdi>', '').replace('</bdo>', '').replace('</blockquote>', '').replace('</cite>', '').replace(
                '</code>',
                '').replace(
                '</del>', '').replace('</dfn>', '').replace('</em>', '').replace('</i>', '').replace('</ins>',
                                                                                                     '').replace(
                '</kbd>',
                '').replace(
                '</mark>', '').replace('</meter>', '').replace('</pre>', '').replace('</progress>', '').replace('</q>',
                                                                                                                '').replace(
                '</rp>', '').replace('</rt>', '').replace('</ruby>', '').replace('</s>', '').replace('</samp>',
                                                                                                     '').replace(
                '</small>', '').replace('</strong>', '').replace('</sub>', '').replace('</sup>', '').replace('</time>',
                                                                                                             '').replace(
                '</u>', '').replace('</var>', '').replace('</wbr>', '').replace('</form>', '').replace('</input>',
                                                                                                       '').replace(
                '</textarea>', '').replace('</button>', '').replace('</select>', '').replace('</optgroup>', '').replace(
                '</option>',
                '').replace(
                '</label>', '').replace('</fieldset>', '').replace('</legend>', '').replace('</datalist>', '').replace(
                '</output>',
                '').replace(
                '</iframe>', '').replace('</img>', '').replace('</map>', '').replace('</area>', '').replace('</canvas>',
                                                                                                            '').replace(
                '</figcaption>', '').replace('</figure>', '').replace('</audio>', '').replace('</source>', '').replace(
                '</track>',
                '').replace(
                '</video>', '').replace('</a>', '').replace('</link>', '').replace('</nav>', '').replace('</ul>',
                                                                                                         '').replace(
                '</ol>', '').replace('</li>', '').replace('</dl>', '').replace('</dt>', '').replace('</dd>',
                                                                                                    '').replace(
                '</menu>',
                '').replace(
                '</commend>', '').replace('</table>', '').replace('</caption>', '').replace('</th>', '').replace(
                '</tr>',
                '').replace(
                '</td>', '').replace('</thead>', '').replace('</tbody>', '').replace('</tfoot>', '').replace('</col>',
                                                                                                             '').replace(
                '</colgroup>', '').replace('</style>', '').replace('</span>', '').replace('</header>',
                                                                                          '').replace(
                '</footer>', '').replace('</section>', '').replace('</article>', '').replace('</aside>', '').replace(
                '</details>',
                '').replace(
                '</dialog>', '').replace('</summary>', '').replace('</head>', '').replace('</meta>', '').replace(
                '</base>',
                '').replace(
                '</script>', '').replace('</noscript>', '').replace('</embed>', '').replace('</object>', '').replace(
                '</param>',
                '').replace(
                '</main>', '').replace('<h1>', '').replace('<h3>', '').replace('<h4>', '').replace(
                '<h5>', '').replace('<h6>', '').replace('</h1>', '').replace('</h3>', '').replace(
                '</h4>', '').replace('</h5>',
                                     '').replace(
                '</h6>', '').replace("<!-->", "").replace("===", "")
        return format_info


if __name__ == '__main__':
    news = DwzhSpider()
    news.parse()
