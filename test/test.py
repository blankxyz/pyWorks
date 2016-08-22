#!/usr/bin/python
# coding=utf-8
import re
import urlparse
import redis

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


def convert_hold_word(url):
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    # print 'scheme:', scheme
    # print 'netloc:', netloc
    # print 'path:', path
    # print 'params:', params
    # print 'query:', query
    # print 'fragment:', fragment
    # if url.find('%') >= 0:

    url_new = urlparse.urlunparse(('', '', conjvert_path(path), params, conjvert_qurey(query), fragment))
    return url_new


def conjvert_path(path):
    # /forum.php
    # print path
    path_without_digit = re.sub(r'\d', '', path)
    return path_without_digit


def conjvert_qurey(query):
    # dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost
    # print query
    q = re.sub(r'=.*?&', '=&', query)
    qurey_without_digit = q[:q.rfind('=')+1]
    return qurey_without_digit

def convert_urls_to_rule(urls):
    ret = []
    for url in urls:
        rule = convert_hold_word(url)
        ret.append((rule,url))
    return ret

if __name__ == '__main__':
    url = 'http://www.cxljl.cn/forum/aaa/thread-111-11.html?dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost'
    # url= 'http://www.cxljl.cn/space-username-%CE%DE%D1%D4%B5%C4%B8%E7.html'
    start_url = 'http://www.cxljl.cn'
    site_domain = 'cxljl.cn'
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    urls = redis_db.get_list_urls()
    print urls
    print convert_urls_to_rule(urls)
