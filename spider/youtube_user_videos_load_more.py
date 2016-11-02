# /bin/env python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
from urlparse import urljoin
import json
import urllib2
from pprint import pprint

channel = ''


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
        self.start_urls = ['https://www.youtube.com/results?search_query=china&page=1']
        self.encoding = 'utf-8'
        # self.max_interval = None

    def get_start_urls(self, data=None):
        return self.start_urls

    def get_videos_info(self, data):
        global channel
        post_list = []
        # try:
        #     imgs = data.xpathall('''//div[@class="yt-lockup-thumbnail"]/*/a/span/span/span/img/@src''')
        #     for img in imgs:
        #         # img_href = img.xpath('''/img/@src''').text()
        #         img_href = img.text().strip()
        #         print img_href
        #         # img_id = img_href[len('https://i.ytimg.com/vi/'):len('https://i.ytimg.com/vi/') + len('aPmh2meR9vQ')]
        #         # print img_id
        #
        #         # img_file = urllib2.urlopen(img_href)
        #         # fd = open(img_id + '.jpg', 'wb')
        #         # fd.write(img_file.read())
        #         # fd.flush()
        #         # fd.close()
        # except Exception, e:
        #     print "get_videos_info() imgs: %s" % e

        try:
            divs = data.xpathall('''//div[@class="yt-lockup-content"]''')
            for div in divs:
                print div.text().strip(),'\n'
                title = div.xpath('''//h3''').text().strip()

                video_href = div.xpath('''//h3/a/@href''').text().strip()
                # print video_href
                # video_id = re.match(re.compile(r"(/watch\?v\=)(.*)"), video_href).group(2)

                # channel = div.xpath('''//div[@class="yt-lockup-byline"]''').text().strip()

                # li[2]: upload_time
                upload_time_str = div.xpath('''//div[@class="yt-lockup-meta"]/ul/li[2]''').text().strip()
                # print upload_time_str
                # upload_time = self.time_convert(upload_time_str)

                # li[1]:views
                views_cnt = None
                views_cnt_str = div.xpath('''//div[@class="yt-lockup-meta"]/ul/li[1]''').text().strip()
                views_cnt = re.match(re.compile(r"(.+?)(\sview+)"), views_cnt_str).group(1)
                views_cnt = re.sub(r",", "", views_cnt)
                if views_cnt == 'No':
                    views_cnt = 0

                # description
                print div.xpath('''//div[2]''').text().strip()
                description = div.xpath('''..//div[contains(@class,"yt-lockup-description")]''')
                if description._root is not None:
                    description = description.text().strip()
                else:
                    description = '-------------------'

                # print '[video_id]', video_id
                # print '[title]', title
                # print '[channel]', channel
                # print '[upload_time]', upload_time_str
                # print '[views_cnt]', views_cnt
                # print '[description]', description, '\n'

                post = {'video_id': url,
                        'title': title,
                        'description': description,
                        'views': views_cnt,
                        'gtime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'upload_time': upload_time_str,
                        'channel': channel,
                        'siteName': self.siteName
                        }
                # print 'get_ajax_video_info():', post
                post_list.append(post)

        except Exception, e:
            print "get_videos_info() content: %s" % e

        return post_list

    def get_more_load_href(self, data):
        next_url = ''
        try:
            # load more button
            more_load_href = data.xpath('''//button[contains(@class,"load-more-button")]/@data-uix-load-more-href''')
            if more_load_href is not None:
                next_url = more_load_href.text().strip()
                # print 'get_ajax_next_href():', next_url

        except Exception, e:
            print "get_more_load_href(): %s" % e

        return next_url

    # # 解析静态html内容，获取各个video信息
    # def parse_json_info(self, roll_more_href):
    #     post_list = []
    #     next_url = ''
    #
    #     resp = self.download('https://www.youtube.com' + roll_more_href)
    #     json_load = json.loads(resp.text)
    #     pprint(json_load)
    #     # content_html
    #     content_html = json_load['content_html']
    #     if content_html != '':
    #         data = htmlparser.Parser(content_html)
    #         post_list = self.get_videos_info(data)
    #
    #     # load_more_widget_html
    #     load_more_widget_html = json_load['load_more_widget_html']
    #     if load_more_widget_html != '':
    #         data = htmlparser.Parser(load_more_widget_html)
    #         next_url = self.get_more_load_href(data)
    #
    #     return post_list, next_url

    # # 解析静态html内容，获取各个video信息
    # def parse_user_videos_html(self, response):
    #     post_list = []
    #     next_url = ''
    #
    #     if response is not None:
    #         try:
    #             response.encoding = self.encoding
    #             unicode_html_body = response.text
    #             # print unicode_html_body
    #             data = htmlparser.Parser(unicode_html_body)
    #
    #             post_list = self.get_videos_info(data)
    #             next_url = self.get_more_load_href(data)
    #
    #         except Exception, e:
    #             print "parse(): %s" % e
    #
    #     return post_list, next_url

    #
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
                post_list = self.get_videos_info(data)
                next_url = self.get_more_load_href(data)
                print next_url
                print len(post_list)
                pprint(post_list)

            except Exception, e:
                print "parse(): %s" % e

        url_list.extend(post_list)

        # if next_url != '':
        #     post_list, next_url = self.parse_json_info(next_url)
        #     url_list.extend(post_list)
        #
        #     print len(post_list), next_url
        #
        #     if next_url != '':
        #         post_list, next_url = self.parse_json_info(next_url)
        #         url_list.extend(post_list)
        #         print len(post_list), next_url
        #
        #         if next_url != '':
        #             post_list, next_url = self.parse_json_info(next_url)
        #             url_list.extend(post_list)
        #             print len(post_list), next_url

        # same both
        # roll_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVEs0QVFBJTNE'
        # print roll_more_url

        print 'url_list:', len(url_list), url_list
        return (url_list, None, None)

    # https://www.youtube.com/watch?v=D4VBS4OXsi0
    def parse_detail_page(self, response=None, url=None):
        try:
            # response.encoding = self.encoding
            # unicode_html_body = response.text
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
    # <button class="yt-uix-button yt-uix-button-size-default yt-uix-button-default load-more-button yt-uix-load-more browse-items-load-more-button" data-uix-load-more-href =
    roll_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVEs0QVFBJTNE'
    click_more_url = '/browse_ajax?action_continuation=1&continuation=4qmFsgJCEhhVQ3l6Ni10YW92bGFPa1BzUHRLNEtORWcaJkVnWjJhV1JsYjNNWUF5QUFNQUk0QVdBQmFnQjZBVE80QVFBJTNE"'
    # url = 'https://www.youtube.com/user/GoldmanSachs/videos?view=0&sort=dd&live_view=500&flow=list'
    url = 'https://www.youtube.com/user/KPMGChinaHK/videos'  # 82个视频
    channel = 'Goldman Sachs'
    resp = spider.download(url)
    urls, fun, next_url = spider.parse(resp)
    # print len(urls)
    # for url in urls:
    # print url


    # ------------ parse_detail_page() ----------
    # url = 'https://www.youtube.com/results?search_query=lion'
    # resp = spider.download(url)
    # res = spider.parse_detail_page(resp, url)
    # for item in res:
    #     for k, v in item.iteritems():
    #         print k, v
