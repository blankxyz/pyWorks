# /bin/env python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
import redis
import json
import urllib2
from pprint import pprint

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.channel_zset_key = 'channel_zset_%s' % self.site_domain
        self.video_info_hset_key = 'video_info_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.start_flg = 0
        self.done_video_info_flg = 1
        self.done_subtitle_flg = 9

    def get_todo_channels(self):
        return self.conn.zrangebyscore(self.channel_zset_key, self.todo_flg, self.todo_flg, withscores=False)

    def set_channel_start(self, channel):
        return self.conn.zadd(self.channel_zset_key, self.start_flg, channel)

    # def add_todo_keyword(self, keyword):
    #     return self.conn.zadd(self.keyword_zset_key, self.todo_flg, keyword)

    def add_channel(self, post):
        return self.conn.zadd(self.channel_zset_key, self.todo_flg, post['channel_href'])

    def set_video_info(self, channel_info, video_info):
        self.conn.hset(self.video_info_hset_key, video_info['video_id'], video_info)
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

        self.request_headers = {'headers':
                                    {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                     'Accept-Encoding': 'gzip, deflate, br',
                                     'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
                                     'Connection': 'keep-alive',
                                     'Cookie': 'PREF=f1=1&cvdm=list',
                                     'Host': 'www.youtube.com',
                                     'Upgrade-Insecure-Requests': '1',
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
                                     }
                                }

        # 网站名称
        self.siteName = "youtube"
        self.site_domain = 'youtube.com'
        self.channel = None
        self.img_download = False
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "07"
        # 入口地址列表
        self.start_urls = ['https://www.youtube.com']
        self.encoding = 'utf-8'
        # self.max_interval = None

    def get_start_urls(self, data=None):
        redis_db = RedisDrive()
        urls = redis_db.get_todo_channels()
        for channel_href in urls:
            url = 'https://www.youtube.com' + channel_href + '/videos'

        return self.start_urls

    def parse_content_html(self, data):
        global channel
        post_list = []

        try:
            divs = data.xpathall('''//div[@class="feed-item-main-content"]''')
            for div in divs:
                # print div.data,'\n'
                title = div.xpath('''//h3''').text().strip()

                video_href = div.xpath('''//h3/a/@href''').text().strip()
                video_id = re.match(re.compile(r"(/watch\?v\=)(.*)"), video_href).group(2)

                img_href = data.xpath(
                    '''//div[@class="yt-lockup-thumbnail"]/span[1]/a[1]/span[1]/span[1]/span[1]/img[1]/@data-thumb''').text().strip()
                # print img_href
                if self.img_download:
                    img_file = urllib2.urlopen(img_href)
                    fd = open('./youtube/img/' + video_id + '.jpg', 'wb')
                    fd.write(img_file.read())
                    fd.flush()
                    fd.close()

                channel = self.channel

                # upload_time
                upload_time_str = div.xpath('''//div[@class="yt-lockup-meta"]/ul/li[1]''').text().strip()
                # upload_time = self.time_convert(upload_time_str)

                # views
                views_cnt_str = div.xpath('''//div[@class="yt-lockup-meta"]/ul/li[last()]''').text().strip()
                views_cnt = re.match(re.compile(r"(.+?)(\sview+)"), views_cnt_str)
                views_cnt = re.sub(r",", "", views_cnt.group(1))
                if views_cnt == 'No':
                    views_cnt = 0

                # description
                description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''')
                if description._root is not None:
                    description = description.text().strip()
                else:
                    description = None

                post = {'video_id': video_id,
                        'title': title,
                        'img_href': img_href,
                        'description': description,
                        'views': views_cnt,
                        'gtime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'upload_time': upload_time_str,
                        'channel': channel,
                        'siteName': self.siteName
                        }

                post_list.append(post)

        except Exception, e:
            print "get_videos_info() content: %s" % e

        return post_list

    def parse_load_more_widget_html(self, data):
        next_url = ''
        try:
            # load more button
            more_load_href = data.xpath('''//button[contains(@class,"load-more-button")]/@data-uix-load-more-href''')
            if more_load_href is not None:
                next_url = more_load_href.text().strip()

        except Exception, e:
            print "get_more_load_href(): %s" % e

        return next_url

    # # 解析静态html内容，获取各个video信息
    def parse_json_info(self, roll_more_href):
        post_list = []
        next_url = ''

        resp = self.download('https://www.youtube.com' + roll_more_href)
        json_load = json.loads(resp.text)

        # content_html
        content_html = json_load['content_html']
        if content_html != '':
            data = htmlparser.Parser(content_html)
            post_list = self.parse_content_html(data)

        # load_more_widget_html
        load_more_widget_html = json_load['load_more_widget_html']
        if load_more_widget_html != '':
            data = htmlparser.Parser(load_more_widget_html)
            next_url = self.parse_load_more_widget_html(data)

        return post_list, next_url

    def parse(self, response):
        url_list = []
        post_list = []
        next_url = ''

        # purl = response.request.url
        # print purl
        if response is not None:
            try:
                response.encoding = self.encoding
                unicode_html_body = response.text
                # print unicode_html_body
                data = htmlparser.Parser(unicode_html_body)
                info_list = self.parse_content_html(data)
                next_url = self.parse_load_more_widget_html(data)
                post_list.extend(info_list)

                if next_url != '':
                    info_list, next_url = self.parse_json_info(next_url)
                    post_list.extend(info_list)

                    if next_url != '':
                        info_list, next_url = self.parse_json_info(next_url)
                        post_list.extend(info_list)
                        #
                        #         if next_url != '':
                        #             info_list, next_url = self.parse_json_info(next_url)
                        #             post_list.extend(info_list)
                        #             # print len(post_list), next_url

            except Exception, e:
                print "parse(): %s" % e

        # same both
        # roll_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVEs0QVFBJTNE'
        # print roll_more_url

        # print 'url_list:', len(url_list), url_list

        pprint(post_list)
        print len(post_list)
        return (url_list, None, None)

    # https://www.youtube.com/watch?v=D4VBS4OXsi0
    def parse_detail_page(self, response=None, url=None):
        try:
            response.encoding = self.encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception, e:
            print "parse_detail_page(): %s" % e
            return None
        if url is None:
            url = response.request.url

        result = []
        div = data.xpath('''//div[#watch-header]''')
        source = self.siteName

        views = div.xpath('''//div[@id="watch-view-count"]''').text().strip()
        content = div.xpath('''//*[@id="watch-description-text"]''').text().strip()
        watch_time = '''//*[@id="watch-uploader-info"]/strong'''

        post = {'title': title,
                'content': content,
                'views': views,
                'watch_time': watch_time,
                'source': source,
                'siteName': self.siteName,
                'url': url,
                }
        result.append(post)

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
        spider.channel = 'Goldman Sachs'
        spider.img_download = True

        # ------------ get_start_urls() ----------
        # urls = spider.get_start_urls()
        # for url in urls:
        #     print url

        # ------------ parse() ----------
        # <button class="yt-uix-button yt-uix-button-size-default yt-uix-button-default load-more-button yt-uix-load-more browse-items-load-more-button" data-uix-load-more-href =
        roll_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVEs0QVFBJTNE'
        click_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVE80QVFBJTNE"'
        # url = 'https://www.youtube.com/user/GoldmanSachs/videos?view=0&sort=dd&live_view=500&flow=list'
        url = 'https://www.youtube.com/user/KPMGChinaHK/videos'  # 82个视频
        resp = spider.download(url)
        urls, fun, next_url = spider.parse(resp)


        # ------------ parse_detail_page() ----------
        # url = 'https://www.youtube.com/results?search_query=lion'
        # resp = spider.download(url)
        # res = spider.parse_detail_page(resp, url)
        # for item in res:
        #     for k, v in item.iteritems():
        #         print k, v


if __name__ == '__main__':
    test(unit_test=False)
