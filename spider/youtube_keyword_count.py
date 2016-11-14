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

        #redis
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_zset_key = '%s_keyword_zset' % self.siteName
        self.video_info_hset_key = '%s_video_info_hset' % self.siteName
        # self.channel_zset_key = '%s_channel_zset' % self.siteName
        # self.channel_info_hset_key = '%s_channel_info_hset' % self.siteName
        self.todo_flg = -1
        self.start_flg = 0


    def get_todo_keywords(self):
        return self.conn.zrangebyscore(self.keyword_zset_key, min=self.todo_flg, max=self.todo_flg,
                                           withscores=False)

    def get_all_keywords_cnt(self):
        return self.conn.zcard(self.keyword_zset_key)

    def get_videos_cnt(self):
        return self.conn.hlen(self.video_info_hset_key)

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

    def get_start_urls(self, data=None):
        return self.start_urls

    def parse(self, response):

        url_list = []
        keywords = self.conn.zrangebyscore(self.keyword_zset_key, min=self.todo_flg, max=self.todo_flg,
                                           withscores=False)
        for keyword in keywords:
            q = urllib2.quote(keyword)  # （例）达赖喇嘛
            url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + q
            url_list.append(url)

        return (url_list, None, None)

    def parse_detail_page(self, response=None, url=None):
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
            self.set_keyword_today_cnt(keyword, cnt)

        return (url_list, None, None)


# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        mySpider = MySpider()
        mySpider.proxy_enable = False
        mySpider.init_dedup()
        mySpider.init_downloader()

        print '[spider simulation] now starting ..........'
        keywords = mySpider.get_todo_keywords()
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
            mySpider.set_keyword_today_cnt(keyword, cnt)


    else:  # ---------- unit test -----------------------------
        print 'now:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        spider = MySpider()
        spider.proxy_enable = False
        spider.init_dedup()
        spider.init_downloader()

        # spider.create_redis_keywords()

        print 'done/total:', (spider.get_all_keywords_cnt() - len(spider.get_todo_keywords())), '/', spider.get_all_keywords_cnt()
        print 'videos cnt / score summy:', spider.get_videos_cnt(), '/', spider.get_keywords_score_summy()

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
