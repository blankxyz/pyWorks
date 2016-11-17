#!/usr/bin python
# coding=utf-8
import time
import signal
import datetime
import re
import redis
import requests
import pycurl
import urllib2
import traceback
import cStringIO
import random
from  multiprocessing import Process, Pool
import threading
import gevent.pool
import gevent.queue
import gevent.event
from gevent import threadpool
from gevent import monkey
import log
import util
import setting
import htmlparser

# 全局Event变量，用于退出时线程间同步
eventExit = None
# 命令行参数对象，保存从命令行中得到的参数
cmd_args = None

REDIS_SERVER = 'redis://127.0.0.1/12'

# Filters: 1)Upload date: today  2)Sort by: Upload date
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='

thread_count = 0

thread_lock = threading.Lock()

monkey.patch_all()


class DownloaderCurl(object):
    def __init__(self):
        self.proxy = "127.0.0.1:1080"
        self.retry_num = 5
        self.timeout = 300
        self.headers = ["Content-Type:application/json;charset=utf-8",
                        "Accept-Encoding:gzip,deflate,sdch",
                        "Accept-Language:zh-CN,zh;q=0.8"]

    def get_html(self, url):
        # curl https://www.youtube.com --socks5 127.0.0.1:1080
        # buf = cStringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.TIMEOUT, self.timeout)
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.PROXY, self.proxy)
        curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        curl.setopt(pycurl.MAXREDIRS, self.retry_num)
        # curl.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0')
        # curl.setopt(pycurl.HTTPHEADER, headers)
        # curl.setopt(curl.WRITEFUNCTION, buf.write)
        try:
            ret = curl.perform()
            # print buf.getvalue()
            return ret
        except Exception, e:
            print "error code:", curl.getinfo(curl.HTTP_CODE)
            traceback.print_exc()
            return None


class DownloaderRequests(object):
    def __init__(self):
        self.proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
                        'Connection': 'keep-alive',
                        'Cookie': 'PREF=f1=1222&cvdm=list',  # must be set 'list'
                        'Host': 'www.youtube.com',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
                        }

    def get_html(self, url):
        try:
            resp = requests.get(url, proxies=self.proxies, headers=self.headers)
            return resp.content
        except Exception, e:
            print 'get_html() error',e
            return None


class SpiderMan(object):
    def __init__(self):
        self.siteName = 'youtube'
        self.site_domain = 'www.youtube.com'
        self.info_flag = '07'
        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.download = DownloaderRequests()
        # self.download = DownloaderCurl()
        self.keyword_zset_key = '%s_keyword_zset' % self.siteName
        self.search_result_urls_zset_key = '%s_search_result_urls_zset' % self.siteName
        self.video_info_hset_key = '%s_video_info_hset' % self.siteName
        self.todo_flg = -1
        self.start_flg = 0

    def time_convert(self, ago_time_str):
        '''
        Args:
            ago_time_str: 例：'1 hour ago' or '2 minutes ago'
        Returns:
            计算XX时间之前的结果
            注意：英文中的复数形式匹配：结尾加s
        '''
        ret_time = datetime.datetime.now()
        if ago_time_str is None:
            return ret_time

        num_str = re.match(re.compile(r"(\d+)\s[a-zA-Z]+"), ago_time_str)
        if num_str:
            num = int(num_str.group(1))
            if 'second' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(seconds=num))
            if 'minute' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(minutes=num))
            if 'hour' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(hours=num))
            if 'day' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(days=num))

        return ret_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_start_urls(self):
        print 'get_start_urls() start.'
        urls = []
        keywords = self.conn.zrangebyscore(self.keyword_zset_key,
                                           min=self.todo_flg,
                                           max=self.todo_flg,
                                           withscores=False)
        # print keywords
        for keyword in keywords[:20]:
            # url = PRE_SEARCH_URL + urllib2.quote(keyword)
            url = PRE_SEARCH_URL + keyword
            urls.append(url)
            print 'get_start_urls() keyword: %s' % keyword
            self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)

            ############################
            self.parse(url)

        print 'get_start_urls() end.'
        return urls

    def parse(self, url):
        '''
        根据keyword的检索结果（结果件数），生成带页数信息的url。
        '''
        url_list = []
        cnt = 0

        try:
            print 'parse() start.', url
            html_content = self.download.get_html(url)
            if html_content is None:
                return (url_list, None, None)

            data = htmlparser.Parser(html_content)
            cnt_str = data.xpath('''//p[contains(@class,"num-results")]''')
            cnt_str = cnt_str.text().strip()

            print 'parse() debug:', cnt_str

            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str)
            if cnt_str:
                cnt_str = cnt_str.group(2)
                cnt_str = re.sub(r",", "", cnt_str)
                cnt = int(cnt_str)

            if cnt > 0:
                pages = (cnt / 20) + 1
                if pages > 20:
                    pages = 2

                for page in range(1, pages + 1):
                    request_url = url + '&page=%d' % page
                    url_list.append(request_url)

                    self.conn.zadd(self.search_result_urls_zset_key, self.todo_flg, request_url)

        except Exception, e:
            print "parse(): error %s" % e
            return (url_list, None, None)

        print 'parse() end.', url, 'has [ %d ] pages' % len(url_list)
        return (url_list, None, None)

    def parse_detail_page(self):
        '''
        解析带有页数信息的URL的内容，取得各个项目内容
        '''
        global thread_lock
        result = []
        thread_lock.acquire()
        # thread_count += 1

        urls = self.conn.zrangebyscore(self.search_result_urls_zset_key,
                                       min=self.todo_flg,
                                       max=self.todo_flg,
                                       start=0,
                                       num=1,
                                       withscores=False)
        print 'parse_detail_page() start. [urls] ', urls

        if len(urls) == 0:
            print 'parse_detail_page() nothing.'
            return result

        try:
            url = urls[0]
            self.conn.zadd(self.search_result_urls_zset_key, self.start_flg, url)
            keyword = url[len(PRE_SEARCH_URL):]
            keyword = re.match(re.compile(r"(.*)(&page=\d+)"), keyword).group(1)
            keyword = urllib2.unquote(keyword)

            html_content = self.download.get_html(url)
            data = htmlparser.Parser(html_content)
            # 需要包含各个视频信息左侧的图片div
            divs = data.xpathall('''//div[contains(@class,"yt-lockup-video")]''')
            for div in divs:
                ad = div.xpath('''//span[contains(@class,"yt-badge-ad")]''').text().strip()
                if ad == 'Ad':  # 去除广告
                    continue

                channel = div.xpath('''//div[contains(@class,"yt-lockup-byline")]/a''').text().strip()  # class中会有空格
                channel_url = div.xpath('''//div[contains(@class,"yt-lockup-byline")]/a/@href''').text().strip()

                title = div.xpath('''//h3''').text().strip()

                upload_time_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[1]''').text().strip()
                upload_time = self.time_convert(upload_time_str)

                thumb_img_src = div.xpath('''//span[contains(@class,"yt-thumb-simple")]/img/@src''').text().strip()

                video_href = div.xpath('''//h3/a/@href''').text().strip()
                video_id = video_href[len('/watch?v='):]  # /watch?v=Wza_nSeLH9M

                views = None
                views_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[last()]''').text().strip()
                if views_str:
                    views = re.match(re.compile(r"(.*)(\sview+)"), views_str)
                    if views:
                        views = views.group(1)
                        views = re.sub(r",", "", views)
                        if views == 'No':
                            views = 0

                description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''')
                if description._root is not None:
                    description = description.text().strip()
                else:
                    description = ''

                video_info = {'info_flag': self.info_flag,
                              'url': 'https://www.youtube.com' + video_href,
                              'video_id': video_id,
                              'title': title.decode('utf8'),
                              'pic_urls': [thumb_img_src],
                              'video_urls': ['https://www.youtube.com' + video_href],
                              'content': description.decode('utf8'),
                              'visitCount': views,
                              'channel': channel.decode('utf8'),
                              'channel_url': channel_url,
                              'ctime': upload_time,
                              'site_domain': self.site_domain,
                              'siteName': self.siteName,
                              }

                self.conn.hset(self.video_info_hset_key, video_info['video_id'], video_info)
                result.append(video_info)

            print 'parse_detail_page() end. [keyword] %s, [result cnt] %d' % (keyword, len(result))
            self.conn.zincrby(self.keyword_zset_key, value=keyword, amount=len(result))

        except Exception, e:
            print "parse_detail_page() error. %s" % e

        thread_lock.release()
        return result


