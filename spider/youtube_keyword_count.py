#!/usr/bin/python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
from urlparse import urljoin
import urllib2
from pprint import pprint
import redis

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_today_zset_key = 'keyword_today_zset_%s' % self.site_domain
        self.keyword_hour_zset_key = 'keyword_hour_zset_%s' % self.site_domain
        self.keyword_zset_key = 'keyword_zset_%s' % self.site_domain
        self.search_today_url_zset_key = 'search_today_url_zset_%s' % self.site_domain
        self.search_hour_url_zset_key = 'search_hour_url_zset_%s' % self.site_domain
        self.channel_zset_key = 'channel_zset_%s' % self.site_domain
        self.channel_info_hset_key = 'channel_info_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.start_flg = 0
        self.done_video_info_flg = 1
        self.done_sbutitle_flg = 9

    def copy_keywords(self, keyword):
        # self.conn.zadd(self.keyword_today_zset_key, self.todo_flg, keyword)
        # self.conn.zadd(self.keyword_hour_zset_key, self.todo_flg, keyword)
        # self.conn.zadd('test', self.todo_flg, keyword)
        for i in range(1, 51): # page:1-50
            search_today_url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + urllib2.quote(keyword) + '&page=%d' % i
            self.conn.zadd(self.search_today_url_zset_key, self.todo_flg, search_today_url)

    def create_redis_keywords(self):
        fd = open('./youtube/keyword_news.txt', 'r')
        keywords = fd.readlines()
        fd.close()
        for keyword in keywords:
            self.copy_keywords(keyword)

    def set_keyword_today_cnt(self, keyword, cnt):
        return self.conn.zadd(self.keyword_today_zset_key, cnt, keyword)

    def set_keyword_hour_cnt(self, keyword, cnt):
        return self.conn.zadd(self.keyword_hour_zset_key, cnt, keyword)

    def get_todo_keywords_today(self):
        return self.conn.zrangebyscore(self.keyword_today_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_keyword_start_today(self, keyword):
        return self.conn.zadd(self.keyword_today_zset_key, self.start_flg, keyword)

    def get_todo_keywords_hour(self):
        return self.conn.zrangebyscore(self.keyword_hour_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_keyword_start_hour(self, keyword):
        return self.conn.zadd(self.keyword_hour_zset_key, self.start_flg, keyword)


class MySpider(spider.Spider):
    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)

        # 网站名称
        self.siteName = "youtube"
        self.site_domain = 'youtube.com'
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "07"

        # 入口地址列表
        self.start_urls = ['https://www.youtube.com/results?search_query=lion&page=1']
        self.encoding = 'utf-8'
        # self.max_interval = None

    def get_start_urls(self, data=None):
        return self.start_urls

    def parse(self, response):
        url_list = []
        redis_db = RedisDrive()
        keywords = redis_db.get_todo_keywords_today()
        for keyword in keywords:
            q = urllib2.quote(keyword)  # （例）达赖喇嘛
            url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + q
            url_list.append(url)

        return (url_list, None, None)

    def parse_detail_page(self, response=None, url=None):
        redis_db = RedisDrive()
        url_list = []

        if response is not None:
            try:
                response.encoding = self.encoding
                unicode_html_body = response.text
                # print unicode_html_body
                data = htmlparser.Parser(unicode_html_body)
            except Exception, e:
                print "parse(): %s" % e
                return (url_list, None, None)

            purl = response.request.url
            keyword = purl[len("https://www.youtube.com/results?sp=EgIIAg%253D%253D&q="):]
            # print keyword
            keyword = urllib2.unquote(keyword)
            # print keyword

            result_count_str = data.xpath(
                '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
            cnt_str = result_count_str.text()
            # print cnt_str
            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str).group(2)
            # cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sresults)"), cnt_str).group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            cnt = int(cnt_str)
            print keyword, cnt
            redis_db.set_keyword_today_cnt(keyword, cnt)

        return (url_list, None, None)


# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        mySpider = MySpider()
        mySpider.proxy_enable = False
        mySpider.init_dedup()
        mySpider.init_downloader()

        print '[spider simulation] now starting ..........'
        redis_db = RedisDrive()
        keywords = redis_db.get_todo_keywords_today()
        i = 0
        for keyword in keywords:
            i = i + 1
            q = urllib2.quote(keyword)  # 达赖喇嘛
            url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + q
            response = mySpider.download(url)
            try:
                response.encoding = 'utf-8'
                unicode_html_body = response.text
                data = htmlparser.Parser(unicode_html_body)
            except Exception, e:
                print "parse(): %s" % e
                return

            result_count_str = data.xpath(
                '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
            cnt_str = result_count_str.text()
            # print cnt_str
            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str).group(2)
            # cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sresults)"), cnt_str).group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            cnt = int(cnt_str)

            print '%d / %d' % (i, len(keywords)), keyword, cnt
            redis_db.set_keyword_today_cnt(keyword, cnt)


    else:  # ---------- unit test -----------------------------
        spider = MySpider()
        spider.proxy_enable = False
        spider.init_dedup()
        spider.init_downloader()

        redis_db = RedisDrive()
        redis_db.create_redis_keywords()

        # ------------ get_start_urls() ----------
        # urls = spider.get_start_urls()
        # for url in urls:
        #     print url

        # ------------ parse() ----------
        # china+beijing&lclk=short&filters=short
        # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
        # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
        # url = 'https://www.youtube.com/results?search_query=lion&page=1'
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=%E4%B8%AD%E5%9B%BD%E9%93%B6%E8%A1%8C%E6%8A%95%E8%B5%84'  # today: sp=EgIIAg%253D%253D
        # keyword = urllib2.quote('达赖喇嘛')  # 达赖喇嘛
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + keyword
        # resp = spider.download(url)
        # urls, fun, next_url = spider.parse(resp)
        # print len(urls)
        # for url in urls:
        #     print url


        # ------------ parse_detail_page() ----------
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=%E8%BE%BE%E8%B5%96%E5%96%87%E5%98%9B'
        # resp = spider.download(url)
        # res = spider.parse_detail_page(resp, url)
        # pprint(res)
        # for item in res:
        #     for k, v in item.iteritems():
        #         print k, v


if __name__ == '__main__':
    test(unit_test=True)
    # test(unit_test=False)
