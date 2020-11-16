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
from utils.datautil import format_info_int_re,filter_emoji, all_tag_replace_html
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#自由亚洲电台  完结  (存在字体小(br没有标签做不了)，br引起没空2格的问题)  没有把title作为唯一
#https://www.rfa.org/mandarin/

class g_RfaNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:rfanews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "rfanews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.rfa.org/mandarin/',
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
        log.info('spider start...')                # "https://www.rfa.org/mandarin/ytbdzhuantixilie",
        urls = [
            {"url": "https://www.rfa.org/mandarin/yataibaodao", "name": "亚太报道"},
            {"url": "https://www.rfa.org/mandarin/Xinwen", "name": "快讯"},
            {"url": "https://www.rfa.org/mandarin/zhuanlan", "name": "专栏"},
            {"url": "https://www.rfa.org/mandarin/pinglun", "name": "评论"}
        ]
        for url in urls:
            name = url['name']
            url = url['url']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                html1 = etree.HTML(con)
                if 'Xinwen' in url:
                    detail_urls = html1.xpath('//*[@id="sectioncontent"]/div/h2/a/@href')
                else:
                    detail_urls = html1.xpath('//*[@id="sectioncontent"]/div/div/a/@href')
                for detail_url in detail_urls:
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = detail_url_code+'自由亚洲电台'
                    md5 = make_md5(md5_)
                    # if hexists_md5_filter(md5, self.mmd5):
                    #     log.info(self.project_name + " info data already exists!")
                    # else:
                    self.get_detail(detail_url, md5, detail_url_code, name)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, detail_url, md5, detail_url_code, name):
        global ImageId
        #print(detail_url)
        st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
        if st2:
            soup = BeautifulSoup(con2, 'lxml')
            publish_time = soup.select('#story_date')
            #print(publish_time[0].text)
            if self.is_date(publish_time[0].text) == True:
                today = now_datetime_no()
                aa = caltime_datetime(today, publish_time[0].text)
                #print(aa)
                if aa > -2:
                    html1 = etree.HTML(con2)
                    title = html1.xpath('//*[@id="storypagemaincol"]/h1')[0].text
                    #print(title)
                    # 拿到contents中的img的src和 title
                    imgsrcs = html1.xpath('//*[@id="headerimg"]/img/@src')
                    imgsrc = ''
                    #print(len(imgsrcs))
                    if len(imgsrcs) > 0:
                        imgsrc = html1.xpath('//*[@id="headerimg"]/img/@src')[0]
                    #print(imgsrc)
                    imgtext = ''
                    imgtexts = html1.xpath('//*[@id="headerimg"]/img/@title')
                    if len(imgtexts) > 0:
                        imgtext = html1.xpath('//*[@id="headerimg"]/img/@title')[0]
                    #print(imgtext)

                    content = self.get_content_html(con2)
                    # #print(content)
                    if (len(imgsrcs) == 1):
                        #图片存在于文章头部
                        ii = get_image(imgsrc)
                        r_i = update_img(ii)
                        #print(r_i)
                        img_ = '<img src="{}"/>\n'.format(r_i)
                        if imgtext != '':
                            con_ = img_ + '<p>{}</p>'.format(imgtext) + '\n' + content
                        else:
                            con_ = img_ + '\n' + content
                    else:
                        con_ = content
                    #print(con_)
                    spider_time = now_datetime()
                    s_spider_time = spider_time.split(' ')[1]
                    # 采集时间
                    body = con_
                    cn_title = title
                    create_time = spider_time
                    group_name = name
                    title = title
                    title = filter_emoji(title)
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
                    cn_boty = ''
                    column_id = ''
                    creator = ''
                    if_top = ''
                    source_id = 10352
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
        for divcon in soup.select('#storytext'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("div", {"class": "image-inline captioned"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = con.replace(" ", "")
            #print(con)
            con = self.filter_html(con)
            #print(con)
            con = self.remove_tag(con, "a")
            #print(con)
            content = self.filter_html_end(con)
            #print(content)
            content = content.replace(" ", "")
            #print(content)
            content = self.filter_html_end_end(content)
            #print(content)
            content = filter_emoji(content)
            #print(content)
        return content

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<img>', '').replace('<b></b>', '').replace('<div>', '<p>').replace('</div>', '</p>').strip().replace('\r', '').replace('\n','')
            format_info = format_info.replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('<p></p>', '')
            format_info = format_info.replace("</p> <p>", "</p>\n<p>")
            format_info = format_info.replace("</p><p>", "</p>\n<p>")
        return format_info

 # TODO 最后过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('\n', '').replace('<b></b>', '').replace('<b>', '<p>').replace('</b>', '<p>').replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('<p></p>', '').replace("</p><p>", "</p>\n<p>")
            format_info = str(format_info).strip()
        return format_info

# TODO 最后过滤
    def filter_html_end_end(self, format_info):
        if format_info:
            format_info = format_info.replace('\n', '').replace('<b></b>', '').replace('<b>', '<p>').replace('</b>', '<p>').replace('<br/><br/>', '<p>').replace('<br/>', '</p><p>').replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('<p></p>', '').replace("</p><p>", "</p>\n<p>")
            format_info = str(format_info).strip()
        return format_info

if __name__ == '__main__':
    news = g_RfaNewsSpider()
    news.parse()
