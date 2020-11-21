# -*- encoding:utf-8 -*-
import sys


sys.path.append('..')
import time
import json
import execjs
import requests
from retry import retry
from mylog.mlog import log
from utils.get_ips import get_ip

if sys.version_info[0] == 2:  # Python 2
    pass
else:  # Python 3
    pass
import locale

locale.getdefaultlocale()[1]

headers = {
    "User-Agent": "Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11",
    "cookie": "_ga=GA1.3.601448104.1547798526; _gid=GA1.3.1453839211.1547798526; 1P_JAR=2019-1-18-9; NID=156=XjyaaJc-Uth1E6-WwtVYETyLCEXqtEKL9G8xxLlOSX0lIVehPC8uE_hdsJqEMAbu2eSjcEG8Aq5WRawU9JQsirT2VESCsYnlCmBwK4cbWYNMgNkUVgLO_dH1YbJnKUY-UhcImcYCJ8u6MnT3Pnwb7CkmyxrWpWfcFvzatvgFj0w"
}

proxies = get_ip()


class Py4Js(object):
    def __init__(self):
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 
        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 

        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 

    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)

    def getTk(self, text):
        return self.ctx.call("TL", text)


@retry(tries=3)
def translate(content):
    # try:
    if len(content) == 0:
        texts = ''
        return texts
    js = Py4Js()
    tk = js.getTk(content)
    # content = quote(content)
    url = "https://translate.google.cn/translate_a/single?client=webapp&sl=auto&tl=en&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=gt&ssel=0&tsel=3&kc=0&tk={}".format(
        tk)
    data = {"q": content}
    response = requests.post(url, data=data, headers=headers, proxies=proxies)
    result = response.content
    item = json.loads(result)
    texts = ""
    for i in range(0, len(item[0])):
        if str(item[0][i][0]) != "None":
            texts += str(item[0][i][0])
    return texts
    # except:
    #       return ""


# @retry(tries=3)
def translate_zh(content, info_cn):
    num = 0
    while True:
        try:
            if len(content) == 0:
                return ""
            js = Py4Js()
            tk = js.getTk(content)
            url = "https://translate.google.cn/translate_a/single?client=webapp&sl=" + info_cn + "&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&pc=1&otf=1&ssel=0&tsel=0&kc=1&tk={}".format(
                tk)
            data = {"q": content}
            response = requests.post(url, data=data, headers=headers, proxies=proxies)
            result = response.content
            item = json.loads(result)
            translated = ""
            for i in range(0, len(item[0])):
                if str(item[0][i][0]) != "None":
                    translated += str(item[0][i][0])
        except Exception as e:
            time.sleep(1)
            translated = ""
        if translated:
            break
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            time.sleep(1)
        break
    return translated


# 将英文翻译成中文
@retry(tries=3)
def zh(content):
    texts = ""
    # try:
    if len(content) == 0:
        return texts
    js = Py4Js()
    tk = js.getTk(content)
    # content = quote(content)
    url = "https://translate.google.cn/translate_a/single?client=webapp&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&otf=1&ssel=3&tsel=6&kc=4&tk={}&q={}".format(
        tk, content)
    response = requests.get(url, headers=headers, proxies=proxies)
    result = response.content
    item = json.loads(result)

    for i in range(0, len(item[0])):
        if str(item[0][i][0]) != "None":
            texts += str(item[0][i][0])
    return texts


# 意大利语翻中文
@retry(tries=3)
def it(content):
    texts = ""
    # try:
    if len(content) == 0:
        return texts
    js = Py4Js()
    tk = js.getTk(content)
    # content = quote(content)
    url = "https://translate.google.cn/translate_a/single?client=webapp&sl=it&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&otf=1&ssel=3&tsel=6&kc=4&tk={}&q={}".format(
        tk, content)
    response = requests.get(url, headers=headers, proxies=proxies)
    result = response.content
    item = json.loads(result)

    for i in range(0, len(item[0])):
        if str(item[0][i][0]) != "None":
            texts += str(item[0][i][0])
    return texts


# except Exception as e:
#     print e
#     return ""


def split_string(str, cutting_method):
    item = str.split(cutting_method)
    interception_len = len(item) / 2
    interception1 = ".".join(item[:interception_len])
    interception2 = ".".join(item[interception_len:len(item)])
    return interception1, interception2


def get_string(str, cutting_method):
    list = []
    interception1, interception2 = split_string(str, cutting_method)
    if len(interception1) > 5000:
        list1 = get_string(interception1, cutting_method)
        list = list + list1
    else:
        list.append(interception1)
    if len(interception2) > 5000:
        list1 = get_string(interception2, cutting_method)
        list = list + list1
    else:
        list.append(interception2)
    return list


# 自动检测语言后翻译成英文
def get_translate(context):
    str = ""
    if len(context) > 5000:
        list = get_string(context, ".")
        count = 0
        for item in list:
            count += 1
            if count != len(list):
                item = item + "."
            str += translate(item)
    else:
        str = translate(context)
    print('-------------', str)
    return str


