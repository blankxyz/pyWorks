#!/usr/bin/env python
# coding=utf-8

import re
import datetime
import urlparse
import redis
import spider
import setting
import urllib
from bs4 import BeautifulSoup, Comment
import requests
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
        self.siteName = "all"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.start_urls = 'http://bbs.tianya.cn/'
        self.site_domain = 'bbs.tianya.cn'
        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/14')
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.list_urls_keyword_zset_key = 'list_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_keyword_zset_key = 'detail_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.todo_urls_limits = 10
        self.todo_flg = -1
        self.done_flg = 0
        self.max_level = 7  # 最大级别
        self.detail_level = 99
        self.dedup_key = 'dedup'
        # self.cleaner = syq_clean_url.Cleaner(
        #     self.site_domain, redis.StrictRedis.from_url('redis://192.168.110.110/0'))
        self.cleaner = syq_clean_url.Cleaner(
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/0'))

    def convert_regex_format(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
        '''
        ret = ''
        digit = '\d'
        word = '[a-zA-Z]'
        cnt = 0
        pos = 0
        temp = ''
        while pos <= len(rule):
            if rule[pos:pos + len(digit)] == digit:
                if temp.find(digit) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (digit, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (word, cnt)
                pos = pos + len(word)
            elif pos == len(rule):
                ret = ret + temp
                break
            else:
                ret = ret + temp + rule[pos]
                temp = ''
                cnt = 0
                pos = pos + 1
        return ret

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

    def is_detail_rule_0(self, url):
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        rules = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                                           max=999999, min=0, start=0, num=rule0_cnt, withscores=False)
        for rule0 in rules:
            if re.search(rule0, url):
                print '[rule0]', rule0, '<-', url
                return True #符合详情页规则
        return False #不确定

    def is_detail_rule_1(self ,url):
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        rules = self.conn.zrevrangebyscore(self.detail_urls_rule1_zset_key,
                        max=999999, min=0, start=0, num=rule1_cnt, withscores=False)
        for rule1 in rules:
            if re.search(rule1, url):
                self.conn.zincrby(self.detail_urls_rule1_zset_key, value=rule1, amount=1)
                print '[rule1]', rule1, '<-', url
                return True #符合详情页规则
        return False #不确定

    def is_list_by_rule(self, soup, url):
        # print 'is_list_by_rule start'
        # 最优先确定规则
        path = urlparse.urlparse(url).path
        if len(path) == 0:
            return True
        if path == '/':
            return True
        if path[-1] == '/':
            return True

        #post;content;detail
        detail_keyword_list = self.conn.zrange(self.detail_urls_keyword_zset_key,start=0,end=999)
        for key in detail_keyword_list:
            if path.lower().find(key) >0:
                self.conn.zincrby(self.detail_urls_keyword_zset_key, value=key, amount=1)
                # print 'detail_keyword_list',False
                return False

        # list;index
        list_keyword_list = self.conn.zrange(self.list_urls_keyword_zset_key,start=0,end=999)
        for key in list_keyword_list:
            if path.lower().find(key) > 0:
                self.conn.zincrby(self.list_urls_keyword_zset_key, value=key, amount=1)
                # print 'list_keyword_list',True,path,key
                return True

        # 优先使用rule1
        if self.is_detail_rule_1(url) == True:
            # print 'detail_rule_1()',True
            return False
        # # 使用rule0
        if self.is_detail_rule_0(url) == True:
            return False
        # 判断面包屑中有无的‘正文’
        # if self.is_current_page(soup, url) == True:
        #     # print 'is_current_page() True'
        #     return False

        return True
        # print 'is_list_by_rule start',url,ret

    def convert_path_to_rule0(self, url):
        '''
        http://baike.k618.cn/20140515/thread-3327665-1-1.html ->
        http://baike.k618.cn/20140515/[a-zA-Z]{6}-\d{7}-\d{1}-\d{1}.html
        '''
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        pos1 = path.rfind('/')
        pos2 = path.find('.')
        if pos2 < 0: pos2 = len(path)
        regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
        regex = re.sub(r'\d', '\d', regex)
        regex = path[:pos1 + 1] + regex + path[pos2:]
        regex = urlparse.urlunparse((scheme, netloc, regex, '', '', ''))
        return self.convert_regex_format(regex)

    def convert_path_to_rule1(self, rule0):
        '''
        http://baike.k618.cn/20140515/[a-zA-Z]{6}-\d{7}-\d{1}-\d{1}.html ->
        http://baike.k618.cn/\d{8}/[a-zA-Z]{6}-\d{7}-\d{1}-\d{1}.html
        '''
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(rule0)
        if path.count('/') >= 2:
            pos2 = path.rfind('/')
            pos1 = path[:pos2 - 1].rfind('/')
            regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
            regex = re.sub(r'\d', '\d', regex)
            rule1 = self.convert_regex_format(regex)
            rule1 = path[:pos1 + 1] + rule1 + path[pos2:]
            return urlparse.urlunparse((scheme, netloc, rule1, '', '', ''))
        else:
            return None

    def get_todo_urls(self):
        urls = []
        try:
            urls = self.conn.zrangebyscore(self.list_urls_zset_key, self.todo_flg, self.todo_flg)
            if len(urls) > self.todo_urls_limits:
                urls = urls[0:self.todo_urls_limits]
            for url in urls:
                self.conn.zadd(self.list_urls_zset_key, self.done_flg, url)
        except Exception, e:
            print "[ERROR] get_todo_urls(): %s" % e
        return urls

    def header_maker(self, text=''):
        if not text:
            text = {'Proxy-Connection': 'keep-alive',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Upgrade-Insecure-Requests': 1,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
                    }
        return text

    def get_clean_soup(self, url):
        headers = self.header_maker()
        try:
            data = requests.get(url, headers=headers, timeout=5)
        except Exception, e:
            print "[ERROR]get_clean_soup()",e
            return None
        soup = BeautifulSoup(data.content, 'lxml')
        # print 'before',soup.prettify()
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]
        [input.extract() for input in soup('input')]
        [input.extract() for input in soup('form')]
        [foot.extract() for foot in soup(attrs={'class': 'footer'})]
        [foot.extract() for foot in soup(attrs={'class': 'bottom'})]
        # print 'after',soup.prettify()
        return soup

    def urls_join(self, org_url, links):
        urls = []
        for link in links:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link.strip())
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                # url = urlparse.urljoin(org_url, urllib.quote(link))
                url = urlparse.urljoin(org_url, link)
            urls.append(url)

        return urls

    def get_page_valid_urls(self, soup, org_url):
        all_links = []
        remove_links = []
        try:
            for tag in soup.find_all("a"):
                if tag.has_attr('href'):
                    all_links.append(tag['href'])

            for tag in soup.find_all("a", href=re.compile(r"(javascript.*?|#.*?)", re.I)):
                if tag.has_attr('href'):
                    remove_links.append(tag['href'])

            # tag = soup.find("a", text=re.compile(u"下一页")) # 下一页 下页
            # if tag:
            #     if tag.has_attr('href'):
            #         remove_links.append(tag['href'])
            #
            #     for t in tag.find_previous_siblings('a', recursive=False):
            #         if t.has_attr('href'):
            #             remove_links.append(t['href'])
            #
            #     for t in tag.find_next_siblings('a', recursive=False):
            #         if t.has_attr('href'):
            #             remove_links.append(t['href'])

        except Exception, e:
            print '[ERROR] get_page_valid_urls()',e

        removed = list(set(all_links) - set(remove_links))

        urls = self.urls_join(org_url, removed)
        # print len(all_links), all_links
        # print len(remove_links), remove_links
        # print len(removed), removed
        # print len(urls), urls
        urls = self.filter_links(urls)
        return urls

    def is_current_page(self, soup, org_url):
        links = []
        for tag in soup.find_all(text=re.compile(u"正文")):
            parent = tag.find_parent(recursive=False)
            if len(parent.find_all('a')) > 0:
                for link in parent.find_all('a'):
                    if link.has_attr('href'):
                        links.append(link['href'])
                #保存面包屑
                urls = self.urls_join(org_url,links)
                for url in urls:
                    if self.conn.zrank(self.list_urls_zset_key, url) is None:
                        self.conn.zadd(self.list_urls_zset_key, self.todo_flg, url)
                return True

        return False

    def extract_detail_rule_0(self, url):
        # rule0 是无条件转换（url一定是详情页）
        url_rule = self.convert_path_to_rule0(url)
        if url_rule:
            self.conn.zincrby(self.detail_urls_rule0_zset_key, value = url_rule, amount = 1)
        else:
            print '[ERROR] extract_detail_rule_0()',url
        return

    def extract_detail_rule_1(self):
        rules_0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        rules_0 = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                        max=999999, min=0, start=0, num=rules_0_cnt, withscores=True)
        for rule_0, score_0 in dict(rules_0).iteritems():
            rule_1 = self.convert_path_to_rule1(rule_0)
            if rule_1:
                self.conn.zincrby(self.detail_urls_rule1_zset_key, value=rule_1, amount=score_0)
        return

    def get_start_urls(self, data=None):
        if self.conn.zrank(self.list_urls_zset_key, self.start_urls) is None:
            self.conn.zadd(self.list_urls_zset_key, self.todo_flg, self.start_urls)
        return [self.start_urls]
        # return []

    def parse(self, response):
        urls = self.get_todo_urls()
        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        # print 'parse_detail_page() start'
        result = []
        if response is None: return result

        if url is None: org_url = response.request.url
        else: org_url = response.url

        try:
            soup = self.get_clean_soup(org_url)
            if soup is None: return []
            links = self.get_page_valid_urls(soup, org_url)
            for link in links:
                s = self.get_clean_soup(link)
                if self.is_list_by_rule(s, link):
                    print 'list  :',link
                    if self.conn.zrank(self.list_urls_zset_key, link) is None:
                        self.conn.zadd(self.list_urls_zset_key, self.todo_flg, urllib.unquote(link))
                else:
                    print 'detail:', link
                    if self.conn.zrank(self.detail_urls_zset_key, link) is None:
                        self.conn.zadd(self.detail_urls_zset_key, 0, urllib.unquote(link))
            # print 'parse_detail_page() end'
        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)
            # print 'parse_detail_page end'
        return result

# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False: # spider simulation
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
            print 'start_urls:', start_urls
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
        url = 'http://bbs.tianya.cn/post-41-1236689-1.shtml'
        print 'url:',url
        mySpider = MySpider()
        #预置数据
        mySpider.conn.zadd(mySpider.list_urls_zset_key, mySpider.todo_flg, mySpider.start_urls)
        #预置匹配规则
        mySpider.conn.zadd(mySpider.detail_urls_rule1_zset_key,mySpider.done_flg,'/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
        mySpider.conn.zadd(mySpider.detail_urls_rule1_zset_key,mySpider.done_flg,'/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html')
        mySpider.conn.zadd(mySpider.detail_urls_rule1_zset_key,mySpider.done_flg,'/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html')

        # soup = mySpider.get_clean_soup(url)
        #----------------------------------------------------------
        # print mySpider.is_list_by_rule(url)
        #----------------------------------------------------------
        # rule0 = mySpider.convert_path_to_rule0(url)
        # print url, '->', rule0
        # rule1 = mySpider.convert_path_to_rule1(rule0)
        # print rule0, '->', rule1
        print mySpider.is_list_certain(url)

if __name__ == '__main__':
    test(unit_test = False)
    # test(unit_test = True)
    # import cProfile
    # cProfile.run("test(unit_test = False)")
