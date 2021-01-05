#coding=utf-8
import json

import requests

def get_ip():
    #请求地址
    url = "http://tiqu.linksocket.com:81/abroad?num=1&type=2&lb=1&sb=0&flow=1&regions=tw&n=0"
    response = requests.get(url=url)
    result = response.text
    details = json.loads(result)
    proxyHost = details['data'][0]['ip']
    proxyPort = details['data'][0]['port']
    #代理服务器
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }

    proxies = {
        "http" : proxyMeta,
        "https" : proxyMeta
    }
    return proxies


if __name__ == '__main__':
    proxies = get_ip()
    print(proxies)
    exit(-1)
    targetUrl = 'https://www.philstar.com/headlines'
    resp = requests.get(targetUrl, proxies=proxies)
    print(resp.status_code)
    print(resp.text)