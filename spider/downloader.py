#!/usr/bin/env python
# coding:utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：downloader.py
功能：该模块实现网页下载； 
　　　目前实现的功能有：
　　　　　随机切换代理
      支持　content-encoding：　gzip　deflate
      retry
      redirect
代码历史：
2014-02-27：庞  威，代码创建
'''

import time
import copy
import random
import logging

import requests

import log
import proxy
import setting
import util


class Downloader(object):
    def __init__(self, proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 available_proxy=setting.PROXY_AVAILABLE,
                 proxy_url=setting.PROXY_URL,
                 cookie_enable=setting.COOKIE_ENABLE,
                 timeout=setting.HTTP_TIMEOUT):
        super(Downloader, self).__init__()

    def download(self, request, **kwargs):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
                   'Connection': 'keep-alive',
                   'Cookie': 'PREF=f1=1222&cvdm=list',
                   'Host': 'www.youtube.com',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
                   }
        proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}

        response = requests.get(url=request, proxies=proxies, headers=headers)
        return response


if __name__ == '__main__':
    url = 'https://www.youtube.com'
    downloader = Downloader()
    resp = downloader.download(url)
    print resp.text