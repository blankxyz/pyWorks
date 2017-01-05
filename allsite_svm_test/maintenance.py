#!/usr/bin python
# coding=utf-8

import redis
import time
import pymongo
import socket
import urllib
import json
from pprint import pprint

MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'

REDIS_SERVER = 'redis://192.168.187.101/2'  # 'redis://192.168.174.130/12'

URL_PRE = "http://ip.taobao.com/service/getIpInfo.php?ip="


class Util():
    @staticmethod
    def domain_ip_location(domain):
        '''
        # {"code":0,
        #  "data":
        #  {"country":"\u4e2d\u56fd",
        #   "country_id":"CN",
        #   "area":"\u534e\u5357",
        #   "area_id":"800000",
        #   "region":"\u6d77\u5357\u7701",
        #   "region_id":"460000",
        #   "city":"\u6d77\u53e3\u5e02",
        #   "city_id":"460100",
        #   "county":"",
        #   "county_id":"-1",
        #   "isp":"\u7535\u4fe1",
        #   "isp_id":"100017",
        #   "ip":"124.225.214.205"}
        # }
        '''
        ip = socket.gethostbyname_ex(domain)[-1][0]
        data = urllib.urlopen(URL_PRE + ip).read()
        j = json.loads(data)
        # pprint(j)
        return j["data"]["city"]


class MongoDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.allsite_db
        self.site_cn_all = self.db.site_cn_all

    def insert_one(self, domain, site, name, city, crawlTime, hubPageCnt):
        self.site_cn_all.insert({"domain": domain,
                                 "site": site,
                                 "name": name,
                                 "city": city,
                                 "crawlTime": crawlTime,
                                 "hubPageCnt": hubPageCnt
                                 })


class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.hash_cn_domain_site = 'hash_cn_domain_site'  # 网站域名: 首页地址
        self.hash_cn_site_index = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.hash_cn_domain_site_name = 'hash_cn_domain_site_name'  # 首页地址: 网站名字
        self.zset_domain_crawltime = 'zset_domain_crawltime'
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def get_listPage_cnt(self, domain):
        cnt = 0
        domain_key = self.site_hub_pre % domain
        if self.conn.keys(domain_key):
            cnt = self.conn.scard(domain_key)

        return cnt

    def marge(self):
        self.conn.delete(self.hash_cn_domain_site_name)
        cnt = self.conn.hlen(self.hash_cn_domain_site)
        l = self.conn.hgetall(self.hash_cn_domain_site)
        for (domain, site) in l.items():
            name = self.conn.hget(self.hash_cn_site_index, site)
            hubPageCnt = self.get_listPage_cnt(domain)
            crawlTime = self.conn.zscore(self.zset_domain_crawltime, domain)
            if crawlTime:
                crawlTime = int(float(crawlTime))
                timeArray = time.localtime(crawlTime)
                crawlTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            else:
                crawlTime = ''

            self.conn.hset(self.hash_cn_domain_site_name, domain,
                           {'site': site, 'name': name, 'hubPageCnt': hubPageCnt, 'crawlTime': crawlTime})
            cnt = cnt - 1

            mgd = MongoDriver()
            # city = Util.domain_ip_location(domain)
            city = ''
            mgd.insert_one(domain, site, name, city, crawlTime, hubPageCnt)
            print 'process the redis key remain: ', cnt, domain, crawlTime

    def get_all_domain_site_name(self):
        ret = []
        l = self.conn.hgetall(self.hash_cn_domain_site_name)
        # pprint(l)
        for (domain, site_name) in l.items():
            site_name = eval(site_name)
            ret.append([domain, site_name['site'],
                        site_name['name']])

        return ret


def main():
    db = DBDriver()
    db.marge()
    # db.get_all_domain_site_name()
    # print Util.domain_ip_location('online.sh.cn')


if __name__ == '__main__':
    main()
