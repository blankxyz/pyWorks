#!/usr/bin python
# coding=utf-8

import redis

class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_cn_domain_site = 'hash_cn_domain_site'  # 网站域名: 首页地址
        self.hash_cn_site_index = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.hash_cn_domain_site_index = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def move(self):
        l = self.conn.hgetall(self.hash_cn_site_index)
        for (k,v) in l.items():
