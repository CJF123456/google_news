import sys

import requests

sys.path.append('..')
from utils.timeUtil import format_time
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
from utils.common import get_list_page_get, data_insert_mssql
from utils.ossUtil import get_image,update_img
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
#联合早报
#https://www.zaobao.com/

class g_Lianhe_zaobaoNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:zaobaonews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "zaobaonews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.voachinese.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

    # 判断日期是否为合法输入，年月日的格式需要与上面对应，正确返回True，错误返回False，注意大小写。
    def is_date(self, date):
        try:
            time.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False
    def login(self,user, password):
        url = 'https://acc-auth.sphdigital.com/SPHAuth/rest/auth/new/authenticate'
        data = {"IDToken1":user,"IDToken2":password,"qry_str":"","goto":"https://acc-auth.sphdigital.com/amserver/cdcservlet?TARGET=https://www.zaobao.com.sg:443/dummypost/ampostpreserve?6099fe0b-b351-2342-a6bb-0e2d5a305e11&RequestID=77B4BCB0EB929180832F87122D9F5B2F6F21B646EBB6E8D20AF949803C4E75B3&MajorVersion=1&MinorVersion=0&ProviderID=https://www.zaobao.com.sg:443/amagent&IssueInstant=2020-10-29T11:38:57Z","svc":"zbs","screenName":"LoginPV","g-recaptcha-response":""}
        response = requests.post(url, data=data)
        con = response.text
        #print(con)
        soup = BeautifulSoup(con, 'lxml')
        LARES = soup.select('input[type="hidden"]')[0].get('value').replace('&#x2b;','+').split('&')[0].replace('=','')+'=='
        #print(LARES)
        ampostpreserve = str(con).split('#x3f;')[1].split('">')[0]
        #print(ampostpreserve)
        url1 = 'https://www.zaobao.com.sg/dummypost/ampostpreserve?{}'.format(ampostpreserve)
        data1 = {'LARES': LARES}
        header = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://acc-auth.sphdigital.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        response1 = requests.post(url1, data=data1, headers=header)
        # #print(response1.text)
    def parse(self):
        log.info('spider start...')
        urls = [
            # {"url": "https://www.zaobao.com.sg/znews/sea", "name": "联合早报-东南亚"},
            {"url": "https://www.zaobao.com.sg/special/report/politic/southchinasea", "name": "联合早报-南海争端"},
            {"url": "https://www.zaobao.com.sg/special/report/politic/hkpol", "name": "联合早报-香港政情"},
            {"url": "https://www.zaobao.com.sg/special/report/politic/taiwan", "name": "联合早报-台海局势"},
            {"url": "https://www.zaobao.com.sg/special/report/politic/korea", "name": "联合早报-朝鲜问题"},
            {"url": "https://www.zaobao.com.sg/realtime/china", "name": "联合早报"}, #中国
            {"url": "https://www.zaobao.com.sg/realtime/world", "name": "联合早报"}, #国际
            {"url": "https://www.zaobao.com.sg/realtime/singapore", "name": "联合早报"}, #新加坡
            {"url": "https://www.zaobao.com.sg/zfinance/realtime", "name": "联合早报"},  # 即时
            {"url": "https://www.zaobao.com.sg/finance/china", "name": "联合早报"},  # 中国财经
            {"url": "https://www.zaobao.com.sg/finance/world", "name": "联合早报"},  # 全球财经
            {"url": "https://www.zaobao.com.sg/finance/singapore", "name": "联合早报"},  # 狮城财经
            {"url": "https://www.zaobao.com.sg/finance/world", "name": "联合早报"},  # 观点-社论
            {"url": "https://www.zaobao.com.sg/special/report/politic/chinaustradewar", "name": "联合早报"},  # 中美贸易战
            {"url": "https://www.zaobao.com.sg/special/report/politic/cnpol", "name": "联合早报"},  # 中国政情
            {"url": "https://www.zaobao.com.sg/special/report/politic/sino-us", "name": "联合早报"},  # 中美关系
            {"url": "https://www.zaobao.com.sg/special/report/politic/sino-jp", "name": "联合早报"},  # 中日关系
            {"url": "https://www.zaobao.com.sg/special/report/politic/mypol", "name": "联合早报"},  # 马国政局
            {"url": "https://www.zaobao.com.sg/special/report/politic/thaipolitics", "name": "联合早报"},  # 泰国政局
            {"url": "https://www.zaobao.com.sg/special/report/politic/attack", "name": "联合早报"},  # 全球反恐

            # {"url": "https://beltandroad.zaobao.com/beltandroad/news", "name": "联合早报"},  # 新闻与分析
            # {"url": "https://beltandroad.zaobao.com/beltandroad/analysis", "name": "联合早报"},  # 视角
        ]
        for u in urls:
            url = u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                html1 = etree.HTML(con)
                detail_urls = html1.xpath('.//a[@class="article-type-link"]')
                for detail_url in detail_urls:
                    #print(detail_url)
                    title = detail_url.xpath('./h2')[0].text
                    detail_url = 'https://www.zaobao.com.sg' + detail_url.get('href')
                    #print(detail_url)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title
                    md5 = make_md5(md5_)
                    # if hexists_md5_filter(md5, self.mmd5):
                    #     log.info(self.project_name + " info data already exists!")
                    # else:
                    self.get_detail(detail_url, md5, detail_url_code, title, name)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, title, name):
        try :
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            # #print(con2)
            if '以继续阅读全文' not in con2:
                e_epublish_time = ''
                s_epublish_time = ''
                if st2:
                    soup = BeautifulSoup(con2, 'lxml')
                    publish_time = ''
                    if '年' in con2:  #> em
                        publish_times = soup.select('h4.title-byline.date-published')
                        #print(publish_times)
                        if len(publish_times) == 1:
                            pp = publish_times[0].text
                            #print(pp)
                            if '年' in pp:
                                dd = str(pp).replace(' ','').replace('年', '-').replace('月', '-').replace('日', ' ').replace('发布', '').replace('/', '').replace('AM', ' AM').replace('PM', ' PM')
                                s_epublish_time = dd.split(' ')[0]
                                #print(s_epublish_time)
                                if 'AM' in dd:
                                    ee_publish_time = dd.split(' ')[1].split('AM')[0]+':00' + ' AM'
                                elif 'PM' in dd:
                                    ee_publish_time = dd.split(' ')[1].split('PM')[0] + ':00' + ' PM'
                                #print(ee_publish_time)
                                e_publish_time = self.get_date_am_pm(ee_publish_time)
                                #print(e_publish_time)
                    else:
                        print('发布时间有问题')

                    if self.is_date(s_epublish_time) == True and s_epublish_time != '':
                        if '视频：' not in str(soup):
                            today = now_datetime_no()
                            aa = caltime_datetime(today, s_epublish_time)
                            #print(aa)
                            if aa > -30:
                                content = self.get_content_html(con2)
                                # #print(content)
                                img = ''
                                img_ = ''
                                img_text = ''
                                if 'figure-media-gallery-img' in str(soup):
                                    imgs = soup.select('div.figure-media-gallery-img > img')
                                    if len(imgs) > 0:
                                        img = imgs[0]['data-src']
                                        img_text = imgs[0]['data-caption']
                                elif 'figure-media' in str(soup):
                                    imgs = soup.select('div.figure-media > img')
                                    if len(imgs) > 0:
                                        img = imgs[0]['data-src']
                                        img_text = imgs[0]['title']
                                #print(img)
                                #print(img_text)
                                if img != '':
                                    # 图片存在于文章头部
                                    img = img.split('?')[0]
                                    img_ = '<img src="{}"/>\n'.format(img)
                                    content = img_ + '<p>{}</p>\n'.format(img_text)+ content
                                #print(content)
                                spider_time = now_datetime()
                                s_spider_time = spider_time.split(' ')[1]
                                # 采集时间
                                body = content
                                cn_title = str(title).strip()
                                create_time = spider_time
                                group_name = name
                                title = str(title).strip()
                                title = filter_emoji(title)
                                update_time = spider_time
                                website = detail_url
                                Uri = detail_url
                                Language = "zh"
                                DocTime = publish_time + ' ' + s_spider_time
                                if e_publish_time != '':
                                    DocTime = s_epublish_time + ' ' + e_publish_time
                                CrawlTime = spider_time
                                Hidden = 0  # 去确认
                                file_name = ""
                                file_path = ""
                                classification = ""
                                cn_boty = ''
                                column_id = ''
                                creator = ''
                                if_top = ''
                                if '联合早报-东南亚' in name:
                                    source_id = 10335
                                elif '联合早报-南海争端' in name:
                                    source_id = 10336
                                elif '联合早报-香港政情' in name:
                                    source_id = 10337
                                elif '联合早报-台海局势' in name:
                                    source_id = 10338
                                elif '联合早报-朝鲜问题' in name:
                                    source_id = 10339
                                else:
                                    source_id = 10340
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
        for divcon in soup.select('.article-content.js-fontsized'):
            [s.extract() for s in divcon('figure')]
            [s.extract() for s in divcon.find_all("section", {"id": "imu"})]
            [s.extract() for s in divcon.find_all("script", {"type": "text/javascript"})]
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

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result


 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace(' ', '')\
                .replace('<span>', '<p>').replace('</span>', '</p>').replace('<p><p>', '<p>').replace('</p></p>', '</p>')\
                .replace('\r', '').replace('\n', '')\
            .replace('<h3>', '').replace('</h3>', '')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<a>', '').replace('</a>', '').replace('<strong>', '').replace('</strong>', '')\
                .replace('<p><p>', '<p>').replace('</p></p>', '</p>').replace('<p></p>', "").replace('</p><p>', '</p>\n<p>')
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
    news = g_Lianhe_zaobaoNewsSpider()
    # user = 'NIXIAOYAN@SEASTOR.COM.CN'
    # password = 'XDseastor2020'
    # news.login(user, password)
    news.parse()
