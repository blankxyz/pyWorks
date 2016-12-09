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


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class HubPageHandler(tornado.web.RequestHandler):
    def get(self):
        hubPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get', hubPage
        db = DBDriver()
        hubPages = db.get_hubPage(hubPage)

        pprint(hubPages)

        self.render(
            "hubPages.html",
            hubPages=hubPages)


class ListJsonHandler(tornado.web.RequestHandler):
    def get(self):
        global g_site_index_list, g_recordsTotal, g_recordsFiltered

        draw = self.get_argument('draw')
        start = self.get_argument('start')
        length = self.get_argument('length')
        search = self.get_argument('search[value]')

        init(search)

        start = int(start)
        length = int(length)
        end = start + length
        # # if start and length != '-1':

        print '[info] get() draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search

        j = json.dumps({"draw": draw,
                        "recordsTotal": g_recordsTotal,
                        "recordsFiltered": g_recordsFiltered,
                        'data': g_site_index_list[start:end]})

        self.write(j)


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
            (r"/getHubPage", HubPageHandler),
            (r"/getListJson", ListJsonHandler)
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def init(search):
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
            if re.match(search,siteName,re.UNICODE):
                g_site_index_list.append([hubPage, siteName])
        else:
            g_site_index_list.append([hubPage, siteName])

    g_site_index_list.sort(reverse=False)
    g_recordsTotal = len(g_site_index_list)
    g_recordsFiltered = g_recordsTotal

    pprint('init is complate!')


def main():
    init('')

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
