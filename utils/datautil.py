#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/28 15:20
# @Author  : cjf
# @Site    : 
# @File    : datautil.py
# @Software: PyCharm
import sys

sys.path.append('..')
import datetime
import random
import re
import time


def format_p_null(format_info):
    '''
    格式化<p>
    '''
    format_info = format_info.replace("<hr/>", "").replace("        ", "").replace("       ", ""). \
        replace("     ", "").replace("   ", "").replace("﻿ ", "").replace("<p> ﻿</p>", ""). \
        replace("\n", "").replace("</ p>", "</p>").replace("\n", ""). \
        replace("<p>  </p>", ""). \
        replace("<p>   </p>", "").replace("\n", "").replace("</ p>", "</p>"). \
        replace("<p>:</p>", "").replace("<p>：</p>", "").replace("<p></p>", "").replace("<p> </p>", ""). \
        replace("<p> </p>", "").replace("<p>  </p>", "").replace(
        "<p></p>", "").replace(
        "<p><p>", "<p>").replace("<p>:</p>", "").replace("<p>：</p>", "").replace("<p><p>", "<p>").replace("</p></p>",
                                                                                                          "</p>").replace(
        "<p></p>", "")
    return format_info


def get_uuid1():
    '''
    基于时间戳。由MAC地址、当前时间戳、随机数生成。可以保证全球范围内的唯一性，
    但MAC的使用同时带来安全性问题，局域网中可以使用IP来代替MAC
    :return:
    '''
    import uuid
    return str(uuid.uuid1())


def format_info_list_str(format_info):
    '''
    list 转str 去掉空格等信息
    :param format_info:
    :return:
    '''
    if format_info:
        format_info = ''.join(format_info)
        format_info = format_info.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0',
                                                                                                                 '')
    else:
        format_info = ''
    return format_info


def format_info_list_str_(format_info):
    '''

    :param format_info:
    :return:
    '''
    if format_info:
        format_info = ''.join(format_info)
        format_info = format_info.replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', '')
    else:
        format_info = ''
    return format_info


def format_str_info__(format_info):
    '''
    :param format_info:
    :return:
    '''
    if format_info:
        format_info = format_info.replace('\r', '').replace('\n', '').replace('\t', '').replace('\'',
                                                                                                '\"')
        format_info.lstrip()
        format_info = filter_emoji(format_info)
    else:
        format_info = ""
    return format_info


def format_str_info_text(format_info):
    '''

    :param format_info:
    :return:
    '''
    if format_info:
        format_info = format_info.replace('\r', '').replace('\n', '').replace('\t', '')
        format_info.lstrip()
        format_info = filter_emoji(format_info)
    else:
        format_info = ""
    return format_info


def format_grade_list_float(format_info):
    '''
    list 转 float
    :param format_info:
    :return:
    '''
    if format_info:
        format_info = ''.join(format_info)
        format_info = format_info.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
    else:
        format_info = 0
    return format_info


def format_str_info(format_info):
    '''
    格式化str 过滤特殊字符表情等
    :param format_info:
    :return:
    '''
    if format_info:
        format_info = format_info.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
        format_info.lstrip()
        format_info = filter_emoji(format_info)
    else:
        format_info = ""
    return format_info


def format_info_list_int(format_info):
    '''
    list 转int
    :param format_info:
    :return:
    '''
    if format_info:
        format_info = int(''.join(format_info))
    else:
        format_info = 0
    return format_info


def format_info_day(format_info):
    '''
    格式化天数
    :param format_info:
    :return:
    '''
    if '天' in format_info:
        day_num = re.findall("\d+日?", format_info)[0]
        if day_num:
            day_num1 = ''.join(day_num)
            day_num = day_num1.replace("日行程", "").lstrip()
            day_num = day_num.replace("日", "").lstrip()
            day_num = format_info_int_re(day_num)
    elif '日' in format_info:
        day_num = re.findall("\d+日?", format_info)[0]
        if day_num:
            day_num1 = ''.join(day_num)
            day_num = day_num1.replace("日行程", "").lstrip()
            day_num = day_num.replace("日", "").lstrip()
            day_num = format_info_int_re(day_num)
    else:
        day_num = 0
    return day_num


