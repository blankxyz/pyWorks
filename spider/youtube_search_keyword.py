# /bin/env python
# coding=utf-8
import spider
import setting
import htmlparser
import datetime
import time, re
from urlparse import urljoin


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
        print ago
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
        url_list = []
        if response is not None:
            try:
                response.encoding = self.encoding
                unicode_html_body = response.text
                print unicode_html_body
                data = htmlparser.Parser(unicode_html_body)
            except Exception, e:
                print "parse(): %s" % e
                return (url_list, None, None)
            purl = response.request.url
            print purl

            result_count_str = data.xpath(
                '''//div[2]/div[4]/div/div[5]/div/div/div/div[1]/div/div[2]/div[1]/ol/li[1]/div/div[1]/div/p''')
            cnt_str = result_count_str.text()
            cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str).group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            cnt = int(cnt_str)
            print cnt, cnt / 20

            divs = data.xpathall('''//div[@class="yt-lockup-content"]''')
            for div in divs:
                # print div.text(),'\n'
                title = div.xpath('''//h3''').text()

                video_href = div.xpath('''//h3/a/@href''').text()
                url_list.append('https://www.youtube.com' + video_href)
                video_id = re.match(re.compile(r"(/watch\?v\=)(.*)"), video_href).group(2)

                channel = div.xpath('''//div[@class="yt-lockup-byline"]''').text()

                upload_time_str = div.xpath('''//div[@class="yt-lockup-meta"]/*/li[1]''').text()
                upload_time = self.time_convert(upload_time_str)

                views_cnt_str = div.xpath('''//div[@class="yt-lockup-meta"]/*/li[last()]''').text()
                views_cnt = re.match(re.compile(r"(.*)(\sview+)"), views_cnt_str).group(1)
                views_cnt = re.sub(r",", "", views_cnt)
                if views_cnt == 'No': views_cnt = 0

                description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''').text()

                print '[video_id]', video_id
                print '[title]', title
                print '[channel]', channel
                print '[upload_time]', upload_time
                print '[views_cnt]', views_cnt
                print '[description]', description, '\n'

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
    # china+beijing&lclk=short&filters=short
    # "https://www.youtube.com/results?search_query=how+to+get+stun+gun+in+gta+5+online&amp;lclk=week&amp;filters=week" rel="nofollow"
    # https://www.youtube.com/results?filters=video,today,short,4k&search_query=lion
    # url = 'https://www.youtube.com/results?search_query=lion&page=1'
    #urk= 'https://www.youtube.com/results?q=china&sp=CAMSAhAC' channel search
    url = 'https://www.youtube.com/results?sp=CAISCAgBEAEYASAB&q=china'
    url = 'https://www.youtube.com/user/thefoodranger/videos'
    more_url = 'https://www.youtube.com/browse_ajax?action_continuation=1&continuation=4qmFsgI8EhhVQ2lBcV9TVTBFRDFDNnZXRk1udzhFa2caIEVnWjJhV1JsYjNNZ0FEQUNPQUZnQVdvQWVnRXl1QUVB'
    resp = spider.download(url)
    urls, fun, next_url = spider.parse(resp)
    print len(urls)
    for url in urls:
        print url


    # ------------ parse_detail_page() ----------
    # url = 'https://www.youtube.com/results?search_query=lion'
    # resp = spider.download(url)
    # res = spider.parse_detail_page(resp, url)
    # for item in res:
    #     for k, v in item.iteritems():
    #         print k, v

