import sys
sys.path.append('..')
import datetime
import json
import random
import re
import time
from bs4 import BeautifulSoup
from configs import useragents
from configs.dbconfig import NewsTaskSql
from configs.headers import pc_headers
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.ossUtil import get_image,update_img
from utils.common import get_list_page_get, data_insert_mssql
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
from utils.translate import cat_to_chs
#苹果即时  11-12日是157   14日是159
#https://tw.appledaily.com/home/
#焦点接口太多，咱不采集
# {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/collections?query=%7B%22id%22%3A%22D272ZFMULZDQBOR77XY5PVPQMI%22%2C%22website%22%3A%22tw-appledaily%22%7D&d=150&_website=tw-appledaily", "name": "焦点"},
# {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/collections?query=%7B%22id%22%3A%2222H32QP4IFAEBOCODMXRDUNDP4%22%2C%22website%22%3A%22tw-appledaily%22%7D&d=150&_website=tw-appledaily", "name": "焦点"},
# {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/collections?query=%7B%22id%22%3A%22E7QDZ2JVMFHCVLFHRT6FTVXOLM%22%2C%22website%22%3A%22tw-appledaily%22%7D&d=150&_website=tw-appledaily", "name": "焦点"}

class g_AppledailyNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:appledailynews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "appledailynews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.chinaaid.net/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

    # 判断日期是否为合法输入，年月日的格式需要与上面对应，正确返回True，错误返回False，注意大小写。
    def is_date(self, date):
        try:
            time.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False

    def parse(self):
        log.info('spider start...')
        urls = [
            {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22taxonomy.tags.text.raw%253A%25E7%25BE%258E%25E4%25B8%25AD%25E5%258F%25B0%25E4%25BA%25A4%25E9%258B%2592%2520AND%2520type%253Dstory%2520%22%2C%22feedSize%22%3A%22100%22%2C%22sort%22%3A%22display_date%3Adesc%22%7D&filter=%7B_id%2Ccontent_elements%7B_id%2Ccanonical_url%2Ccreated_date%2Cdisplay_date%2Cheadlines%7Bbasic%7D%2Clast_updated_date%2Cpromo_items%7Bbasic%7B_id%2Ccaption%2Ccreated_date%2Cheight%2Clast_updated_date%2Cpromo_image%7Burl%7D%2Ctype%2Curl%2Cversion%2Cwidth%7D%2Ccanonical_website%2Ccredits%2Cdisplay_date%2Cfirst_publish_date%2Clocation%2Cpublish_date%2Crelated_content%2Csubtype%7D%2Crevision%2Csource%7Badditional_properties%2Cname%2Csource_id%2Csource_type%2Csystem%7D%2Ctaxonomy%7Bprimary_section%7B_id%2Cpath%7D%2Ctags%7Btext%7D%7D%2Ctype%2Cversion%2Cwebsite%2Cwebsite_url%7D%2Ccount%2Ctype%2Cversion%7D&d=159&_website=tw-appledaily", "name": "美中台交锋"},
            {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22taxonomy.primary_section._id%3A%5C%22%2Frealtime%2Finternational%5C%22%2BAND%2Btype%3Astory%2BAND%2Bdisplay_date%3A%5Bnow-48h%2Fh%2BTO%2Bnow%5D%22%2C%22feedSize%22%3A%22100%22%2C%22sort%22%3A%22display_date%3Adesc%22%7D&d=159&_website=tw-appledaily", "name": "国际"},
            {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22taxonomy.primary_section._id%3A%5C%22%2Frealtime%2Fpolitics%5C%22%2BAND%2Btype%3Astory%2BAND%2Bdisplay_date%3A%5Bnow-200h%2Fh%2BTO%2Bnow%5D%22%2C%22feedSize%22%3A%22100%22%2C%22sort%22%3A%22display_date%3Adesc%22%7D&d=159&_website=tw-appledaily", "name": "政治"},
            {"url": "https://tw.appledaily.com/pf/api/v3/content/fetch/content-by-tag?query=%7B%22size%22%3A50%2C%22tag%22%3A%22mt_%E5%B0%88%E9%A1%8C%20AND%20type%3Dstory%22%2C%22website%22%3A%22tw-appledaily%22%7D&filter=%7B_id%2Ccontent_elements%7B_id%2Ccanonical_url%2Ccreated_date%2Cdisplay_date%2Cheadlines%7Bbasic%7D%2Clast_updated_date%2Cpromo_items%7Bbasic%7B_id%2Ccaption%2Ccreated_date%2Cheight%2Clast_updated_date%2Cpromo_image%7Burl%7D%2Ctype%2Curl%2Cversion%2Cwidth%7D%2Ccanonical_website%2Ccredits%2Cdisplay_date%2Cfirst_publish_date%2Clocation%2Cpublish_date%2Crelated_content%2Csubtype%7D%2Crevision%2Csource%7Badditional_properties%2Cname%2Csource_id%2Csource_type%2Csystem%7D%2Ctaxonomy%7Bprimary_section%7B_id%2Cpath%7D%2Ctags%7Btext%7D%7D%2Ctype%2Cversion%2Cwebsite%2Cwebsite_url%7D%2Ccount%2Ctype%2Cversion%7D&d=159&_website=tw-appledaily", "name": "专题"}
            ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                # #print(con)
                details = json.loads(con)
                for detail_url in details['content_elements']:
                    #print(detail_url)
                    try:
                        d_url = detail_url['website_url']
                        display_date = detail_url['display_date']
                        title = detail_url['headlines']['basic']
                        if 'promo_image' in str(detail_url['promo_items']['basic']):
                            caption = ''
                            img = detail_url['promo_items']['basic']['promo_image']['url']
                        elif 'caption' in str(detail_url['promo_items']['basic']):
                            caption = detail_url['promo_items']['basic']['caption']
                            img = detail_url['promo_items']['basic']['url']
                        elif 'subtitle' in str(detail_url['promo_items']['basic']):
                            caption = ''
                            img = detail_url['promo_items']['basic']['url']
                        url = 'https://tw.appledaily.com'+d_url
                        #print(url, display_date, title, caption, img)
                        #print(len(display_date))
                        if len(display_date) == 24:
                            UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
                        else:
                            UTC_FORMAT = "%Y-%m-%dT%H:%M:%fZ"
                        utc_time = datetime.datetime.strptime(display_date, UTC_FORMAT)
                        local_time = utc_time + datetime.timedelta(hours=8)
                        dc_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
                        #print(dc_time)  # 2017-07-28 16:28:47.776000
                        # 详情页url
                        detail_url_code = str(format_info_int_re(url))
                        md5_ = title+'苹果即时'
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail(url, dc_time, title, caption, img, md5, detail_url_code, name)
                        #     exit(-1)
                    except Exception as e:
                        print(e)
                        pass
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, url, display_date, title, imgtext, imgsrc, md5, detail_url_code, name):
        try:
            global ImageId
            st2, con2 = get_list_page_get(url, pc_headers, 'utf-8')
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                s_publish_time =display_date.split(' ')[0]
                e_publish_time = display_date.split(' ')[1]
                if self.is_date(s_publish_time) == True:
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, s_publish_time)
                        #print(aa)
                        if aa > -1:
                            content = self.get_content_html(con2)
                            # #print(content)
                            # 拿到contents中的img的src和 title
                            if imgsrc != '':
                                # 图片存在于文章头部
                                ii = get_image(imgsrc)
                                r_i = update_img(ii)
                                #print(r_i)
                                img_ = '<img src="{}"/>\n'.format(r_i)
                                if imgtext != '':
                                    con_ = img_ + '<p>{}</p>'.format(imgtext) + '\n' + content
                                else:
                                    con_ = img_ + content
                            else:
                                con_ = content
                            #print(imgsrc)
                            #print(imgtext)
                            #print(con_)
                            spider_time = now_datetime()
                            s_spider_time = spider_time.split(' ')[1]
                            # 采集时间
                            body = con_
                            cn_title = ''.join(cat_to_chs(title))
                            create_time = spider_time
                            group_name = name
                            title = title
                            title = filter_emoji(title)
                            update_time = spider_time
                            website = url
                            Uri = url
                            Language = "zh"
                            DocTime = s_publish_time + ' ' + e_publish_time
                            CrawlTime = spider_time
                            Hidden = 0  # 去确认
                            file_name = ""
                            file_path = ""
                            classification = ""
                            cn_boty = ''.join(cat_to_chs(con_))
                            column_id = ''
                            creator = ''
                            if_top = ''
                            source_id = 10379
                            summary = ''
                            summary = filter_emoji(summary)
                            UriId = detail_url_code
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
                    #print('发布日期不符合格式')
                    pass
        except Exception as e:
            print(e)
            pass

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<b>', '').replace('</b>', '').replace('<h3>', '<p>').replace('</h3>','</p>').replace("</p><p>", "</p>\n<p>") \
                .replace('<p>跟上國際脈動，快來按讚</p>', "").replace('<p>相關新聞：</p>', "").replace('相關新聞：', '') \
                .replace('<p>以下是：</p>', "")
            format_info = format_info.split('<p>來臉書按讚，掌握國際事不間斷！</p>')[0]
        return format_info

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<section>', "").replace('</section>', "")\
                .replace('<p> </p>', '').strip().replace('\r', '').replace('\n', '').replace('<mark>', '').replace('</mark>', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>")
        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('#articleBody'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"class": "box--position-absolute-center ont-size--16 box--display-flex flex--wrap tags-container"})]
            [s.extract() for s in divcon.find_all("p", {"class": "text--desktop text--mobile article-text-size_md  tw-max_width"})]
            [s.extract() for s in divcon.find_all("div", {"class": "box--pad-vertical-lg"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = self.filter_html(con)
            # #print(con)
            con = con.replace(" ", "")
            # #print(con)
            con = self.remove_tag(con, "a")
            # #print(con)
            content = self.filter_html_end(con)
            # #print(content)
        return content

if __name__ == '__main__':
    news = g_AppledailyNewsSpider()
    news.parse()
