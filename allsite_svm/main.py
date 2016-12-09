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


define("port", default=8000, help="run on the given port", type=int)

class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_site_index = 'hash_site_index'  # 网站域名（首页地址）: 名字
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
        site_index_list = []
        db = DBDriver()
        l = db.get_site_index()

        cnt = 0
        for (hubPage, siteName) in l.items():
            # if cnt == 100:
            #     break
            cnt = cnt + 1

            if 'http://www.' in hubPage:
                hubPage = hubPage[len('http://www.'):]
            elif 'http://' in hubPage:
                hubPage = hubPage[len('http://'):]

            site_index_list.append((hubPage, siteName))

        # pprint(site_index_list)

        self.render(
            "index.html",
            site_index_list=site_index_list)

class HubPageHandler(tornado.web.RequestHandler):
    def get(self):
        hubPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get',hubPage
        db = DBDriver()
        hubPages = db.get_hubPage(hubPage)

        pprint(hubPages)

        self.render(
            "hubPages.html",
            hubPages=hubPages)


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
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def test():
    db = DBDriver()
    # http://xjmtzyw.com

if __name__ == "__main__":
    # test()
    main()