def sleep_small():
    '''
    0.5-2.1秒的短时间随机休眠
    :return:
    '''
    num = random.uniform(0.5, 2.1)
    time.sleep(num)


def sleep_short():
    '''
    3-5秒的短时间随机休眠
    :return:
    '''
    num = random.uniform(3, 5)
    time.sleep(num)


def sleep_long():
    '''
    10-20秒的长时间随机休眠
    :return:
    '''
    num = random.uniform(10, 20)
    time.sleep(num)


def format_info_int_re(format_info):
    '''
    正则匹配整数
    :param format_info:
    :return:
    '''
    format_info = format_info_list_str(format_info)
    if format_info:
        format_info1 = ''.join(format_info).lstrip()
        format_info = int(re.findall('\d+', format_info1)[0])
    else:
        format_info = 0
    return format_info


def format_int_float_re(format_info):
    '''
    正则匹配整数及小数
    :param format_info:
    :return:
    '''
    try:
        find_float = lambda x: re.search("\d+(\.\d+)?", x).group()
        format_info = format_info_list_str(format_info)
        if format_info:
            x = ''.join(format_info).lstrip()
            float = find_float(x)
        else:
            float = 0
    except AttributeError as e:
        print(e)
        float = 0
    return float


def hasNumbers(inputString):
    '''
    判断是否包含数字
    :param inputString:
    :return:
    '''
    return bool(re.search(r'\d', inputString))


def control_time(info):
    '''
    控制时间 如：几天前
    :param info:
    :return:
    '''
    info_time = (datetime.datetime.now() - datetime.timedelta(minutes=int(info))).strftime("%Y-%m-%d %H:%M:%S")
    return info_time


def format_list_float_int(format_info):
    '''
    list转化成整型和浮点型
    :param format_info:
    :return:
    '''
    if format_info:
        format_info1 = ''.join(format_info).lstrip()
        if '.' in format_info:
            format_info = float(re.findall('\d+\.\d+', format_info1)[0])
        else:
            format_info = int(re.findall('\d+', format_info1)[0])
    else:
        format_info = 0
    return format_info


def format_list_wan_float(format_info):
    '''
    list 转化成万成浮点型
    :param format_info:
    :return:
    '''
    global number
    if format_info:
        format_info1 = ''.join(format_info).lstrip()
        r = re.findall('[\d+\.\d]*', format_info1)
        number = float(r[0])
        if '万' in format_info1:
            number *= 10000
    return number


def check_contain_chinese(check_str):
    '''
    是否包含中文
    :param check_str:
    :return:
    '''
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
        else:
            return False


def filter_chinese(check_str):
    '''
    是否包含中文
    :param check_str:
    :return:
    '''
    t = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]', check_str)
    return ''.join(t)


def filter_emoji(desstr, restr=''):
    '''
    过滤表情[\ud83c\udc00-\ud83c\udfff]|[\ud83d\udc00-\ud83d\udfff]|[\u2600-\u27ff]
                        '''
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


def mathutf(info):
    pat = re.compile(r'[\u4e00-\u9fa5]+')
    result = pat.findall(info)
    return result[0]


# TODO p标签
def format_p_tag(con_text):
    con_ = con_text.split("<p>")
    content = []
    for con in con_:
        if con.startswith("<p>"):
            pass
        else:
            con = "<p>" + con
        if con.endswith("</p>"):
            pass
        else:
            con = con + "</p>"
        content.append(con)
    return ''.join(content)


def format_content_p(con_text):
    con_ = con_text.split("<p>")
    contents = []
    for con in con_:
        if con:
            if "<p>" in con:
                con = con.replace("<p>", "").strip().lstrip()
            if "</p>" in con:
                con = con.replace("</p>", "").strip().lstrip()
            if con.startswith("延伸阅读"):
                pass
            else:
                contents.append(con)
        else:
            pass
    contents_p = []
    for con_p in contents:
        con_p = "<p>" + con_p + "</p>"
        contents_p.append(con_p)
    content_html = "".join(contents_p)
    return content_html


