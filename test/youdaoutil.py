#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-11-17 14:03
# @Author  : cjf
# @Version : 1.0
# @File    : youdaoutil.py
# @Software: PyCharm
# @Desc    : None
import hashlib
import json
import random
import time
from mylog.mlog import log
from utils.common import post_list_page_no_proxies
from utils.datautil import sleep_small


def youdao_id_en(con):
    global con_en
    num = 0
    while True:
        url_ = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        headers_ = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
            "Referer": "http://fanyi.youdao.com/",
            "Cookie": "OUTFOX_SEARCH_USER_ID=1652516314@10.108.160.100; OUTFOX_SEARCH_USER_ID_NCOO=120640644.01846737; JSESSIONID=aaaJTKtlJxbeXfLP5cwvx; ___rl__test__cookies=1603527703671"
        }
        input_data = con
        time_ = str(int(time.time() * 1000))  # 以毫秒为单位的时间戳
        time_salt = time_ + str(random.randint(0, 9))  # salt加盐操作 以毫秒为单位的时间戳 + 随机数字
        # 拼接字符串进行md5加密，生成sign值
        a = "fanyideskweb" + input_data + time_salt + "]BjuETDhU)zqSxf-=B#7m"
        sign = hashlib.md5(a.encode()).hexdigest()
        form_data = {
            "i": input_data,  # 要被翻译的数据
            "from": "id",
            "to": "cn",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": time_salt,  # 以毫秒为单位的时间戳 + 随机数字
            "sign": sign,  # 未知的js加密后的数据
            "lts": time_,  # 以毫秒为单位的时间戳
            "bv": "4abf2733c66fbf953861095a23a839a8",
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTlME",
        }
        try:
            st, con = post_list_page_no_proxies(url_, headers_, data=form_data)
            if st:
                con_ = json.loads(con)
                con_ = con_.get("translateResult")
                con_ = con_[0][0]
                con_en = con_['tgt']
        except:
            log.info("youdao erro")
            con_en = ""
        sleep_small()
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            # log.info(text)
            break
    return con_en


def id_con_to_cn_con(info, cn_info):
    global cn_content
    p_cons = info.split("</p><p>")
    cn_list = []
    for p_con in p_cons:
        p_con = u"" + p_con.replace("<p>", "").replace("</p>", "")
        if p_con:
            cn_con = youdao_id_en(p_con)
            if cn_con:
                cn_list.append(cn_con)
            else:
                cn_content = ""
                break
    cn_content = "</p><p>".join(cn_list)
    if cn_content.startswith("<p>"):
        cn_content = cn_content
    else:
        cn_content = "<p>" + cn_content
    if cn_content.endswith("</p>"):
        cn_content = cn_content
    else:
        cn_content = cn_content + "</p>"
    return cn_content

if __name__ == '__main__':
    contents_html = '<p>Menteri Pertahanan Prabowo Subianto. (ANTARA/ADITYA PRADANA PUTRA)</p><p>Jakarta (ANTARA) - Terdapat beberapa berita politik kemarin (Senin, 16/11) yang menjadi perhatian pembaca dan masih menarik untuk dibaca, yakni elektabilitas Prabowo Subianto dari hasil survei indEX hingga Komisi Nasional Hak Asasi Manusia (Komnas HAM) mengusulkan peringatan HAM Internasional pada 10 Desember 2020.</p><p>Berikut sejumlah berita politik kemarin yang masih menarik untuk dibaca hari ini:</p><p>Survei indEX: Elektabilitas Prabowo Subianto paling tinggi</p><p>Survei yang dilakukan oleh Indonesia Elections and Strategic (indEX) Research menunjukkan peta pertarungan menuju Pilpres 2024 masih dikuasai oleh Prabowo Subianto yang kembali unggul dan menjaga jarak dari pesaing utamanya, Ganjar Pranowo dan Ridwan Kamil.</p><p>"Sementara itu naiknya elektabilitas Prabowo juga diikuti dengan melorotnya Anies Baswedan dan Sandiaga Uno," kata Direktur Eksekutif indEX Research Vivin Sri Wahyuni dalam siaran pers di Jakarta, Senin.</p><p>Selengkapnya di sini</p><p>Komnas HAM serahkan laporan kematian Pendeta Yeremia ke Presiden</p><p>Komnas HAM menyerahkan laporan hasil penyelidikan perkara kasus kematian Pendeta Yeremia Zanambani di Intan Jaya, Papua kepada Presiden Joko Widodo.</p><p>"Yang juga serius kami bicarakan soal kasus penembakan Pendeta Yeremia hasil temuan Komnas HAM kepada Bapak Presiden dan lebih jauh soal Papua," kata Ketua Komnas HAM Ahmad Taufan Damanik di lingkungan Istana Kepresidenan RI, Jakarta, Senin.</p><p>Selengkapnya di sini</p><p>Wapres: Indonesia masih kekurangan lembaga keuangan mikro syariah</p><p>Wakil Presiden Ma’ruf Amin mengatakan Indonesia, sebagai negara dengan jumlah penduduk Muslim terbesar di dunia, masih sedikit memiliki jumlah lembaga keuangan mikro berbasis syariah; sehingga perlu dibangun lebih banyak Baitul Maal wa Tamwil (BMT).</p><p>"Indonesia, sebagai negara dengan 221 juta penduduk Muslim, masih kekurangan lembaga keuangan mikro syariah. Oleh karena itu, perlu dibangun pusat pelatihan lembaga mikro syariah di berbagai daerah, sebagai pusat pembinaan dan pengembangan BMT," kata Ma’ruf Amin saat membuka web seminar BMT Summit 2020 secara virtual dari Jakarta, Senin.</p><p>Selengkapnya di sini</p><p>KPU Makassar tetapkan debat kedua di Jakarta</p><p>KPU Kota Makassar menetapkan debat publik kedua akan dilaksanakan di Kota Jakarta.</p><p>“Dengan berbagai pertimbangan, debat kedua akan tetap dilaksanakan di Jakarta. Untuk waktunya antara tanggal 23 atau 24 November 2020 ini,” kata Komisioner Endang Sari usai melakukan rapat dengan pihak keamanan di salah satu hotel di Makassar, Senin.</p><p>Selengkapnya di sini</p><p>Komnas HAM sampaikan usulan ke Presiden soal Hari HAM Internasional</p><p>Komisi Nasional Hak Asasi Manusia (Komnas HAM) menyampaikan secara langsung usulan atau rekomendasi kepada Presiden RI Joko Widodo untuk memperingati Hari HAM Internasional pada 10 Desember 2020.</p><p>Usai bertemu Presiden Jokowi, Ketua Komnas HAM Ahmad Taufan Damanik di kompleks Istana Kepresidenan, Jakarta, Senin, mengatakan bahwa pihaknya mengusulkan agar Presiden tidak hanya berpidato soal Hari HAM Internasional pada tahun ini, tetapi pidato Hari HAM Internasional agar dijadikan seremonial kelembagaan negara setiap tahun sehingga menjadi bentuk penghormatan terhadap HAM.</p><p>Selengkapnya di sini</p>'
    con = id_con_to_cn_con(contents_html,"")
    print(con)
