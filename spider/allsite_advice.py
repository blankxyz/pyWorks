#!/usr/bin/python
# coding=utf-8

import re
import os
import datetime
import urlparse
import redis
import spider
import setting
import urllib
import ConfigParser
from bs4 import BeautifulSoup, Comment
import requests
import allsite_clean_url

####################################################################
# INIT_CONFIG = '/work/spider/allsite.ini' #linux
INIT_CONFIG = './allsite.ini'  # windows
# INIT_CONFIG = '/Users/song/workspace/pyWorks/spider/allsite.ini' #mac
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

MODE = config.get('spider', 'mode')
START_URLS = config.get('spider', 'start_urls')
SITE_DOMAIN = config.get('spider', 'site_domain')
BLACK_DOMAIN_LIST = config.get('spider', 'black_domain_list')
DETAIL_RULE_LIST = config.get('spider', 'detail_rule_list')
LIST_RULE_LIST = config.get('spider', 'list_rule_list')


#############################################################################

class Util(object):
    def __init__(self):
        pass

    def convert_path_to_rule(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print path
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''
        # print suffix,path
        split_path = path.split('/')
        # print split_path
        new_path_list = []
        for p in split_path:
            regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', regex)
            new_path_list.append(self.convert_regex_format(regex))
        # print new_path
        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

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

    def convert_regex_format_keyword(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
        '''
        ret = ''
        digit = '\d'
        word = 'unkown'
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
        self.site_domain = SITE_DOMAIN
        self.black_domain_list = BLACK_DOMAIN_LIST
        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.detail_rules = []
        self.list_rules = []
        self.dedup_key = 'dedup'
        self.cleaner = allsite_clean_url.Cleaner(
            site_domain=self.site_domain,
            black_domain_list=self.black_domain_list,
            conn=redis.StrictRedis.from_url(REDIS_SERVER))

    def filter_links(self, urls):
        print '[INFO]filter_links() start', len(urls), urls
        try:
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
            urls = filter(lambda x: not self.cleaner.in_black_list(x), urls)  # bbs. mail.
            # print 'filter_links() in_black_list', len(urls)
            # 链接时间过滤
            # urls = filter(lambda x: not self.cleaner.is_old_url(x), urls)
            # 非第一页链接过滤
            urls = filter(lambda x: not self.cleaner.is_next_page(x), urls)
            # print 'filter_links() is_next_page', len(urls)
            # 去重
            urls = list(set(urls))
            # print 'filter_links() set', len(urls)
            # 404
            # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
            # print '[INFO]filter_links() end', len(urls), urls
        except Exception, e:
            print '[ERROR]filter_links()', e
        return urls


    def get_clean_soup(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
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
        # print '[INFO]urls_join() start',org_url,links
        urls = []
        for link in links:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link.strip())
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                # url = urlparse.urljoin(org_url, urllib.quote(link))
                # print '[INFO]urljoin()', org_url, link
                url = urlparse.urljoin(org_url, link)

            urls.append(url)

        # print '[INFO]urls_join() end', urls
        return urls

    def get_page_valid_urls(self, soup, org_url):
        print '[INFO]get_page_valid_urls() start'
        all_links = []
        remove_links = []
        try:
            for tag in soup.find_all("a"):
                if tag.has_attr('href'):
                    all_links.append(tag['href'])

            for tag in soup.find_all("a", href=re.compile(r"(javascript.*?|#.*?)", re.I)):
                if tag.has_attr('href'):
                    remove_links.append(tag['href'])

        except Exception, e:
            print '[ERROR]get_page_valid_urls()', e

        removed = list(set(all_links) - set(remove_links))

        urls = self.urls_join(org_url, removed)
        # print len(all_links), all_links
        # print len(remove_links), remove_links
        # print len(removed), removed
        print len(urls), urls
        urls = self.filter_links(urls)
        print '[INFO]get_page_valid_urls() end'
        return urls

    def parse_detail_page(self, response=None, url=None):
        advice_regexs = []
        if response is None: return advice_regexs

        if url is None:
            org_url = response.request.url
        else:
            org_url = response.url

        try:
            soup = self.get_clean_soup(response)
            if soup is None: return []
            links = self.get_page_valid_urls(soup, org_url)
            util = Util()
            for link in links:
                regex = util.convert_regex_format_keyword(link)
                advice_regexs.append(regex)

        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)
        return advice_regexs


########################################################################################
if __name__ == '__main__':
    mySpider = MySpider()
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()

    response = mySpider.download(mySpider.start_urls)

    ret = mySpider.parse_detail_page(response, (mySpider.start_urls))
    print ret