# TODO 替换各种不用的标签
def filter_html_clear_format(format_info):
    if format_info:
        format_info = format_info.replace('<div>', '').replace('</div>', '').replace('<span>', '').replace(
            '</span>', '').replace('<button>', '').replace('</button>', ''). \
            replace('<svg>', '').replace('</svg>', '').replace('<figure>', '').replace('</figure>', '') \
            .replace('<figcaption>', '').replace('</figcaption>', '') \
            .replace('<path>', '').replace('</path>', '') \
            .strip().replace('\r', '').replace('\n', '').replace('+<!-->3+<!-->2', '')
        format_info = format_info.replace("</p><p>", "</p>\n<p>").replace("<picture>", "") \
            .replace("</picture>", "").replace("<img>", "").replace("<a>", "").replace("</a>", "") \
            .replace("<b>", "").replace("</b>", "").replace("<main>", "").replace("</main>", "") \
            .replace("<ul>", "").replace("</ul>", "").replace("<p></p>", "").replace("<i>", "").replace("</i>", '')
    if "「版權宣告" in format_info:
        format_info = format_info.split("「版權宣告")[0]
    elif "「版权声明：" in format_info:
        format_info = format_info.split("「版权声明：")[0]
    elif "<p>推荐阅读" in format_info:
        format_info = format_info.split("推荐阅读")[0]
    elif "<p>推荐阅读" in format_info:
        format_info = format_info.split("推荐阅读")[0]
    elif "<p>记者" in format_info:
        format_info = format_info.split("<p>记者")[0]
    elif "<p>编译" in format_info:
        format_info = format_info.split("<p>编译")[0]
    elif "<p>审校" in format_info:
        format_info = format_info.split("<p>审校")[0]
    elif "<p>更多" in format_info:
        format_info = format_info.split("<p>更多")[0]

    return format_info


def label_filter(k_soup):
    ks = k_soup.find_all('div')
    for k in ks:
        del (k["class"])
        del (k["class"])
        del (k["data-index"])
        del (k["data-seq"])
        del (k["data-pid"])
        del (k["data-poiid"])
        del (k["style"])
        del (k["id"])
        del (k["data-mddid"])
        del (k["data-poster"])
    ks = k_soup.find_all('p')
    for k in ks:
        del (k["data-seq"])
        del (k["class"])
    ks = k_soup.find_all('a')
    for ka in ks:
        del (ka["class"])
        del (ka["data-kw"])
        del (ka["href"])
        del (ka["target"])
        del (ka["style"])
        del (ka["data-cs-p"])
        del (ka["data-poiid"])
    ks = k_soup.find_all('img')
    for kimg in ks:
        del (kimg["alt"])
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["data-src"])
        del (kimg["style"])
        del (kimg['data-rt-src'])
        del (kimg['data-file'])
        del (kimg['src'])
    ks = k_soup.find_all('h2')
    for kimg in ks:
        del (kimg["alt"])
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src1'])
    ks = k_soup.find_all('span')
    for kimg in ks:
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src1'])
    ks = k_soup.find_all('i')
    for kimg in ks:
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src'])
    ks = k_soup.find_all('iframe')
    for kimg in ks:
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src'])
        del (kimg['allowfullscreen'])
    return k_soup


def label_filter_imgsrc(k_soup):
    ks = k_soup.find_all('div')
    for k in ks:
        del (k["class"])
        del (k["class"])
        del (k["data-index"])
        del (k["data-seq"])
        del (k["data-pid"])
        del (k["data-poiid"])
        del (k["style"])
        del (k["id"])
        del (k["data-mddid"])
    ks = k_soup.find_all('p')
    for k in ks:
        del (k["data-seq"])
        del (k["class"])
    ks = k_soup.find_all('a')
    for ka in ks:
        del (ka["class"])
        del (ka["data-kw"])
        del (ka["href"])
        del (ka["target"])
        del (ka["style"])
        del (ka["data-cs-p"])
        del (ka["data-poiid"])
    ks = k_soup.find_all('img')
    for kimg in ks:
        del (kimg["alt"])
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["data-src"])
        del (kimg["style"])
        del (kimg['data-rt-src'])
        del (kimg['data-file'])
    ks = k_soup.find_all('h2')
    for kimg in ks:
        del (kimg["alt"])
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["style"])
        del (kimg['data-rt-src1'])
        del (kimg['data-src'])
        del (kimg['data-originalpic'])
        del (kimg['data-file'])
    ks = k_soup.find_all('span')
    for kimg in ks:
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src1'])
    ks = k_soup.find_all('i')
    for kimg in ks:
        del (kimg["class"])
        del (kimg["data-pid"])
        del (kimg["src"])
        del (kimg["style"])
        del (kimg['data-rt-src'])
    return k_soup


