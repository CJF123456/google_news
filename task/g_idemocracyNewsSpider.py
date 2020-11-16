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
#华人民主书院   完结  没有把title作为唯一
# #https://idemocracy.asia/


class g_IdemocracyNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:idemocracynews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "idemocracynews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://idemocracy.asia/',
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
                {"url": "https://idemocracy.asia/vision", "name": "观点"},
        ]
        for url in urls:
            st, con = get_list_page_get(url['url'], pc_headers, 'utf-8')
            name = url['name']
            if st:
                soup = BeautifulSoup(con, 'lxml')
                t1 = soup.find_all('a')
                href_lists = []
                for t2 in t1:
                    t3 = t2.get('href')
                    # #print(t3)
                    if 'vision/' in t3:
                        # 详情页url
                        detail_url_code = str(format_info_int_re(t3))
                        md5_ = detail_url_code+'华人民主书院'
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            if '276' not in t3:  #276十八大的有问题，手动编辑的
                                self.get_detail('https://idemocracy.asia' + t3, md5, detail_url_code, name)

        log.info(self.project_name + ' spider succ.')

    def get_detail(self, detail_url, md5, detail_url_code, name):
        global ImageId
        #print(detail_url)
        st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st2:
            soup = BeautifulSoup(con2, 'lxml')
            publish_time = soup.select('span.field-content > span.date-display-single')
            #print(publish_time[0].text)
            if self.is_date(publish_time[0].text) == True:
                today = now_datetime_no()
                aa = caltime_datetime(today, publish_time[0].text)
                #print(aa)
                if aa > -1:
                    title = soup.select('h1.page-title')[0].text
                    #print(title)
                    for divcon in soup.select('.views-field.views-field-body'):
                        [s.extract() for s in divcon('figure')]
                        locu_content = divcon.prettify()
                        con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                        # #print(con)
                        con = self.filter_html(con)
                        # #print(con)
                        content_ = self.remove_tag(con, "a")
                        content = filter_emoji(content_)
                        content = self.filter_end(content)
                        #print(content)
                        spider_time = now_datetime()
                        s_spider_time = spider_time.split(' ')[1]
                        # 采集时间
                        body = content
                        cn_title = ''.join(cat_to_chs(title))
                        create_time = spider_time
                        group_name = name
                        title = title
                        # title = filter_emoji(title)
                        update_time = spider_time
                        website = detail_url
                        Uri = detail_url
                        Language = "zh"
                        DocTime = publish_time[0].text + ' '+s_spider_time
                        CrawlTime = spider_time
                        Hidden = 0  # 去确认
                        file_name = ""
                        file_path = ""
                        classification = ""
                        cn_boty = ''.join(cat_to_chs(content))
                        column_id = ''
                        creator = ''
                        if_top = ''
                        source_id = 10353
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

    # TODO 去掉strong
    def remove_strong(self, con_):
        if "<strong>" in con_:
            results = re.sub(r'<(strong)', "", con_)
            content = results
            if "<p></p>" in content:
                content = content.replace("<p></p>", "").lstrip()
        elif "<img>" in con_:
            results = re.sub(r'<img.*）', "", con_)
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

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<ul>', '').replace('</ul>', '')\
                .replace('<b><a>', '').replace('</a></b>', '').replace('<b>', '').replace('</b>', '')\
                .replace('<strong>','').replace('</strong>','').replace('<li>', '').replace('</li>', '').replace('<b></b>', '')\
                .replace('<p> </p>', '').strip().replace('\r', '').replace('\n', '').replace('+<!-->3+<!-->2', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>").replace(' ','')
            format_info = format_info.replace('<span>', '<span style="font-family: DengXian; font-size: 38pt;">')
        return format_info

    def filter_end(self, content):
        if '（文章純屬作者個人觀點，不代表華人民主書院立場。）'in content:
            content =content.replace('（文章純屬作者個人觀點，不代表華人民主書院立場。）', '<p>（文章純屬作者個人觀點，不代表華人民主書院立場。）</p>')
        if '發表於' in content:
            content = content.replace('發表於', '<p>發表於</p>')
        content = content.replace('<h3>', '').replace('</h3>', '').replace('<wbr/>', '').replace('<p></p>', '').replace("</p><p>", "</p>\n<p>")
        return content

if __name__ == '__main__':
    news = g_IdemocracyNewsSpider()
    news.parse()
