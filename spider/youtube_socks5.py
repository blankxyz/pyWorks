# coding=utf-8

import spider
import setting
import htmlparser
import time
import datetime
import re
import redis
import urllib2
import json
from urlparse import urljoin
from dedup import dedup
from db import DB
import MySQLdb
import copy
import cPickle as pickle
import urllib


class MySpider(spider.Spider):
    def __init__(self,
                 proxy_enable=True,  # setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)

        # 网站名称
        self.siteName = "kuwo"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "07"

        # 入口地址列表
        self.start_urls = [None]
        self.encoding = 'utf8'
        self.site_domain = 'kuwo.cn'
        self.dedup_uri = None
        try:
            self.url_db = redis.StrictRedis.from_url('redis://192.168.110.51/9')
        except:
            self.url_db = None
        # self.conn = redis.StrictRedis.from_url("redis://192.168.120.214/2")
        self.redis_key = 'quixey_redis_uri'
        redis_uri = self.url_db.get(self.redis_key)
        self.conn = redis.StrictRedis.from_url(redis_uri)
        self.key_urls = 'list_kuwo_album_urls_details'
        # self.dedup_key = 'zset_kuwo_url'

        self.mysql_key = 'quixey_mysql_uri'
        mysql_uri = self.url_db.get(self.mysql_key)
        self.db = DB().create(mysql_uri)
        self.table_name = 'gmx_kuwo_album'
        self.limits = 100
        self.url_dic = {}
        self.proxy_url = "http://spider-ip-sync.istarshine.net.cn/proxy.txt"

    def __del__(self):
        try:
            for url in self.url_dic.keys():
                self.url_db.lpush(self.key_urls, url)
        except:
            pass

    def get_start_urls(self, data=None):
        '''
        返回start_urls
        '''
        return self.start_urls

    def parse(self, response):
        pipe = self.url_db.pipeline()
        for i in xrange(self.limits):
            # pipe.rpoplpush(self.key_urls, self.key_urls)
            pipe.rpop(self.key_urls)
        resp = []
        url_list = []
        try:
            urls = pipe.execute()
        except:
            urls = []
        page_urls = [url for url in urls if url is not None]
        for url in page_urls:
            self.url_dic[url] = 0
            url_new = "http://www.kuwo.cn/album/%s" % url
            req = {
                'url': 'asdas',
                'method': 'GET',
                'proxies': {
                    'http': 'socks5://127.0.0.1:1080',
                    'https': 'socks5://127.0.0.1:1080',
                }
            }
            url_list.append(req)
        return (url_list, None, None)

    def handle_post(self, post):
        post = copy.deepcopy(post)
        for k, v in post.iteritems():
            print k, v
            if isinstance(v, unicode):
                v = v.encode("utf8")
            if not isinstance(v, str) and not isinstance(v, int) and not isinstance(v, float):
                v = json.dumps(v)
            try:
                v = MySQLdb.escape_string(v)
            except:
                pass
            post.update({k: v})
        return post

    def to_redis(self, post):
        post.update({"config_id": -166,})
        post.update({
            "@context": post.get("context"),
            "@id": post.get("id"),
            "__gtime": time.time(),
        })
        try:
            post.pop("ori_url")
        except:
            pass
        key = 'custom_data'
        # key = 'custom_data_quixey_test'
        self.conn.lpush(key, pickle.dumps(post))
        return

    def to_mysql_and_redis(self, post, pop_url):  # pop_url是需要弹出的链接,跟redis中的链接保持一致
        dic = self.handle_post(post)
        redis_flag = 0
        mysql_flag = 0
        try:
            self.to_redis(post)
            redis_flag = 1
        except:
            try:
                self.to_redis(post)
                redis_flag = 1
            except Exception as e:
                print u"入redis失败%s" % e
        try:
            self.db.table(self.table_name).add(dic)
            mysql_flag = 1
        except:
            try:
                self.db.table(self.table_name).add(dic)
                mysql_flag = 1
            except Exception as e:
                print u"入mysql失败%s" % e
                # 更新MySQL                ####日更新网站
                mysql_flag = 1
        if redis_flag and mysql_flag:
            try:
                self.url_dic.pop(pop_url)
            except Exception as e:
                print u"弹出失败%s" % e

    def parse_detail_page(self, response=None, url=None):
        '''
        详细页解iii析
        '''

        ori_url = url
        try:
            response.encoding = self.encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception, e:
            print "parse_detail_page(): %s" % e
            return None
        albumid = url.strip("/").split("/")[-1]
        url = "http://m.kuwo.cn/newh5/album/content?albumid=%s" % albumid

        name = data.xpath('''//div[@class="comm"]/h1''').text().strip()
        if not name:
            # name = ""
            print len(name), "##########ZZ"
            return

        import requests

        a = requests.get(url='https://youtube.com', proxies={})
        a.content
        a.encoding = 'utf-8'
        a.text

        image1 = data.xpath('''//div[@class="s_img"]/a/img/@lazy_src''').text().strip()
        image = [image1]
        if image == [""]:
            image = []

        description = data.xpath('''//div[@id="moreContent"]''').replace("\s+", " ").text().strip()
        if not description: description = ""

        ratingValue1 = data.xpath('''//span[@class="scoreFont"]''').text().strip()
        ratingValue = float(ratingValue1) if ratingValue1 else 0.0
        aggregateRating = {
            "ratingCount": 0,
            "ratingValue": ratingValue,
        }

        author_name = data.xpath('''//ul[@class="tipscomm"]/li[1]''').text().replace("歌手：", "").strip()
        if not author_name:
            author_name = ""
        author_urls = data.xpath('''//div[@class="list"]/ul/li[1]/p[@class="s_name"]/a/@href''').text().strip()
        try:
            unicode_html_body = self.download(author_urls)
            author_data = htmlparser.Parser(unicode_html_body.text)
        except Exception, e:
            try:
                unicode_html_body = self.download(author_urls)
                author_data = htmlparser.Parser(unicode_html_body.text)
            except Exception, e:
                print "parse_detail_page(): %s" % e
                # return None
                author_url = ""
        if author_data:
            singerId = author_data.xpath('''//div[@class="artistTop"]/@data-artistid''').text().strip()
            author_url = "http://m.kuwo.cn/?artistid=%s" % singerId
        author = [{
            "name": author_name,
            "url": author_url,
        }]

        datePublished = data.xpath('''//ul[@class="tipscomm"]/li[3]''').text().replace("发行时间：", "").strip()
        if not datePublished:
            datePublished = ""

        genre1 = data.xpath('''//ul[@class="tipscomm"]/li[4]''').text().replace("专辑标签：", "").strip()
        genre = [genre1]
        if genre == [""]:
            genre = []

        publisher1 = data.xpath('''//ul[@class="tipscomm"]/li[2]''').text().replace("唱片公司：", "").strip()
        if not publisher1:
            publisher1 = ""
        publisher = [{
            "name": publisher1,
            "url": "",
        }]

        numTracks1 = data.xpath('''//ul[@class="tipscomm"]/li[5]''').text().replace("歌曲数：", "").strip()
        numTracks = int(numTracks1) if numTracks1 else 0

        viewCount1 = data.xpath('''//ul[@class="tipscomm"]/li[6]''').text().replace("收听量：", "").strip()
        viewCount = int(viewCount1) if viewCount1 else 0

        tracks = data.xpathall('''//div[@class="m_list clearfix"]/form//ul/li''')
        track = []
        for track1 in tracks:
            name1 = track1.xpath('''//p[2]''').text().strip()
            url1 = track1.xpath('''//p[2]/a/@href''').text().split("?")[0].strip()
            # author_list = []
            # author_name1 = track1.xpath('''//p[4]/a''').text().strip()
            # author_url1 = track1.xpath('''//p[4]/a/@href''').text().split("?")[0].strip()
            # author2 = {
            #             "name":author_name1,
            #             "url":author_url1,
            # }
            # author_list.append(author2)
            track2 = {
                "name": name1,
                # "author":author_list,
                "url": url1,
            }
            track.append(track2)

        post = {
            "id": url,  # @
            "created": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),  # @
            "crawled": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),  # @
            "httpStatus": "200",  # @
            "numTracks": numTracks,  ## !
            "description": description,  # @
            "image": image,  ##########@
            "name": name,  # @
            "aggregateRating": aggregateRating,
            "genre": genre,  ##########@
            "datePublished": datePublished,
            "publisher": publisher,  ########## @
            "favoriteCount": 0,  ##
            "author": author,  ###########@
            "track": track,  ###########@
            "context": "http://schemas.quixey.com/2015/07/china-phoenix/scrape/verticals/MusicGroup.jsonld",
            # @       #注：还有些字段图片上有单sgame没有，注意
            "breadcrumb": [],  ##########@
            "alternateName": [],  ###########@
            "comment": [],  ##########@
            "commentCount": 0,  ##
            "keywords": [],  ##########@
            "inLanguage": [],  ##########@
            "review": [],  ##########@
            "reviewCount": 0,  ##
            "shareCount": 0,  ##
            "viewCount": viewCount,  ##
            "attributes": [],  ##########@
            "url": url,  # @
            "ori_url": ori_url,
        }

        pop_url = ori_url.split("/")[-1].strip()
        self.to_mysql_and_redis(post, pop_url)

        print u"入库完成"
        print "################################################################"

        return None


if __name__ == '__main__':
    spider = MySpider()
    spider.proxy_enable = True
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

    url = 'http://www.kuwo.cn/album/279756'  # 样例
    resp = spider.download(url)
    res = spider.parse_detail_page(resp, url)
    for item in res:
        for k, v in item.iteritems():
            print k, v





