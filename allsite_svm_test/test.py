#!/usr/bin python
# coding=utf-8

import redis
from pprint import pprint

class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_cn_domain_site = 'hash_cn_domain_site'  # 网站域名: 首页地址
        self.hash_cn_site_index = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.hash_cn_domain_site_name = 'hash_cn_domain_site_name'  # 首页地址: 网站名字
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def move(self):
        cnt = self.conn.hlen(self.hash_cn_domain_site)
        l = self.conn.hgetall(self.hash_cn_domain_site)
        for (domain, site) in l.items():
            name = self.conn.hget(self.hash_cn_site_index, site)
            self.conn.hset(self.hash_cn_domain_site_name, domain, {'site': site, 'name': name})
            cnt = cnt - 1
            print cnt

    def get_all_domain_site_name(self):
        ret = []
        l = self.conn.hgetall(self.hash_cn_domain_site_name)
        # pprint(l)
        for (domain, site_name) in l.items():
            site_name = eval(site_name)
            ret.append([domain, site_name['site'], site_name['name']])

        return ret

def main():
    db = DBDriver()
    # db.move()
    db.get_all_domain_site_name()


if __name__ == '__main__':
    main()
