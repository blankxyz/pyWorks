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
        self.siteName = "k618"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        # self.start_urls = 'http://www.k618.cn/'
        # self.start_urls = 'http://bbs.tianya.cn/list-apply-1.shtml'
        self.start_urls = 'http://bbs.tianya.cn/'
        # self.encoding = 'gbk'
        self.encoding = 'utf-8'
        # self.site_domain = 'sina.com.cn'
        # self.site_domain = 'k618.cn'
        self.site_domain = 'bbs.tianya.cn'
        # self.conn = redis.StrictRedis.from_url('redis://192.168.100.15/6')
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/4')
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
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/6'))

    def convert_regex_format(self,rule):
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
        while pos < len(rule):
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
            else:
                ret = ret + temp + rule[pos]
                temp = ''
                cnt = 0
                pos = pos + 1
        return ret

    def get_url_level(self, url):
        level = self.conn.zscore(self.ok_urls_zset_key, url)
        if level in None:
            level = 0
        return level

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
        # print 'is_list_by_link_density start'
        response = self.download(url)
        doc = myreadability.Document(response.content, encoding=self.encoding)
        ret = doc.is_list() # 链接密度
        return ret

    def is_list_by_rule_0(self, url):
        #[rule0] rule0收集数>100时，匹配次数>10 的前10%高频度规则
        # path = urlparse.urlparse(url).path
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        if rule0_cnt > 5:
            rules = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                                               max=999999, min=10, start=0, num=rule0_cnt/10, withscores=True)
            for rule0, score in dict(rules).iteritems():
                if re.search(rule0, url):
                    print '[rule0]', rule0, '<-', url
                    return False #符合详情页规则
        return True #不确定

    def is_list_by_rule_1(self ,url):
        #[rule1] rule1收集数>10时，匹配次数>20 的前20%高频度规则
        # path = urlparse.urlparse(url).path
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        if rule1_cnt > 5:
            rules = self.conn.zrevrangebyscore(self.detail_urls_rule1_zset_key,
                            max=999999, min=20, start=0, num=rule1_cnt/5, withscores=True)
            for rule1, score in dict(rules).iteritems():
                if re.search(rule1, url):
                    self.conn.zincrby(self.detail_urls_rule1_zset_key, value=rule1, amount=1)
                    print '[rule1]', rule1, '<-', url
                    return False #符合详情页规则
        return True #不确定

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
            if path.find('index') > 0:
                return True
            # 优先使用rule1
            if self.is_list_by_rule_1(url) == False:
                return False
            # 使用rule0
            if self.is_list_by_rule_0(url) == False:
                return False
            # 使用链接密度
            return self.is_list_by_link_density(url)
        # print 'is_list_by_rule start',url,ret

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
        return urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc + path[:pos1 + 1] + tag + path[pos2:]

    def convert_path_to_rule1(self, path):
        '''
        /news/201404/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm
        '''
        path = urlparse.urlparse(path).path
        if path.count('/') >= 2:
            pos2 = path.rfind('/')
            pos1 = path[:pos2 - 1].rfind('/')
            tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
            tag = re.sub(r'\d', '\d', tag)
            regex = path[:pos1 + 1] + tag + path[pos2:]
            rule1 = self.convert_regex_format(regex)
            return urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc + rule1
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
            print u"[Info] get_page_valid_urls() %s '下一页' not found @href [url] %s" % (e,org_url)

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
            url = urlparse.urljoin(org_url, urllib.quote(link))
            # print org_url, link, '->' ,url
            ret_urls.append(url)
        # print 'get_page_valid_urls() [urljoin]', ret_urls

        ret_urls = self.filter_links(ret_urls)
        # print 'get_page_valid_urls() end',ret_urls
        return ret_urls

    def extract_detail_rule_0(self, url):
        # rule0 是无条件转换（url一定是详情页）
        url_rule = self.convert_path_to_rule0(url)
        if url_rule:
            self.conn.zincrby(self.detail_urls_rule0_zset_key, value = url_rule, amount = 1)
        else:
            print '[ERROR] extract_detail_rule_0()',url
            self.conn.zadd(self.error_urls_zset_key,1, urllib.unquote(url))
        return

    def extract_detail_rule_1(self):
        #[rule1] rule0>100时，采集rule0的前10%高频规则，并累加rule0中的分数，需要确定匹配
        rules_0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        if rules_0_cnt > 50: # 100 rule0(score>20) -> rule1
            # 所有rule1清零
            rule1_org = self.conn.zrange(self.detail_urls_rule1_zset_key, start=0, end=-1)
            for rule1 in rule1_org:
                self.conn.zrem(self.detail_urls_rule1_zset_key, rule1)
            # rule1 重新积分
            rules_0 = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                            max=999999, min=20, start=0, num=rules_0_cnt/10, withscores=True)
            for rule_0, score_0 in dict(rules_0).iteritems():
                rule_1 = self.convert_path_to_rule1(rule_0)
                if rule_1:
                    self.conn.zincrby(self.detail_urls_rule1_zset_key, value=rule_1, amount=score_0)
        return

    def get_start_urls(self, data=None):
        if self.conn.zrank(self.list_urls_zset_key, self.start_urls) is None:
            self.conn.zadd(self.list_urls_zset_key, self.todo_flg, self.start_urls)
        return [self.start_urls]

    def parse(self, response):
        urls = self.get_todo_urls()
        return urls, None, None

    def parse_detail_page(self, response=None, url=None):
        # print 'parse_detail_page() start'
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
            # print 'parse_detail_page() data.html', data.html()
            valid_urls = self.get_page_valid_urls(data, org_url)
            # print '111111'
            for valid_url in valid_urls:
                # print '222222'
                if self.is_list_by_rule(valid_url):
                    # print 'list:',valid_url
                    if self.conn.zrank(self.list_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.list_urls_zset_key, self.todo_flg, urllib.unquote(valid_url))
                else:
                    # print 'detail:', valid_url
                    if self.conn.zrank(self.detail_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.detail_urls_zset_key, 0, urllib.unquote(valid_url))
                    self.extract_detail_rule_0(valid_url)
                    self.extract_detail_rule_1()

            print 'parse_detail_page() end'
        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)
            print 'parse_detail_page end'
        return result

if __name__ == '__main__':
    unit_test = False
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

