#!/usr/bin/env python
# coding=utf-8

import re
import time
import datetime
import urlparse
import redis
import spider
import setting
import htmlparser
import myreadability
import HTMLParser
import syq_clean_url

class MySpider(spider.Spider):

    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(
            self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)
        # 网站名称
        self.siteName = "k618"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.start_urls = 'http://www.k618.cn/'
        # self.start_urls = 'http://bj.esf.sina.com.cn/'
        # self.encoding = 'utf-8'
        self.encoding = 'gbk'
        # self.site_domain = 'sina.com.cn'
        self.site_domain = 'k618.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/8')
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.todo_urls_limits = 10
        self.todo_flg = -1
        self.done_flg = 0
        self.max_level = 7  # 最大级别
        self.detail_level = 99
        self.dedup_key = None
        self.cleaner = syq_clean_url.Cleaner(
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/5'))

    def convert_path_to_rule0(self, url):
        '''
        http://baike.k618.cn/thread-3327665-1-1.html ->
        /[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]-\d\d\d\d\d\d\d-\d-\d.html
        '''
        path = urlparse.urlparse(url).path
        pos1 = path.rfind('/')
        pos2 = path.find('.')
        if pos2 < 0:
            pos2 = len(path)
        tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
        tag = re.sub(r'\d', '\d', tag)
        return urlparse.urlparse(url).netloc + path[:pos1 + 1] + tag + path[pos2:]

    def filter_links(self, urls):
        # print 'filter_links() all',len(urls)
        # 下载页
        urls = filter(lambda x: not self.cleaner.is_download(x), urls)
        # print 'filter_links() is_download', len(urls)
        # 错误url识别
        urls = filter(lambda x: not self.cleaner.is_error_url(x), urls)
        # print 'filter_links() is_error_url', len(urls)
        # 清洗无效参数#?
        urls = self.cleaner.url_clean(urls)
        # 跨域检查
        urls = filter(lambda x: self.cleaner.check_cross_domain(x), urls)
        # print 'filter_links() check_cross_domain', len(urls)
        #过滤详情页
        # urls = filter(lambda x: not self.cleaner.is_detail_by_regex(x), urls)
        # 黑名单过滤
        urls = filter(lambda x: not self.cleaner.in_black_list(x), urls) # bbs. mail.
        # print 'filter_links() in_black_list', len(urls)
        # 链接时间过滤
        # urls = filter(lambda x: not self.cleaner.is_old_url(x), urls)
        # 非第一页链接过滤
        # urls = filter(lambda x: not self.cleaner.is_next_page(x), urls)
        # print 'filter_links() is_next_page', len(urls)
        # ' http://news.k618.cn/zxbd/201606/t20160612_7703993.html'
        # ' http://news.k618.cn/zxbd/201606/t20160612_7703952.html' 视为同一url
        rule_lst = []
        urls_tmp = []
        for url in urls:
            rule0 = self.convert_path_to_rule0(url)
            if rule0 not in rule_lst:
                rule_lst.append(rule0)
                urls_tmp.append(url)
        urls = urls_tmp

        # print 'filter_links() rule0', len(urls)

        # 去重
        urls = list(set(urls))
        # print 'filter_links() set', len(urls)
        # 404
        # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
        # print 'filter_links()', len(urls)
        return urls

    def get_start_urls(self, data=None):
        return [self.start_urls]

    def get_page_valid_urls(self, data, org_url):
        urls = []
        links = data.xpathall("//a/@href | //iframe/@src")

        for link in links:
            url = urlparse.urljoin(org_url, link.text().strip())
            # if url[-1] != '/': url = url + '/'
            urls.append(url)
        urls = self.filter_links(urls)
        return urls

    def have_crumbs(self, url):
        response = self.downloader.download(url)
        unicode_html_body = response.content
        data = htmlparser.Parser(unicode_html_body)
        tags = data.xpathall("//div")
        for tag in tags:
            # print tag
            try:
                if tag.regex(r'^\s*>+\s*$'):
                    print '[have_crumbs() yes]' + url
                    return True
                else:
                    print '[have_crumbs() no]' + tag
                    return False
            except Exception, e:
                print '[have_crumbs() no]' + tag
                return False
            # print '-' * 80
            # print p
            # print '-' * 80
            # un = HTMLParser.HTMLParser().unescape(p.text())
            # print un
            # print '-' * 80
            # print un.regex(r"^\s*>+\s*$").str().strip()
            # print '-' * 80

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
        num = 0
        # p1 = data.xpathall("//div[contains(@class,'bre urlparse  n  ad')] | //div[contains(@class,'crumb')] | //div[contains(@class,'nav')]")
        # crumbs = data.xpathall("//div[contains(@class,'crumb')]")
        # for crumb in crumbs:
        #     # if p.regex(r'^\s*>+\s*$') or p.regex(r'^\s*>>+\s*$'):
        #     #     num += 5
        #     print '-' * 80
        #     print crumb
        #     print '-' * 80
        #     un = HTMLParser.HTMLParser().unescape(crumb.text())
        #     print un
        #     print '-' * 80
        #     print un.regex(r"^\s*>+\s*$").str().strip()
        #     print '-' * 80
        # a = data.xpathall("//a/@href | //iframe/@src")
        # print a
        return

    def parse(self, response):
        try:
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            valid_urls = self.get_page_valid_urls(data, response.url)
            for valid_url in valid_urls:
                if self.have_crumbs(valid_url):
                    self.get_breadcrumb(data)
                else:
                    print valid_url
        except Exception, e:
            print "[ERROR] parse_detail_page(): %s" % e
        return [], None, None

    def parse_detail_page(self, response=None, url=None):
        result = []
        return result

if __name__ == '__main__':
    detail_job_list = []  # equal to run.py detail_job_queue
    # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
    def __detail_page_urls(urls, func):
        next_page_url = None
        if func is not None:
            if urls:
                for url in urls:
                    response = mySpider.download(url)
                    try:
                        list_urls, callback, next_page_url = func(
                            response)  # parse()
                        for url in list_urls:
                            detail_job_list.append(url)
                    except Exception, e:
                        print '[ERROR] main() Exception:', e
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

