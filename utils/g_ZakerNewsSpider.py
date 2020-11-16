import datetime
import sys
sys.path.append('..')
import random
import re
import time
from bs4 import BeautifulSoup
from configs import useragents
from configs.dbconfig import NewsTaskSql
from configs.headers import pc_headers
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.common import get_list_page_get, data_insert_mssql
from utils.ossUtil import get_image,update_img
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#ZAKER—北京-国内
#https://www.myzaker.com/

class g_ZakerNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:zaobaonews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "zaobaonews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.myzaker.com/',
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
            {"url": "https://www.myzaker.com/channel/10000", "name": "北京"},
            {"url": "https://www.myzaker.com/channel/1", "name": "国内"}
        ]
        for u in urls:
            url = u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                # print(con)
                soup = BeautifulSoup(con, 'lxml')
                t1 = soup.select('div.article-wrap > a')
                for t2 in t1:
                    if '//www.myzaker.com/article' in str(t2):
                        # print(t2)
                        t3 = t2.get('href')
                        #print(t3)
                        title = t2.get('title')
                        #print(title)
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = title
                        md5 = make_md5(md5_)
                        # if hexists_md5_filter(md5, self.mmd5):
                        #     log.info(self.project_name + " info data already exists!")
                        # else:
                        if 'article/5faa7fe932ce40a50b000051' not in t3:
                        # if 'article/5faa767432ce40b60b00002d' in t3:
                            self.get_detail('https:' + t3, md5, detail_url_code, title, name)

        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, title, name):
        try :
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            #print(con2)
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_times = soup.select('span.time')
                # print(publish_times)
                s_publish_time = ''
                if len(publish_times) == 1:
                    pp = publish_times[0].text
                    # print(pp)
                    if '分钟前' in pp:
                        dd = int(str(pp).replace('分钟前', ''))
                        publish_time = (
                            (datetime.datetime.now() - datetime.timedelta(minutes=dd)).strftime("%Y-%m-%d %H:%M:%S"))
                    elif '小时前' in pp:
                        dd = int(str(pp).replace('小时前', ''))
                        publish_time = (
                            (datetime.datetime.now() - datetime.timedelta(hours=dd)).strftime("%Y-%m-%d %H:%M:%S"))
                    elif '昨天' in pp:
                        publish_time = (
                            (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
                    elif '前天' in pp:
                        publish_time = (
                            (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
                    s_publish_time = publish_time.split(' ')[0]
                else:
                    print('发布时间有问题')

                if self.is_date(s_publish_time) == True and s_publish_time != '':
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, s_publish_time)
                        # print(aa)
                        if aa > -1:
                            content = self.get_content_html(con2)
                            #print(content)
                            if '<p>' != content:
                                find_ts = re.findall("<p>.*", content.replace('</p><p>', '</p>\n<p>').replace('<p>', '\n<p>'))
                                con_text = ''
                                for c in find_ts:
                                    if '△' not in c:
                                        con_text = con_text + c
                                find_ts2 = re.findall("<p>.*",con_text.replace('</p><p>', '</p>\n<p>').replace('<p>', '\n<p>'))
                                con_text2 = ''
                                for c in find_ts2:
                                    if '▲' not in c:
                                        con_text2 = con_text2 + c
                                #print(con_text2)
                                img_text = ''
                                i = 0
                                for f in find_ts2:
                                    if '△' in f:
                                        i = i + 1
                                        if i == 1:
                                            img_text = str(f).replace('<p>', '')
                                    elif '▲' in f:
                                        i = i + 1
                                        if i == 1:
                                            img_text = str(f).replace('<p>', '')
                                #print(img_text)
                                img = ''
                                img_ = ''
                                # img_text = ''
                                if 'opacity_0' in str(con2):
                                    imgs = soup.select('div.content_img_div.perview_img_div > img.lazy.opacity_0 ')
                                    if len(imgs) > 0:
                                        img = imgs[0]['data-original']
                                # print(img)
                                # print(img_text)
                                if img != '':
                                    # 图片存在于文章头部
                                    ii = get_image(img)
                                    r_i = update_img(ii)
                                    # print(r_i)
                                    img_ = '<img src="{}"/>\n'.format(r_i)
                                    if img_text != '':
                                        con_ = img_ + '<p>{}</p>'.format(img_text) + '\n' + con_text2
                                    else:
                                        con_ = img_ + '\n' + con_text2
                                else:
                                    con_ = con_text2
                                # print(content)
                                spider_time = now_datetime()
                                # 采集时间
                                body = con_
                                cn_title = str(title).strip()
                                create_time = spider_time
                                group_name = name
                                title = str(title).strip()
                                title = filter_emoji(title)
                                update_time = spider_time
                                website = detail_url
                                Uri = detail_url
                                Language = "zh"
                                DocTime = publish_time
                                CrawlTime = spider_time
                                Hidden = 0  # 去确认
                                file_name = ""
                                file_path = ""
                                classification = ""
                                cn_boty = ''
                                column_id = ''
                                creator = ''
                                if_top = ''
                                if '北京' in name:
                                    source_id = 10370
                                else:
                                    source_id = 10371
                                summary = ''
                                summary = filter_emoji(summary)
                                UriId = detail_url_code
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
                                print('视频数据')
                else:
                    # print('发布日期不符合格式')
                    pass
        except Exception as e:
            print(e)
            pass

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('#content'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"class": "iframe_video"})]
            [s.extract() for s in divcon.find_all("div", {"class": "video_container"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            #print(con)
            con = con.replace(" ", "")
            #print(con)
            con = self.filter_html(con)
            #print(con)
            con = self.remove_tag(con, "a")
            #print(con)
            con = self.filter_html_end(con)
            con = con.replace('<p><p>', '<p>').replace('<p><p>', '<p>').replace('</p></p>', '</p>')
            #print(con)
        return con


 # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '<p>').replace('</div>', '</p>').replace(' ', '').replace('<img>', '')\
                .replace('<strong>', '').replace('</strong>', '').replace('<p></p>', '<p>').replace('<p><p>', '<p>')\
                .replace('</p></p>', '</p>').replace('\r', '').replace('\n', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('\r', '').replace('\n', '').replace('<p></p>', '<p>').replace('<p><p>', '<p>')\
                .replace('</p></p>', '</p>').replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        return format_info.replace('\r', '').replace('\n', '')


if __name__ == '__main__':
    news = g_ZakerNewsSpider()
    # t3 = '//www.myzaker.com/article/5faa75d78e9f090cfe47dfc9'
    # md5 = ''
    # detail_url_code = '78'
    # title = '就在今天上午，中国创造一项新纪录'
    # name = '国内'
    # news.get_detail('https:' + t3, md5, detail_url_code, title, name)
    news.parse()
