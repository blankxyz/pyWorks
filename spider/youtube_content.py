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
        self.start_urls = ['https://www.youtube.com/']
        self.encoding = 'utf-8'
        # self.max_interval = None

    def get_start_urls(self, data=None):
        return self.start_urls

    def parse(self, response):

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
            urls = data.xpathall('''//a[@id="pageLink"]''')
            for url in urls:
                p_url = url.xpath("//@href").text()
                url = urljoin(purl, p_url)
                url_list.append(url)

        return (url_list, None, None)

    def parse_detail_page(self, response=None, url=None):
        '''''
        详细页解析
        '''
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
        title = data.xpath('''//*[@id="eow-title"]''').text().strip()
        source = self.siteName

        views = data.xpath('''//*[@id="watch7-views-info"]/div[1]''').text().strip()
        content = data.xpath('''//*[@id="watch-description-text"]''').text().strip()
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
    # url = 'http://tieba.baidu.com/f?kw=%C4%CF%D1%F4'
    # resp = spider.download(url)
    # urls, fun, next_url = spider.parse(resp)
    # for url in urls:
    #     print url

    # ------------ parse_detail_page() ----------
    url = 'https://www.youtube.com/watch?v=smkyorC5qwc'
    resp = spider.download(url)
    res = spider.parse_detail_page(resp, url)
    for item in res:
        for k, v in item.iteritems():
            print k, v
