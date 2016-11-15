#!/usr/bin python
# coding=utf-8
import time
import datetime
import re
import redis
import pycurl
import urllib2
import traceback
import cStringIO
from multiprocessing import Process, Pool
import htmlparser

REDIS_SERVER = 'redis://127.0.0.1/13'

# Filters: 1)Upload date: today  2)Sort by: Upload date
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='


# url = 'https://www.youtube.com'
# proxies = {
#     'method': 'GET',
#     'proxies': {
#         'https': 'socks5://127.0.0.1:1080',
#     }
# }
# /
# print requests.get(url, proxies=proxies)

# import requesocks as requests
# session = requests.Session()
# session.proxies = {'http': 'socks5://127.0.0.1:1080',
#                    'https': 'socks5://127.0.0.1:1080'}
# resp = session.get('https://www.youtube.com/')
# print(resp.text)

class Downloader(object):
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
        url = "https://www.youtube.com"
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


class Util(object):
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


class SpiderMan(object):
    def __init__(self):
        self.siteName = 'youtube'
        self.site_domain = 'www.youtube.com'
        self.info_flag = '07'
        self.encoding = 'utf-8'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.download = Downloader()
        self.keyword_zset_key = '%s_keyword_zset' % self.siteName
        self.video_info_hset_key = '%s_video_info_hset' % self.siteName
        self.todo_flg = -1
        self.start_flg = 0

    def get_start_urls(self):
        urls = []
        keywords = self.conn.zrangebyscore(self.keyword_zset_key, self.todo_flg, self.todo_flg,
                                           withscores=False)
        for keyword in keywords[:20]:
            # url = PRE_SEARCH_URL + urllib2.quote(keyword)
            url = PRE_SEARCH_URL + keyword
            urls.append(url)
            print 'get_start_urls()', keyword, url
            self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)
        # print urls
        return urls

    def parse(self, url):
        '''
        根据keyword的检索结果（结果件数），生成带页数信息的url。
        '''
        url_list = []
        try:
            html_body = self.download.get_html(url)
            data = htmlparser.Parser(html_body)
        except Exception, e:
            print "parse(): %s" % e
            return (url_list, None, None)

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
                # print 'url:', purl + '&page=%d' % (page+1)
                url_list.append(purl + '&page=%d' % page)

        print 'parse()', purl, '>>>> %d pages' % len(url_list)
        return (url_list, None, None)

    def parse_detail_page(self, url):
        result = []
        try:
            html_body = self.download.get_html(url)
            data = htmlparser.Parser(html_body)
        except Exception, e:
            print "parse_detail_page(): error: %s" % e
            return (result, None, None)

        req_url = response.request.url
        print 'parse_detail_page():', req_url

        keyword = req_url[len(PRE_SEARCH_URL):]
        keyword = re.match(re.compile(r"(.*)(&page=\d+)"), keyword).group(1)
        keyword = urllib2.unquote(keyword)

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
            upload_time = Util.time_convert(upload_time_str)

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
            # pprint(result)

        print 'parse_detail_page()', keyword, len(result)
        self.conn.zincrby(self.keyword_zset_key, value=keyword, amount=len(result))
        return result


# ---------- run -----------------------------
def run(unit_test):
    spiderman = SpiderMan()
    proc = Pool(processes=10)
    result_list = []
    for i in range(30):
        result_list.append(proc.apply_async(spiderman.get_start_urls))

    proc.close()
    proc.join()


if __name__ == '__main__':
    # test(unit_test=True)
    run(unit_test=False)
