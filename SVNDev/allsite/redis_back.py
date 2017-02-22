#!/usr/bin/python
# coding=utf-8

import redis
import json
from pprint import pprint
import datetime

EXPORT_REDIS_SERVER = 'redis://192.168.187.55/15'
IMPORT_REDIS_SERVER = 'redis://127.0.0.1/10'

CONFIG_ID = '37556'  # 全站爬虫配置ID

##################################################################################################
class Backup(object):
    def __init__(self):
        self.conn_export = redis.StrictRedis.from_url(EXPORT_REDIS_SERVER)
        self.conn_import = redis.StrictRedis.from_url(IMPORT_REDIS_SERVER)
        self.export_path = 'export/'

        self.weixin_sns_info_file = self.export_path + 'weixin_sns_info_backup.json'
        self.weixin_time_location_file = self.export_path + 'weixin_time_location_backup.json'
        self.weixin_lbs_info_file = self.export_path + 'weixin_lbs_info_backup.json'


    def get_info_list(self):
        days = []
        for i in range(31):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            days.append(day.strftime('%Y%m%d'))

        for i in range(1, 10):
            j = (self.conn_export.hget(d + '_cfgid_td', CONFIG_ID + '_d' + str(i)))

        return self.conn_export.hgetall(self.weixin_sns_info_hset_key)

    def get_sns_info_cnt(self):
        return self.conn_export.hlen(self.weixin_sns_info_hset_key)

    def set_sns_info_list(self, sns_info_list):
        for k, v in sns_info_list.items():
            self.conn_import.hset(self.weixin_sns_info_hset_key, k, v)

    def get_time_location_list(self):
        return self.conn_export.hgetall(self.weixin_time_location_hset_key)

    def get_time_location_cnt(self):
        return self.conn_export.hlen(self.weixin_time_location_hset_key)

    def set_time_location_list(self, sns_time_location_list):
        for k, v in sns_time_location_list.items():
            self.conn_import.hset(self.weixin_time_location_hset_key, k, v)

    def get_lbs_info_list(self):
        return self.conn_export.hgetall(self.weixin_lbs_info_hset_key)

    def get_lbs_info_cnt(self):
        return self.conn_export.hlen(self.weixin_lbs_info_hset_key)

    def set_lbs_info_list(self, lbs_info_list):
        for k, v in lbs_info_list.items():
            self.conn_import.hset(self.weixin_lbs_info_hset_key, k, v)


def info_export():
    exp = Backup()
    print exp.weixin_sns_info_hset_key, exp.get_sns_info_cnt()
    info_list = exp.get_sns_info_list()
    j = json.dumps(info_list)
    fd = open(exp.weixin_sns_info_file, 'w')
    fd.write(j)
    fd.close()


def info_import():
    imp = Backup()
    fd = open(imp.weixin_sns_info_file, 'r')
    j = fd.read()
    pp = json.loads(j)
    # pprint(pp)
    fd.close()
    imp.set_sns_info_list(pp)
    print 'import:', imp.weixin_sns_info_hset_key


def time_location_export():
    exp = Backup()
    print exp.weixin_time_location_hset_key, exp.get_time_location_cnt()
    info_list = exp.get_time_location_list()
    j = json.dumps(info_list)
    fd = open(exp.weixin_time_location_file, 'w')
    fd.write(j)
    fd.close()


def time_location_import():
    imp = WinxinBackup()
    fd = open(imp.weixin_time_location_file, 'r')
    j = fd.read()
    pp = json.loads(j)
    # pprint(pp)
    fd.close()
    imp.set_time_location_list(pp)
    print 'import:', imp.weixin_time_location_hset_key


def lbs_info_export():
    exp = WinxinBackup()
    print exp.weixin_lbs_info_hset_key, exp.get_lbs_info_cnt()
    info_list = exp.get_lbs_info_list()
    j = json.dumps(info_list)
    fd = open(exp.weixin_lbs_info_file, 'w')
    fd.write(j)
    fd.close()


def lbs_info_import():
    imp = WinxinBackup()
    fd = open(imp.weixin_lbs_info_file, 'r')
    j = fd.read()
    pp = json.loads(j)
    # pprint(pp)
    fd.close()
    imp.set_lbs_info_list(pp)
    print 'import:', imp.weixin_lbs_info_hset_key


if __name__ == '__main__':
    # sns_info_export()
    sns_info_import()

    # time_location_export()
    time_location_import()

    # lbs_info_export()
    lbs_info_import()
