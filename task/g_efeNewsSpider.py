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
from utils.translate import translated_cn, en_con_to_cn_con
from utils.ossUtil import get_image,update_img
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#西班牙埃菲社（EFE） 完结
#https://www.efe.com/efe/english/4

class g_EfeNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:efenews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "efenews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.efe.com/efe/',
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
            {"url": "https://www.efe.com/efe/english/world/50000262", "name": "world"},
            {"url": "https://www.efe.com/efe/english/business/50000265", "name": "business"}
        ]
        for u in urls:
            url = u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                soup = BeautifulSoup(con, 'lxml')
                detail_urls = soup.find_all("li", class_="importante")
                for url in detail_urls:
                    u = url.select('article > a')
                    uu = u[0].get('href')
                    detail_url = 'https://www.efe.com' + uu
                    # #print(detail_url)
                    title = url.select('div.caption')[0].contents[2].strip()
                    # #print(title)
                    img = 'https:'+ url.select('img.lazy')[0].get('data-original')
                    # #print(img)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title+'西班牙埃菲社'
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        self.get_detail(detail_url, md5, detail_url_code, title, name, img)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, title, name, img):
        try:
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            # #print(con2)
            s_epublish_time = ''
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_time = ''
                if 'dateModified' in con2:
                    display_dates = soup.select('time[itemprop="dateModified"]')[0].get('datetime')
                    #print(display_dates)
                    if display_dates != '':
                        # #print(len(display_dates))
                        if len(display_dates) == 24:
                            UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
                        else:
                            UTC_FORMAT = "%Y-%m-%dT%H:%M:%fZ"
                        utc_time = datetime.datetime.strptime(display_dates, UTC_FORMAT)
                        local_time = utc_time + datetime.timedelta(hours=8)
                        publish_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
                        # #print(publish_time)  # 2017-07-28 16:28:47.776000
                        s_epublish_time = publish_time.split(' ')[0]
                else:
                    print('发布时间有问题')

                if self.is_date(s_epublish_time) == True and s_epublish_time != '':
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, s_epublish_time)
                        #print(aa)
                        if aa > -1:
                            content = self.get_content_html(con2)
                            # #print(content)
                            if img != '':
                                # 图片存在于文章头部
                                img_text = soup.select('p[itemprop="description name caption"]')[0].text
                                #print(img_text)
                                ii = get_image(img)
                                r_i = update_img(ii)
                                # #print(r_i)
                                img_ = '<img src="{}"/>\n'.format(r_i)
                                cn_content = '<p>{}</p>\n'.format(img_text) + content
                                content = img_ + cn_content
                            # #print(content)
                            spider_time = now_datetime()
                            # 采集时间
                            body = content.replace('\n', '').replace('\t', '')
                            cn_title = translated_cn(str(title).strip(), 'en')
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
                            cn_boty = img_ + translated_cn(cn_content, 'en').replace('“ ', '"').replace('</ p>', '</p>').strip().replace('\n', '').replace('\t','')
                            column_id = ''
                            creator = ''
                            if_top = ''
                            source_id = 10386
                            summary = ''
                            summary = filter_emoji(summary)
                            UriId = detail_url_code
                            keyword = ''
                            info_val = (body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top,
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

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('#div_texto'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("section", {"id": "imu"})]
            [s.extract() for s in divcon.find_all("script", {"type": "text/javascript"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = self.filter_html(con)
            # #print(con)
            con = self.filter_html_end(con)
            # #print(con)
        return con

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result


 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '')\
                .replace('\r', '').replace('\n', '')\
            .replace('<h3>', '').replace('</h3>', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<a>', '').replace('</a>', '').replace('<strong>', '').replace('</strong>', '')\
                .replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        return format_info

    def get_date_am_pm(self, d):
        #print(d)
        if d.find("AM") >= 0:
            time = d.strip("AM")
            if time == "12:00:00":
                time = "00:00:00"
            time = time.split(':')
            hh = int(time[0])
            mm = int(time[1])
            ss = int(time[2])
            if hh == 12 and (mm > 0 or ss > 0):
                hh = 0
            #print("%02d:%02d:%02d" % (hh, mm, ss))
        else:
            time = d.strip("PM")
            time = time.split(':')
            hh = int(time[0])
            mm = int(time[1])
            ss = int(time[2])
            if hh != 12:
                hh = hh + 12
            #print("%02d:%02d:%02d" % (hh, mm, ss))
        return "%02d:%02d:%02d" % (hh, mm, ss)

if __name__ == '__main__':
    news = g_EfeNewsSpider()
    news.parse()
