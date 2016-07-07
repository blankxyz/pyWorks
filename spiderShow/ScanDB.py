#!/usr/bin/env python
# coding=utf-8
from threading import Timer
import datetime
import time
import redis
import MySQLdb
import json


class ScanDB:

    def __init__(self,site_domain,redis_db):
        # self.site_domain = 'k618.cn'
        self.site_domain = site_domain
        self.conn = redis.StrictRedis.from_url(redis_db)
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.crumbs_urls_zset_key = 'crumbs_urls_zset_%s' % self.site_domain
        self.hub_todo_urls_zset_key = 'hub_todo_urls_zset_%s' % self.site_domain
        self.hub_level_urls_zset_key = 'hub_level_urls_zset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        self.offline = False

    def process(self, interval):
        if self.offline is False:
            show_data = []
            conn = MySQLdb.connect(
                host=self.host, user=self.user, passwd=self.password, port=self.port, charset="utf8")
            cur = conn.cursor()
            conn.select_db('allsite')
            cnt = cur.execute("select * from process")
            print cnt
            rs = cur.fetchall()
            for r in rs:
                # print r
                process = {}
                process['time'] = r[0]
                process['rule0'] = r[1]
                process['rule1'] = r[2]
                process['detail'] = r[3]
                process['list'] = r[4]
                process['list_done'] = r[5]
                show_data.append(process)
            conn.commit()
            cur.close()
            conn.close()
            # dump json to file
            jsonStr = json.dumps(show_data)  # object to json encode
            fp = open(self.path + "db-process.json", 'w')
            fp.write(jsonStr)
            fp.close()
        else:
            fp = open(self.path + "db-process.json", 'r')
            jsonStr = fp.read()
            fp.close()
            # print  jsonStr
        return jsonStr

    def collageCount_allsite(self):
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        detail_cnt = self.conn.zcard(self.detail_urls_zset_key)
        list_cnt = self.conn.zcard(self.list_urls_zset_key)
        list_done_urls = self.conn.zrangebyscore(
            self.list_urls_zset_key, self.done_flg, self.done_flg)
        list_done_cnt = len(list_done_urls)
        t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cnt_info = {'times': t_stamp, 'rule0_cnt': rule0_cnt, 'rule1_cnt': rule1_cnt,
                    'detail_cnt': detail_cnt, 'list_cnt': list_cnt, 'list_done_cnt': list_done_cnt}
        self.conn.hset(
            self.process_cnt_hset_key, t_stamp, json.dumps(cnt_info))
        print cnt_info
        jsonStr = json.dumps(cnt_info)
        fp = open("process-allsite.json", 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()

    def collageCount_crumbs(self):
        crumbs_cnt = self.conn.zcard(self.crumbs_urls_zset_key)
        hub_level_cnt = self.conn.zcard(self.hub_level_urls_zset_key)
        hub_cnt = self.conn.zcard(self.hub_todo_urls_zset_key)
        hub_done_urls = self.conn.zrangebyscore(
            self.hub_todo_urls_zset_key, self.done_flg, self.done_flg)
        hub_done_cnt = len(hub_done_urls)
        t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cnt_info = {'times': t_stamp, 'crumbs_cnt': crumbs_cnt, 'hub_cnt': hub_cnt,
                    'hub_level_cnt': hub_level_cnt, 'hub_done_cnt': hub_done_cnt}
        # self.conn.hset(
        #     self.process_cnt_hset_key, t_stamp, json.dumps(cnt_info))
        print cnt_info
        jsonStr = json.dumps(cnt_info)
        fp = open("process-tianya.json", 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()

    def exportDB(self):
        #列表页
        total = self.conn.zcard(self.list_urls_zset_key)
        fp = open('export-'+self.list_urls_zset_key+'('+ str(total) +').log','a')
        fp.write('total:' + str(total) + '\n')
        for line in self.conn.zrange(self.list_urls_zset_key,0,-1,withscores=True):
            (k, v) = line
            fp.write(k + ',' + str(v) + '\n')
        fp.close()

        # 详情页
        total = self.conn.zcard(self.detail_urls_zset_key)
        fp = open('export-' + self.detail_urls_zset_key +'('+ str(total) + ').log', 'a')
        fp.write('total:' + str(total) + '\n')
        for line in self.conn.zrange(self.detail_urls_zset_key, 0, -1, withscores=True):
            (k, v) = line
            fp.write(k + ',' + str(v) + '\n')
        fp.close()

        # url0
        total = self.conn.zcard(self.detail_urls_rule0_zset_key)
        fp = open('export-' + self.detail_urls_rule0_zset_key +'('+ str(total) + ').log', 'a')
        fp.write('total:' + str(total) + '\n')
        for line in self.conn.zrange(self.detail_urls_rule0_zset_key, 0, -1, withscores=True):
            (k, v) = line
            fp.write(k + ',' + str(v) + '\n')
        fp.close()

        # url1
        if self.conn.exists(self.detail_urls_rule1_zset_key):
            total = self.conn.zcard(self.detail_urls_rule1_zset_key)
            fp = open('export-' + self.detail_urls_rule1_zset_key +'('+ str(total) + ').log', 'a')
            fp.write('total:' + str(total) + '\n')
            for line in self.conn.zrange(self.detail_urls_rule1_zset_key, 0, -1, withscores=True):
                (k,v) = line
                fp.write(k + ',' + str(v) + '\n')
            fp.close()

if __name__ == '__main__':
    timer_interval = 1
    # scan = ScanDB(site_domain='bbs.tianya.cn', redis_db='redis://127.0.0.1/1') #天涯bbs
    # scan = ScanDB(site_domain='yangtse.com',redis_db='redis://127.0.0.1/2') #扬子晚报
    # scan = ScanDB(site_domain='liuyan.people.com.cn', redis_db='redis://127.0.0.1/3') #地方领导留言板
    # scan = ScanDB(site_domain='ynet.com', redis_db='redis://127.0.0.1/13') #北青网
    # scan = ScanDB(site_domain='cpd.com.cn', redis_db='redis://127.0.0.1/9') #中国警察网
    # scan = ScanDB(site_domain='bjnews.com.cn', redis_db='redis://127.0.0.1/10') #新京报
    # scan = ScanDB(site_domain='cankaoxiaoxi.com', redis_db='redis://127.0.0.1/12') #参考消息
    # scan = ScanDB(site_domain='thepaper.cn', redis_db='redis://127.0.0.1/11')  # 澎湃新闻
    scan = ScanDB(site_domain='bashan.com', redis_db='redis://127.0.0.1/7')  # 巴山财经
    scan = ScanDB(site_domain='hsw.cn', redis_db='redis://127.0.0.1/8')  # 华商报

    t = Timer(timer_interval, scan.collageCount_crumbs)
    t = Timer(timer_interval, scan.collageCount_allsite)
    t.start()

    while True:
        time.sleep(60)
        scan.collageCount_allsite()
        # scan.collageCount_crumbs()


    #---------------------------------------------
    # scan.exportDB()
