# coding=utf-8
from pprint import pprint
import time, datetime
import pymongo
import redis
import json

from django.utils import html as django_html  # .remove_tags(value, tags)

# from .setting import CONFIG_ID, REDIS_SERVER, MONGODB_SERVER, MONGODB_PORT, MONGODB_SERVER_DIRECT, MONGODB_PORT_DIRECT, \
#     OK_PERCENT, UNKOWN

MONGODB_SERVER = '192.168.16.223'
MONGODB_PORT = 37017

REDIS_COMMENTS_SERVER = 'redis://192.168.16.223/8'


class RedisDriver(object):
    def __init__(self):
        self.conn_comments = redis.StrictRedis.from_url(REDIS_COMMENTS_SERVER)

    def get_commentsQueueSize(self):
        ret = []
        names = ["qq", "toutiao", "ifeng", "163", "tianya", "sina"]

        for name in names:
            ret.append(self.conn_comments.llen('comment_task:' + name))

        return ret

    def get_commentsCacheQueueSize(self):
        ret = []
        names = ["60", "120", "300", "600", "1800", "3600", "7200", "14000", "28800", "57600", "86400"]
        for name in names:
            ret.append(self.conn_comments.llen('comment_task_cache:' + name))

        return ret

    def get_newsCnt(self):
        pre_key = 'news_count:'
        qq, toutiao, ifeng, wangyi, sina = [], [], [], [], []
        days = []

        for i in range(6, -1, -1):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            d = day.strftime('%Y-%m-%d')
            days.append(d)
            if self.conn_comments.hkeys(pre_key + d):
                qq.append(int(bytes.decode(self.conn_comments.hget(pre_key + d, 'comment_task:' + 'qq'))))
                toutiao.append(int(bytes.decode(self.conn_comments.hget(pre_key + d, 'comment_task:' + 'toutiao'))))
                ifeng.append(int(bytes.decode(self.conn_comments.hget(pre_key + d, 'comment_task:' + 'ifeng'))))
                wangyi.append(int(bytes.decode(self.conn_comments.hget(pre_key + d, 'comment_task:' + '163'))))
                sina.append(int(bytes.decode(self.conn_comments.hget(pre_key + d, 'comment_task:' + 'sina'))))

        return days, qq, toutiao, ifeng, wangyi, sina


class MongoDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.comment_db = self.client.NewsComments
        self.comment = self.comment_db.comment
        self.news = self.comment_db.news

    def get_news_search_cnt(self, search):
        cond = dict()
        if search:
            cond['url'] = {'$regex': search}

        cnt = self.news.find(cond).count()
        return cnt

    def get_comments_search_cnt(self, search):
        cond = dict()
        if search:
            cond['post_url'] = {'$regex': search}

        cnt = self.comment.find(cond).count()
        return cnt

    def get_news_comments_cnt(self):
        ret = list(self.news.aggregate([{'$group': {'_id': '', 'comment_sum': {'$sum': '$comment_count'}}}]))
        return ret[0]['comment_sum']

    def get_commentInfo_list(self, search, skip_num, page_size):
        ret = []
        cond = dict()
        if search:
            cond['post_url'] = {'$regex': search}
        # ('post_url', pymongo.DESCENDING)
        l = self.comment.find(cond).sort([('ctime', pymongo.DESCENDING)]). \
            skip(skip_num).limit(page_size)
        for info in l:
            info.pop('_id')  # json编码error ObjectId('5812bedd6fce0d8637532ef1') is not JSON serializable
            info['ctime'] = datetime.datetime.fromtimestamp(info['ctime']).strftime("%Y-%m-%d %H:%M:%S")
            info['gtime'] = datetime.datetime.fromtimestamp(info['gtime']).strftime("%Y-%m-%d %H:%M:%S")
            ret.append(info)

        return ret


if __name__ == '__main__':
    r = RedisDriver()

    db = MongoDriver()
    # search = ''
    # page = 13276
    # PAGE_SIZE = 20
    # result = db.get_commentInfo_list(search, (int(page) - 1) * PAGE_SIZE, PAGE_SIZE)
    # pprint(result)
    pprint(db.get_comments_search_cnt(''))
