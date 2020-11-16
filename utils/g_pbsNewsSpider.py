import sys
sys.path.append('..')
import random
import re
import time
from bs4 import BeautifulSoup
from lxml import etree
from configs import useragents
from configs.dbconfig import NewsTaskSql
from configs.headers import pc_headers
from filters.hashFilter import make_md5, hexists_md5_filter
from mylog.mlog import log
from utils.ossUtil import get_image, update_img
from utils.common import get_list_page_get, data_insert_mssql
from utils.translate import translated_cn, en_con_to_cn_con
from utils.datautil import filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#泰国PBS
#https://www.thaipbsworld.com/

class g_PbsNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:pbsnews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "pbsnews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.thaipbsworld.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

    # 判断日期是否为合法输入，年月日的格式需要与上面对应，正确返回True，错误返回False，注意大小写。
    def is_date(self, str):
        try:
            time.strptime(str, "%Y-%m-%d")
            return True
        except:
            return False

    def parse(self):
        log.info('spider start...')
        urls = [
            {"url": "https://www.thaipbsworld.com/category/news/politics/", "name": "POLITICS"},
            {"url": "https://www.thaipbsworld.com/category/news/asean-headline/", "name": "ASEAN"}
        ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:#div.news-post.large-post.post > div.post-title
                soup = BeautifulSoup(con, 'lxml')
                details = soup.findAll(class_=re.compile("^news-post large-post post"))
                for detail in details:
                    # 详情页url
                    detail_url = detail.select('div.post-title > h2 > a')
                    d_url = detail_url[0].get('href')
                    print(d_url)
                    title = detail_url[0].text
                    print(title)
                    imgs = detail.select('div.post-gallery > div.thumb-wrap > img')
                    img = ''
                    print(len(imgs))
                    if len(imgs) == 1:
                        img = imgs[0].get('src')
                    img_texts = detail.select('div.post-gallery > div.content-caption')
                    img_text = ''
                    if len(img_texts) == 1:
                        img_text = img_texts[0].text
                    detail_url_code = ''
                    md5_ = title+'泰国怕不是'
                    md5 = make_md5(md5_)
                    datas = detail.select('div.post-title > ul > li:nth-child(1)')
                    s_epublish_time = ''
                    if len(datas) == 1:
                        display_dates = datas[0].text
                        dd = str(display_dates).strip().replace(' ', '')
                        print(dd)
                        if dd != '':
                            m_time, y_month = self.get_month_en(dd)
                            d_time = dd.split('{}'.format(y_month))[1].split(',')[0]
                            y_time = dd.split(',')[1].split('-')[0]
                            s_epublish_time = y_time + '-' + m_time + '-' + d_time
                    # if hexists_md5_filter(md5, self.mmd5):
                    #     log.info(self.project_name + " info data already exists!")
                    # else:
                    self.get_detail(d_url, md5, detail_url_code, name, title, img, img_text, s_epublish_time)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, detail_url, md5, detail_url_code, name, title, img, img_text, s_epublish_time):
        global ImageId
        #print(detail_url)
        st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st2:
            if self.is_date(s_epublish_time) == True:
                today = now_datetime_no()
                aa = caltime_datetime(today, s_epublish_time)
                print(aa)
                if aa > -5:
                    content = self.get_content_html(con2)
                    # #print(content)
                    img_ = ''
                    if img != '':
                        # 图片存在于文章头部
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
                    #print(con_)
                    spider_time = now_datetime()
                    s_spider_time = spider_time.split(' ')[1]
                    # 采集时间
                    body1 = cn_content.replace('<p> <p>', '<p>').replace('</p> </p>', '</p>') \
                        .replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('< / p>', '</p>').replace(
                        '<p> p>', '').replace('<p> >', '').replace('\n', '').replace('\t', '')
                    if img_ != '':
                        body = img_ + body1
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
                    column_id = ''
                    creator = ''
                    if_top = ''
                    source_id = 10378
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

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('div.the-content'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("blockquote", {"class": "twitter-tweet"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            print(con)
            con = self.filter_html(con)
            print(con)
            con = self.remove_tag(con, "a")
            print(con)
            content = self.filter_html_end(con)
            print(content)
        return content

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<img>', '').replace('<strong>', '<p>').replace('</strong>', '</p>').strip()\
                .replace('<ul>', '').replace('</ul>', '').replace('<li>', '<p>').replace('</li>', '</p>').replace('<h2>', '<p>').replace('</h2>', '</p>').replace('\r', '').replace('\n', '')
        return format_info

 # TODO 最后过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('\n', '').replace('     ', '').replace('<p>   </p>', '').replace('<p> </p>', '').replace('</p> <p>', '</p>\n<p>')
            format_info = str(format_info).strip()
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
        return month, y_month

if __name__ == '__main__':
    news = g_PbsNewsSpider()
    news.parse()
