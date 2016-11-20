#!/usr/bin/python
# coding=utf-8

import redis
import json
from pprint import pprint

EXPORT_REDIS_SERVER = 'redis://192.168.187.56/0'
IMPORT_REDIS_SERVER = 'redis://127.0.0.1/10'


##################################################################################################
class WinxinBackup(object):
    def __init__(self):
        self.conn_export = redis.StrictRedis.from_url(EXPORT_REDIS_SERVER)
        self.conn_import = redis.StrictRedis.from_url(IMPORT_REDIS_SERVER)
        self.weixin_info_hset_key = 'hash_weixin_snsinfo'

    def get_weixin_info(self):
        return self.conn_export.hgetall(self.weixin_info_hset_key)

    def get_weixin_cnt(self):
        return self.conn_export.hlen(self.weixin_info_hset_key)

    def set_weixin_info_list(self, sns_info_list):
        for k, v in sns_info_list.items():
            self.conn_import.hset(self.weixin_info_hset_key, k, v)


def export():
    backup = WinxinBackup()
    print backup.get_weixin_cnt()
    info_list = backup.get_weixin_info()
    # for k,v in info_list.items():
    j = json.dumps(info_list)
    fd = open('./weixin.json', 'w')
    fd.write(j)
    fd.close()


def import_redis():
    imp = WinxinBackup()
    fd = open('./weixin.json', 'r')
    j = fd.read()
    pp = json.loads(j)
    pprint(pp)
    fd.close()
    # pprint(pp['12381551676090822951'])
    imp.set_weixin_info_list(pp)


if __name__ == '__main__':
    # export()
    import_redis()
