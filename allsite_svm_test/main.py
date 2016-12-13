#!/usr/bin python
# coding=utf-8

import os.path
import json
import datetime
import re
import signal
import urllib
import requests
import redis
import pymongo
import time
from math import *

import tornado.autoreload
from pprint import pprint
import tornado.locale
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.log import LogFormatter
import tornado.web
from tornado.escape import json_encode
from tornado.options import define, options

define("port", default=9000, help="run on the given port", type=int)

g_site_index_list = []
g_recordsTotal = 0
g_recordsFiltered = 0
g_hubPages = []

class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_site_index = 'hash_cn_site_index'  # 网站域名（首页地址）: 名字
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def get_site_index(self):
        return self.conn.hgetall(self.hash_site_index)

    def get_hubPage(self, hubPage):
        ret = []
        hubPage_key = self.site_hub_pre % hubPage

        if self.conn.keys(hubPage_key):
            print '[info] get_hubPage() found.', hubPage_key
            ret = self.conn.smembers(hubPage_key)
        else:
            print '[info] get_hubPage() not found.', hubPage_key
        return ret

    def get_hubPage_cnt(self, hubPage):
        cnt = 0
        hubPage_key = self.site_hub_pre % hubPage
        if self.conn.keys(hubPage_key):
            cnt = self.conn.scard(hubPage_key)

        return cnt


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class HubPageHandler(tornado.web.RequestHandler):
    def get(self):
        global g_hubPages

        hubPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get', hubPage
        db = DBDriver()
        g_hubPages = db.get_hubPage(hubPage)

        # pprint(hubPages)

        self.render(
            "hubPages.html",
            hubPages=g_hubPages)


class HubPage2Handler(tornado.web.RequestHandler):
    def get(self):
        hubPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get', hubPage

        draw = self.get_argument('draw', '')
        start = self.get_argument('start', '0')
        length = self.get_argument('length', '20')
        search = self.get_argument('search[value]', '')

        db = DBDriver()
        hubPages = list(db.get_hubPage(hubPage))
        start = int(start)
        length = int(length)
        end = start + length

        # pprint(hubPages)
        print '[info] HubPage2Handler get() draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search
        # j = json.dumps({"draw": draw,
        #                 "recordsTotal": len(hubPages),
        #                 "recordsFiltered": len(hubPages),
        #                 'data': hubPages[start:end]})

        j = json.dumps({"data": hubPages[start:end]})
        self.write(j)


class SiteListJsonHandler(tornado.web.RequestHandler):
    def get(self):
        site_index_list = []
        global g_site_index_list, g_recordsTotal, g_recordsFiltered
        db = DBDriver()

        draw = self.get_argument('draw')
        start = self.get_argument('start')
        length = self.get_argument('length')
        search = self.get_argument('search[value]')

        init(search)

        start = int(start)
        length = int(length)
        end = start + length
        # # if start and length != '-1':

        for i in g_site_index_list[start:end]:
            hubPage = i[0]
            hubPageCnt = db.get_hubPage_cnt(hubPage)
            site_index_list.append([i[0], str(hubPageCnt), i[1]])

        print '[info] SiteListJsonHandler get() draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search
        # pprint(site_index_list)

        j = json.dumps({"draw": draw,
                        "recordsTotal": g_recordsTotal,
                        "recordsFiltered": g_recordsFiltered,
                        'data': site_index_list})

        self.write(j)


class MatchHugPageHandler(tornado.web.RequestHandler):
    # def get(self):
    #     print '[info] MatchHugPageHandler() get'
    #     pprint(self.request.body_arguments)
    #     data = self.get_body_argument('data')
    #     pprint(data)
    #     self.write('ok')

    def post(self):
        print '[info] MatchHugPageHandler() post'
        para = self.request.body_arguments
        # jdata = json.loads(para)
        pprint(para)
        (k,v) = para.items()[0]
        data = eval(k)['data']
        data = list(set(data))
        # for link in data:
        #     for hubPages in g_hubPages:
        #         if hubPages


        # print type(data)

        resp = {'response':data}
        resp_json = tornado.escape.json_encode(resp)
        pprint(resp_json)
        self.write(resp_json)

def signal_handler(signum, frame):
    tornado.ioloop.IOLoop.instance().stop()


signal.signal(signal.SIGINT, signal_handler)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            static_js_path=os.path.join(os.path.dirname(__file__), "static/js"),
            debug=True,
        )
        handlers = [
            (r"/", MainHandler),
            (r"/getSiteListJson", SiteListJsonHandler),
            (r"/getHubPage", HubPageHandler),
            (r"/getHubPage2", HubPage2Handler),
            (r"/matchHubpage", MatchHugPageHandler)
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def init(search):
    print '[info] init() search:', search
    global g_site_index_list, g_recordsTotal, g_recordsFiltered
    g_site_index_list = []

    db = DBDriver()
    l = db.get_site_index()

    for (hubPage, siteName) in l.items():
        if 'http://www.' in hubPage:
            hubPage = hubPage[len('http://www.'):]
        elif 'http://' in hubPage:
            hubPage = hubPage[len('http://'):]

        if search:
            print type(siteName), siteName
            if re.match(search, siteName, re.UNICODE):
                print '[info] init() matched.', siteName
                g_site_index_list.append([hubPage, siteName])
        else:
            g_site_index_list.append([hubPage, siteName])

    g_site_index_list.sort(reverse=False)
    g_recordsTotal = len(g_site_index_list)
    g_recordsFiltered = g_recordsTotal

    print('init is complate!')


def main():
    init('')

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
