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
        # self.start_urls = 'http://baby.k618.cn/'
        # self.start_urls = 'http://www.yangtse.com/'
        self.start_urls = 'http://www.ynet.com/' # 北青网
        # self.start_urls = 'http://www.thepaper.cn/' # 澎湃新闻
        # self.start_urls = 'http://bbs.tianya.cn/'
        self.encoding = 'gbk' #k618 扬子晚报 地方领导留言板 北青网
        # self.encoding = 'utf-8' #tianya 澎湃新闻
        # self.site_domain = 'sina.com.cn'
        # self.site_domain = 'k618.cn'
        # self.site_domain = 'yangtse.com'
        self.site_domain = 'ynet.com' # 北青网
        # self.site_domain = 'thepaper.cn' # 澎湃新闻
        # self.site_domain = 'bbs.tianya.cn'
        # self.conn = redis.StrictRedis.from_url('redis://192.168.100.15/6')
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/5')
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

    def get_url_level(self, url):
        level = self.conn.zscore(self.ok_urls_zset_key, url)
        if level in None: level = 0
        return level

    def filter_links(self, urls):
        print 'filter_links() start', len(urls), urls
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
        print 'filter_links() end', len(urls), urls
        return urls

    def is_current_page(self, org_url):
        '''
        面包屑含有‘正文’,则判定为详情页,返回 True
        注）提取面包屑里面的链接
        '''
        response = self.download(org_url)
        char = re.search(r'charset=(.*)>',response.text)
        if char:
            if re.search("utf", char.group(1), re.I):
                encode = "utf8"
            elif re.search("gb", char.group(1), re.I):
                encode = "gbk"
            elif re.search('big5', char.group(1), re.I):
                encode = "big5"
        else:
            encode = "utf8"

        response.encoding = encode
        unicode_html_body = response.text  # unicode
        parse = htmlparser.Parser(data=unicode_html_body)
        nav_links = parse.replace('[\n\r]','').regexall(u'<div.*?正文.*?div>')
        # print nav_links
        for nav in nav_links:
            nav = nav.data[nav.data.rfind('<div'):]
            # print nav
            if nav.count('</a>') >0:
                hrefs = re.findall(r'href=\"(.*?)\"', nav)
                for href in hrefs:
                    scheme, netloc, path, params, query, fragment = urlparse.urlparse(href)
                    if scheme:
                        url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
                    else:
                        href = urlparse.urlunparse(('', '', path, params, query, ''))
                        url = urlparse.urljoin(org_url, href)
                        if self.conn.zrank(self.list_urls_zset_key, url) is None:
                            self.conn.zadd(self.list_urls_zset_key, self.todo_flg, url)
                return True
        return False

    def is_list_by_link_density(self, url):
        # print 'is_list_by_link_density start'
        response = self.download(url)
        doc = myreadability.Document(response.content, encoding=self.encoding)
        ret = doc.is_list() # 链接密度
        # ret = doc.is_list_main_div()  # 链接密度
        return ret

    def is_list_by_rule_0(self, url):
        #[rule0] rule0收集数>100时，匹配次数>10 的前10%高频度规则
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        if rule0_cnt > 5:
            rules = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                                               max=999999, min=10, start=0, num=rule0_cnt/10, withscores=False)
            for rule0 in rules:
                if re.search(rule0, url):
                    print '[rule0]', rule0, '<-', url
                    return False #符合详情页规则
        return True #不确定

    def is_list_by_rule_1(self ,url):
        #[rule1] rule1收集数>10时，匹配次数>20 的前20%高频度规则
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        if rule1_cnt > 5:
            rules = self.conn.zrevrangebyscore(self.detail_urls_rule1_zset_key,
                            max=999999, min=20, start=0, num=rule1_cnt/5, withscores=False)
            for rule1 in rules:
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
            if path.find('index') > 0 or path.find('list') >0 and path.find('post') < 0 and path.find('content') < 0:
                return True
            if path[1:].isalpha():
                return True
            # 优先使用rule1
            if self.is_list_by_rule_1(url) == False:
                return False
            # 使用rule0
            if self.is_list_by_rule_0(url) == False:
                return False
            # 判断面包屑中有无的‘正文’
            if self.is_current_page(url) == True:
                return False
            # 使用链接密度
            return self.is_list_by_link_density(url)
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
        # regex = urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc + path[:pos1 + 1] + regex + path[pos2:]
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
            # return urlparse.urlparse(rule0).scheme +'://'+ urlparse.urlparse(rule0).netloc + path[:pos1 + 1] + rule1 + path[pos2:]
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

    def get_page_valid_urls(self, data, org_url):
        print 'get_page_valid_urls() start',org_url
        urls = []
        all_links = []
        remove_links = []
        # 移除下一页及其他
        try:
            self_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/@href")
            print 'self_links', self_links
            # print '222222'
        except Exception, e:
            print u"[Info] get_page_valid_urls() [@href] %s not found 下一页. [Exception] %s" % (org_url, e)
        else:
            for link in self_links: remove_links.append(link.text().strip())

        try:
            next_links = data.xpathall(u"//a[text()='下一页' or text()='下页']/preceding-sibling::a/@href")
            print 'next_links', next_links
        except Exception, e:
            print u"[Info] get_page_valid_urls() [@href] %s not found 下一页 及其他. [Exception] %s" % (org_url, e)
        else:
            for link in next_links: remove_links.append(link.text().strip())

        #移除footer及其他
        try:
            foot_links= data.xpathall(u"//a[text()='联系我们']/@href")
            print 'foot_links',foot_links
        except Exception, e:
            print u"[Info] get_page_valid_urls() [@href] %s not found 关于我们. [Exception] %s" % (org_url, e)
        else:
            for link in foot_links: remove_links.append(link.text().strip())

        try:
            footer_preceding = data.xpathall(u"//a[text()='联系我们']/preceding-sibling::a/@href")
            footer_following = data.xpathall(u"//a[text()='联系我们']/following-sibling::a/@href")
            print 'footer_links',footer_preceding,footer_following
        except Exception, e:
            print u"[Info] get_page_valid_urls() [@href] %s not found 关于我们 及其他. [Exception] %s" % (org_url, e)
        else:
            for link in footer_preceding: remove_links.append(link.text().strip())
            for link in footer_following: remove_links.append(link.text().strip())

        # print 'get_page_valid_urls() [self_links]', self_links
        # print 'get_page_valid_urls() [next_links]', next_links
        # links = data.xpathall("//a/@href | //iframe/@src")
        links = data.xpathall("//a[string-length(text())<=10]/@href | //iframe/@src")
        # print org_url
        # print data.html()
        print '//a',len(links), links
        for link in links:
            all_links.append(link.text().strip())
        print 'get_page_valid_urls() [all_links]',all_links

        links = list(set(all_links) - set(remove_links))
        print 'get_page_valid_urls() [all_links-remove_links]', links
        for link in links:
            # print org_url, link, '->'
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link)
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                # url = urlparse.urljoin(org_url, urllib.quote(link))
                url = urlparse.urljoin(org_url, link)
            urls.append(url)
            # url = urlparse.urljoin(org_url, urllib.quote(path))
            # print org_url, link, '->' ,url
        # print 'get_page_valid_urls() [urljoin]', urls
        urls = self.filter_links(urls)
        # print 'get_page_valid_urls() end',urls
        return urls

    def extract_detail_rule_0(self, url):
        # rule0 是无条件转换（url一定是详情页）
        url_rule = self.convert_path_to_rule0(url)
        if url_rule:
            self.conn.zincrby(self.detail_urls_rule0_zset_key, value = url_rule, amount = 1)
        else:
            print '[ERROR] extract_detail_rule_0()',url
            self.conn.zadd(self.error_urls_zset_key,1, url)
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
        # return []

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
            # print '000000'
            valid_urls = self.get_page_valid_urls(data, org_url)
            # print '111111'
            for valid_url in valid_urls:
                # print '222222'
                if self.is_list_by_rule(valid_url):
                    print 'list  :',valid_url
                    # if self.conn.zrank(self.list_urls_zset_key, valid_url+'/'):
                    #     break
                    if self.conn.zrank(self.list_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.list_urls_zset_key, self.todo_flg, urllib.unquote(valid_url))
                        # self.conn.zadd(self.list_urls_zset_key, self.todo_flg, valid_url)
                else:
                    print 'detail:', valid_url
                    if self.conn.zrank(self.detail_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.detail_urls_zset_key, 0, urllib.unquote(valid_url))
                        # self.conn.zadd(self.detail_urls_zset_key, 0, valid_url)
                    self.extract_detail_rule_0(urllib.unquote(valid_url))
                    self.extract_detail_rule_1()
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
        # url = 'http://bbs.tianya.cn/'
        # url = 'http://www.yangtse.com/yzkl'
        # url = 'http://news.ynet.com/2.1.0/85245.html'
        # url = 'http://news.ynet.com/2.1.0/83911.html'
        # url = 'http://edu.ynet.com/2.1.0/29293.html'
        url = 'http://sports.ynet.com/2.1.0/85507.html'
        print '[url]',url
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

        print mySpider.is_list_by_rule(url)

if __name__ == '__main__':
    test(unit_test = True)
    # import cProfile
    # cProfile.run("test(unit_test = False)")