def list_page_thread():
    myspider = SpiderMan()
    myspider.get_start_urls()


def detail_page_thread():
    myspider = SpiderMan()
    myspider.parse_detail_page()


def stop_spider():
    gevent.killall(timeout=30)


def run_spider():
    # monkey.patch_all()

    global eventExit

    signal.signal(signal.SIGTERM, stop_spider)

    list_thread_pool = gevent.pool.Pool(setting.LIST_PAGE_THREAD_NUM)
    detail_page_thread_pool = gevent.pool.Pool(setting.DETAIL_PAGE_THREAD_NUM)

    for _ in xrange(setting.LIST_PAGE_THREAD_NUM):
        time.sleep(random.random())
        list_thread_pool.spawn(list_page_thread)

    time.sleep(60)

    for _ in range(setting.DETAIL_PAGE_THREAD_NUM):
        detail_page_thread_pool.spawn(detail_page_thread)

    timeouter = gevent.Timeout(60)
    try:
        timeouter.start()

        list_thread_pool.join()
        detail_page_thread_pool.join()
    #
    except gevent.Timeout, e:
        log.logger.debug("internal timeout triggered: %s" % e)
    finally:
        timeouter.cancel()


def multi_process_runner():
    import multiprocessing

    process_pool = []

    def stop_process(signum, frame):
        for p in process_pool:
            p.terminate()

    signal.signal(signal.SIGTERM, stop_process)

    for _ in xrange(1):
        p = multiprocessing.Process(target=run_spider)
        p.start()
        process_pool.append(p)

    for p in process_pool:
        p.join()


def main():
    multi_process_runner()

    # max_thread_cnt = 10
    # process_cnt = 10000
    # threads = []
    #
    # pool = Pool(processes=16)  # default is cpu_count()
    # for i in range(process_cnt):
    #     print 'process num: [%d]' % i
    #     pool.apply_async(get_start_urls_process)
    #
    # pool.close()
    # pool.join()
    # pool.terminate()
    # print '----------- process end ---------------'
    #
    # for _ in xrange(max_thread_cnt):
    #     t = threading.Thread(target=parse_detail_page_thread, args=())
    #     threads.append(t)
    #     t.start()
    #
    # for t in threads:
    #     t.join()
    # print '----------- thread end ---------------'


if __name__ == '__main__':
    main()