def all_tag_replace_html(format_info):
    if format_info:
        format_info = format_info.replace('<!DOCTYPE>', '').replace('<html>', '').replace('<title>', '').replace(
            '<body>', '').replace('<br>', '').replace('<br/>', '').replace('<hr>', '').replace('<!--...-->',
                                                                                               '').replace('<abbr>',
                                                                                                           '').replace(
            '<address>', '').replace('<b>', '').replace('<bdi>', '').replace('<bdo>', '').replace('<blockquote>',
                                                                                                  '').replace(
            '<cite>', '').replace('<code>', '').replace('<del>', '').replace('<dfn>', '').replace('<em>', '').replace(
            '<i>',
            '').replace(
            '<ins>', '').replace('<kbd>', '').replace('<mark>', '').replace('<meter>', '').replace('<pre>', '').replace(
            '<progress>', '').replace('<q>', '').replace('<rp>', '').replace('<rt>', '').replace('<ruby>', '').replace(
            '<s>',
            '').replace(
            '<samp>', '').replace('<small>', '').replace('<strong>', '').replace('<sub>', '').replace('<sup>',
                                                                                                      '').replace(
            '<time>', '').replace('<u>', '').replace('<var>', '').replace('<wbr>', '').replace('<form>', '').replace(
            '<input>',
            '').replace(
            '<textarea>', '').replace('<button>', '').replace('<select>', '').replace('<optgroup>', '').replace(
            '<option>',
            '').replace(
            '<label>', '').replace('<fieldset>', '').replace('<legend>', '').replace('<datalist>', '').replace(
            '<output>',
            '').replace(
            '<iframe>', '').replace('<img>', '').replace('<map>', '').replace('<area>', '').replace('<canvas>',
                                                                                                    '').replace(
            '<figcaption>', '').replace('<figure>', '').replace('<audio>', '').replace('<source>', '').replace(
            '<track>',
            '').replace(
            '<video>', '').replace('<a>', '').replace('<link>', '').replace('<nav>', '').replace('<ul>', '').replace(
            '<ol>',
            '').replace(
            '<li>', '').replace('<dl>', '').replace('<dt>', '').replace('<dd>', '').replace('<menu>', '').replace(
            '<commend>',
            '').replace(
            '<table>', '').replace('<caption>', '').replace('<th>', '').replace('<tr>', '').replace('<td>', '').replace(
            '<thead>', '').replace('<tbody>', '').replace('<tfoot>', '').replace('<col>', '').replace('<colgroup>',
                                                                                                      '').replace(
            '<style>', '').replace('<div>', '').replace('<span>', '').replace('<header>', '').replace('<footer>',
                                                                                                      '').replace(
            '<section>', '').replace('<article>', '').replace('<aside>', '').replace('<details>', '').replace(
            '<dialog>',
            '').replace(
            '<summary>', '').replace('<head>', '').replace('<meta>', '').replace('<base>', '').replace('<script>',
                                                                                                       '').replace(
            '<noscript>', '').replace('<embed>', '').replace('<object>', '').replace('<param>', '').replace('<main>',
                                                                                                            '').replace(
            '</html>', '').replace('</title>', '').replace('</body>', '').replace(
            '</br>', '').replace('</hr>', '').replace('</!--...-->', '').replace('</abbr>', '').replace('</address>',
                                                                                                        '').replace(
            '</b>',
            '').replace(
            '</bdi>', '').replace('</bdo>', '').replace('</blockquote>', '').replace('</cite>', '').replace('</code>',
                                                                                                            '').replace(
            '</del>', '').replace('</dfn>', '').replace('</em>', '').replace('</i>', '').replace('</ins>', '').replace(
            '</kbd>',
            '').replace(
            '</mark>', '').replace('</meter>', '').replace('</pre>', '').replace('</progress>', '').replace('</q>',
                                                                                                            '').replace(
            '</rp>', '').replace('</rt>', '').replace('</ruby>', '').replace('</s>', '').replace('</samp>', '').replace(
            '</small>', '').replace('</strong>', '').replace('</sub>', '').replace('</sup>', '').replace('</time>',
                                                                                                         '').replace(
            '</u>', '').replace('</var>', '').replace('</wbr>', '').replace('</form>', '').replace('</input>',
                                                                                                   '').replace(
            '</textarea>', '').replace('</button>', '').replace('</select>', '').replace('</optgroup>', '').replace(
            '</option>',
            '').replace(
            '</label>', '').replace('</fieldset>', '').replace('</legend>', '').replace('</datalist>', '').replace(
            '</output>',
            '').replace(
            '</iframe>', '').replace('</img>', '').replace('</map>', '').replace('</area>', '').replace('</canvas>',
                                                                                                        '').replace(
            '</figcaption>', '').replace('</figure>', '').replace('</audio>', '').replace('</source>', '').replace(
            '</track>',
            '').replace(
            '</video>', '').replace('</a>', '').replace('</link>', '').replace('</nav>', '').replace('</ul>',
                                                                                                     '').replace(
            '</ol>', '').replace('</li>', '').replace('</dl>', '').replace('</dt>', '').replace('</dd>', '').replace(
            '</menu>',
            '').replace(
            '</commend>', '').replace('</table>', '').replace('</caption>', '').replace('</th>', '').replace('</tr>',
                                                                                                             '').replace(
            '</td>', '').replace('</thead>', '').replace('</tbody>', '').replace('</tfoot>', '').replace('</col>',
                                                                                                         '').replace(
            '</colgroup>', '').replace('</style>', '').replace('</div>', '').replace('</span>', '').replace('</header>',
                                                                                                            '').replace(
            '</footer>', '').replace('</section>', '').replace('</article>', '').replace('</aside>', '').replace(
            '</details>',
            '').replace(
            '</dialog>', '').replace('</summary>', '').replace('</head>', '').replace('</meta>', '').replace('</base>',
                                                                                                             '').replace(
            '</script>', '').replace('</noscript>', '').replace('</embed>', '').replace('</object>', '').replace(
            '</param>',
            '').replace(
            '</main>', '').replace('<h1>', '').replace('<h2>', '').replace('<h3>', '').replace('<h4>', '').replace(
            '<h5>', '').replace('<h6>', '').replace('</h1>', '').replace('</h2>', '').replace('</h3>', '').replace(
            '</h4>', '').replace('</h5>',
                                 '').replace(
            '</h6>', '').replace("<!-->", "").replace("===", "").replace("<!--0-->", "").replace("<!--1-->", "") \
            .replace("<!--2-->", "").replace("<!--4-->", "").replace("<!--5-->", "").replace("<!--6-->", "").replace(
            "<!--7-->", "").replace("<!--8-->", "").replace("<!--9-->", "").replace("<!--10-->", "").replace(
            "<!--11-->", "").replace(
            "<!--12-->", "").replace("<!--3-->", "").replace("<!--99-->", "")
    return format_info


