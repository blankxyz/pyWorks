#!/usr/bin/python
# coding=utf-8

import redis
import json
import time
import datetime

REDIS_SERVER = 'redis://192.168.187.56/0'


##################################################################################################
class WinxinBackup(object):
    def __init__(self):
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.weixin_info_hset_key = 'hash_weixin_snsinfo'

    def get_weixin_info(self):
        return self.conn.hgetall(self.weixin_info_hset_key)

    def get_weixin_cnt(self):
        return self.conn.hlen(self.weixin_info_hset_key)


def export():
    backup = WinxinBackup()
    print backup.get_weixin_cnt()
    info_list = backup.get_weixin_info()
    #for k,v in info_list.items():
    j = json.dumps(info_list)
    fd = open('./weixin.json','w')
    fd.write(j)
    fd.close()

if __name__ == '__main__':
    export()
