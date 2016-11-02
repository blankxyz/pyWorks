# /bin/env python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
from urlparse import urljoin
import urllib2
from pprint import pprint


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

    def time_convert(self, ago):
        # print ago
        x = 3
        ago_time = datetime.datetime.now()
        if 'seconds' in ago:
            ago_time = (datetime.datetime.now() - datetime.timedelta(seconds=x))
        if 'minutes' in ago:
            ago_time = (datetime.datetime.now() - datetime.timedelta(minutes=x))
        if 'hours' in ago:
            ago_time = (datetime.datetime.now() - datetime.timedelta(hours=x))
        if 'days' in ago:
            ago_time = (datetime.datetime.now() - datetime.timedelta(days=x))
        # if 'months' in ago:
        #     ago_time = (datetime.datetime.now() - datetime.timedelta(months=x))
        # if 'years' in ago:
        #     ago_time = (datetime.datetime.now() - datetime.timedelta(years=x))

        return ago_time.strftime("%Y-%m-%d %H:%M:%S")

    def parse(self, response):
        post_list = []
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
            print purl

            result_count_str = data.xpath(
                '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
            cnt_str = result_count_str.text()
            # print cnt_str
            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str).group(2)
            # cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sresults)"), cnt_str).group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            cnt = int(cnt_str)
            pages = (cnt / 20) + 1
            print 'results and pages:', cnt, pages

            # divs = data.xpathall('''//div[@class="yt-lockup-content"]''')
            divs = data.xpathall('''//div[@class="yt-lockup-dismissable yt-uix-tile"]''')
            # divs = data.xpathall('''//div[@id="results"]''')
            for div in divs:
                # title
                title = div.xpath('''//h3''').text().strip()

                # channel
                channel = div.xpath('''//div[@class="yt-lockup-byline"]''').text().strip()

                # upload_time
                upload_time_str = div.xpath('''//div[@class="yt-lockup-meta"]/*/li[1]''').text().strip()
                upload_time = self.time_convert(upload_time_str)

                # thumb_img
                # src="//i2.ytimg.com/vi/MXO7K76RRqg/mqdefault.jpg"
                thumb_img_src = div.xpath('''//span[@class="yt-thumb-simple"]/img/@src''').text().strip()
                #video_id
                video_id = None
                print thumb_img_src
                (video_id, _, img_ext) = re.search(r'\/(.+?)\/(.+?)\.(.+?)$', thumb_img_src).groups()
                print (video_id, _, img_ext)
                # img_file_name = video_id + '.' + img_ext

                thumb_img_url = 'https:' + thumb_img_src

                # fp = open('./youtube/img/' + img_file_name, 'wb')
                # fp.write(urllib2.urlopen(thumb_img_url).read())
                # fp.close()

                # views
                views = None
                views_str = div.xpath('''//div[@class="yt-lockup-meta"]/*/li[last()]''').text().strip()
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
                    description = '-------------------'

                post = {'video_id': video_id,
                        'title': title,
                        'thumb_img_url': thumb_img_url,
                        'description': description,
                        'views': views,
                        'channel': channel,
                        'upload_time': upload_time,
                        'siteName': self.siteName,
                        }
                post_list.append(post)
                # # print '[video_id]', video_id
                # print '[title]', title
                # print '[channel]', channel
                # print '[upload_time]', upload_time
                # print '[views_cnt]', views_cnt
                # print '[description]', description, '\n'

        # print len(post_list)
        # pprint(post_list)

        return (url_list, None, None)

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
        div = data.xpath('''//div[@id="watch7-main"]''')

        title = div.xpath('''//h1''').text().strip()
        thumb_img = div.xpath('''//img/@src''')
        views = div.xpath('''//div[@class,"watch-view-count"]''').text().strip()
        description = div.xpath('''//*[@id="watch-description-text"]''').text().strip()
        # watch_time = '''//*[@id="watch-uploader-info"]/strong'''
        watch_time = None
        channel = div.xpath('''//div[@class="yt-user-info"]''').text().strip()
        subscriber_cnt = div.xpath('''//span[contains(@class,"yt-subscriber-count")]''').text().strip()
        post = {'title': title,
                'description': description,
                'views': views,
                'thumb_img_url': thumb_img_url,
                'channel': channel,
                'subscriber_cnt': subscriber_cnt,
                'watch_time': watch_time,
                'siteName': self.siteName,
                'url': url,
                }
        result.append(post)

        return result


if __name__ == '__main__':
    spider = MySpider()
    spider.proxy_enable = False
    spider.init_dedup()
    spider.init_downloader()

    # ------------ get_start_urls() ----------
    # urls = spider.get_start_urls()
    # for url in urls:
    #     print url

    # ------------ parse() ----------
    # china+beijing&lclk=short&filters=short
    # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
    # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
    # url = 'https://www.youtube.com/results?search_query=lion&page=1'
    url = 'https://www.youtube.com/results?sp=CAISAggC&q=china'  # ok
    resp = spider.download(url)
    urls, fun, next_url = spider.parse(resp)
    # print len(urls)
    # for url in urls:
    #     print url


    # ------------ parse_detail_page() ----------
    # url = 'https://www.youtube.com/watch?v=MXO7K76RRqg'
    # resp = spider.download(url)
    # res = spider.parse_detail_page(resp, url)
    # pprint(res)
    # for item in res:
    #     for k, v in item.iteritems():
    #         print k, v
