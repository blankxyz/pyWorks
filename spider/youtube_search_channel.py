# /bin/env python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
import redis
import urllib2
from pprint import pprint

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_zset_key = 'keyword_zset_%s' % self.site_domain
        self.channel_zset_key = 'channel_zset_%s' % self.site_domain
        self.channel_info_hset_key = 'channel_info_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.start_flg = 0
        self.done_video_info_flg = 1
        self.done_sbutitle_flg = 9

    def get_todo_channels(self):
        return self.conn.zrangebyscore(self.channel_zset_key, self.start_flg, self.start_flg, withscores=False)

    def set_keyword_start(self,keyword):
        return self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)

    def add_todo_keyword(self, keyword):
        return self.conn.zadd(self.keyword_zset_key, self.todo_flg, keyword)

    def add_channel(self, post):
        return self.conn.zadd(self.channel_zset_key, self.todo_flg, post['channel_href'])

    def set_channel_info(self, channel_info):
        self.conn.hset(self.channel_info_hset_key, channel_info['channel_href'], channel_info)
        self.conn.zincrby(self.channel_zset_key, value=channel_info['channel_href'], amount=1)

        # def set_info_done(self, video_id, post):
        #     self.conn.hset(self.video_info_hset_key, video_id, post)
        #     return self.conn.zadd(self.video_info_hset_key, self.done_video_info_flg, video_id)


##################################################################################################
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
        # 类别码，01新闻、02论坛、03博客、04微博、05平媒、06微信、07 视频、99搜索引擎
        self.info_flag = "07"
        # 入口地址列表
        self.start_urls = ['https://www.youtube.com']
        self.encoding = 'utf-8'
        # self.max_interval = None

    def get_start_urls(self, data=None):
        self.start_urls = []
        redis_db = RedisDrive()
        keywords = redis_db.get_todo_keywords()
        for word in keywords:
            url = 'https://www.youtube.com/results?q=%s&sp=CAMSAhAC' % word
            self.start_urls.append(url)
            redis_db.set_keyword_start(word)

        return self.start_urls  # must be a list type

    # 提取 'https://www.youtube.com/results?q=[keyword]&sp=CAMSAhAC&page=[num]'
    def parse(self, response):
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

            org_url = response.request.url

            result_cnt_str = data.xpath(
                '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''').text().strip()
            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), result_cnt_str).group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            result_cnt = int(cnt_str)

            if result_cnt >= 1000:
                pages = 1000 / 20
            else:
                pages = (result_cnt / 20) + 1

            for i in range(pages):
                url_list.append(org_url + '&page=%s' % (i + 1))

        pprint(url_list)
        return (url_list, None, None)

    def parse_detail_page(self, response=None, url=None):
        result = []
        if response is not None:
            try:
                response.encoding = self.encoding
                unicode_html_body = response.text
                # print unicode_html_body
                data = htmlparser.Parser(unicode_html_body)
                if data.xpath('''//div[@class="display-message"]''').text().strip() == 'No more results':
                    print response.url, ': No more results!'
                    return (result, None, None)

            except Exception, e:
                print "parse_detail_page(): %s" % e
                return (result, None, None)

            redis_db = RedisDrive()
            divs = data.xpathall('''//div[@class="yt-lockup-content"]''')
            for div in divs:

                # 去除广告
                ad_str = div.xpath('''//div[@class="yt-lockup-byline"]/span''').text().strip()
                if ad_str == 'Ad':
                    continue

                # channel_name
                channel_name = div.xpath('''//h3''').text().strip()

                # channel_href
                channel_href = div.xpath('''//h3/a/@href''').text().strip()

                # videos
                videos = None
                videos_str = div.xpath('''//div[@class="yt-lockup-meta"]/*/li[last()]''').text().strip()
                if videos_str:
                    videos = re.match(re.compile(r"(.*)(\svideo+)"), videos_str)
                    if videos:
                        videos = videos.group(1)
                        videos = re.sub(r",", "", videos)
                        if videos == 'No':
                            videos = 0

                # subscribe
                subscribe = div.xpath('''//span[contains(@class,"yt-subscriber-count")]''').text().strip()
                subscribe = re.sub(r",", "", subscribe)

                # description
                description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''')
                if description._root is not None:
                    description = description.text().strip()
                else:
                    description = '-------------------'

                channel_info = {'channel_name': channel_name,
                                'channel_href': channel_href,
                                'videos': videos,
                                'description': description,
                                'subscribe': subscribe,
                                }

                redis_db.add_channel(channel_info)
                redis_db.set_channel_info(channel_info)
                result.append(channel_info)

        pprint(result)
        print len(result)

        return result


# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        print '[spider simulation] now starting ..........'
        redis_db = RedisDrive()
        redis_db.conn.zadd(redis_db.keyword_zset_key, redis_db.todo_flg, 'china')

        for cnt in range(1000):
            print '[loop]', cnt, '[time]', datetime.datetime.utcnow()
            detail_job_list = []  # equal to run.py detail_job_queue

            # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
            def __detail_page_urls(urls, func):
                next_page_url = None
                if func is not None:
                    if urls:
                        for url in urls:
                            try:
                                response = mySpider.download(url)
                                list_urls, callback, next_page_url = func(response)  # parse()
                                for url in list_urls:
                                    detail_job_list.append(url)
                            except Exception, e:
                                print '[ERROR] main() Exception: %s' % e
                                list_urls, callback, next_page_url = [], None, None

                            __detail_page_urls(list_urls, callback)

                            if next_page_url is not None:
                                print 'next_page_url'
                                __detail_page_urls([next_page_url], func)

            # --equal to run.py list_page_thread() -------------------------
            mySpider = MySpider()
            mySpider.proxy_enable = False
            mySpider.init_dedup()
            mySpider.init_downloader()
            start_urls = mySpider.get_start_urls()  # get_start_urls()
            __detail_page_urls(start_urls, mySpider.parse)  # parse()

            # --equal to run.py detail_page_thread() -------------------------
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                pprint(ret)
                # for item in ret:
                #     for k, v in item.iteritems():
                #         print k, v

    else:  # ---------- unit test -----------------------------
        spider = MySpider()
        spider.proxy_enable = False
        spider.init_dedup()
        spider.init_downloader()

        redis_db = RedisDrive()
        redis_db.conn.zadd(redis_db.keyword_zset_key, redis_db.todo_flg, 'china')

        # ------------ get_start_urls() ----------
        # urls = spider.get_start_urls()
        # for url in urls:
        #     print url

        # ------------ parse() ----------
        # china+beijing&lclk=short&filters=short
        # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
        # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
        # url = 'https://www.youtube.com/results?search_query=lion&page=1'
        # url = 'https://www.youtube.com/results?q=china&sp=CAMSAhAC'  # ok
        # resp = spider.download(url)
        # urls, fun, next_url = spider.parse(resp)
        # print len(urls)
        # for url in urls:
        #     print url

        # ------------ parse_detail_page() ----------
        url = 'https://www.youtube.com/results?q=china&sp=CAMSAhAC&page=29'
        resp = spider.download(url)
        res = spider.parse_detail_page(resp, url)
        pprint(res)
        # for item in res:
        #     for k, v in item.iteritems():
        #         print k, v


if __name__ == '__main__':
    test(unit_test=False)
