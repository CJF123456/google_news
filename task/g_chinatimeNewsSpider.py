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
from utils.datautil import format_info_int_re,filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#中时电子报  完结
#https://www.chinatimes.com/?chdtv
from utils.translate import cat_to_chs

class g_ChinatimeNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:chinatimenews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "chinatimenews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.chinatimes.com/chinese/',
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
            {"url": "https://www.chinatimes.com/politic/total?page=2&chdtv", "name": "政治"},
            {"url": "https://www.chinatimes.com/opinion/total?page=1&chdtv", "name": "言论"},
            {"url": "https://www.chinatimes.com/money/total?page=1&chdtv", "name": "财经"},
            {"url": "https://www.chinatimes.com/world/total?page=1&chdtv", "name": "军事"},
            {"url": "https://www.chinatimes.com/armament/total?page=1&chdtv", "name": "两岸"},
            {"url": "https://www.chinatimes.com/chinese/total?page=1&chdtv", "name": "国际"}
        ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                soup = BeautifulSoup(con, 'lxml')
                t1 = soup.select('div.col > h3.title > a')
                for t2 in t1:
                    #print(t2)
                    title = t2.text
                    #print(title)
                    t3 = t2.get('href')
                    #print(t3)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(t3))
                    md5_ = title+'中时电子报'
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        self.get_detail('https://www.chinatimes.com' + t3+'?chdtv', md5, detail_url_code, title, name)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, url, md5, detail_url_code, title, name):
        try:
            global ImageId
            #print(url)
            st2, con2 = get_list_page_get(url, pc_headers, 'utf-8')
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                s_publish_time = soup.select('div.meta-info-wrapper >div.meta-info > time> span.date')
                if '/' in str(s_publish_time[0]):
                    s_publish_time = s_publish_time[0].text.replace('/', '-')
                    #print(s_publish_time)
                    e_publish_time = soup.select('div.meta-info-wrapper > div.meta-info > time> span.hour')
                    e_publish_time = e_publish_time[0].text+':00'
                    #print(e_publish_time)
                    if self.is_date(s_publish_time) == True:
                        if '视频：' not in str(soup):
                            today = now_datetime_no()
                            aa = caltime_datetime(today, s_publish_time)
                            #print(aa)
                            if aa > -1:
                                content = self.get_content_html(con2)
                                # #print(content)
                                soup2 = BeautifulSoup(con2, 'lxml')
                                imgs = soup2.select('div.main-figure > figure > div.photo-container > img')
                                img1 = self.get_img(imgs)
                                # #print(img1)
                                content = img1 + '\n' + content
                                if img1 == '':
                                    imgs = soup2.select('div.article-body > figure > div.photo-container > img')
                                    img1 = self.get_img(imgs)
                                    # #print(img1)
                                    content = img1 + '\n' + content
                                    # #print(content)
                                #print(content)
                                spider_time = now_datetime()
                                s_spider_time = spider_time.split(' ')[1]
                                # 采集时间
                                body = content
                                title = title.replace(' ', '').strip()
                                cn_title = ''.join(cat_to_chs(title))
                                create_time = spider_time
                                group_name = name
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
                                cn_boty = ''.join(cat_to_chs(content))
                                column_id = ''
                                creator = ''
                                if_top = ''
                                source_id = 10390
                                summary = ''
                                summary = filter_emoji(summary)
                                UriId = detail_url_code
                                keyword = ''
                                info_val = (body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name,if_top,keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime, CrawlTime,Hidden, file_name, file_path)
                                # 入库mssql
                                data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                                  self.project_name)
                    else:
                        #print('发布日期不符合格式')
                        pass
        except Exception as e:
            print(e)
            pass

    def get_img(self, imgs):
        con_ = ''
        for i in imgs:
            img = i.get('src')
            alt = i.get('alt')
            if img != '':
                # 图片存在于文章头部
                img_ = '<img src="{}"/>\n'.format(img)
                if alt != '':
                    con_ = img_ + '<p>{}</p>'.format(alt)
                else:
                    con_ = img_
        return con_

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '')\
                .replace('<blockquote>', '').replace('</blockquote>', '')\
                .replace('<iframe>', '').replace('</iframe>', '').replace(' ', '').replace('<p></p>', '').strip().replace(
                '\r', '').replace('\n', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        if '……更多內容請點閱本視頻節目觀看分享！' in format_info:
            format_info = format_info.replace('……更多內容請點閱本視頻節目觀看分享！', '')
        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('.article-body'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"class": "ad"})]
            [s.extract() for s in divcon.find_all("div", {"class": "promote-word"})]
            [s.extract() for s in divcon.find_all("div", {"class": "article-source"})]
            [s.extract() for s in divcon.find_all("div", {"class": "ad text-wrap-around"})]
            [s.extract() for s in divcon.find_all("div", {"class": "article-hash-tag"})]
            [s.extract() for s in divcon.find_all("div", {"class": "custom-embeded-code"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = self.filter_html(con)
            # #print(con)
            con = con.replace(" ", "")
            # #print(con)
            con = self.filter_html_end(con)
            # #print(con)
        return con


if __name__ == '__main__':
    news = g_ChinatimeNewsSpider()
    news.parse()
