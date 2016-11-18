#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import datetime
from datetime import timedelta
import pycurl
import htmlparser
import redis
import urllib2
from tornado.httpclient import AsyncHTTPClient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import ioloop, gen, queues

REDIS_SERVER = 'redis://127.0.0.1/11'

siteName = "youtube"
conn = redis.StrictRedis.from_url(REDIS_SERVER)
keyword_zset_key = '%s_keyword_zset' % siteName
video_info_hset_key = '%s_video_info_hset' % siteName
search_result_urls_zset_key = '%s_search_result_urls_zset' % siteName
todo_flg = -1
start_flg = 0

proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
           'Connection': 'keep-alive',
           'Cookie': 'PREF=f1=1222&cvdm=list',  # must be set 'list'
           'Host': 'www.youtube.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
           }
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='

keyword_url_queue = queues.Queue()
keyword_page_url_queue = queues.Queue()


def time_convert(ago_time_str):
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


def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)


def get_start_urls():
    urls = []
    keywords = conn.zrangebyscore(keyword_zset_key, todo_flg, todo_flg, withscores=False)
    for keyword in keywords[:20]:
        url = PRE_SEARCH_URL + keyword
        urls.append(url)
        conn.zadd(keyword_zset_key, start_flg, keyword)
    return urls


def parse(response):
    '''
    根据keyword的检索结果（结果件数），生成带页数信息的url。
    '''
    url_list = []
    if response is None:
        print '[info] parse() response is None'
        return ([None], None, None)

    try:
        req_url = response.request.url
        response.encoding = 'utf-8'
        data = htmlparser.Parser(response.body)

        cnt_str = data.xpath(
            '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
        cnt_str = cnt_str.text()
        cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str)
        if cnt_str:
            cnt_str = cnt_str.group(2)
        else:
            cnt_str = ''

        cnt_str = re.sub(r",", "", cnt_str)
        cnt = int(cnt_str)

        if cnt > 0:
            pages = (cnt / 20) + 1
            if pages > 20:
                pages = 20

            for page in range(1, pages + 1):
                request_url = req_url + '&page=%d' % page
                url_list.append(request_url)
                conn.zadd(search_result_urls_zset_key, todo_flg, request_url)

    except Exception, e:
        print "[error] parse() error is [%s]" % e
        return (url_list, None, None)

    print '[info] parse() [get %d pages] %s' % (len(url_list), req_url)
    return (url_list, None, None)


def parse_detail_page(response):
    result = []
    urls = conn.zrangebyscore(search_result_urls_zset_key,
                              min=todo_flg,
                              max=todo_flg,
                              start=0,
                              num=1,
                              withscores=False)
    print 'parse_detail_page() start. [urls] ', urls

    if len(urls) == 0:
        print 'parse_detail_page() nothing.'
        return result

    try:
        url = urls[0]
        conn.zadd(search_result_urls_zset_key, start_flg, url)
        keyword = url[len(PRE_SEARCH_URL):]
        keyword = re.match(re.compile(r"(.*)(&page=\d+)"), keyword).group(1)
        keyword = urllib2.unquote(keyword)

        data = htmlparser.Parser(response.body)
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
            upload_time = time_convert(upload_time_str)

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

            video_info = {'info_flag': info_flag,
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
                          'site_domain': site_domain,
                          'siteName': siteName,
                          }

            conn.hset(video_info_hset_key, video_info['video_id'], video_info)
            result.append(video_info)

        print 'parse_detail_page() end. [keyword] %s, [result cnt] %d' % (keyword, len(result))
        conn.zincrby(keyword_zset_key, value=keyword, amount=len(result))

    except Exception, e:
        print "parse_detail_page() error. %s" % e

    return result


@gen.coroutine
def downloader(url):
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_request = HTTPRequest(
        url,
        headers=headers,
        prepare_curl_callback=prepare_curl_socks5,
        proxy_host="localhost",
        proxy_port=1080
    )
    # response = yield AsyncHTTPClient().fetch(http_request, raise_error=False) # ok
    response = yield CurlAsyncHTTPClient().fetch(http_request)  # ok
    raise gen.Return(response)


@gen.coroutine
def get_keyword_page_url():
    try:
        keyword_url = yield keyword_url_queue.get()
        print 'get_keyword_page_url()', keyword_url
        response = yield downloader(keyword_url)
        print type(response)
        (url_list, _, _) = parse(response)
        for url in url_list:
            keyword_page_url_queue.put(url)
    finally:
        keyword_url_queue.task_done()


@gen.coroutine
def worker():
    while not keyword_url_queue.empty():
        yield get_keyword_page_url()


@gen.coroutine
def main():
    urls = get_start_urls()
    print urls
    for url in urls:  # 生产者
        yield keyword_url_queue.put(url)

    for _ in range(1000):  # 消费者
        worker()

    yield keyword_url_queue.join(timeout=timedelta(seconds=300))


if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(main)
