#!/usr/bin/env python
# coding=utf-8

import re
import cgi
import json
import urllib
import datetime
import urlparse
from pprint import pprint

import redis

import spider
import setting
import htmlparser


class MySpider(spider.Spider):
    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)
        # 网站名称
        self.siteName = "sina"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"

        self.start_urls = 'http://www.sina.com.cn/'
        self.encoding = 'utf8'
        self.site_domain = 'sina.com.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/8')
        # self.all_urls_list_key = 'all_urls_list_%s'%self.site_domain
        self.all_urls_zset_key = 'all_urls_zset_%s' % self.site_domain

        self.max_level = 6  # 最大级别
        self.dedup_key = None

    def clean_links(self, urls):
        new_urls = []
        for url in urls:
            url = url.split('#')[0]
            url = url.split('?')[0]
            url = url.strip()
            if 'http' not in url[0:5] or self.site_domain not in url:
                continue
            if '.jpg' in url or '.png' in url:
                continue
            new_urls.append(url)
        return new_urls

    def is_list_page(self, url):
        return True

    def get_breadcrumb(self, data):
        '''
        1）"breadcrumb"
        //div[contains(@class,"bread")]
        //div[contains(@class,"crumb")]
        2）'>' ‘>>’
        3）//div[contains(@class,'nav')] or
           Nav NAV
        4) 文字长度小于7
        '''
        return []

    def get_urlLevel(self, url):
        # todo get url's level from redis score
        return 0

    def get_start_urls(self, data=None):
        if self.conn.zadd(self.all_urls_zset_key, 0, self.start_urls):
            self.conn.lpush('all_urls_list_%s' % self.site_domain, self.start_urls)
        return [None]

    def parse(self, response):
        urls = []
        try:
            response.encoding = self.encoding
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            from_url = response.content.url
            links = data.xpathall("//a[@href] | //iframe[@src]")
            links = self.clean_links(links)
            # todo convert link to url format
            for link in links:
                if self.is_list_page(link):
                    level = self.get_urlLevel(from_url)
                    if level < self.max_level:
                        self.conn.zadd(self.all_urls_zset_key, level + 1, link)
                else:
                    self.conn.zadd(self.all_urls_zset_key, self.max_level, link)
                    urls.append(link)
            return (urls, None, None)
        except Exception, e:
            print "parse(): %s" % e
            return ([], None, None)

    def parse_detail_page(self, response=None, url=None):
        urls = []
        try:
            response.encoding = self.encoding
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)

            urls = self.get_breadcrumb(data)

            return urls
        except Exception, e:
            print "parse_detail_page(): %s" % e
            return []


if __name__ == '__main__':
    global detail_job_list  # equal to run.py detail_job_queue
    detail_job_list = []


    # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_job_queue) -----
    def __detail_page_urls(urls, func):
        print '-' * 80
        if func is not None:
            if urls:
                for url in urls:
                    response = mySpider.download(url)
                    try:
                        list_urls, callback, next_page_url = func(response)  # parse()
                        for url in list_urls: detail_job_list.append(url)
                    except Exception, e:
                        print 'Exception'
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
    __detail_page_urls(start_urls, mySpider.parse)  # parse()

    # --equal to run.py detail_page_thread() -------------------------
    ret = []
    for url in detail_job_list:
        resp = mySpider.download(url)
        ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
        for item in ret:
            for k, v in item.iteritems():
                print k, v
