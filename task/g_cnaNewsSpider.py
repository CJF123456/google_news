import json
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
from utils.ossUtil import get_image,update_img
from mylog.mlog import log
from utils.common import get_list_page_get, data_insert_mssql, post_download_html_post
from utils.datautil import format_info_int_re,filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#中央社  完结
#http://www.cna.com.tw/
from utils.translate import cat_to_chs

class g_CnaNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:cnanews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "cnanews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'http://www.cna.com.tw/',
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
            {"url": "aipl", "name": "政治"},
            {"url": "acn", "name": "两岸"},
            {"url": "aie", "name": "产经"},
            {"url": "aloc", "name": "地方"},
            {"url": "2227", "name": "专题-政治"},
            {"url": "2212", "name": "专题-政治"},
            {"url": "2012", "name": "专题-政治"},
            {"url": "1697", "name": "专题-政治"},
            {"url": "aopl", "name": "国际"}
        ]
        for url in urls:
            name = url['name']
            s_url = url['url']
            url = 'https://www.cna.com.tw/cna2018api/api/WNewsList'
            if name == '专题-政治':
                url = 'https://www.cna.com.tw/cna2018api/api/WTopic'
            pc_headers.pop('Host', 'www.cna.com.tw')
            pc_headers.pop('Accept', 'application/json, text/javascript, */*; q=0.01')
            pc_headers.pop('X-Requested-With', 'XMLHttpRequest')
            pc_headers.pop('Content-Type', 'application/json')
            pc_headers.pop('Origin', 'https://www.cna.com.tw')
            pc_headers.pop('Referer', 'https://www.cna.com.tw/list/aopl.aspx')
            data = {"action": "0", "category": "{}".format(s_url), "pagesize": "30", "pageidx":1}
            if name == '专题-政治':
                data = {"action": "0", "category": "newstopic", "tno": s_url, "pagesize": "30", "pageidx": 1}
            st, con = post_download_html_post(url, pc_headers, data=data)
            if st:
                # print(con)
                details = json.loads(con)
                for t2 in details['ResultData']['Items']:
                    #print(t2)
                    title = t2['HeadLine']
                    #print(title)
                    detail_url = t2['PageUrl']
                    #print(detail_url)
                    img = t2['ImageS']
                    CreateTime = t2['CreateTime']
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title+'中央社'
                    md5 = make_md5(md5_)
                    if hexists_md5_filter(md5, self.mmd5):
                        log.info(self.project_name + " info data already exists!")
                    else:
                    # if 'news/aipl/202011090256.aspx' in detail_url:
                        self.get_detail(detail_url, md5, detail_url_code, title, img, CreateTime, name)
        log.info(self.project_name + ' spider succ.')

    def get_detail(self, detail_url, md5, detail_url_code, title, img, CreateTime, name):
        try:
            global ImageId
            #print(url)
            s_publish_time = CreateTime.split(' ')[0].replace('/', '-')
            e_publish_time = CreateTime.split(' ')[1]+':00'
            today = now_datetime_no()
            aa = caltime_datetime(today, s_publish_time)
            if aa > -1:
                #print(aa)
                st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
                if st2:
                    # #print(con2)
                    soup = BeautifulSoup(con2, 'lxml')
                    if '视频：' not in str(soup):
                        content = self.get_content_html(con2)
                        # print(content)
                        img_text = ''
                        if img != '':
                            img_texts = soup.select('div.picinfo')
                            for i in img_texts:
                                img_text = img_text+ i.text
                        #print(img_text)

                        if img != '':
                            # 图片存在于文章头部
                            ii = get_image(img)
                            r_i = update_img(ii)
                            # print(r_i)
                            img_ = '<img src="{}"/>\n'.format(r_i)
                            if img_text != '':
                                con_ = img_ + '<p>{}</p>'.format(img_text) + '\n' + content
                            else:
                                con_ = img_ + '\n' + content
                        else:
                            con_ = content
                        con_ = con_.replace('<span>', '<span style="font-family: DengXian; font-size: 38pt;">')
                        #print(con_)
                        spider_time = now_datetime()
                        # 采集时间
                        body = con_
                        title = title.strip()
                        cn_title = ''.join(cat_to_chs(title))
                        create_time = spider_time
                        group_name = name
                        title = filter_emoji(title)
                        update_time = spider_time
                        website = detail_url
                        Uri = detail_url
                        Language = "zh"
                        DocTime = s_publish_time + ' ' + e_publish_time
                        CrawlTime = spider_time
                        Hidden = 0  # 去确认
                        file_name = ""
                        file_path = ""
                        classification = ""
                        cn_boty = ''.join(cat_to_chs(con_))
                        column_id = ''
                        creator = ''
                        if_top = ''
                        source_id = 10380
                        summary = ''
                        summary = filter_emoji(summary)
                        UriId = detail_url_code
                        keyword = ''
                        info_val = (
                        body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top,
                        keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime,
                        CrawlTime, Hidden, file_name, file_path)
                        # 入库mssql
                        data_insert_mssql(info_val, NewsTaskSql.t_doc_info_insert, md5, self.mmd5,
                                          self.project_name)
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

    # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '')\
               .replace('<p></p>', '').strip().replace(
                '\r', '').replace('\n', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
        if '本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用' in format_info:
            format_info = format_info.replace('本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。', '')
        return format_info

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        num = 0
        for divcon in soup.select('div.centralContent > div.paragraph'):
            num = num +1
            if num == 1:
                [s.extract() for s in divcon('figure')]
                [s.extract() for s in divcon.find_all("div", {"class": "paragraph moreArticle"})]
                [s.extract() for s in divcon.find_all("div", {"class": "SubscriptionInner mySubscriptionInner"})]
                [s.extract() for s in divcon.find_all("div", {"class": "paragraph moreArticle"})]
                [s.extract() for s in divcon.find_all("span", {"class": "dic-icon"})]
                [s.extract() for s in divcon.find_all("div", {"class": "dictionary-box hidden open"})]
                [s.extract() for s in divcon.find_all("div", {"class": "dictionary-box hidden"})]
                [s.extract() for s in divcon.find_all("div", {"class": "news-dic-text"})]
                [s.extract() for s in divcon.find_all("span", {"class": "news-dic-all seeArticlemore"})]
                [s.extract() for s in divcon.find_all("p", {"class": "dictionary-title"})]
                [s.extract() for s in divcon.find_all("div", {"class": "news-dic-all seeArticlemore"})]
                [s.extract() for s in divcon.find_all("div", {"class": "news-dic-all closeBox"})]
                [s.extract() for s in divcon.find_all("div", {"class": "picinfo"})]
                locu_content = divcon.prettify()
                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
                #print(con)
                con = con.replace(" ", "")
                # print(con)
                con = self.filter_html(con)
                # print(con)
                con = self.filter_html_end(con)
                # print(con)
        return con


if __name__ == '__main__':
    news = g_CnaNewsSpider()
    news.parse()
