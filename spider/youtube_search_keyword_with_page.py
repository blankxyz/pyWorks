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
        self.search_today_url_zset_key = 'search_today_url_zset_%s' % self.site_domain
        # self.search_hour_url_zset_key = 'search_hour_url_zset_%s' % self.site_domain
        self.video_info_hset_key = 'video_info_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.start_flg = 0

    def get_todo_url_today(self):
        return self.conn.zrangebyscore(self.search_today_url_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_url_today_result_cnt(self, url, result_cnt):
        self.conn.zadd(self.search_today_url_zset_key, result_cnt, url)

    def set_video_info(self, video_info):
        self.conn.hset(self.video_info_hset_key, video_info['video_id'], video_info)


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
        self.start_urls = ['http://www.youtube.com']
        self.encoding = 'utf-8'
        # self.max_interval = None
        self.request_headers = {'headers':
                                    {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                     'Accept-Encoding': 'gzip, deflate, br',
                                     'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
                                     'Connection': 'keep-alive',
                                     'Cookie': 'PREF=f1=1222&cvdm=list',
                                     'Host': 'www.youtube.com',
                                     'Upgrade-Insecure-Requests': '1',
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
                                     }
                                }

    def get_start_urls(self, data=None):
        return self.start_urls

    def time_convert(self, ago_time_str):
        '''
        Args:
            ago_time_str: 例如：'1 hour ago' or '2 minutes ago'
        Returns:
            计算XX时间之前的结果
            注意：英文中的复数形式匹配：结尾加s
        '''
        ret_time = datetime.datetime.now()
        num_str = re.match(re.compile(r"(\d+)\s[a-zA-Z]+"), ago_time_str).group(1)
        if ago_time_str is None:
            return ret_time

        num = int(num_str)
        if 'second' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(seconds=num))
        if 'minute' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(minutes=num))
        if 'hour' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(hours=num))
        if 'day' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(days=num))

        return ret_time.strftime("%Y-%m-%d %H:%M:%S")

    # 不管检索结果，直接生成请求url（含页数）。
    def parse(self, response):
        url_list = []
        redis_db = RedisDrive()
        todo_urls = redis_db.get_todo_url_today()
        if len(todo_urls) > 100:
            url_list.extend(todo_urls[:100])
        else:
            url_list.extend(todo_urls)

        print 'parse()', len(url_list), url_list
        return (url_list, None, None)

    # （例）https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=%E5%8D%81%E5%85%AB%E5%A4%A7%E5%85%AD%E4%B8%AD&page=11
    # 解析
    def parse_detail_page(self, response=None, url=None):
        redis_db = RedisDrive()
        result = []
        if response is None:
            print "parse_detail_page(): response is None"
            return result

        try:
            response.encoding = self.encoding
            unicode_html_body = response.text
            # print unicode_html_body
            data = htmlparser.Parser(unicode_html_body)
        except Exception, e:
            print "parse_detail_page(): %s" % e
            return (result, None, None)

        req_url = response.request.url

        # 查询结果无（0件）
        result_count_str = data.xpath(
            '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
        cnt_str = result_count_str.text().strip()
        # print cnt_str
        cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str).group(2)
        # cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sresults)"), cnt_str).group(2)
        cnt_str = re.sub(r",", "", cnt_str)
        cnt = int(cnt_str)
        if cnt == 0:
            print "parse_detail_page(): not found"
            redis_db.set_url_today_result_cnt(req_url, cnt)
            return result

        # 查询结果有
        # divs = data.xpathall('''//div[@class="yt-lockup-content"]''')
        divs = data.xpathall('''//div[contains(@class,"yt-lockup-video")]''')
        for div in divs:
            ad = div.xpath('''//span[contains(@class,"yt-badge-ad")]''').text().strip()
            if ad == 'Ad':  # 去除广告
                continue

            # channel
            # contains()：class中会有空格
            channel = div.xpath('''//div[contains(@class,"yt-lockup-byline")]/a''').text().strip()

            # title
            title = div.xpath('''//h3''').text().strip()

            # upload_time
            upload_time_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[1]''').text().strip()
            upload_time = self.time_convert(upload_time_str)

            # thumb_img
            thumb_img_src = div.xpath('''//span[contains(@class,"yt-thumb-simple")]/img/@src''').text().strip()
            # thumb_img_url = 'https:' + thumb_img_src
            # fp = open('./youtube/img/' + img_file_name, 'wb')
            # fp.write(urllib2.urlopen(thumb_img_url).read())
            # fp.close()

            # video_id
            video_href = div.xpath('''//h3/a/@href''').text().strip()
            video_id = video_href[len('/watch?v='):]  # /watch?v=Wza_nSeLH9M

            # views
            views = None
            views_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[last()]''').text().strip()
            if views_str:
                views = re.match(re.compile(r"(.*)(\sview+)"), views_str)
                if views:
                    views = views.group(1)
                    views = re.sub(r",", "", views)
                    if views == 'No':
                        views = 0

            # description
            description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''')
            if description._root is not None:
                description = description.text().strip()
            else:
                description = ''

            video_info = {'info_flag': self.info_flag,
                          'url': 'https://www.youtube.com' + video_href,
                          'video_id': video_id,
                          'title': title,
                          'pic_urls': thumb_img_src,
                          'video_urls': 'https://www.youtube.com' + video_href,
                          'content': description,
                          'visitCount': views,
                          'channel': channel,
                          'ctime': upload_time,
                          'site_domain': self.site_domain,
                          'siteName': self.siteName,
                          }

            redis_db.set_video_info(video_info)
            result.append(video_info)

        redis_db.set_url_today_result_cnt(req_url, len(result))
        return result


# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        print '[spider simulation] now starting ..........'
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
            ret = []
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                pprint(ret)
                print('parse_detail_page():', len(ret))

    else:  # ---------- unit test -----------------------------
        spider = MySpider()
        spider.proxy_enable = False
        spider.init_dedup()
        spider.init_downloader()

        # ------------ get_start_urls() ----------
        # urls = spider.get_start_urls()
        # pprint(urls)
        # print(len(urls))

        # ------------ parse() ----------
        # china+beijing&lclk=short&filters=short
        # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
        # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
        # url = 'https://www.youtube.com/results?search_query=lion&page=1'
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=%E4%B8%AD%E5%9B%BD%E9%93%B6%E8%A1%8C%E6%8A%95%E8%B5%84'  # today: sp=EgIIAg%253D%253D
        # keyword = urllib2.quote('达赖喇嘛')  # 达赖喇嘛
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=' + keyword
        # print url
        # resp = spider.download(url)
        # urls, fun, next_url = spider.parse(resp)
        # print len(urls)
        # pprint(urls)

        # ------------ parse_detail_page() ----------
        # url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=beijing&page=6'
        url = 'https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=beijing'
        resp = spider.download(url)
        res = spider.parse_detail_page(resp, url)
        pprint(res)
        print len(res)


if __name__ == '__main__':
    test(unit_test=True)
    # test(unit_test=False)