# 检测语言后翻译成中文
def get_translate_zh(context):
    global str
    if len(context) > 5000:
        list = get_string(context, ".")
        count = 0
        for item in list:
            count += 1
            if count != len(list):
                item = item + '.'
            str += translate_zh(item)
    else:
        str = translate_zh(context)
    return str


# 英文翻译中文
@retry(tries=3)
def get_zh(context):
    str = ""
    if len(context) > 5000:
        list = get_string(context, ".")
        count = 0
        for item in list:
            count += 1
            if count != len(list):
                item = item + "."
            str += zh(item)
    else:
        str = zh(context)
    return str


if __name__ == '__main__':
    # print get_zh('A man killed his daughter, son-in-law and two grandsons in the Jalalpur area. His motive was reportedly that his daughter chose her own husband four years ago.The incident took place in Pindi Bhattian, according to SAMAA TV correspondent Bilal Akbar.According to the police all four were killed using a sharp blade.The bodies have been sent to the local taluka headquarters hospital.The authorities say the man fled after the incident but the police were able to arrest him after conducting raids. A case has been registered against him at the Jalalpur Bhattian police station.')
    # print get_translate_zh("Topman Ren Zhengfei wast zijn handen in onschuld. Dan doen we gewoon beter ons best voor de landen die ons wel verwelkomen, zei hij dinsdag. Zijn lidmaatschap van de communistische partij betekent niet dat hij zijn klanten, waar dan ook ter wereld, zou schaden. ‘Het principe van handel is: de klant gaat voor. Mijn politieke overtuiging en zakelijk handelen zijn niet noodzakelijk intiem met elkaar verstrengeld.’Het voor Huawei rampzalige jaar 2018 werd afgerond met de arrestatie van Rens dochter Meng Wanzhou, financieel hoofd van het bedrijf. Ze werd vorige maand in Canada opgepakt op verzoek van de Verenigde Staten, die haar van fraude en het schenden van sancties met Iran beschuldigen. In Vancouver wacht ze onder strenge bewaking af of het daadwerkelijk tot uitlevering komt.Canadese clashDe verhoudingen tussen Canada en China zijn sindsdien ijzig. In China zijn bij wijze van vergeldingsmaatregel enkele Canadezen opgepakt, bijvoorbeeld met vage aantijgingen van spionage. Beijing voerde maandag de druk een tandje op: een Canadese man die betrokken zou zijn bij de smokkel van ruim 200 kilo amfetamine kreeg de doodstraf. Eerder was hij in een proces dat 2,5 jaar duurde tot vijftien jaar veroordeeld, maar in hoger beroep kwam de rechtbank in Dalian binnen enkele uren tot de conclusie dat die straf te licht was. De Canadese regering heeft dinsdag Beijing om genade gevraagd.")
    # print(get_zh('hello').decode('utf-8'))
    # s = Py4Js()
    # get_translate_zh('[ โยธิน เปาอินทร์ กับ การดูแลผู้สูงอายุ ผู้ป่วยติดเตียงเพื่อลดความเหลื่อมล้ำในจังหวัดอ่างทอง ] . อีกเพียง 53 วัน ก็จะถึงวันที่ 20 ธันวาคม 2563 ที่จะมีการเลือกตั้งท้องถิ่นครั้งสำคัญ เพราะเป็นการเลือกตั้งท้องถิ่นครั้งแรกในรอบเกือบสิบปี . สนามการเลือกตั้งท้องถิ่นแรก คือ สนามระดับองค์การบริหารส่วนจังหวัด หรือ อบจ. . พวกเรา #คณะก้าวหน้า ตั้งใจทำงานการเมืองท้องถิ่นให้ดี นำเสนอนโยบายที่ตอบสนองความต้องการของประชาชน ผู้สมัครนายก อบจ. จังหวัดอ่างทองในนามของคณะก้าวหน้า คือ โยธิน เปาอินทร์ . คุณโยธินมีความฝันอยากเห็นสังคมที่เท่าเทียม เขาต้องการลดระดับความเหลื่อมล้ำในสังคม หากเขาได้รับความไว้วางใจจากประชาชนในจังหวัดอ่างทอง คุณโยธินตั้งใจลงทุนสร้างศูนย์บริบาลผู้สูงอายุและผู้ป่วยติดเตียงในทุกอำเภอ และสร้างศูนย์ฟอกไตเพิ่มในจังหวัด . ครอบครัวที่มีผู้สูงอายุที่ช่วยเหลือตัวเองไม่ได้ ผู้ป่วยติดเตียง และผู้ป่วยไตเรื้อรัง มักเป็นครอบครัวที่มีความเครียดสูง การดูแลผู้ป่วยเหล่านี้ต้องใช้คนดูแลเต็มเวลา ไม่ว่าจะเพื่อป้อนอาหาร การพลิกตัว ทำความสะอาด หรือการพาไปฟอกไตสัปดาห์ละสองครั้ง แต่ละครั้งใช้เวลาแทบจะทั้งวันในการเดินทางและการรักษา . สมาชิกในครอบครัวอย่างน้อยหนึ่งคนต้องเสียโอกาสในการทำมาหากินเพื่อดูแลผู้ป่วย สมาชิกคนอื่นต้องแบกรับภาระทางเศรษฐกิจแทนผู้ป่วยและคนดูแล . สวัสดิการสาธารณสุขที่ไม่เพียงพอของภาครัฐทำให้ประชาชนต้องแบกรับปัญหาเหล่านี้ด้วยตัวเอง สำหรับครอบครัวที่มีรายได้น้อย หากมีผู้สูงอายุ ผู้ป่วยติดเตียง หรือผู้ป่วยไต เหมือนยิ่งถูกซ้ำเติมให้ยากจนลงอีก . ศูนย์บริบาลผู้ป่วยติดเตียงและผู้สูงอายุที่เราออกแบบไว้เป็นนโยบายที่ผู้สมัคร นายก อบจ. ของคณะก้าวหน้าหลายจังหวัดนำไปประยุกต์ใช้เป็นนโยบาย . ที่ จ.อ่างทอง คุณโยธินต้องการสร้างศูนย์บริบาลขนาด 20 เตียงทั้ง 7 อำเภอ อำเภอละแห่ง โดยใช้งบประมาณศูนย์ละ 25 ล้านในการก่อสร้าง ภายใต้งบประมาณที่จำกัด คุณโยธินวางแผนลงทุนไว้ปีละ 2 อำเภอ จะได้ครบ 7 ศูนย์ 7 อำเภอ ในเวลา 4 ปีของสมัยบริหารพอดี . ในศูนย์บริบาลนี้ มีบริการดูแลผู้ป่วยติดเตียงและผู้สูงอายุรายวัน และระยะสั้น บริการกายภาพบำบัด มีห้องสันทนาการและพื้นที่กิจกรรม เช่น หนังสือ หมากรุก ทีวี และวงสนทนา ในราคาที่ย่อมเยาและได้มาตรฐาน . จังหวัดอ่างทองเป็นจังหวัดที่มีสัดส่วนผู้สูงอายุต่อประชากรทั้งจังหวัดเยอะเป็นอันดับ 7 ของประเทศ (ดูภาพตารางประกอบ) การมีบริการเข่นนึ้จะช่วยลดภาระครอบครัวที่ลำบากได้ เช่น หากสมาชิกในครอบครัวต้องเดินทางไปค้าขายค้างคืนต่างจังหวัดก็สามารถนำผู้ป่วยมาฝากรับบริการที่ศูนย์ได้ . นอกจากนี้ คุณโยธินยังเห็นว่าในอ่างทองมีโรงเรียนขนาดเล็กที่ถูกยุบรวม แล้วอาคารถูกปล่อยให้ว่างเปล่าเป็นจำนวนหนึ่ง หากเราสามารถขอถ่ายโอนโรงเรียนเปล่านี้จากกระทรวงศึกษาธิการ แล้วมาตกแต่งใหม่เป็นศูนย์บริบาล ก็จะลดเงินลงทุนก่อสร้างได้อีก . อ่างทองมีงบประมาณ อบจ. ปีละประมาณ 350 ล้านบาท หนึ่งวาระหรือ 4 ปี ผู้บริหารมีงบประมาณ 1,400 ล้านบาท  . ผมเชื่อว่าหากงบประมาณจำนวนนี้ถูกนำมาใช้อย่างมีประสิทธิภาพ ไม่มีการโกงกิน คนอ่างทองต้องเห็นการเปลี่ยนแปลงในทางที่ดีขึ้นในจังหวัดอย่างแน่นอน . ขอเชิญประชาชนชาวอ่างทองไปใช้สิทธิเลือกตั้งท้องถิ่นครั้งแรกในรอบเกือบสิบปีในวันที่ 20 ธันวาคม 2563 ให้โอกาสคุณโยธินได้เข้าไปบริหาร อบจ. เพื่อสร้างอ่างทองให้ดีกว่านี้ . #เปลี่ยนประเทศไทยเริ่มได้ที่บ้านเรา')
    print(it(
        'Centrodestra nel caos, in un giorno segnato dallo scontro frontale tra Lega e Forza Italia: Matteo Salvini accusa gli azzurri di fare \'inciuci\' con il nemico e di pensare ai "rimpasti", Silvio Berlusconi, in serata, cerca di gettare acqua sul fuoco, ma invano. Prima parla di "presunte divergenze con forze alleate", poi però picchia duro ricordando alla coalizione che senza il suo partito in Italia ci sarebbe "una destra isolata e perdente" come il Front National francese.'))
