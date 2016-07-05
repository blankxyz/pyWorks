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
        self.siteName = "test"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        # self.start_urls = 'http://baby.k618.cn/'
        self.start_urls = 'http://www.yangtse.com/'
        # self.start_urls = 'http://www.thepaper.cn/' # 澎湃新闻
        # self.start_urls = 'http://bbs.tianya.cn/'
        self.encoding = 'gbk' #k618 扬子晚报 地方领导留言板 北青网
        # self.encoding = 'utf-8' #tianya 澎湃新闻
        # self.site_domain = 'sina.com.cn'
        # self.site_domain = 'k618.cn'
        self.site_domain = 'yangtse.com'
        # self.site_domain = 'ynet.com' # 北青网
        # self.site_domain = 'thepaper.cn' # 澎湃新闻
        # self.site_domain = 'bbs.tianya.cn'
        # self.conn = redis.StrictRedis.from_url('redis://192.168.100.15/6')
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/15') # 详情页专用
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.todo_urls_limits = 10
        self.todo_flg = -1
        self.done_flg = 0
        self.detail_flg = 9
        self.max_level = 7  # 最大级别
        self.detail_level = 99
        self.dedup_key = None
        self.cleaner = syq_clean_url.Cleaner(
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/6'))


    def get_url_level(self, url):
        level = self.conn.zscore(self.ok_urls_zset_key, url)
        if level in None: level = 0
        return level

    def filter_links(self, urls):
        # print 'filter_links() start', len(urls), urls
        # 下载页
        urls = filter(lambda x: self.cleaner.is_suffixes_ok(x), urls)
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
        # for url in urls:
        #     if  self.conn.zrank(self.detail_urls_zset_key, url) is not None:
        #         print 'remove:', url
        #         urls.remove(url)
        # 去重
        urls = list(set(urls))
        # print 'filter_links() set', len(urls)
        # 404
        # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
        # print 'filter_links() end', len(urls), urls
        return urls

    def is_current_page(self, org_url):
        '''
        面包屑含有‘正文’,则判定为详情页,返回 True
        注）提取面包屑里面的链接
        '''
        encode = "utf8"
        response = self.download(org_url)
        char = re.search(r'charset=(.*)>',response.text)
        if char:
            if re.search("utf", char.group(1), re.I):
                encode = "utf8"
            elif re.search("gb", char.group(1), re.I):
                encode = "gbk"
            elif re.search('big5', char.group(1), re.I):
                encode = "big5"
        response.encoding = encode
        unicode_html_body = response.text  # unicode
        parse = htmlparser.Parser(data=unicode_html_body)
        nav_links = parse.replace('[\n\r]','').regexall(u'<div.*?正文.*?div>')
        for nav in nav_links:
            nav = nav.data[nav.data.rfind('<div'):]
            if nav.count('</a>') >0: return True
        return False

    def is_list_by_link_density(self, url):
        response = self.download(url)
        doc = myreadability.Document(response.content, encoding=self.encoding)
        ret = doc.is_list()
        return ret

    def is_list_by_rule(self, url):
        # print 'is_list_by_rule start'
        path = urlparse.urlparse(url).path
        if len(path) == 0:
            return True
        else:
            # 最优先确定规则
            if path == '/':
                return True
            if path[-1] == '/':
                return True
            if self.conn.zrank(self.list_urls_zset_key, url):
                return True
            if path.find('index') > 0 or path.find('list') >0 and path.find('post') < 0 and path.find('content') < 0 and path.find('detail') < 0:
                return True
            if path[1:].isalpha():
                return True
            # 判断面包屑中有无的‘正文’
            if self.is_current_page(url) == True:
                return False
            # 使用链接密度
            return self.is_list_by_link_density(url)
        # print 'is_list_by_rule start',url,ret

    def get_todo_urls(self):
        urls = []
        try:
            urls = self.conn.zrangebyscore(self.list_urls_zset_key, self.done_flg, self.done_flg)
            # print 'get_todo_urls() zrangebyscore', urls
            if len(urls) > self.todo_urls_limits:
                urls = urls[0:self.todo_urls_limits]
            for url in urls:
                self.conn.zadd(self.list_urls_zset_key, self.detail_flg, url)
        except Exception, e:
            print "[ERROR] get_todo_urls(): %s" % e
        return urls

    def get_remove_links(self, data, org_url):
        remove_links = []
        # 移除下一页及其他
        try:
            self_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/@href")
            # print 'self_links', self_links
        except Exception, e:
            pass
            # print u"[Info] get_remove_links() [@href] %s not found 下一页. [Exception] %s" % (org_url, e)
        else:
            for link in self_links: remove_links.append(link.text().strip())

        try:
            next_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/preceding-sibling::a/@href")
            # print 'next_links', next_links
        except Exception, e:
            pass
            # print u"[Info] get_remove_links() [@href] %s not found 下一页 及其他. [Exception] %s" % (org_url, e)
        else:
            for link in next_links: remove_links.append(link.text().strip())

        #移除footer及其他
        try:
            foot_links= data.xpathall(u"//a[text()='联系我们']/@href")
            # print 'foot_links',foot_links
        except Exception, e:
            pass
            # print u"[Info] get_remove_links() [@href] %s not found 关于我们. [Exception] %s" % (org_url, e)
        else:
            for link in foot_links: remove_links.append(link.text().strip())

        try:
            footer_preceding = data.xpathall(u"//a[text()='联系我们']/preceding-sibling::a/@href")
            footer_following = data.xpathall(u"//a[text()='联系我们']/following-sibling::a/@href")
            # print 'footer_links',footer_preceding,footer_following
        except Exception, e:
            pass
            # print u"[Info] get_remove_links() [@href] %s not found 关于我们 及其他. [Exception] %s" % (org_url, e)
        else:
            for link in footer_preceding: remove_links.append(link.text().strip())
            for link in footer_following: remove_links.append(link.text().strip())
        return remove_links

    def get_page_valid_urls(self, data, org_url):
        print 'get_page_valid_urls() start',org_url
        urls = []
        all_links = []

        remove_links = self.get_remove_links(data, org_url)
        # links = data.xpathall("//a/@href | //iframe/@src")
        short_links = data.xpathall("//a[string-length(text())<=10]/@href | //iframe/@src")
                                    # print org_url
        # print '//a',len(short_links), short_links
        for link in short_links:
            all_links.append(link.text().strip())
        # print 'get_page_valid_urls() [all_links]',all_links

        links = list(set(all_links) - set(remove_links))
        # print 'get_page_valid_urls() [all_links-remove_links]', links
        for link in links:
            # print org_url, link, '->'
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link)
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                url = urlparse.urljoin(org_url, link)
            urls.append(url)
        # print 'get_page_valid_urls() [urljoin]', urls
        valid_urls = self.filter_links(urls)
        # print 'get_page_valid_urls() end',urls
        for valid_url in valid_urls:
            if self.is_list_by_rule(valid_url) is False:
                if self.conn.zrank(self.detail_urls_zset_key, valid_url) is None:
                    self.conn.zadd(self.detail_urls_zset_key, 0, urllib.unquote(valid_url))
        return urls


    def get_page_valid_urls_long(self, data, org_url):
        print 'get_page_valid_urls_long() start',org_url
        urls = []
        all_links = []

        long_links = data.xpathall("//a[string-length(text())>10]/@href")
        # print '//a > 10',len(short_links), short_links
        for link in long_links:
            all_links.append(link.text().strip())
        for link in all_links:
            # print org_url, link, '->'
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link)
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                url = urlparse.urljoin(org_url, link)
            urls.append(url)
        # print 'get_page_valid_urls_long() [urljoin]', urls
        valid_urls = self.filter_links(urls)
        # print 'get_page_valid_urls_long() end',urls
        for valid_url in valid_urls:
            if self.is_list_by_rule(valid_url) is False:
                if self.conn.zrank(self.detail_urls_zset_key, valid_url) is None:
                    self.conn.zadd(self.detail_urls_zset_key, 0, urllib.unquote(valid_url))
        print 'get_page_valid_urls_long() end'
        return urls

    def get_start_urls(self, data=None):
        return [self.start_urls]

    def parse(self, response):
        urls = self.get_todo_urls()
        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        print 'parse_detail_page() start'
        result = []
        if response is None:
            return result

        if url is None:
            org_url = response.request.url
        else:
            org_url = response.url

        try:
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            # long links
            self.get_page_valid_urls_long(data, org_url)
            # short links
            # self.get_page_valid_urls(data, org_url)

            print 'parse_detail_page() end'
        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)
            print 'parse_detail_page end(error)'
        return result

