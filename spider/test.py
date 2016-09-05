#!/usr/bin/python
#coding=utf-8

import datetime
import spider
import htmlparser
from urlparse import urljoin
import re


class MySpider(spider.Spider):
    def __init__(self, cmd_args=None):
        spider.Spider.__init__(self, cmd_args=cmd_args)
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.siteName = "tianyya"
        self.site_domain = 'bbs.tianya.cn'
        self.start_urls = [
            'http://bbs.tianya.cn/post-41-1236689-1.shtml'
        ]
        self.encoding = 'utf-8'
        # self.max_interval = None
        self.ctim = {}

    def get_detail_page_urls(self, data):
        '''
        从列表页获取详情页url; 返回列表
        '''
        detail_page_urls = ['http://bbs.tianya.cn/post-41-1236689-1.shtml']
        return detail_page_urls

    def parse_detail_page(self, response, url=None):
        result = []
        unicode_html_body = response.text
        data = htmlparser.Parser(unicode_html_body)
        url = response.request.url

        utc_now = datetime.datetime.utcnow()
        title = data.xpath('''//*[@id='post_head']/h1/span[1]/span''').text().strip()
        source = self.siteName
        ctime = self.ctim.get(url, utc_now)
        content = data.xpath('''//*[@id='bd']/div[4]/div[1]/div/div[2]/div[1]''').text().strip()
        post = {
            'url': url,
            'title': title,
            'source': source,
            'ctime': ctime,
            'gtime': utc_now,
            'content': content,
            'siteName': self.siteName,
            'data_db': self.data_db,
        }
        result.append(post)
        return result


if __name__ == "__main__":
    spider = MySpider()
    spider.proxy_enable = False
    spider.init_dedup()
    spider.init_downloader()

    # ------------ parse() ----------
    url = 'http://bbs.tianya.cn/post-41-1236689-1.shtml'
    resp = spider.download(url)
    res = spider.parse_detail_page(resp, url)

    if res is not None:
        for item in res:
            for k, v in item.iteritems():
                print k, v
