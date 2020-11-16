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
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
from utils.translate import cat_to_chs
#世界日报--泰国  (完结) font导致的字体小，和span导致没空2格   在线上跑，不出数据？？？
#http://www.udnbkk.com
class g_UdnbkkNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:udnbkknews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "udnbkknews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'http://www.udnbkk.com',
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
            {"url": "http://www.udnbkk.com/portal.php?mod=list&catid=46&page=1", "name": "政治"},
            {"url": "http://www.udnbkk.com/portal.php?mod=list&catid=46&page=2", "name": "政治"},
        ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                html1 = etree.HTML(con)
                detail_urls = html1.xpath('//*[@class="bb_divt"]/a')
                for detail_url in detail_urls:
                    print(detail_url.get('href'))
                    title = detail_url.text
                    print(title)
                    url = detail_url.get('href')
                    if 'www.udnbkk.com/article-' in url:
                        # 详情页url
                        detail_url_code = str(format_info_int_re(url))
                        md5_ = title+'世界日报'
                        md5 = make_md5(md5_)
                        if hexists_md5_filter(md5, self.mmd5):
                            log.info(self.project_name + " info data already exists!")
                        else:
                            self.get_detail(url, md5, detail_url_code, title, name)
                        # exit(-1)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, detail_url, md5, detail_url_code, title, name):
        try:
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_time = soup.select('p.xg1')
                print(publish_time)
                for p_time in publish_time:
                    p_time = p_time.text
                    #print(p_time)
                    if ':' in p_time and '|' in p_time:
                        publish_time = p_time.split('|')[0].strip()
                        print(publish_time)
                        s_publish_time = publish_time.split(' ')[0]
                        e_publish_time = publish_time.split(' ')[1]+':00'
                        #print(self.is_date(s_publish_time))
                        if self.is_date(s_publish_time) == True:
                            if '视频：' not in str(soup):
                                today = now_datetime_no()
                                aa = caltime_datetime(today, s_publish_time)
                                print(aa)
                                if aa > -1:
                                    content = self.get_content_html(con2)
                                    #print(content)
                                    # 拿到contents中的img的src
                                    imgsrc = ''
                                    imgtext = ''#article_content > div:nth-child(1) > p:nth-child(1) > a > img
                                    for img in soup.select('#article_content >div >p >a >img'):
                                        if img.has_attr('src'):
                                            imgsrc = 'http://www.udnbkk.com/'+img.attrs['src']
                                    for imgtext in soup.select('#article_content >div >p >b'):
                                        imgtext = str(imgtext)
                                        #print(imgtext)
                                    #print(imgsrc)
                                    #print(imgtext)
                                    #print(imgsrc != '')
                                    if imgsrc != '':
                                        # 图片存在于文章头部
                                        ii = get_image(imgsrc)
                                        r_i = update_img(ii)
                                        #print(r_i)
                                        img_ = '<img src="{}"/>\n'.format(r_i)
                                        if imgtext != '':
                                            con_ = img_ + '<p>{}</p>'.format(imgtext) + '\n' + content
                                        else:
                                            con_ = img_ + '\n' + content
                                    else:
                                        con_ = con
                                    con_ = con_.replace('<span>', '<span style="font-family: DengXian; font-size: 38pt;">')
                                    #print(con_)
                                    spider_time = now_datetime()
                                    # 采集时间
                                    body = con_
                                    cn_title = ''.join(cat_to_chs(title))
                                    create_time = spider_time
                                    group_name = name
                                    title = title
                                    title = filter_emoji(title)
                                    update_time = spider_time
                                    website = detail_url
                                    Uri = detail_url
                                    Language = "zh"
                                    DocTime = s_publish_time+' '+e_publish_time
                                    CrawlTime = spider_time
                                    Hidden = 0  # 去确认
                                    file_name = ""
                                    file_path = ""
                                    classification = ""
                                    cn_boty = ''.join(cat_to_chs(con_))
                                    column_id = ''
                                    creator = ''
                                    if_top = ''
                                    source_id = 10374
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


    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', "<p>").replace('</div>', "</p>").replace('<p></p>', "").replace('<b>', '').replace('</b>', '')\
                .replace('<br>', '\n').replace('<br/>', '\n').replace('<p> </p>', "").strip().replace('\r', "").replace('\n', "")
            format_info = format_info.replace(" ", "").replace('<td>', '').replace('</td>', '').replace('<font>', '').replace('</font>', '')\
                .replace('</span>\n</p>', '</span></p>').replace('</p><p>', '</p>\n<p>')
            #print(con)
        return format_info

    # TODO 最后过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<p><p>', "").replace('</p></p>', "").replace('</p>\n</p>', "")\
                .replace('</span>', '</span>\n').replace('<p></p>', '').replace(' ', '').strip()
        return format_info

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result


    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('#article_content'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("p", {"style": "text-align: center;"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = self.filter_html(con)
            # #print(con)
            con = self.remove_tag(con, "a")
            # #print(con)
            con = self.filter_html_end(con)
            # #print(con)
        return con

if __name__ == '__main__':
    news = g_UdnbkkNewsSpider()
    news.parse()
