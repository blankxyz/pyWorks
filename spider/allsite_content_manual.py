#!/usr/bin/python
# coding=utf-8

import re
import os
import datetime
import urlparse
import htmlparser
import redis
import spider
import setting
import urllib
import ConfigParser
from bs4 import BeautifulSoup, Comment
import requests
import allsite_clean_url

####################################################################
# INIT_CONFIG = '/work/spider/run_allsite.ini' #linux
# INIT_CONFIG = './run_allsite.ini' #windows
INIT_CONFIG = '/Users/song/workspace/pyWorks/spider/run_allsite.ini'  # mac
####################################################################
config = ConfigParser.ConfigParser()
if len(config.read(INIT_CONFIG)) == 0:
    print '[ERROR]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[INFO] read the config file.', INIT_CONFIG

# redis
REDIS_SERVER = config.get('redis', 'redis_server')
DEDUP_SETTING = config.get('redis', 'dedup_server')

# spider-modify-start
# START_URLS = None
# SITE_DOMAIN = None
# BLACK_DOMAIN_LIST = None
# DETAIL_RULE_LIST = None
# LIST_RULE_LIST = None
# spider-modify-end

START_URLS = config.get('spider', 'start_urls')
SITE_DOMAIN = config.get('spider', 'site_domain')
BLACK_DOMAIN_LIST = config.get('spider', 'black_domain_list')
DETAIL_RULE_LIST = config.get('spider', 'detail_rule_list')
LIST_RULE_LIST = config.get('spider', 'list_rule_list')

TITLE_EXP = None
CONTENT_EXP = None
AUTHOR_EXP = None
CTIME_EXP = None

#############################################################################

class MySpider(spider.Spider):
    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(
            self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)
        # 网站名称
        self.siteName = "all"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.start_urls = START_URLS
        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.detail_urls_set_key = 'detail_urls_set_%s' % self.site_domain  # 输入详情页URL
        self.todo_urls_limits = 100
        self.dedup_key = 'dedup'

    def get_start_urls(self, data=None):
        return [self.start_urls]

    def parse(self, response):
        urls = []
        for i in range(self.todo_urls_limits):
            url = self.conn.spop(self.detail_urls_set_key)
            if url is not None or url != '':
                urls.append(url)

        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        # print '[INFO]parse_detail_page() start'
        try:
            response.encoding = self.encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception, e:
            print "parse_detail_page(): %s" % e
            return None
        if url is None:
            url = response.request.url

        result = []
        title = data.xpath('''//tr[@valign="top"]//strong''').text().strip()
        source = self.siteName
        ctime = data.xpath('''//td[@align="middle"]/text()'''). \
            replace(u'年', '-').replace(u'月', '-').replace(u'日', '').regex('(\d+-\d+-\d+)').datetime()
        content = data.xpath('''//div[@id="ozoom"]''').text().strip()
        utc_now = datetime.datetime.utcnow()
        post = {'title': title,
                'content': content,
                'ctime': ctime,
                'gtime': utc_now,
                'source': source,
                'siteName': self.siteName,
                'data_db': self.data_db,
                'url': url,
                }
        result.append(post)
        return result

##### ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        print '[spider simulation] now starting ..........'
        for cnt in range(10000):
            print '[loop]', cnt, '[time]', datetime.datetime.utcnow()
            detail_job_list = []  # equal to run.py detail_job_queue

            # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
            def __detail_page_urls(urls, func):
                next_page_url = None
                if func is not None:
                    if urls:
                        for url in urls:
                            try:
                                response = mySpider.download(url)
                                list_urls, callback, next_page_url = func(response)  # parse()
                                for url in list_urls:
                                    detail_job_list.append(url)
                            except Exception, e:
                                print '[ERROR] main() Exception: %s' % e
                                list_urls, callback, next_page_url = [], None, None

                            __detail_page_urls(list_urls, callback)

                            if next_page_url is not None:
                                print 'next_page_url'
                                __detail_page_urls([next_page_url], func)

            # --equal to run.py list_page_thread() -------------------------
            mySpider = MySpider()
            mySpider.proxy_enable = False
            mySpider.init_dedup()
            mySpider.init_downloader()
            start_urls = mySpider.get_start_urls()  # get_start_urls()
            print '[test]start_urls:', start_urls
            __detail_page_urls(start_urls, mySpider.parse)  # parse()

            # --equal to run.py detail_page_thread() -------------------------
            ret = []
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                for item in ret:
                    for k, v in item.iteritems():
                        print k, v
    else:  # ---------- unit test -----------------------------
        print '[unit test] now starting ..........'
        url = 'http://bbs.tianya.cn/post-41-1236689-1.shtml'
        # url = 'http://cpt.xtu.edu.cn/a/keyanchengguo/keyanxiangmu/2013/0414/109.html'
        print 'url:', url
        mySpider = MySpider()
        # 预置数据
        # 预置匹配规则
        mySpider.get_start_urls()
        # mySpider.init_downloader()
        # resp = mySpider.download(url)
        # soup = mySpider.get_clean_soup(resp)
        # ----------------------------------------------------------

if __name__ == '__main__':
    test(unit_test=False)
    # test(unit_test=True)
    # import cProfile
    # cProfile.run("test(unit_test = False)")
