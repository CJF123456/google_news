#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 9:28
# @Author  : chenjianfeng
# @Site    :
# @File    : common.py
# @Software: PyCharm

import sys



sys.path.append('..')
import textwrap
from googletrans import Translator
from mylog.mlog import log
from utils.langconv import Converter
from utils.tran_google import translate_zh

# id 印尼 en 英文
def translated_cn_google(text, cn_info):
    global translated
    num = 0
    while True:
        try:
            translator = Translator(service_urls=['translate.google.cn'])
            translated = translator.translate(text, src=cn_info, dest='zh-cn').text.lstrip().strip()
        except Exception as e:
            # log.info(e)
            # log.info(text)
            translated = ""
        if translated:
            break
        num = num + 1
        if num >= 10:
            translated = ""
            log.info("translator fail")
            # log.info(text)
            break
    return translated


def en_con_to_cn_con_google(info, cn_info):
    global cn_content
    p_cons = info.split("</p><p>")
    cn_list = []
    for p_con in p_cons:
        p_con = u"" + p_con.replace("<p>", "").replace("</p>", "")
        if p_con:
            cn_con = translated_cn_google(p_con, cn_info)
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


def translated_cn(context, cn_info):
    translated = translate_zh(context,cn_info)
    return translated

def en_con_to_cn_con(tran_str, cn_info):
    global cn_content
    tran_str_ = tran_str.replace("</p><p>", "2021112323").replace("<p>", "").replace("</p>", "")
    no_cn_contents = []
    cn_contents = []
    if len(tran_str_) < 4999:
        no_cn_contents.append(tran_str_)
    else:
        no_con_s = textwrap.wrap(tran_str_, 4999)
        for no_con_ in no_con_s:
            no_cn_contents.append(no_con_)
    for no_cn_content in no_cn_contents:
        cn_con=translated_cn(no_cn_content, cn_info)
        if "重播重播视频" in cn_con:
            pass
        else:
            cn_contents.append(cn_con)
    cn_content = "".join(cn_contents).replace("2021112323", "</p><p>").replace("\n", "").strip().lstrip()
    if cn_content.startswith("<p>"):
        cn_content = cn_content.strip().lstrip()
    else:
        cn_content = "<p>" + cn_content.strip().lstrip()
    if cn_content.endswith("</p>"):
        cn_content = cn_content.strip().lstrip()
    else:
        cn_content = cn_content + "</p>"
    cn_content = cn_content.replace("\n", "").strip().lstrip()
    return cn_content


