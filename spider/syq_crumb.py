#!/usr/bin/env python
# coding=utf-8

import re
import time
import datetime
import urlparse
import redis
from bs4 import BeautifulSoup, Comment
import spider
import setting
import htmlparser
import requests
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
        self.encoding = 'utf-8'
        # self.site_domain = 'sina.com.cn'
        self.site_domain = 'k618.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/8')
        self.crumbs_urls_zset_key = 'crumbs_urls_zset_%s' % self.site_domain
        self.hub_urls_zset_key = 'hub_urls_zset_%s' % self.site_domain
        self.hub_urls_level_zset_key = 'hub_urls_level_zset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        self.todo_urls_limits = 100
        self.max_level = 5  # 最大级别
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
        return path[:pos1 + 1] + tag + path[pos2:]

    def filter_links(self, urls):
        # print 'filter_links() all',len(urls)
        # 下载页
        # urls = filter(lambda x: not self.cleaner.is_download(x), urls)
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
        # urls = filter(lambda x: not self.cleaner.in_black_list(x), urls) # bbs. mail.
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
            if url.rfind('.htm')>0 or url.rfind('.shtm')>0:
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
        if self.conn.zrank(self.hub_urls_zset_key, self.start_urls) is None:
            self.conn.zadd(self.hub_urls_zset_key, self.todo_flg, self.start_urls)
        if self.conn.zrank(self.hub_urls_level_zset_key, self.start_urls) is None:
            self.conn.zadd(self.hub_urls_level_zset_key, 0, self.start_urls)
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

    def header_maker(self):
        header = {'Proxy-Connection': 'keep-alive',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                  'Accept-Encoding': 'gzip, deflate, sdch',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
                  }
        return header

    def get_clean_soup(self,url):
        headers = self.header_maker()
        try:
            data = requests.get(url, headers=headers, timeout=5)
        except:
            print("[error] connect")
            return None
        soup = BeautifulSoup(data.content, 'lxml')
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [s.extract() for s in soup('script')]
        [input.extract() for input in soup('input')]
        [input.extract() for input in soup('form')]
        [blank.extract() for blank in soup(text=re.compile("^\s*?\n*?$"))]
        [foot.extract() for foot in soup(attrs={'class': 'footer'})]
        [foot.extract() for foot in soup(attrs={'class': 'bottom'})]
        [s.extract() for s in soup('style')]
        return soup

    def marge_url(self,url, href):
        # print 'marge_url() start'
        if url is None:
            return None
        elif href == './':
            return url
        elif href == '../':
            if url[-1] == '/':
                url = url[:-1]
                pos = url.rfind('/')
                return url[:pos + 1]
            else:
                pos = url.rfind('/')
                return url[:pos + 1]
        else:
            netloc = urlparse.urlparse(url).netloc
            if netloc[-1] != '/':
                netloc += '/'
            return urlparse.urlparse(url).scheme + '://'  + netloc + href

    def find_breadcrumbs(self, url):
        '''
        1）"breadcrumb"
        //div[contains(@class,"bread")]
        //div[contains(@class,"crumb")]
        2）'>' ‘>>’
        3）//div[contains(@class,'nav')] or
           Nav NAV
        4) 文字长度小于7
        '''
        crumbs = []
        soup = self.get_clean_soup(url)
        if not soup:
            return False

        # [样式] 'bbs.jjh.k618.cn/thread-3327506-1-10.html'
        em_tags =  soup.findAll('em', text='›')
        # print a_tag.parent
        if em_tags:
            a_tags = em_tags[-1].parent.findAll('a')
            for a_tag in a_tags:
                # print url, a_tag.get('href'), self.marge_url(url, a_tag.get('href'))
                crumbs.append(self.marge_url(url, a_tag.get('href')))

        # [样式] 'http://news.k618.cn/zxbd/201606/t20160613_7705874.html'
        a_tags = soup.findAll('a')
        for a_tag in a_tags:
            # print a_tag.parent
            tags = a_tag.parent.findAll(text=re.compile(r'^\s*›+\s*$', re.U))
            if tags:
                for href in [a_tag.get('href')]:
                    # print url, href, self.marge_url(url, href)
                    crumbs.append(self.marge_url(url, href))

        return list(set(crumbs))
        # tags2 = soup.findAll(text=re.compile(r'(正文|当前位置|当前的位置)\s*$', re.U))
        # print tags2

    def get_todo_urls(self):
        urls = []
        try:
            # get todo_flag urls
            urls = self.conn.zrangebyscore(self.hub_urls_zset_key, self.todo_flg, self.todo_flg)
            if len(urls) > self.todo_urls_limits:
                urls = urls[0:self.todo_urls_limits]
            # if hub level >= max(5) end
            # for url in urls:
            #     if self.conn.zscore(self.hub_urls_level_zset_key, url) >= self.max_level:
            #         urls.remove(url)
            for url in urls:
                self.conn.zadd(self.hub_urls_zset_key, self.done_flg, url)

        except Exception, e:
            print "[ERROR] get_todo_urls(): %s" % e
        return urls

    def parse(self, response):
        urls = self.get_todo_urls()
        print urls
        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        result = []
        if response is None:
            return result
        try:
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            valid_urls = self.get_page_valid_urls(data, response.url)
            for valid_url in valid_urls:
                crumbs = self.find_breadcrumbs(valid_url)
                if crumbs: # save to redis
                    for crumb in crumbs:
                        if self.conn.zrank(self.crumbs_urls_zset_key, crumb) is None:
                            self.conn.zadd(self.crumbs_urls_zset_key, 0, crumb)
                else:
                    # set todo flag
                    if self.conn.zrank(self.hub_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.hub_urls_zset_key, self.todo_flg, valid_url)
                    # record hub level
                    if self.conn.zrank(self.hub_urls_level_zset_key, valid_url) is None:
                        # 取得父url的score
                        score = self.conn.zscore(self.hub_urls_level_zset_key, response.url)
                        if score is None: score = 0
                        # score +1 ，有可能多次设置 level
                        self.conn.zadd(self.hub_urls_level_zset_key, score+1, valid_url)
        except Exception, e:
            # self.conn.zadd(self.hub_urls_zset_key, self.done_flg, response.url)
            print "[ERROR] parse_detail_page(): %s" % e

        return result

if __name__ == '__main__':
    for cnt in range(1000):
        print '[loop]',cnt,'[time]',datetime.datetime.utcnow()
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

    # # --unit test-------------------------
    # url = 'http://news.k618.cn/zxbd/201606/t20160613_7705874.html'
    # url = 'http://bbs.jjh.k618.cn/thread-2742091-1-549.html'
    # mySpider = MySpider()
    # mySpider.proxy_enable = False
    # mySpider.init_dedup()
    # mySpider.init_downloader()
    # print mySpider.find_breadcrumbs(url)