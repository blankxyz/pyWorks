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


##################################################################################################
class Util(object):
    def __init__(self):
        pass

    # 未匹配URL归类算法
    def compress_url(self, url):
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
        # if url.find('%') >= 0:
        url_new = urlparse.urlunparse((scheme, netloc, self.compress_path_digit(path), params,
                                       self.compress_qurey(query), fragment))
        return url_new

    def compress_path_digit(self, path):
        # http://www.ynsf.ccoo.cn/forum/board-61399-1-1.html
        # -> http://www.ynsf.ccoo.cn/forum/board-999-999-999.html
        path_without_digit = re.sub(r'\d+', '999', path)
        return path_without_digit

    def compress_qurey(self, query):
        # dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost
        # print query
        q = re.sub(r'=.*?&', '=&', query)
        qurey_without_digit = q[:q.rfind('=') + 1]
        return qurey_without_digit

    def compress_path_alpha(self, url):
        # http://www.ynsf.ccoo.cn/forum/board-999-999-999.html
        # -> http://www.ynsf.ccoo.cn/aaa/aaa-999-999-999.html
        # url ='http://www.ynsf.ccoo.cn/forum/board-999-999-999.html'
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print type(scheme), type(netloc), type(path), type(params), type(query), type(fragment)
        if path.rfind('.') >= 0:
            path_without_alpha = re.sub(r'[a-zA-Z]+', 'aaa', path[:path.rfind('.')]) + path[path.rfind('.'):]
        else:
            path_without_alpha = re.sub(r'[a-zA-Z]+', 'aaa', path)
        # path_without_alpha = path
        # print (scheme, netloc, path_without_alpha, params, query, fragment)
        return urlparse.urlunparse((scheme, netloc, path_without_alpha, params, query, fragment))

    def convert_urls_to_category(self, urls):
        category_dict = {}
        for url in urls:
            category = self.compress_url(url)
            if category_dict.has_key(category):
                url_list = category_dict.pop(category)
                url_list.append(url)
                category_dict.update({category: url_list})
            else:
                url_list = [url]
                category_dict.update({category: url_list})
        return category_dict

    def compress_category_alpha(self, category_dict):
        category_compress_dict = {}
        category_list = []
        for (category, url_list) in category_dict.items():
            category_compress = self.compress_path_alpha(category)
            category_list.append((category_compress,len(url_list)))

        category_set = set([k for (k,v) in category_list])
        for category in category_set:
            l = 0
            for (k, v) in category_list:
                if category == k:
                    l += v
            category_compress_dict.update({category: l})

        return category_compress_dict


def union_query(category_dict):
    ret = {}
    # {'/shop/index.php?act=&area_id=&brand=&key=&op=&order=':
    # ['http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=0&op=list&order=0',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=1&op=list&order=2',
    # 'http://shop.cxljl.cn/shop/index.php?act=brand&area_id=0&brand=365&key=2&op=list&order=2'],
    #
    # '/shop/index.php?act=&brand=&key=&op=&order=':
    # ['http://shop.cxljl.cn/shop/index.php?act=brand&brand=365&key=0&op=list&order=0',
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
    util = Util()
    url = 'http://www.ynsf.ccoo.cn/forum/login.asp?comeurl='
    # url= 'http://www.cxljl.cn/space-username-%CE%DE%D1%D4%B5%C4%B8%E7.html'
    # url = '/shop/index.php?key=&act=&area_id=&brand=&op=&order='
    start_url = 'http://www.ynsf.ccoo.cn'
    site_domain = 'ynsf.ccoo.cn'
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    unkown_url_list = redis_db.get_list_urls()

    # 数字归一化后分类统计
    category_dict = util.convert_urls_to_category(unkown_url_list)
    category_keys = category_dict.keys()
    l = 0
    for k, v in category_dict.items(): l += len(v)
    print 'category_dict', l, category_dict
    print 'category_list', len(category_keys), category_keys

    category_compress_dict = util.compress_category_alpha(category_dict)
    l = 0
    for k, v in category_compress_dict.items():  l += v
    print 'category_compress_dict', l, category_compress_dict
    # category_compress_list = []
    # category_cnt_list = []
    # for (k, v) in category_compress_dict.items():
    #     category_compress_list.append(k)
    #     category_cnt_list.append(str(v))
    #
    # category_str = ("'" + "','".join(category_compress_list) + "'")
    # category_matched_cnt = ','.join(category_cnt_list)
    #
    # print 'category_str', category_str
    # print 'category_matched_cnt', category_matched_cnt