if __name__ == '__main__':
    contents_html='<img src="http://apposs2020.oss-cn-beijing.aliyuncs.com/411e13c0a7e8a53440a379bf28571de1.png"/> <p>In order to address the authoritarian resurgence, democracies have a values-based competitive advantage, observers suggest. The incoming U.S. administration needs to link foreign aid and democracy assistance to a broader strategy of democratic transformation, establishing “a blue ribbon commission to rethink democracy promotion” and work through the National Endowment for Democracy (NED). </p> <p>Today’s competition between democracies and authoritarian powers is more than a power struggle: values lie at its heart. For democracies to succeed, they need not only to act in accordance with their values but also to understand that those values are their principal competitive advantage, and to use them as the source of strength that they are, argue Zack Cooper and Laura Rosenberger.</p> <p>The current contest between democracies and autocracies takes place in the political, economic, technological, and information spaces, where authoritarian challengers—especially China and Russia—have seized the initiative, they write for Foreign Affairs: </p> <p> Offsetting autocratic advances will require democracies to seize on the advantagesinherent to their open systems. They must build resilience into democratic institutions by increasing political and financial transparency, protecting voting rights, addressing systemic racism and inequality, bolstering independent media, and strengthening civil society. At the same time, they can exploit the brittleness of authoritarian systems by harnessing truthful information and exposing corruption. </p> <p>A values-based strategy to counter authoritarianism may require democratic policymakers to think and organize themselves in new ways in order to compete in a contest that blurs distinctions between offense and defense and among domestic, economic, and foreign policies, Cooper and Rosenberger suggest.</p> <p> The fading light of liberal democracy https://t.co/xhPMKDMImbvia @financialtimes </p><p> — Democracy Digest (@demdigest) December 22, 2020 </p> <p>The incoming U.S. administration needs to “connect foreign assistance and democracy promotion for a larger strategy of democratic transformation,” including the establishment of “a blue ribbon commission to rethink democracy promotion in our international broadcasting institutions like Radio Free Europe and Voice of America,” says Melinda Haring, Deputy Director of the Eurasia Center at the Atlantic Council. </p> <p>“They need to be more selective about the place where they work and not waste our dollars,” she tells a National Interest symposium, adding that the USG should work through the National Endowment for Democracy (NED).“It’s not about how much you spend, but it’s really about efficacy,” she adds. </p> <p>But this amounts to “democracy lite, democracy promotion lite,” argues the University of Chicago’s John Mearsheimer. “We’re no longer in a unipolar world where the United States could ignore great power politics and concentrate on democracy promotion,” he tells the symposium. “We are now in a multipolar world, we’re facing a pure competitor, and we don’t have the time to engage seriously in democracy promotion.” </p> <p>The new Congressional appropriations bill provides fresh resources for democracy assistance: </p> <p> Connect politics to economics </p> <p>“For the first time this century, among countries with more than 1m people, there are now fewer democracies than there are non-democratic regimes.” This sobering sentence is by the Oxford university historian Timothy Garton Ash in an essay on “ The Future of Liberalism”. The observation reflects what Stanford University’s Larry Diamond labels the “democratic recession”. To understand what is happening, one must connect politics to economics, notes analyst Martin Wolf. </p> <p>Former World Bank economist Branko Milanovic, argued in Capitalism Alone, published last year, that capitalist economies go with two distinct political systems in leading economies: the “liberal” model of the US and its allies and China’s “political” model. But a third political version of capitalism exists: demagogic authoritarian capitalism, he writes for the FT: </p> <p> This can arise out of collapsed communism, as in today’s Russia, or out of enfeebled democracy, as in Brazil or Turkey. Demagogic authoritarian capitalism is a hybrid. As in the Chinese system of bureaucratic authoritarian capitalism, the ruler is above the law and democratically unaccountable — elections are a sham. But power is personal, not institutionalised. This is corrupt gangster politics. It rests on the personal loyalty of sycophants and cronies. </p> <p>“Liberal democracy does have one big advantage: its main opponent,” Wolf adds. “As Harvard’s Samantha Power notes, China’s approval rating in Gallup polling is a median of 32 per cent among over 130 countries. It has hardly budged in 10 years. People respect China, but do not like it. China also confronts the challenge of sustaining economic dynamism without a credible rule of law.” </p> <p> Democratic Values Are a Competitive Advantage https://t.co/9fqrluvIdkvia @ForeignAffairs </p><p> — Democracy Digest (@demdigest) December 22, 2020 </p> <p> ‘Russia is what it is’? </p> <p>If you would listen to people in Washington carefully, it seems that they’re talking about a major interference in Russian domestic politics,” adds Dmitri K. Simes, President and CEO of the Center for the National Interest: </p> <p> It’s not some time far away, but actually only several months from now on the eve of Russian parliamentary elections in September 2021, with a real desire to create problems for Putin’s authoritarian regime. Now, Putin’s authoritarian regime, to put it mildly, is not a model of democracy. And there are a lot of issues with Russian law, with Russian compliance with international norms, and, of course, with Russian attitude to the United States. But Russia is what it is. </p> <p>“Democracy is not a state,” the late Congressman John Lewiswrote this summer. “It is an act,” argue analysts David Adlerand Stephen Wertheim.The Biden administration should apply Lewis’s parting insight not only by restoring democratic norms but also and especially by promoting democratic rule. Rather than fixate on the symptoms of democratic discontent – the “populists, nationalists and demagogues” whom Biden has pledged to confront – his administration should attack the disease, they write for the Guardian. </p> <p>Does U.S. support for advancing democracy create an incentive for autocrats to collaborate? </p> <p>“The US does believe that individuals have endowed rights that are being denied them by the Russian government and the Chinese government,” adds Harvard University’s Graham Allison: </p> <p> That means that in the US agenda, regime change to democracy is not an implausible thing for an autocratic leader like Putin or Xi to worry about. Indeed, when Xi and Putin get together, what do they talk about? They talk about, “The American threat to our good governance of our regimes. Namely, to get rid of me.” So if you’re trying to drive two parties together, a very good way to do that is to persuade each of them that your aspiration is to change their regime. </p>'


    ss = en_con_to_cn_con(contents_html, 'en')
    #print(ss)


def cat_to_chs(sentence):  # 传入参数为列表
    """
    将繁体转换成简体
    :param line:
    :return:
    """
    sentence = ",".join(sentence)
    sentence = Converter('zh-hans').convert(sentence)
    sentence.encode('utf-8')
    return sentence.split(",")
