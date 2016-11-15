#!/usr/bin/python
# coding=utf-8

import redis
from pprint import pprint
import json

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class Monitor(object):
    def __init__(self):
        self.siteName = 'youtube'
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_zset_key = '%s_keyword_zset' % self.siteName
        self.video_info_hset_key = '%s_video_info_hset' % self.siteName
        self.channel_zset_key = '%s_channel_zset' % self.siteName
        self.channel_info_hset_key = '%s_channel_info_hset' % self.siteName
        self.todo_flg = -1
        self.start_flg = 0

    def set_keyword_cnt(self, keyword, cnt):
        self.conn.zadd(self.keyword_zset_key, cnt, keyword)

    def get_todo_keywords(self):
        return self.conn.zrangebyscore(self.keyword_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_keyword_start(self, keyword):
        return self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)

    def add_channel_list(self, channel_url):
        if self.conn.zrank(self.channel_zset_key, channel_url):
            self.conn.zincrby(self.channel_zset_key, channel_url, amount=1)
        else:
            self.conn.zadd(self.channel_zset_key, 0, channel_url)

    def get_videos(self):
        return self.conn.hgetall(self.video_info_hset_key)

    def extract_channel(self):
        videos = self.get_videos()
        for k,v in videos.iteritems():
            # print json.dumps(v)
            video_info = eval(v)
            # print channel['channel_url']
            self.add_channel_list(video_info['channel_url'])


def test():
    monitor = Monitor()
    monitor.extract_channel()

if __name__ == '__main__':
    test()
