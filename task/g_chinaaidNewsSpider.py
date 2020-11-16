import sys
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
#对华援助新闻网  完结
#https://www.chinaaid.net/

class g_ChinaaidNewsSpider(object):
    def __init__(self):
        # 来源
        self.mmd5 = 'guoqiang:chinaaidnews'
        self.image_mmd5 = 'guoqiang:image'
        self.project_name = self.__class__.__name__
        self.site = "chinaaidnews"
        self.pc_headers = {
            'User-Agent': random.choice(useragents.pc_agents),
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.chinaaid.net/',
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
            {"url": "/search/label/d新闻中心?&max-results=8", "name": "焦点新闻"},
            {"url": "/search/label/a教会逼迫?&max-results=8", "name": "宗教自由"},
            {"url": "/search/label/a维权律师?&max-results=8", "name": "人权法治"},
            {"url": "/search/label/热点追踪?&max-results=8", "name": "热点追踪"},
            {"url": "/search/label/a公共外交?&max-results=8", "name": "公共外交"},
            {"url": "/search/label/a媒体报道?&max-results=8", "name": "媒体报道"},
            {"url": "/search/label/b对华评论?&max-results=8", "name": "对华评论"},
            {"url": "/search/label/理论百家?&max-results=8", "name": "理论百家"},
            {"url": "/search/label/d转载新闻?&max-results=8", "name": "国际倡导"},
            {"url": "/search/label/人权侵犯?&max-results=8", "name": "人权侵犯"},
            {"url": "/search/label/公民社会?&max-results=8", "name": "公民社会"}
        ]
        for u in urls:
            url = 'https://www.chinaaid.net' + u['url']
            name = u['name']
            st, con = get_list_page_get(url, pc_headers, 'utf-8')
            if st:
                html1 = etree.HTML(con)
                detail_urls = html1.xpath('.//a[@class="a-black-noborder"]')
                for detail_url in detail_urls:
                    title = detail_url.text
                    detail_url = detail_url.get('href')
                    #print(detail_url)
                    # 详情页url
                    detail_url_code = str(format_info_int_re(detail_url))
                    md5_ = title+'对华援助新闻网'
                    md5 = make_md5(md5_)
                    # if hexists_md5_filter(md5, self.mmd5):
                    #     log.info(self.project_name + " info data already exists!")
                    # else:
                    self.get_detail(detail_url, md5, detail_url_code, name)
                    # exit(-1)
        log.info(self.project_name + ' spider succ.')


    def get_detail(self, detail_url, md5, detail_url_code, name):
        try :
            global ImageId
            st2, con2 = get_list_page_get(detail_url, pc_headers, 'utf-8')
            # #print(con2)
            if st2:
                soup = BeautifulSoup(con2, 'lxml')
                publish_time = ''
                e_publish_time = ''
                if '年' in con2:
                # Blog1 > div.blog-posts.hfeed > div > div > div > div.post-entry > p:nth-child(2) > span
                # Blog1 > div.blog-posts.hfeed > div > div > div > div.post-entry > p:nth-child(4) > span
                # Blog1 > div.blog-posts.hfeed > div > div > div > div.post-entry > p:nth-child(3) > span
                    publish_times = soup.select('div.post-entry > p:nth-child(2) > span')
                    #print(publish_times)
                    if len(publish_times) == 0:
                        publish_times = soup.select('div.post-entry > p:nth-child(2) > span')
                        if len(publish_times) == 1:
                            pp = publish_times[0].text
                            #print(pp)
                            if '年' in pp:
                                s_epublish_time = pp.replace('年', '-').replace('月', '-').replace('日', '')
                                publish_time = s_epublish_time.split(' ')[0]
                                e_publish_time = s_epublish_time.split(' ')[1]
                        elif len(publish_times) == 0:
                            publish_times = soup.select('div.post-entry > p:nth-child(3) > span')
                            if len(publish_times) != 0:
                                pp = publish_times[0].text
                                #print(pp)
                                if '年' in pp:
                                    s_epublish_time = pp.replace('年', '-').replace('月', '-').replace('日', '')
                                    publish_time = s_epublish_time.split(' ')[0]
                                    e_publish_time = s_epublish_time.split(' ')[1]
                    if len(publish_times) == 7:
                        pp = ''
                        for p in publish_times:
                            pp = pp + p.text
                        #print(pp)
                        if '年' in pp:
                            s_epublish_time = pp.replace('年', '-').replace('月', '-').replace('日', '')
                            publish_time = s_epublish_time.split(' ')[0]
                            e_publish_time = s_epublish_time.split(' ')[1]
                    if e_publish_time == '':
                        publish_time = soup.select('span.heading-date')
                        publish_time = publish_time[0].text
                        publish_time = format_time(publish_time, '%m/%d/%Y', '%Y-%m-%d')
                        #print(publish_time)
                if self.is_date(publish_time) == True and publish_time != '':
                    if '视频：' not in str(soup):
                        today = now_datetime_no()
                        aa = caltime_datetime(today, publish_time)
                        #print(aa)
                        if aa > -2:
                            html1 = etree.HTML(con2)
                            title = html1.xpath('//*[@id="Blog1"]/div[1]/div/div/div/h2')[0].text
                            #print(title)
                            # 拿到contents中的img的src和 title
                            imgsrcs = html1.xpath('//*[@class="separator"]/a')
                            imgsrc = ''
                            imgtext = ''
                            #print(len(imgsrcs))
                            if len(imgsrcs) > 0:
                                imgsrc = html1.xpath('//*[@class="separator"]/a')[0].get('href')
                                imgtexts = html1.xpath('//*[@id="Blog1"]/div[1]/div/div/div/div[2]/p[4]/span[2]/span[3]')
                                if len(imgtexts) > 0:
                                    if 'blog-post_18.html' not in detail_url:
                                        imgtext = html1.xpath('//*[@id="Blog1"]/div[1]/div/div/div/div[2]/p[4]/span[2]/span[3]')[0].text
                            elif 'tr-caption-container' in str(con2):
                                imgsrc = html1.xpath('//table[@class="tr-caption-container"]//img[@src]')[0].get('src')
                                imgtexts = html1.xpath('//*[@class="tr-caption"]')
                                if len(imgtexts) > 0:
                                    imgtext = html1.xpath('//*[@class="tr-caption"]')[0].text
                            #print(imgsrc)
                            #print(imgtext)
                            content = self.get_content_html(con2)
                            # #print(content)
                            if imgsrc != None or imgsrc != '':
                                if (len(imgsrcs) == 1):
                                    #图片存在于文章头部
                                    ii = get_image(imgsrc)
                                    r_i = update_img(ii)
                                    #print(r_i)
                                    img_ = '<img src="{}"/>\n'.format(r_i)
                                    if imgtext != '':
                                        con_ = img_+'<p>{}</p>'.format(imgtext)+'\n'+content
                                    else:
                                        con_ = img_ + '\n' + content
                                elif imgsrc != '' or imgsrc != None:
                                    # 图片存在于文章头部
                                    ii = get_image(imgsrc)
                                    r_i = update_img(ii)
                                    #print(r_i)
                                    img_ = '<img src="{}"/>\n'.format(r_i)
                                    con_ = img_+'<p>{}</p>'.format(imgtext)+'\n'+content
                                else:
                                    con_ = content
                            con_ = con_.replace('<p></p>', '')
                            #print(con_)
                            spider_time = now_datetime()
                            s_spider_time = spider_time.split(' ')[1]
                            # 采集时间
                            body = con_
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
                                DocTime = publish_time + ' ' + e_publish_time
                            CrawlTime = spider_time
                            Hidden = 0  # 去确认
                            file_name = ""
                            file_path = ""
                            classification = ""
                            cn_boty = ''
                            column_id = ''
                            creator = ''
                            if_top = ''
                            source_id = 10351
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
            #print(e)
            pass

    # TODO 内容格式化
    def get_content_html(self, html):
        global con
        soup = BeautifulSoup(html, 'lxml')
        for divcon in soup.select('.post-entry'):
            [s.extract() for s in divcon('figure')]
            # [s.extract() for s in divcon.find_all("ul", {"style": "margin-top: 0in;"})]
            [s.extract() for s in divcon.find_all("td", {"class": "tr-caption"})]
            locu_content = divcon.prettify()
            con = re.sub(r'(<[^>\s]+)\s[^>]+?(>)', r'\1\2', locu_content)
            # #print(con)
            con = self.filter_html(con)
            # #print(con)
            con = con.replace(" ", "")
            # #print(con)
            con = self.filter_html_end(con)
            # #print(con)
            con = self.replace_tag(con)
            # #print(con)
        return con

    # TODO 去掉指定标签
    def remove_tag(self, con_, tag):
        from w3lib import html
        result = html.remove_tags_with_content(con_, which_ones=(tag), encoding=None)
        return result

    # TODO 替换span标签成  内联样式
    def replace_tag(self, con):
        con = con.replace('<p><span></span></p>', "").strip()
        con = con.replace('<p></p>', "").strip()
        con = con.replace('<span></span>', "").strip()
        con = con.replace('<span>', '<span style="font-family: DengXian; font-size: 38pt;">')
        return con

 # TODO 初始过滤
    def filter_html(self, format_info):
        if format_info:
            format_info = format_info.replace('<div>', '').replace('</div>', '').replace(' ', '').replace('<p><span></span></p>', '').strip().replace(
                '\r', '').replace('\n', '').replace('<o:p></o:p>', '').replace('<o:p>','').replace('</o:p>','').replace('<br/>','')
        return format_info

    # TODO 初始过滤
    def filter_html_end(self, format_info):
        if format_info:
            format_info = format_info.replace('<table>', '').replace('<tbody>', '').replace('<tr>', '').replace('<td>', '')\
                .replace('<a>', '').replace('</table>', '').replace('</tbody>', '').replace('</tr>', '').replace('</td>', '').replace('</a>', '')\
                .replace('<p><img></p>', '').replace('<img>', '\n').replace('<ul>', '').replace('<li>', '').replace('</ul>', '').replace('</li>', '')\
                .replace('<p></p>', "").replace('</p><p>', '</p>\n<p>').strip()
        if '链接：' in format_info:
            format_info = format_info.replace('《善劝胡锡进》链接：', '').replace('https://chinadigitaltimes.net/chinese/2020/01/贾学伟｜善劝胡锡进/','')
        format_info = format_info.replace('<p><span style="font-family: DengXian; font-size: 38pt;"></span></p>', '').strip()
        return format_info


if __name__ == '__main__':
    news = g_ChinaaidNewsSpider()
    news.parse()
