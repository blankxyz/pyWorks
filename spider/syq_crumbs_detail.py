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
import urllib
import allsite_clean_url

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
        # self.start_urls = 'http://bbs.tianya.cn/list-apply-1.shtml'
        # self.start_urls = 'http://bbs.tianya.cn/'
        self.encoding = 'gbk' # k618
        # self.encoding = 'utf-8' # tianya
        # self.site_domain = 'sina.com.cn'
        self.site_domain = 'k618.cn'
        # self.site_domain = 'bbs.tianya.cn'
        # self.conn = redis.StrictRedis.from_url('redis://192.168.100.15/6')
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/6')
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_output_zset_key = 'detail_urls_output_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.todo_urls_limits = 10
        self.todo_flg = -1
        self.done_flg = 0
        self.detail_flg = 9
        self.max_level = 7  # 最大级别
        self.detail_level = 99
        self.dedup_key = None
        self.cleaner = allsite_clean_url.Cleaner(
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/6'))

    def filter_links(self, urls):
        # print 'filter_links() start', len(urls), urls
        # 下载页
        # urls = filter(lambda x: self.cleaner.is_suffixes_ok(x), urls)
        # print 'filter_links() is_download', len(urls)
        # 错误url识别
        urls = filter(lambda x: not self.cleaner.is_error_url(x), urls)
        # print 'filter_links() is_error_url', len(urls)
        # 清洗无效参数#?
        urls = self.cleaner.url_clean(urls)
        # 跨域检查
        urls = filter(lambda x: self.cleaner.check_cross_domain(x), urls)
        # print 'filter_links() check_cross_domain', len(urls)
        # 黑名单过滤
        urls = filter(lambda x: not self.cleaner.in_black_list(x), urls) # bbs. mail.
        # print 'filter_links() in_black_list', len(urls)
        # 链接时间过滤
        # urls = filter(lambda x: not self.cleaner.is_old_url(x), urls)
        # 非第一页链接过滤
        urls = filter(lambda x: not self.cleaner.is_next_page(x), urls)
        # print 'filter_links() is_next_page', len(urls)
        # 去重
        # for url in urls:
        #     if  self.conn.zrank(self.detail_urls_zset_key, url) is not None:
        #         print 'remove:', url
        #         urls.remove(url)
        urls = list(set(urls))
        # print 'filter_links() set', len(urls)
        # 404
        # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
        # print 'filter_links() end', len(urls), urls
        return urls

    def is_list_by_link_density(self, url):
        response = self.download(url)
        doc = myreadability.Document(response.content, encoding=self.encoding)
        ret = doc.is_list() # 链接密度
        return ret

    def is_list_by_list_urls(self, url):
        #todo
        if self.conn.zrank(self.list_urls_zset_key, url):
            return True
        else:
            return False

    def get_detail_urls(self, urls):
        for url in urls:
            self.conn.zadd(self.detail_urls_output_zset_key, self.done_flg, url)

    def get_page_valid_urls(self, data, org_url):
        # print 'get_page_valid_urls() start',org_url
        ret_urls = []
        all_links = []
        remove_links = []
        try:
            self_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/@href")
            next_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/preceding-sibling::a/@href")
            # print '222222'
        except Exception, e:
            self_links = []
            next_links = []
            print u"[Info] get_page_valid_urls() [@href] %s not found next page link. [Exception] %s" % (org_url, e)

        for link in self_links:
            remove_links.append(link.text().strip())
        for link in next_links:
            remove_links.append(link.text().strip())

        # print 'get_page_valid_urls() [self_links]', self_links
        # print 'get_page_valid_urls() [next_links]', next_links

        links = data.xpathall("//a/@href | //iframe/@src")
        # print 'get_page_valid_urls() [//a/@href | //iframe/@src]',len(links), links
        for link in links:
            all_links.append(link.text().strip())
        # print 'get_page_valid_urls() [all_links]',all_links

        links = list(set(all_links) - set(remove_links))
        # print 'get_page_valid_urls() [all_links-remove_links]', links
        for link in links:
            # print org_url, link, '->'
            p = urlparse.urlparse(link)
            if p.scheme:
                url = link.split('#')[0]
            else:
                if p.path:
                    link = p.path
                if p.params:
                    link += ';' + p.params
                if p.query:
                    link += '?' + p.query
                url = urlparse.urljoin(org_url, link)
            # print org_url, link, '->' ,url
            ret_urls.append(url)
        # print 'get_page_valid_urls() [urljoin]', ret_urls

        ret_urls = self.filter_links(ret_urls)
        # print 'get_page_valid_urls() end',ret_urls
        return ret_urls

    def get_start_urls(self, data=None):
        urls = self.conn.zrangebyscore(self.list_urls_zset_key, self.done_flg, self.done_flg)
        if len(urls) > self.todo_urls_limits:
            urls = urls[0:self.todo_urls_limits]
        for url in urls:
            self.conn.zadd(self.list_urls_zset_key, self.detail_flg, url)
        return urls

    def parse(self, response):
        valid_urls = []
        org_url = ''
        if response is None:
            return [],None,None

        try:
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            org_url = response.request.url
            valid_urls = self.get_page_valid_urls(data, org_url)
            for valid_url in valid_urls:
                if self.is_list_by_list_urls(valid_url):
                    valid_urls.remove(valid_url)
            self.get_detail_urls(valid_urls)
        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)
            # print 'parse end'
        return valid_urls, None, None

    def parse_detail_page(self, response=None, url=None):
        print 'parse_detail_page()'
        result = []
        return result

# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is not True: # spider simulation
        print '[spider simulation] now starting ..........'
        for cnt in range(1000):
            print '[loop]',cnt,'[time]',datetime.datetime.utcnow()
            detail_job_list = []  # equal to run.py detail_job_queue
            # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
            def __detail_page_urls(urls, func):
                next_page_url = None
                if func is not None:
                    if urls:
                        for url in urls:
                            try:
                                response = mySpider.download(url)
                                list_urls, callback, next_page_url = func(
                                    response)  # parse()
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
            __detail_page_urls(start_urls, mySpider.parse)  # parse()

            # --equal to run.py detail_page_thread() -------------------------
            ret = []
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                for item in ret:
                    for k, v in item.iteritems():
                        print k, v
    else: # ---------- unit test -----------------------------
        print '[unit test] now starting ..........'
        # url ='http://bj.esf.sina.com.cn/detail/203494453' # 详情页 房地产 大量图片
        # url = 'http://photo.sina.com.cn/' # 列表页 图片网站 大量图片
        # url = 'http://photo.auto.sina.com.cn/picture/70218052_1_0_0#70218052' # 详情页 汽车 难
        # url = 'http://photo.sina.com.cn/hist/' # 列表页
        # url = 'http://slide.news.sina.com.cn/j/slide_1_45272_100138.html#p=1' # 详情页
        # url = 'http://bbs.tianya.cn/list-apply-1.shtml'
        url = 'http://bbs.tianya.cn/'
        mySpider = MySpider()
        mySpider.encoding = 'utf-8'
        mySpider.proxy_enable = False
        mySpider.init_dedup()
        mySpider.init_downloader()
        #--------------------------------------
        response = mySpider.download(url)
        unicode_html_body = response.content
        data = htmlparser.Parser(unicode_html_body)
        # print 'parse_detail_page() data.html', data.html()
        valid_urls = mySpider.get_page_valid_urls(data, url)
        print '[unit test]',valid_urls
        # print mySpider.is_list_by_rule(url)

if __name__ == '__main__':
    # run(unit_test = True)
    import cProfile
    cProfile.run("test(unit_test = True)")
