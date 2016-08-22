#!/usr/bin/python
# coding=utf-8
import re
import urlparse
import redis
import urllib

REDIS_SERVER = 'redis://127.0.0.1/14'


class RedisDrive(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果(列表)
        self.detail_urls_set_key = 'detail_urls_set_%s' % self.site_domain  # 计算结果(详情)
        self.unkown_urls_set_key = 'unkown_urls_set_%s' % self.site_domain  # 计算结果(未知)
        self.manual_w_list_rule_zset_key = 'manual_w_list_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_list_rule_zset_key = 'manual_b_list_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.manual_w_detail_rule_zset_key = 'manual_w_detail_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_detail_rule_zset_key = 'manual_b_detail_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.list_rules = []  # 手工配置规则-内存形式
        self.detail_rules = []  # 手工配置规则-内存形式
        self.todo_flg = -1
        self.done_flg = 0
        self.detail_flg = 1
        self.content_flg = 9
        self.end_flg = 99  # 状态管理flg最大值

    def get_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.end_flg, withscores=False)


def compress_url(url):
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    # if url.find('%') >= 0:
    url_new = urlparse.urlunparse(('', '', compress_path(path), params, compress_qurey(query), fragment))
    return url_new


def compress_path(path):
    # /forum.php
    # print path
    path_without_digit = re.sub(r'\d', '', path)
    return path_without_digit


def compress_qurey(query):
    # dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost
    # print query
    q = re.sub(r'=.*?&', '=&', query)
    qurey_without_digit = q[:q.rfind('=') + 1]
    return qurey_without_digit


def convert_urls_to_category(urls):
    category_dict = {}
    for url in urls:
        category = compress_url(url)
        if category_dict.has_key(category):
            url_list = category_dict.pop(category)
            url_list.append(url)
            category_dict.update({category: url_list})
        else:
            url_list = [url]
            category_dict.update({category: url_list})
    return category_dict

def union_query(category_dict):
    ret = {}
    #{'/shop/index.php?act=&area_id=&brand=&key=&op=&order=':
    #['http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=0&op=list&order=0',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=1&op=list&order=2',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=2&op=list&order=2'],
    #
    #'/shop/index.php?act=&brand=&key=&op=&order=':
    #['http://shop.cxljl.cn/shop/index.php?act=brand&brand=365&key=0&op=list&order=0',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&brand=365&key=1&op=list&order=2',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&brand=365&key=2&op=list&order=2'] }
    category_list = category_dict.keys()
    for category in category_list:
        url_list = category_dict.pop(category)
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(category)
        # print scheme, netloc, path, params, query, fragment
        # /shop/index.php  key=&act=&area_id=&brand=&op=&order=
        # -> [('key', ''), ('act', ''), ('area_id', ''), ('brand', ''), ('op', ''), ('order', '')]
        keyvals = urlparse.parse_qsl(query, keep_blank_values=1)
        # print keyvals
        keyvals.sort()
        query = urllib.urlencode(keyvals)
    return query

if __name__ == '__main__':
    # url = 'http://www.cxljl.cn/forum/aaa/thread-111-11.html?dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost'
    # url= 'http://www.cxljl.cn/space-username-%CE%DE%D1%D4%B5%C4%B8%E7.html'
    url = '/shop/index.php?key=&act=&area_id=&brand=&op=&order='
    # start_url = 'http://www.cxljl.cn'
    # site_domain = 'cxljl.cn'
    # redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    # urls = redis_db.get_list_urls()
    # print urls
    # print convert_urls_to_category(urls)
    print sort_query(url)
