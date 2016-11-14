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

# Filters: 1)Upload date: today  2)Sort by: Upload date
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='


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
        # redis
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_zset_key = '%s_keyword_zset' % self.siteName
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

    def get_start_urls(self, data=None):
        urls = []
        keywords = self.conn.zrangebyscore(self.keyword_zset_key, self.todo_flg, self.todo_flg, withscores=False)
        # print keywords[:20]
        for keyword in keywords[:20]:
            # url = PRE_SEARCH_URL + urllib2.quote(keyword)
            url = PRE_SEARCH_URL + keyword
            urls.append(url)
            print 'get_start_urls()', keyword, url
            self.conn.zadd(self.keyword_zset_key, self.start_flg, keyword)

        # print urls
        return urls

    def parse(self, response):
        '''
        根据keyword的检索结果（结果件数），生成带页数信息的url。
        '''
        url_list = []
        if response is not None:
            try:
                response.encoding = self.encoding
                unicode_html_body = response.text
                data = htmlparser.Parser(unicode_html_body)
            except Exception, e:
                print "parse(): %s" % e
                return (url_list, None, None)

            purl = response.request.url

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

    def parse_detail_page(self, response=None, url=None):
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


# ---------- test run function-----------------------------
def test(unit_test):
    if unit_test is False:  # spider simulation
        print '[spider simulation] now starting ..........'
        for cnt in range(1):
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
                # pprint(ret)
                # for item in ret:
                #     for k, v in item.iteritems():
                #         print k, v

    else:  # ---------- unit test -----------------------------
        spider = MySpider()
        spider.proxy_enable = False
        spider.init_dedup()
        spider.init_downloader()

        # ------------ get_start_urls() ----------
        urls = spider.get_start_urls()
        # pprint(urls)
        # print(len(urls))

        # ------------ parse() ----------
        # china+beijing&lclk=short&filters=short
        # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
        # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
        # url = 'https://www.youtube.com/results?search_query=lion&page=1'

        # url = 'https://www.youtube.com/results?sp=CAISAggC&q=49%E6%B4%BE%E5%87%BA%E6%89%80%0A'
        # print url
        # resp = spider.download(url)
        # urls, fun, next_url = spider.parse(resp)
        # print len(urls)
        # pprint(urls)

        # ------------ parse_detail_page() ----------
        # url = 'https://www.youtube.com/watch?v=MXO7K76RRqg'
        # url  ='https://www.youtube.com/results?sp=EgIIAg%253D%253D&q=%E8%BE%BE%E8%B5%96%E5%96%87%E5%98%9B&page=1'
        # resp = spider.download(url)
        # res = spider.parse_detail_page(resp, url)
        # pprint(res)
        # print len(res)


if __name__ == '__main__':
    # test(unit_test=True)
    test(unit_test=False)
