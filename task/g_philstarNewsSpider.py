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
#菲律宾星报 完结
#https://www.philstar.com/

class g_PhilstarNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:philstarnews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "efenews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.philstar.com/',
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
            {"url": "https://www.philstar.com/headlines", "name": "headlines"},
            {"url": "https://www.philstar.com/opinion", "name": "opinion"},
            {"url": "https://www.philstar.com/nation", "name": "nation"},
            {"url": "https://www.philstar.com/world", "name": "world"},
            {"url": "https://www.philstar.com/business", "name": "business"},
        ]
        for u in urls:
            url = u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                soup = BeautifulSoup(con, 'lxml')
                detail_urls = soup.find_all("div", class_="TilesText spec")
                for url in detail_urls:
                    u = url.select('a')
                    detail_url = u[0].get('href')
                    #print(detail_url)
                    title = u[0].text
                    #print(title)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title+'菲律宾星报'
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                        if '31/2053484/metrobank-hikes-provisions-bad-loans-profit-grows' not in detail_url:
                            self.get_detail(detail_url, md5, detail_url_code, title, name)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, title, name):
        try:
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            # #print(con2)
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_time = ''
                if 'sports_article_credits' in con2:
                    display_dates = soup.select('div[id="sports_article_credits"]')[0].text
                    dd = str(display_dates).strip().replace(' ', '')
                    m_time, y_month = self.get_month_en(dd)
                    d_time = dd.split('{}'.format(y_month))[1].split(',')[0]
                    y_time = dd.split(',')[1].split('-')[0]
                    s_epublish_time = y_time+'-'+m_time+'-'+d_time
                    if dd != '':
                        ee_publish_time = ''
                        if 'am' in dd:
                            ee_publish_time = dd.split('-')[2].split('am')[0] + ':00' + ' AM'
                        elif 'pm' in display_dates:
                            ee_publish_time = dd.split('-')[2].split('pm')[0] + ':00' + ' PM'
                        e_publish_time = self.get_date_am_pm(ee_publish_time)
                else:
                    print('发布时间有问题')

                if self.is_date(s_epublish_time) == True and s_epublish_time != '':
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, s_epublish_time)
                        # #print(aa)
                        if aa > -1:
                            content = self.get_content_html(con2)
                            # #print(content)
                            img = soup.select('#sports_header_image > img')[0].get('src')
                            # #print(img)
                            if img != '':
                                # 图片存在于文章头部
                                img_text = soup.select('#sports_header_summary_content')[0].text
                                # #print(img_text)
                                ii = get_image(img)
                                r_i = update_img(ii)
                                # #print(r_i)
                                img_ = '<img src="{}"/>\n'.format(r_i)
                                cn_content = '<p>{}</p>\n'.format(img_text) + content
                                content = img_ + cn_content
                            #print(content)
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
                            DocTime = s_epublish_time+' '+e_publish_time
                            CrawlTime = spider_time
                            Hidden = 0  # 去确认
                            file_name = ""
                            file_path = ""
                            classification = ""
                            cn_boty = img_ + translated_cn(cn_content, 'en').replace('“ ', '"').replace('</ p>','</p>').strip().replace('\n', '').replace('\t', '')
                            column_id = ''
                            creator = ''
                            if_top = ''
                            source_id = 10356
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
        for divcon in soup.select('#sports_article_writeup'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"id": "related_block"})]
            [s.extract() for s in divcon.find_all("div", {"id": "inserted_instream"})]
            [s.extract() for s in divcon.find_all("div", {"id": "inserted_mrec"})]
            [s.extract() for s in divcon.find_all("a", {"target": "_blank"})]
            [s.extract() for s in divcon.find_all("div", {"class": "video-container"})]
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

    def get_date_am_pm(self, d):
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
            # #print("%02d:%02d:%02d" % (hh, mm, ss))
        else:
            time = d.strip("PM")
            time = time.split(':')
            hh = int(time[0])
            mm = int(time[1])
            ss = int(time[2])
            if hh != 12:
                hh = hh + 12
            # #print("%02d:%02d:%02d" % (hh, mm, ss))
        return "%02d:%02d:%02d" % (hh, mm, ss)

 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '')\
                .replace('\r', '').replace('\n', '').replace('<h2>', '<p>').replace('</h2>', '</p>')\
            .replace('<h3>', '').replace('</h3>', '').replace('READ: ', '').replace('|', '').replace('Related video:', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<a>', '').replace('</a>', '')\
                .replace('<strong>', '').replace('</strong>', '').replace('<iframe>', '')\
                .replace('</iframe>', '')\
                .replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        return format_info

    def get_month_en(self, month_info):
        global month
        global y_month
        if month_info:
            if "January" in month_info or "jan" in month_info:
                month = "01"
                y_month = "January"
            elif "February" in month_info or "feb" in month_info:
                month = "02"
                y_month = "February"
            elif "March" in month_info or "mar" in month_info:
                month = "03"
                y_month = "March"
            elif "April" in month_info or "apr" in month_info:
                month = "04"
                y_month = "April"
            elif "May" in month_info or "may" in month_info:
                month = "05"
                y_month = "May"
            elif "June" in month_info or "jun" in month_info:
                month = "06"
                y_month = "June"
            elif "July" in month_info or "jul" in month_info:
                month = "07"
                y_month = "July"
            elif "August" in month_info or "aug" in month_info:
                month = "08"
                y_month = "August"
            elif "September" in month_info or "sep" in month_info:
                month = "09"
                y_month = "September"
            elif "October" in month_info or "oct" in month_info:
                month = "10"
                y_month = "October"
            elif "November" in month_info or "nov" in month_info:
                month = "11"
                y_month = "November"
            elif "December" in month_info or "dec" in month_info:
                month = "12"
                y_month = "December"
        return month,y_month

    def get_date_am_pm(self, d):
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
            # #print("%02d:%02d:%02d" % (hh, mm, ss))
        else:
            time = d.strip("PM")
            time = time.split(':')
            hh = int(time[0])
            mm = int(time[1])
            ss = int(time[2])
            if hh != 12:
                hh = hh + 12
            # #print("%02d:%02d:%02d" % (hh, mm, ss))
        return "%02d:%02d:%02d" % (hh, mm, ss)

if __name__ == '__main__':
    news = g_PhilstarNewsSpider()
    news.parse()
