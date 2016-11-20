#!/usr/bin/python
# coding=utf-8

import redis
import time
import datetime

REDIS_SERVER = 'redis://127.0.0.1/11'


##################################################################################################
class WinxinBackup(object):
    def __init__(self):
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.weixin_info_hset_key = '%hash_weixin_sns'

    def get_weixin_info(self):
        return self.conn.hgetall(self.weixin_info_hset_key)

    def get_weixin_cnt(self):
        return self.conn.hlen(self.weixin_info_hset_key)


def export():
    backup = WinxinBackup()
    print backup.get_weixin_cnt()


if __name__ == '__main__':
    export()
