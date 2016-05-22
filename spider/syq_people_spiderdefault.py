# coding=utf-8
#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved
'''
文件名：wy_ed_dc_qq_news.py
功能：宣汉网爬虫抓取文件。

代码历史：
2014-08-26：庞  威  代码创建
'''
import datetime
import spiderDefault
from urlparse import urljoin
import re
import htmlparser


class MySpider(spiderDefault.Spider):

    def __init__(self, cmd_args=None):
        spiderDefault.Spider.__init__(self, cmd_args=cmd_args)

        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "02"
        self.siteName = "人民网"
        self.site_domain = 'people.com.cn'

        self.start_urls = [
            'http://liuyan.people.com.cn/list.php?fid=3011',
        ]
        self.encoding = 'gbk'
        # self.max_interval = None
        self.debup_uri = None

    def get_start_urls(self, data=None):
        return self.start_urls

    def get_detail_page_urls(self, data):
        '''
        从列表页获取详情页url; 返回列表
        '''
        detail_page_urls = []

        if data is not None:
            url = data.response.request.url
            loops = data.xpathall('''//div[@class='more']/a''')
            for item in loops:
                post_url = item.xpath("//@href").text()
                post_url = urljoin(url, post_url)
                print post_url
                detail_page_urls.append(post_url)
        return detail_page_urls

    def get_detail_page_info(self, data):
        '''
        解析详情页信息；参数data可直接调用xpath,re等方法；
        返回值为字典类型
        '''
        result = []
        if data is None:
            return None

        url = data.response.request.url
        title = data.xpath('''//h4''') .text().strip()
        title = title.split('】')[1].split('|')[0]
        # print format(title.split('】')[1].split('|')[0], '-^200')
        source = self.siteName
        ctime = data.xpath(
            '''//div[@class="title"]/span[@class="time"]/text()''').datetime()
        content = data.xpath('''//div[@class="message"]/p[1]''').text().strip()
        try:
            c1_list = data.xpathall('''//script|//style''')
            for i in c1_list:
                c1 = i.text().strip()
                content = content.replace(c1, "", 1).strip()
        except:
            print 'error@ strip script style'

        channel = data.xpath(
            '''//div[@class="inner"]/div[@class="bread"]/p/a[3]''').text()[:-3]
        utc_now = datetime.datetime.utcnow()
        print self.siteName, channel, title, content, source, ctime, utc_now, url

        post = {
            'url': url,
            'title': title,
            'source': source,
            'ctime': ctime,
            'gtime': utc_now,
            'content': content,
            'siteName': self.siteName,
            'channel': channel,
            'data_db': self.data_db,
        }
        # print post['content']
        result.append(post)
        return result


# ------------ test ----------
if __name__ == "__main__":
    spider = MySpider()
    spider.proxy_enable = False
    spider.init_dedup()
    spider.init_downloader()

    url = spider.get_start_urls()[0]
    urls = []
    resp = spider.download(url)
    urls, fun, next_url = spider.parse(resp)
    for url in urls:
        resp = spider.download(url)
        result = spider.parse_detail_page(response=resp, url=url)
        if result is not None:
            for item in result:
                for k, v in item.iteritems():
                    print k, v
