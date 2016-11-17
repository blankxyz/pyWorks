#!/usr/bin/python
# coding=utf-8

import redis
import time
import datetime

REDIS_SERVER = 'redis://127.0.0.1/12'


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

    def get_all_keywords_cnt(self):
        return self.conn.zcard(self.keyword_zset_key)

    def set_keyword_start(self, keyword):
        return self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)

    def add_channel_list(self, channel_url):
        if self.conn.zrank(self.channel_zset_key, channel_url):
            self.conn.zincrby(self.channel_zset_key, channel_url, amount=1)
        else:
            self.conn.zadd(self.channel_zset_key, 0, channel_url)

    def get_videos(self):
        return self.conn.hgetall(self.video_info_hset_key)

    def get_videos_cnt(self):
        return self.conn.hlen(self.video_info_hset_key)

    def extract_channel(self):
        videos = self.get_videos()
        for k, v in videos.iteritems():
            # print json.dumps(v)
            video_info = eval(v)
            # print channel['channel_url']
            self.add_channel_list(video_info['channel_url'])

    def get_keywords_score_summy(self):
        summy = 0
        keywords = self.conn.zrangebyscore(self.keyword_zset_key, min=self.start_flg, max=999999999, withscores=True)
        for (k, v) in dict(keywords).iteritems():
            summy = summy + int(v)

        return summy

    def create_redis_keywords(self):
        fd = open('./youtube/keyword_news.txt', 'r')
        keywords = fd.readlines()
        for keyword in keywords:
            self.conn.zadd(self.keyword_zset_key, self.todo_flg, keyword.strip('\n'))
        fd.close()


def test():
    monitor = Monitor()
    monitor.extract_channel()


def create():
    monitor = Monitor()
    monitor.create_redis_keywords()


def status():
    monitor = Monitor()

    for _ in range(1):
        all = monitor.get_all_keywords_cnt()
        todo = len(monitor.get_todo_keywords())
        done = all - todo
        videos_cnt = monitor.get_videos_cnt()
        videos_score_summy = monitor.get_keywords_score_summy()

        print '---------------------------------------------'
        print '                     now:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print '              done/total: %d / %d' % (done, all)
        print 'videos cnt / score summy: %d / %d' % (videos_cnt, videos_score_summy)
        time.sleep(60)


if __name__ == '__main__':
    # create()
    status()
    # test()