def all_tag_replace_html_div(format_info):
    if format_info:
        format_info = format_info.replace('<!DOCTYPE>', '').replace('<html>', '').replace('<title>', '').replace(
            '<body>', '').replace('<br>', '').replace('<br/>', '').replace('<hr>', '').replace('<!--...-->',
                                                                                               '').replace('<abbr>',
                                                                                                           '').replace(
            '<address>', '').replace('<b>', '').replace('<bdi>', '').replace('<bdo>', '').replace('<blockquote>',
                                                                                                  '').replace(
            '<cite>', '').replace('<code>', '').replace('<del>', '').replace('<dfn>', '').replace('<em>', '').replace(
            '<i>',
            '').replace(
            '<ins>', '').replace('<kbd>', '').replace('<mark>', '').replace('<meter>', '').replace('<pre>', '').replace(
            '<progress>', '').replace('<q>', '').replace('<rp>', '').replace('<rt>', '').replace('<ruby>', '').replace(
            '<s>',
            '').replace(
            '<samp>', '').replace('<small>', '').replace('<strong>', '').replace('<sub>', '').replace('<sup>',
                                                                                                      '').replace(
            '<time>', '').replace('<u>', '').replace('<var>', '').replace('<wbr>', '').replace('<form>', '').replace(
            '<input>',
            '').replace(
            '<textarea>', '').replace('<button>', '').replace('<select>', '').replace('<optgroup>', '').replace(
            '<option>',
            '').replace(
            '<label>', '').replace('<fieldset>', '').replace('<legend>', '').replace('<datalist>', '').replace(
            '<output>',
            '').replace(
            '<iframe>', '').replace('<img>', '').replace('<map>', '').replace('<area>', '').replace('<canvas>',
                                                                                                    '').replace(
            '<figcaption>', '').replace('<figure>', '').replace('<audio>', '').replace('<source>', '').replace(
            '<track>',
            '').replace(
            '<video>', '').replace('<a>', '').replace('<link>', '').replace('<nav>', '').replace('<ul>', '').replace(
            '<ol>',
            '').replace(
            '<li>', '').replace('<dl>', '').replace('<dt>', '').replace('<dd>', '').replace('<menu>', '').replace(
            '<commend>',
            '').replace(
            '<table>', '').replace('<caption>', '').replace('<th>', '').replace('<tr>', '').replace('<td>', '').replace(
            '<thead>', '').replace('<tbody>', '').replace('<tfoot>', '').replace('<col>', '').replace('<colgroup>',
                                                                                                      '').replace(
            '<style>', '').replace('<span>', '').replace('<header>', '').replace('<footer>',
                                                                                 '').replace(
            '<section>', '').replace('<article>', '').replace('<aside>', '').replace('<details>', '').replace(
            '<dialog>',
            '').replace(
            '<summary>', '').replace('<head>', '').replace('<meta>', '').replace('<base>', '').replace('<script>',
                                                                                                       '').replace(
            '<noscript>', '').replace('<embed>', '').replace('<object>', '').replace('<param>', '').replace('<main>',
                                                                                                            '').replace(
            '</html>', '').replace('</title>', '').replace('</body>', '').replace(
            '</br>', '').replace('</hr>', '').replace('</!--...-->', '').replace('</abbr>', '').replace('</address>',
                                                                                                        '').replace(
            '</b>',
            '').replace(
            '</bdi>', '').replace('</bdo>', '').replace('</blockquote>', '').replace('</cite>', '').replace('</code>',
                                                                                                            '').replace(
            '</del>', '').replace('</dfn>', '').replace('</em>', '').replace('</i>', '').replace('</ins>', '').replace(
            '</kbd>',
            '').replace(
            '</mark>', '').replace('</meter>', '').replace('</pre>', '').replace('</progress>', '').replace('</q>',
                                                                                                            '').replace(
            '</rp>', '').replace('</rt>', '').replace('</ruby>', '').replace('</s>', '').replace('</samp>', '').replace(
            '</small>', '').replace('</strong>', '').replace('</sub>', '').replace('</sup>', '').replace('</time>',
                                                                                                         '').replace(
            '</u>', '').replace('</var>', '').replace('</wbr>', '').replace('</form>', '').replace('</input>',
                                                                                                   '').replace(
            '</textarea>', '').replace('</button>', '').replace('</select>', '').replace('</optgroup>', '').replace(
            '</option>',
            '').replace(
            '</label>', '').replace('</fieldset>', '').replace('</legend>', '').replace('</datalist>', '').replace(
            '</output>',
            '').replace(
            '</iframe>', '').replace('</img>', '').replace('</map>', '').replace('</area>', '').replace('</canvas>',
                                                                                                        '').replace(
            '</figcaption>', '').replace('</figure>', '').replace('</audio>', '').replace('</source>', '').replace(
            '</track>',
            '').replace(
            '</video>', '').replace('</a>', '').replace('</link>', '').replace('</nav>', '').replace('</ul>',
                                                                                                     '').replace(
            '</ol>', '').replace('</li>', '').replace('</dl>', '').replace('</dt>', '').replace('</dd>', '').replace(
            '</menu>',
            '').replace(
            '</commend>', '').replace('</table>', '').replace('</caption>', '').replace('</th>', '').replace('</tr>',
                                                                                                             '').replace(
            '</td>', '').replace('</thead>', '').replace('</tbody>', '').replace('</tfoot>', '').replace('</col>',
                                                                                                         '').replace(
            '</colgroup>', '').replace('</style>', '').replace('</span>', '').replace('</header>',
                                                                                      '').replace(
            '</footer>', '').replace('</section>', '').replace('</article>', '').replace('</aside>', '').replace(
            '</details>',
            '').replace(
            '</dialog>', '').replace('</summary>', '').replace('</head>', '').replace('</meta>', '').replace('</base>',
                                                                                                             '').replace(
            '</script>', '').replace('</noscript>', '').replace('</embed>', '').replace('</object>', '').replace(
            '</param>',
            '').replace(
            '</main>', '').replace('<h1>', '').replace('<h2>', '').replace('<h3>', '').replace('<h4>', '').replace(
            '<h5>', '').replace('<h6>', '').replace('</h1>', '').replace('</h2>', '').replace('</h3>', '').replace(
            '</h4>', '').replace('</h5>',
                                 '').replace(
            '</h6>', '').replace("<!-->", "").replace("===", "")
    return format_info


