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
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
from utils.translate import cat_to_chs
#中国共产党网
#http://cpc.people.com.cn/   完结


class g_CpcNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:cpcnews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "cpcnews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'http://cpc.people.com.cn/',
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
            {"url": "http://cpc.people.com.cn/GB/64093/64094/index.html", "name": "高层动态"},
            {"url": "http://cpc.people.com.cn/GB/64093/117005/index.html", "name": "领导活动"},
            {"url": "http://renshi.people.com.cn/index1.html", "name": "人事"},
            {"url": "http://fanfu.people.com.cn/", "name": "反腐"},
            {"url": "http://theory.people.com.cn/GB/49150/index.html", "name": "理论"}
        ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'gbk')
            if st:
                # print(con)
                soup = BeautifulSoup(con, 'lxml')
                if 'theory.people' in url:
                    t1 = soup.select('div.fl > ul > li > a')
                    for t2 in t1:
                        # #print(t2)
                        title = t2.text
                        #print(title)
                        t3 = t2.get('href')
                        #print(t3)
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = title
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail('http://theory.people.com.cn' + t3, md5, detail_url_code, title, name)
                elif 'fanfu.people' in url:
                    t1 = soup.select('div.hdNews.clearfix > p > strong > a')
                    for t2 in t1:
                        t3 = t2.get('href')
                        title = t2.text
                        #print(t3, title)
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = title
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            if 'http://cpc.people.com.cn' not in t3:
                                self.get_detail('http://fanfu.people.com.cn' + t3, md5, detail_url_code, title, name)
                elif 'renshi.people' in url:
                    #抓任前公告
                    t1 = soup.select('#p2Ab_2 > div.hdNews.clearfix > p > strong > a')
                    for t2 in t1:
                        t3 = t2.get('href')
                        title = t2.text
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = detail_url_code
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail('http://renshi.people.com.cn' + t3, md5, detail_url_code, title, name)

                    # 抓人事任免
                    tt1 = soup.select('#p2Ab_1 > div.hdNews.clearfix > p > strong > a')
                    for t2 in tt1:
                        t3 = t2.get('href')
                        title = t2.text
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = detail_url_code
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail('http://renshi.people.com.cn' + t3, md5, detail_url_code, title, name)
                else:
                    t1 = soup.select('div.fl > ul > li > a')
                    for t2 in t1:
                        # #print(t2)
                        title = t2.text
                        #print(title)
                        t3 = t2.get('href')
                        #print(t3)
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = title+'中国共产党网'
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail('http://cpc.people.com.cn' + t3, md5, detail_url_code, title, name)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, url, md5, detail_url_code, title, name):
        try:
            global ImageId
            # print(url)
            st2, con2 = get_list_page_get(url, pc_headers, 'gbk')
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_time = soup.select('p.sou')
                if '年' in str(publish_time):
                    #print(publish_time)
                    s_publish_time = ''
                    e_publish_time = ''
                    if '来源：' in str(publish_time):
                        publish_time = str(publish_time[0].text).strip().split('来源：')[0].replace('年','-').replace('月','-').replace('日',' ')
                        #print(publish_time)
                        s_publish_time = publish_time.split(' ')[0]
                        e_publish_time = publish_time.strip() + ':00'
                    #print(s_publish_time, e_publish_time)
                    if self.is_date(s_publish_time) == True:
                        if '视频：' not in str(soup):
                            today = now_datetime_no()
                            aa = caltime_datetime(today, s_publish_time)
                            #print(aa)
                            if aa > -1:
                                content = self.get_content_html(con2)
                                # #print(content)
                                imgs = soup.find('div', class_='show_text').find_all('img')
                                # imgs = soup.select('div.show_text > table > tbody > tr > td > img')
                                img_ = ''
                                if len(imgs) > 0:
                                    if 'default' not in imgs[0]['src']:
                                        if 'http:' not in imgs[0]['src']:
                                            img_ = 'http://cpc.people.com.cn' + imgs[0]['src']
                                        else:
                                            img_ = imgs[0]['src']
                                #print(img_)
                                if img_ != '':
                                    img_ = '<img src="{}"/>\n'.format(img_)
                                    content = img_ + content
                                #print(content)
                                spider_time = now_datetime()
                                # 采集时间
                                body = content
                                title = title.replace(' ', '').strip()
                                cn_title = title
                                create_time = spider_time
                                group_name = name
                                title = filter_emoji(title)
                                update_time = spider_time
                                website = url
                                Uri = url
                                Language = "zh"
                                DocTime = e_publish_time
                                CrawlTime = spider_time
                                Hidden = 0  # 去确认
                                file_name = ""
                                file_path = ""
                                classification = ""
                                cn_boty = ''
                                column_id = ''
                                creator = ''
                                if_top = ''
                                source_id = 10372
                                summary = ''
                                summary = filter_emoji(summary)
                                UriId = detail_url_code
                                keyword = ''
                                info_val = (
                                body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name,
                                if_top, keyword, source_id, summary, title, update_time, website, Uri, UriId, Language,
                                DocTime, CrawlTime, Hidden, file_name, file_path)
                                # 入库mssql
                                data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                                  self.project_name)
                    else:
                        #print('发布日期不符合格式')
                        pass
        except Exception as e:
            print(e)
            pass


    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace(' ', '').replace('<img>', '').replace('<p></p>', '').strip().replace(
                '\r', '').replace('\n', '')
            if '更多报道' in format_info:
                format_info = format_info.split('更多报道')[0]
                if '<p><span><strong>' in format_info:
                    format_info = format_info.split('<p><span><strong>')[0]
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        if '<p><span>更多推荐' in format_info:
            format_info = format_info.split('<p><span>更多推荐')[0]
        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('.show_text'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"class": "otitle"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # print(con)
            con = self.filter_html(con)
            # print(con)
            con = con.replace(" ", "")
            # print(con)
            con = self.filter_html_end(con)
            # print(con)
        return con


if __name__ == '__main__':
    news = g_CpcNewsSpider()
    news.parse()
