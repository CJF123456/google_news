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
from utils.ossUtil import get_image,update_img
from utils.common import get_list_page_get, data_insert_mssql
from utils.datautil import format_info_int_re, filter_emoji
from utils.timeUtil import now_datetime, now_datetime_no, caltime_datetime
from utils.translate import cat_to_chs
#韩联社  完结
#https://cn.yna.co.kr/

class g_YnaNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:malaysiakininews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "malaysiakininews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://cn.yna.co.kr/',
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
            {"url": "https://cn.yna.co.kr/politics/index", "name": "政治"},
            {"url": "https://cn.yna.co.kr/society/index", "name": "社会"},
            {"url": "https://cn.yna.co.kr/nk/index", "name": "朝鲜"},
            {"url": "https://cn.yna.co.kr/china-relationship/index", "name": "韩中关系"}
        ]
        for u in urls:
            st, con = get_list_page_get(u['url'], pc_headers, 'utf-8')
            if st:
                name = u['name']
                html1 = etree.HTML(con)
                detail_urls = html1.xpath('//*[@class="tit"]/a')
                for detail_url in detail_urls:
                    #print(detail_url.get('href'))
                    title = detail_url.text
                    #print(title)
                    url = detail_url.get('href')
                    if 'section=politics' in url or 'section=society' in url or 'section=nk' in url or 'section=china-relationship' in url:
                        # 详情页url
                        detail_url_code = str(format_info_int_re(url))
                        md5_ = title+'韩联社'
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
                publish_time = soup.select('div.info-con > span.txt')
                publish_time = publish_time[0].text
                if '政治' in publish_time or '社会' in publish_time or '朝鲜' in publish_time or '韩中关系' in publish_time:
                    if '政治' in publish_time and '年' in publish_time:
                        s_publish_time = publish_time.replace('政治', '').replace('年 ', '-').replace('月 ', '-').split('日')[0].strip()
                        e_publish_time = publish_time.split('日 ')[1]+':00'
                    elif '社会' in publish_time and '年' in publish_time:
                        s_publish_time = publish_time.replace('社会', '').replace('年 ', '-').replace('月 ', '-').split('日')[0].strip()
                        e_publish_time = publish_time.split('日 ')[1]+':00'
                    elif '朝鲜' in publish_time and '年' in publish_time:
                        s_publish_time = publish_time.replace('朝鲜', '').replace('年 ', '-').replace('月 ', '-').split('日')[0].strip()
                        e_publish_time = publish_time.split('日 ')[1]+':00'
                    elif '韩中关系' in publish_time and '年' in publish_time:
                        s_publish_time = publish_time.replace('韩中关系', '').replace('年 ', '-').replace('月 ', '-').split('日')[0].strip()
                        e_publish_time = publish_time.split('日 ')[1]+':00'

                    #print(s_publish_time, e_publish_time)
                    #print(self.is_date(s_publish_time))
                    if self.is_date(s_publish_time) == True:
                        if '视频：' not in str(soup):
                            today = now_datetime_no()
                            aa = caltime_datetime(today, s_publish_time)
                            #print(aa)
                            if aa > -1:
                                # 拿到contents中的img的src
                                imgsrc = ''
                                imgtext = ''
                                for img in soup.select('.yna-img-slide.dis-none >img'):
                                    if img.has_attr('src'):
                                        imgsrc = img.attrs['src']
                                    if img.has_attr('alt'):
                                        imgtext = img.attrs['alt']
                                #print(imgsrc)
                                #print(imgtext)
                                html1 = etree.HTML(con2)
                                contents = html1.xpath('//div[@class="comp-box text-group"]')
                                conts = ''
                                for content in contents:
                                    cont = etree.tostring(content, pretty_print=True, method='html', encoding='utf-8')
                                    cont = cont.decode()
                                    # #print(cont)
                                    conts = conts + cont
                                # #print(conts)
                                conts = conts.split('（完）</p>')[0]+'</p>'
                                con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', conts)
                                # #print(con)
                                con = self.filter_html(con)
                                # #print(con)
                                if imgsrc != '':
                                    # 图片存在于文章头部
                                    ii = get_image(imgsrc)
                                    r_i = update_img(ii)
                                    #print(r_i)
                                    img_ = '<img src="{}"/>\n'.format(r_i)
                                    con_ = img_ + '\n' + con
                                    if imgtext != '':
                                        con_ = img_ + '<p>{}</p>'.format(imgtext) + '\n' + con
                                else:
                                    con_ = con
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
                                cn_boty = ''
                                column_id = ''
                                creator = ''
                                if_top = ''
                                source_id = 10362
                                summary = ''
                                summary = filter_emoji(summary)
                                UriId = detail_url_code
                                keyword = ''
                                info_val = (body, classification, cn_boty, cn_title, column_id, create_time, creator, group_name, if_top, keyword, source_id, summary, title, update_time, website, Uri, UriId, Language, DocTime, CrawlTime,Hidden, file_name, file_path)
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
            format_info = format_info.replace('<div><div>', '').replace('</div></div>', '').replace('<p></p>', '').replace('<p> </p>', '').strip().replace('\r', '').replace('\n', '')
            format_info = format_info.replace("</p><p>", "</p>\n<p>")
        return format_info


if __name__ == '__main__':
    news = g_YnaNewsSpider()
    news.parse()
