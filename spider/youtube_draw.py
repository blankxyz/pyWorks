import matplotlib.pyplot as plt
import redis
import pprint

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_today_zset_key = 'keyword_today_zset_%s' % self.site_domain
        self.keyword_hour_zset_key = 'keyword_hour_zset_%s' % self.site_domain
        self.keyword_zset_key = 'keyword_zset_%s' % self.site_domain
        self.channel_zset_key = 'channel_zset_%s' % self.site_domain
        self.channel_info_hset_key = 'channel_info_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.start_flg = 0
        self.done_video_info_flg = 1
        self.done_sbutitle_flg = 9

    def set_keyword_today_cnt(self, keyword, cnt):
        return self.conn.zadd(self.keyword_today_zset_key, cnt, keyword)

    def set_keyword_hour_cnt(self, keyword, cnt):
        return self.conn.zadd(self.keyword_hour_zset_key, cnt, keyword)

    def get_todo_keywords_today(self):
        return self.conn.zrangebyscore(self.keyword_today_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_keyword_start_today(self, keyword):
        return self.conn.zadd(self.keyword_today_zset_key, self.start_flg, keyword)

    def get_keywords_hour_cnt(self):
        return self.conn.zcard(self.keyword_hour_zset_key)

    def set_keyword_start_hour(self, keyword):
        return self.conn.zadd(self.keyword_hour_zset_key, self.start_flg, keyword)


def draw():
    x = []
    y = []
    redis_db = RedisDrive()
    keywords = redis_db.conn.zrangebyscore(
        redis_db.keyword_today_zset_key, min=1, max=9999999999999999, withscores=True)

    # sorted(keywords, key=lambda w: w[1])
    # print keywords[54000:]

    for keyword, cnt in dict(keywords).iteritems():
        y.append(cnt)

    y.sort()
    print len(y)
    print y[54000:]

    z = []
    for i in y:
        z.append(int(i))

    # print z[54000:]

    # plt.plot(x, y)
    # plt.show()

    # print(redis_db.conn.zrevrangebyscore(redis_db.keyword_today_zset_key, min=40000, max=9999999999999999, withscores=True))


if __name__ == '__main__':
    draw()
