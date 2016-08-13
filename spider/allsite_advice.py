#!/usr/bin/python
# coding=utf-8

import re
import os
import datetime
import urlparse
import redis
import MySQLdb
import spider
import setting
import urllib
import ConfigParser
from bs4 import BeautifulSoup, Comment
import json
import allsite_clean_url

##############################################################################
# INIT_CONFIG = '/work/spider/allsite.ini' #linux
INIT_CONFIG = './allsite.ini'  # windows
# INIT_CONFIG = '/Users/song/workspace/pyWorks/spider/allsite.ini' #mac
##############################################################################
config = ConfigParser.ConfigParser()
if len(config.read(INIT_CONFIG)) == 0:
    print '[ERROR]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[INFO] read the config file.', INIT_CONFIG

# export path
# windows or linux or mac
if os.name == 'nt':
    EXPORT_FOLDER = config.get('windows', 'export_folder')
else:
    EXPORT_FOLDER = config.get('linux', 'export_folder')
# redis
REDIS_SERVER = config.get('redis', 'redis_server')
DEDUP_SETTING = config.get('redis', 'dedup_server')

# spider-modify-start
# START_URLS = None
# SITE_DOMAIN = None
# BLACK_DOMAIN_LIST = None
# DETAIL_RULE_LIST = None
# LIST_RULE_LIST = None
# spider-modify-end
MODE = config.get('spider', 'mode')
START_URLS = config.get('spider', 'start_urls')
SITE_DOMAIN = config.get('spider', 'site_domain')
BLACK_DOMAIN_LIST = config.get('spider', 'black_domain_list')
DETAIL_RULE_LIST = config.get('spider', 'detail_rule_list')
LIST_RULE_LIST = config.get('spider', 'list_rule_list')

#####################################################################################
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
        # print '[INFO]filter_links() start', len(urls), urls
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

        # print '[INFO]filter_links() end', len(urls), urls
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
                if path == '': path = '/'
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                # url = urlparse.urljoin(org_url, urllib.quote(link))
                url = urlparse.urljoin(org_url, link)

            urls.append(url)

        # print '[INFO]urls_join() end', urls
        return urls

    def get_page_valid_urls(self, soup, org_url):
        # print '[INFO]get_page_valid_urls() start', org_url
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
        urls = self.filter_links(urls)
        urls.sort()
        # print '[INFO]get_page_valid_urls() end', len(urls), urls
        return urls

    def parse_detail_page(self, response=None, url=None):
        # print '[INFO]parse_detail_page() start.'
        # advice_regex_dic = {}
        # advice_words_dic = {}
        links = []
        # util = Util()

        if response is None: return []

        if url is None:
            org_url = response.request.url
        else:
            org_url = response.url

        try:
            soup = self.get_clean_soup(response)
            if soup is None: return []
            links = self.get_page_valid_urls(soup, org_url)
            links = list(set(links))

        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)

        return links
########################################################################################
if __name__ == '__main__':
    mySpider = MySpider()
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()
    response = mySpider.download(mySpider.start_urls)

    ret = mySpider.parse_detail_page(response, (mySpider.start_urls))

    print '[INFO]write to ', EXPORT_FOLDER + 'advice(' + SITE_DOMAIN + ').json'
    f = open(EXPORT_FOLDER + 'advice(' + SITE_DOMAIN + ').json', "w")
    f.write(json.dumps(ret))
    f.close()