def all_tag_replace_html_div_a(format_info):
    if format_info:
        format_info = format_info.replace('<!DOCTYPE>', '').replace('<html>', '').replace('<title>', '').replace(
            '<body>', '').replace('<br>', '').replace('<br/>', '').replace('<hr>', '').replace('<!--...-->',
                                                                                               '').replace('<abbr>',
                                                                                                           '').replace(
            '<address>', '').replace('<b>', '').replace('<bdi>', '').replace('<bdo>', '').replace('<blockquote>',
                                                                                                  '').replace(
            '<cite>', '').replace('<code>', '').replace('<del>', '').replace('<dfn>', '').replace('<em>', '').replace(
            '<i>',
            '').replace(
            '<ins>', '').replace('<kbd>', '').replace('<mark>', '').replace('<meter>', '').replace('<pre>', '').replace(
            '<progress>', '').replace('<q>', '').replace('<rp>', '').replace('<rt>', '').replace('<ruby>', '').replace(
            '<s>',
            '').replace(
            '<samp>', '').replace('<small>', '').replace('<strong>', '').replace('<sub>', '').replace('<sup>',
                                                                                                      '').replace(
            '<time>', '').replace('<u>', '').replace('<var>', '').replace('<wbr>', '').replace('<form>', '').replace(
            '<input>',
            '').replace(
            '<textarea>', '').replace('<button>', '').replace('<select>', '').replace('<optgroup>', '').replace(
            '<option>',
            '').replace(
            '<label>', '').replace('<fieldset>', '').replace('<legend>', '').replace('<datalist>', '').replace(
            '<output>',
            '').replace(
            '<iframe>', '').replace('<img>', '').replace('<map>', '').replace('<area>', '').replace('<canvas>',
                                                                                                    '').replace(
            '<figcaption>', '').replace('<figure>', '').replace('<audio>', '').replace('<source>', '').replace(
            '<track>',
            '').replace(
            '<video>', '').replace('<link>', '').replace('<nav>', '').replace('<ul>', '').replace(
            '<ol>',
            '').replace(
            '<li>', '').replace('<dl>', '').replace('<dt>', '').replace('<dd>', '').replace('<menu>', '').replace(
            '<commend>',
            '').replace(
            '<table>', '').replace('<caption>', '').replace('<th>', '').replace('<tr>', '').replace('<td>', '').replace(
            '<thead>', '').replace('<tbody>', '').replace('<tfoot>', '').replace('<col>', '').replace('<colgroup>',
                                                                                                      '').replace(
            '<style>', '').replace('<span>', '').replace('<header>', '').replace('<footer>',
                                                                                 '').replace(
            '<section>', '').replace('<article>', '').replace('<aside>', '').replace('<details>', '').replace(
            '<dialog>',
            '').replace(
            '<summary>', '').replace('<head>', '').replace('<meta>', '').replace('<base>', '').replace('<script>',
                                                                                                       '').replace(
            '<noscript>', '').replace('<embed>', '').replace('<object>', '').replace('<param>', '').replace('<main>',
                                                                                                            '').replace(
            '</html>', '').replace('</title>', '').replace('</body>', '').replace(
            '</br>', '').replace('</hr>', '').replace('</!--...-->', '').replace('</abbr>', '').replace('</address>',
                                                                                                        '').replace(
            '</b>',
            '').replace(
            '</bdi>', '').replace('</bdo>', '').replace('</blockquote>', '').replace('</cite>', '').replace('</code>',
                                                                                                            '').replace(
            '</del>', '').replace('</dfn>', '').replace('</em>', '').replace('</i>', '').replace('</ins>', '').replace(
            '</kbd>',
            '').replace(
            '</mark>', '').replace('</meter>', '').replace('</pre>', '').replace('</progress>', '').replace('</q>',
                                                                                                            '').replace(
            '</rp>', '').replace('</rt>', '').replace('</ruby>', '').replace('</s>', '').replace('</samp>', '').replace(
            '</small>', '').replace('</strong>', '').replace('</sub>', '').replace('</sup>', '').replace('</time>',
                                                                                                         '').replace(
            '</u>', '').replace('</var>', '').replace('</wbr>', '').replace('</form>', '').replace('</input>',
                                                                                                   '').replace(
            '</textarea>', '').replace('</button>', '').replace('</select>', '').replace('</optgroup>', '').replace(
            '</option>',
            '').replace(
            '</label>', '').replace('</fieldset>', '').replace('</legend>', '').replace('</datalist>', '').replace(
            '</output>',
            '').replace(
            '</iframe>', '').replace('</img>', '').replace('</map>', '').replace('</area>', '').replace('</canvas>',
                                                                                                        '').replace(
            '</figcaption>', '').replace('</figure>', '').replace('</audio>', '').replace('</source>', '').replace(
            '</track>',
            '').replace(
            '</video>', '').replace('</link>', '').replace('</nav>', '').replace('</ul>',
                                                                                 '').replace(
            '</ol>', '').replace('</li>', '').replace('</dl>', '').replace('</dt>', '').replace('</dd>', '').replace(
            '</menu>',
            '').replace(
            '</commend>', '').replace('</table>', '').replace('</caption>', '').replace('</th>', '').replace('</tr>',
                                                                                                             '').replace(
            '</td>', '').replace('</thead>', '').replace('</tbody>', '').replace('</tfoot>', '').replace('</col>',
                                                                                                         '').replace(
            '</colgroup>', '').replace('</style>', '').replace('</span>', '').replace('</header>',
                                                                                      '').replace(
            '</footer>', '').replace('</section>', '').replace('</article>', '').replace('</aside>', '').replace(
            '</details>',
            '').replace(
            '</dialog>', '').replace('</summary>', '').replace('</head>', '').replace('</meta>', '').replace('</base>',
                                                                                                             '').replace(
            '</script>', '').replace('</noscript>', '').replace('</embed>', '').replace('</object>', '').replace(
            '</param>',
            '').replace(
            '</main>', '').replace('<h1>', '').replace('<h2>', '').replace('<h3>', '').replace('<h4>', '').replace(
            '<h5>', '').replace('<h6>', '').replace('</h1>', '').replace('</h2>', '').replace('</h3>', '').replace(
            '</h4>', '').replace('</h5>',
                                 '').replace(
            '</h6>', '').replace("<!-->", "").replace("===", "")
    return format_info


def get_month_en(month_info):
    global month
    if month_info:
        if "Jan" in month_info or "jan" in month_info:
            month = "01"
        elif "Feb" in month_info or "feb" in month_info:
            month = "02"
        elif "Mar" in month_info or "mar" in month_info:
            month = "03"
        elif "Apr" in month_info or "apr" in month_info:
            month = "04"
        elif "May" in month_info or "may" in month_info:
            month = "05"
        elif "Jun" in month_info or "jun" in month_info:
            month = "06"
        elif "Jul" in month_info or "jul" in month_info:
            month = "07"
        elif "Aug" in month_info or "aug" in month_info:
            month = "08"
        elif "Sep" in month_info or "sep" in month_info:
            month = "09"
        elif "Sept" in month_info or "sept" in month_info:
            month = "09"
        elif "Oct" in month_info or "oct" in month_info:
            month = "10"
        elif "Nov" in month_info or "nov" in month_info:
            month = "11"
        elif "Dec" in month_info or "dec" in month_info:
            month = "12"
    return month


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