# ---------- test run function-----------------------------
def make_test_list():
    url = 'http://nt.yangtse.com/news/livelihood/'
    print '[url]', url
    mySpider = MySpider()
    mySpider.conn.zadd(mySpider.list_urls_zset_key, 0, url)

def test(unit_test):
    if unit_test is False: # spider simulation
        print '[spider simulation] now starting ..........'
        for cnt in range(10):
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
            __detail_page_urls(start_urls, mySpider.parse)  # parse()

            # --equal to run.py detail_page_thread() -------------------------
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                for item in ret:
                    for k, v in item.iteritems():
                        print k, v
    else: # ---------- unit test -----------------------------
        print '[unit test] now starting ..........'
        mySpider = MySpider()
        # mySpider.encoding = 'utf-8'
        mySpider.encoding = 'gbk'
        mySpider.proxy_enable = False
        mySpider.init_dedup()
        mySpider.init_downloader()

        response = mySpider.download(url)
        unicode_html_body = response.content
        data = htmlparser.Parser(unicode_html_body)
        # print 'parse_detail_page() data.html', data.html()
        # valid_urls = mySpider.get_page_valid_urls(data, url)
        # print valid_urls
        #----------------------------------------------------------
        # print mySpider.is_list_by_rule(url)
        #----------------------------------------------------------
        # url = 'http://baike.k618.cn/aaa/thread-3327665-1-1.html'
        # rule0 = mySpider.convert_path_to_rule0(url)
        # print url, '->', rule0
        # rule1 = mySpider.convert_path_to_rule1(rule0)
        # print rule0, '->', rule1
        print mySpider.is_list_by_link_density(url)

if __name__ == '__main__':
    make_test_list()
    test(unit_test = False)
    # import cProfile
    # cProfile.run("test(unit_test = False)")
