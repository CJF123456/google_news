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
from utils.datautil import format_info_int_re, filter_emoji, all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#马尼拉时报  完结
#www.manilatimes.net

class g_ManilatimesNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:manilatimesnews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "manilatimesnews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.manilatimes.net/news/',
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
            {"url": "https://www.manilatimes.net/news/national/", "name": "nation"},
            {"url": "https://www.manilatimes.net/news/regions/", "name": "regions"},
            {"url": "https://www.manilatimes.net/opinion/", "name": "opnion"},
            {"url": "https://www.manilatimes.net/news/world/", "name": "world"},
            {"url": "https://www.manilatimes.net/supplements/", "name": "more"}
        ]
        for u in urls:
            url = u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                soup = BeautifulSoup(con, 'lxml')
                detail_urls = soup.find_all("h3", class_="entry-title td-module-title")
                for url in detail_urls:
                    u = url.select('a')
                    detail_url = u[0].get('href')
                    # print(detail_url)
                    title = u[0].get('title')
                    # #print(title)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title+'马尼拉时报'
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                    # if 'debt-balance-for-rolly-response/791050/' in detail_url:
                        self.get_detail(detail_url, md5, detail_url_code, title, name)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, title, name):
        try:
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            s_epublish_time = ''
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                if 'entry-date updated td-module-date' in con2:
                    display_dates = soup.select('time[class="entry-date updated td-module-date"]')[0].text
                    dd = str(display_dates).strip().replace(' ', '')
                    m_time, y_month = self.get_month_en(dd)
                    d_time = dd.split('{}'.format(y_month))[1].split(',')[0]
                    y_time = dd.split(',')[1].split('-')[0]
                    s_epublish_time = y_time+'-'+m_time+'-'+d_time
                else:
                    print('发布时间有问题')

                if self.is_date(s_epublish_time) == True and s_epublish_time != '':
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, s_epublish_time)
                        # #print(aa)
                        img_ = ''
                        if aa > -1:
                            content = self.get_content_html(con2)
                            #print(content)
                            imgs = soup.select('.wp-caption.aligncenter > img')
                            img = ''
                            if len(imgs) > 0:
                                img = imgs[0].get('data-src')
                            #print(img)
                            cn_content = ''
                            if img != '':
                                # 图片存在于文章头部
                                img_text = soup.select('.wp-caption-text')[0].text
                                #print(img_text)
                                ii = get_image(img)
                                r_i = update_img(ii)
                                # #print(r_i)
                                img_ = '<img src="{}"/>\n'.format(r_i)
                                if img_text != '':
                                    cn_content = '<p>{}</p>\n'.format(img_text) + content
                                else:
                                    cn_content = content
                            else:
                                cn_content = content
                            # print(cn_content)
                            spider_time = now_datetime()
                            s_spider_time = spider_time.split(' ')[1]
                            # 采集时间
                            body1 = cn_content.replace('<p> <p>', '<p>').replace('</p> </p>', '</p>')\
                                    .replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('< / p>', '</p>').replace('<p> p>', '').replace('<p> >', '').replace('<p>LONDON: </p>', '<p>LONDON: ').replace('<p>QUETTA </p>', '<p>QUETTA').replace('<p>PRISTINA: </p>', '<p>PRISTINA: ').replace('<p>   <p>', '<p>').replace(': </p>', ': ').replace('\n', '').replace('\t', '')
                            if img_ != '':
                                body = img_+body1
                            else:
                                body = body1
                            cn_title = translated_cn(str(title).strip(), 'en')
                            create_time = spider_time
                            group_name = name
                            title = str(title).strip()
                            title = filter_emoji(title)
                            update_time = spider_time
                            website = detail_url
                            Uri = detail_url
                            Language = "zh"
                            DocTime = s_epublish_time + ' ' + s_spider_time
                            CrawlTime = spider_time
                            Hidden = 0  # 去确认
                            file_name = ""
                            file_path = ""
                            classification = ""
                            if img_ != '':
                               cn_boty = img_ + en_con_to_cn_con(body1, 'en').replace('“ ', '"').replace('<hr />', '')
                            else:
                                cn_boty = img_ + en_con_to_cn_con(body1, 'en').replace('“ ', '"').replace('<hr />', '')
                            if '<p>   </p>' != cn_boty:
                                column_id = ''
                                creator = ''
                                if_top = ''
                                source_id = 10357
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
        for divcon in soup.findAll(class_=re.compile("^td_block_wrap tdb_single_content")):
            [s.extract() for s in divcon('script')]
            [s.extract() for s in divcon('style')]
            [s.extract() for s in divcon.find_all("div", {"class": "td-a-ad id_bottom_ad"})]
            [s.extract() for s in divcon.find_all("div", {"class": "td-a-ad id_inline_ad_content-horiz-center"})]
            [s.extract() for s in divcon.find_all("figure", {"class": "wp-caption aligncenter"})]
            [s.extract() for s in divcon.find_all("div", {"class": "td-a-ad id_inline_ad_content-horiz-center"})]
            [s.extract() for s in divcon.find_all("div", {"class": "td-gallery td-slide-on-2-columns"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
           #print(con)
            con = self.filter_html(con)
           #print(con)
            con = self.filter_html_end(con)
           #print(con)
            con = all_tag_replace_html(con)
           #print(con)
        return con

 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '<p>').replace('</div>', '</p>')\
                .replace('\r', '').replace('\n', '').replace('<h2>', '<p>').replace('</h2>', '</p>')\
            .replace('<h3>', '').replace('</h3>', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<a>', '').replace('</a>', '')\
                .replace('  ', '').replace('   ', '').replace('    ', '')\
                .replace('<strong>', '<p>').replace('</strong>', '</p>').replace('<iframe>', '')\
                .replace('</iframe>', '').replace('<p>  </p>', '').replace('<p> </p>', '')\
                .replace('<p></p>', "").replace('</p><p>', '</p>\n<p>').replace('\r', '').replace('\n', '')
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

if __name__ == '__main__':
    news = g_ManilatimesNewsSpider()
    # detail_url = 'https://www.manilatimes.net/2020/11/11/news/world/at-a-glance-world/fb-defaces-pages-of-ex-trump-ally/794536/'
    # md5 = ''
    # detail_url_code = '794536'
    # title = 'FB defaces pages of ex-Trump ally'
    # name = 'world'
    # news.get_detail(detail_url, md5, detail_url_code, title, name)
    news.parse()
