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
EXPORT_FOLDER = config.get('export', 'export_folder')
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


#############################################################################
class Util(object):
    def __init__(self):
        pass

    def convert_path_to_rule_advice(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print path
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''
        split_path = path.split('/')
        new_path_list = []
        for p in split_path:
            # regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', p)
            new_path_list.append(self.convert_regex_format_advice(regex))

        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

    def convert_regex_format_advice(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6,6}/[a-zA-Z]\d{8,8}_\d{6,6}.htm
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
                temp = '%s{%d,%d}' % (digit, cnt, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d,%d}' % (word, cnt, cnt)
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

    def merge_digit(self, rules):
        print '[INFO]merge_digit() start.', len(rules), rules
        for i in range(len(rules)):
            for j in range(i + 1, len(rules), 1):
                if self.is_same_rule(rules[i], rules[j]):
                    rule_new = self.merge_digit_scope(rules[i], rules[j])
                    # 原有全部替换为新规则
                    for k in range(len(rules)):
                        if rules[k] == rules[i]:
                            rules[k] = rule_new

                    for k in range(len(rules)):
                        if rules[k] == rules[j]:
                            rules[k] = rule_new

        rules = list(set(rules))
        rules.sort()
        print '[INFO]merge_digit() end.', len(rules), rules
        return rules

    def is_same_rule(self, rule1, rule2):
        ret = False
        if len(rule1) == len(rule2):
            for i in range(len(rule1)):
                if rule1[i] != rule2[i]:
                    if rule1[i].isdigit() and rule2[i].isdigit():
                        ret = True
                    else:
                        return False
        return ret

    def merge_digit_scope(self, rule1, rule2):
        ''' {1,2} + {2,3} -> {1,3}'''
        rule_new = ''
        for i in range(len(rule1)):
            if cmp(rule1[i], rule2[i]) < 0:
                if rule1[i - 1] == '{':
                    new = rule1[i]
                else:
                    new = rule2[i]
            elif cmp(rule1[i], rule2[i]) > 0:
                if rule1[i - 1] == '{':  # {M,N}
                    new = rule2[i]
                else:
                    new = rule1[i]
            else:
                new = rule1[i]

            rule_new += new

        return rule_new

    def without_digit_regex(self, regex):
        # '/post-culture-\\d{6,6}-\\d{1,1}.shtml' -> '/post-culture--.shtml'
        return re.sub(r'\\d\{\d\,\d\}', "", regex)

    def get_words(self, regex):
        # '/post-culture--.shtml' -> ['post','culture','shtml']
        words = []
        word = ''
        for i in range(len(regex)):
            if regex[i].isalpha():
                word += regex[i]
            else:
                if word != '':
                    words.append(word)
                word = ''

        return words

    def get_regexs_words_with_score(self, regexs, urls):
        print '[INFO]get_regexs_words_score() start.'
        ''' regexs:
            ['/post-\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/list-\\d{1,1}d-\\d{1,1}.shtml',
             '/list-\\d{2,4}-\\d{1,1}.shtml',
             '/list-apply-\\d{1,1}.shtml']

             return  {'apply': 1, 'post': 11, 'list': 3, 'd': 1, 'no': 2}
        '''
        all_words = []
        for regex in regexs:
            without_digit = self.without_digit_regex(regex)
            words = self.get_words(without_digit)
            all_words.extend(words)

        all_words = list(set(all_words))
        # all_words.sort()
        # print all_words

        all_words_dic = {}
        for w in all_words:
            w_cnt = 0
            for r in urls:
                path = urlparse.urlparse(r).path
                without_digit = self.without_digit_regex(path)
                words = self.get_words(without_digit)
                if w in words:
                    w_cnt += 1  # 匹配次数

            all_words_dic[w] = w_cnt

        sum = 0
        for i in all_words_dic.iteritems():
            (k, v) = i
            sum += v

        print '[INFO]get_regexs_words_score() end.', len(all_words_dic), 'sum=', sum, all_words_dic
        return all_words_dic

    def get_hot_words(self, all_words_dic):
        print '[INFO]get_hot_words() start.', all_words_dic
        ret_dict = {}

        sum = 0
        for (k, v) in all_words_dic.iteritems():
            sum += v

        dict = sorted(all_words_dic.iteritems(), key=lambda d: d[1], reverse=True)
        s = 0
        for i in dict:
            (k, v) = i
            if s >= sum * 0.8:
                break
            else:
                ret_dict.update({k: v})
                s += v

        print '[INFO]get_hot_words() end.', s, '/', sum, ret_dict
        return ret_dict

    def get_hot_regexs_with_score(self, merge_digit_list, urls):
        print '[INFO]get_hot_regexs_with_score() start.', len(urls), urls
        ret_dict = {}
        for regex in merge_digit_list:
            r_cnt = 0
            for url in urls:
                path = urlparse.urlparse(url).path
                if re.search(regex, path):
                    r_cnt += 1
            # 计数完毕保存
            ret_dict.update({regex: r_cnt})

        for url in urls:
            found = False
            for r in merge_digit_list:
                path = urlparse.urlparse(url).path
                if re.search(r, path):
                    found = True

            if found == False:
                print '[ERROR]get_hot_regexs_with_score() not match:', url

        sum = 0
        for i in ret_dict.iteritems():
            (k, v) = i
            sum += v

        print '[INFO]get_hot_regexs_with_score() end.', len(ret_dict), 'sum=', sum, ret_dict
        return ret_dict

    def get_hot_regexs(self, regexs_dic):
        print '[INFO]get_hot_regexs() start.', len(regexs_dic), regexs_dic
        ret_dict = {}

        sum = 0
        for (k, v) in regexs_dic.iteritems():
            sum += v

        dict = sorted(regexs_dic.iteritems(), key=lambda d: d[1], reverse=True)
        s = 0
        for i in dict:
            (k, v) = i
            if s >= sum * 0.8:
                break
            else:
                ret_dict.update({k: v})
                s += v

        print '[INFO]get_hot_regexs() end.', s, '/', sum, ret_dict
        return ret_dict

    def merge_word(self, advice_regex_dic, ignore_words):
        print '[INFO]merge_word() start.', advice_regex_dic, ignore_words
        ret_merged_list = []
        merged_word = {}
        for k, v in advice_regex_dic.items():
            matched = False
            # 和所有的忽略词匹配
            for word in ignore_words:
                if k.find(word) >= 0:
                    matched = True
                    replace = '[a-zA-Z]{%d,%d}' % (len(word), len(word))
                    regex = re.sub(word, replace, k)
                    merged_word.update({regex: v})

            # 没有忽略词匹配
            if matched is False:
                merged_word.update({k: v})

        l = [k for k, v in merged_word.items()]
        ret_merged_list = self.merge_digit(l)

        print '[INFO]merge_word() end.', ret_merged_list
        return ret_merged_list


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

        print '[INFO]filter_links() end', len(urls), urls
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
        print '[INFO]get_page_valid_urls() start', org_url
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
        print '[INFO]get_page_valid_urls() end', len(urls), urls
        return urls

    def parse_detail_page(self, response=None, url=None):
        print '[INFO]parse_detail_page() start.'
        advice_regex_dic = {}
        advice_words_dic = {}
        links = []
        util = Util()

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
            regexs = []
            for link in links:
                if link != '' and link[-1] != '/':
                    regex = util.convert_path_to_rule_advice(link)
                    if regex != '': regexs.append(regex)

            # 转换规则后
            regexs = list(set(regexs))
            regexs.sort()

            merge_digit_list = util.merge_digit(regexs)
            merge_digit_list.append('\/$')
            merge_digit_list.sort()

            regex_dic = util.get_hot_regexs_with_score(merge_digit_list, links)
            advice_regex_dic = util.get_hot_regexs(regex_dic)

            word_dic = util.get_regexs_words_with_score(merge_digit_list, links)
            advice_words_dic = util.get_hot_words(word_dic)

            # ignore_words = list(set([k for k, v in advice_words_dic.items()]) - set(['list', 'post', 'thread']))
            # advice_merge_word_list = util.merge_word(advice_regex_dic, ignore_words)

        except Exception, e:
            print "[ERROR] parse_detail_page(): %s [url] %s" % (e, org_url)

        print '[INFO]parse_detail_page() end.', len(advice_regex_dic), advice_regex_dic
        print '[INFO]parse_detail_page() end.', len(advice_words_dic), advice_words_dic

        return advice_regex_dic, advice_words_dic, links


########################################################################################
if __name__ == '__main__':
    util = Util()
    mySpider = MySpider()
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()
    response = mySpider.download(mySpider.start_urls)

    ret = mySpider.parse_detail_page(response, (mySpider.start_urls))

    f = open(EXPORT_FOLDER + 'advice(' + SITE_DOMAIN + ').json', "w")
    f.write(json.dumps(ret))
    f.close()
