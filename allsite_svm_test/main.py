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
g_ListPages = []
g_site_url = ''


def topPage_to_domain(topPage):
    domain = ''
    if 'http://www.' in topPage:
        domain = topPage[len('http://www.'):]
    elif 'http://' in topPage:
        domain = topPage[len('http://'):]
    return domain


class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_cn_domain_site = 'hash_cn_domain_site'  # 网站域名: 首页地址
        self.hash_cn_site_name = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def get_domain_site(self):
        return self.conn.hgetall(self.hash_cn_domain_site)

    def get_site_name(self, site):
        return self.conn.hget(self.hash_cn_site_name, site)

    def get_listPages(self, domain):
        ret = []
        hubPage_key = self.site_hub_pre % domain

        if self.conn.keys(hubPage_key):
            print '[info] get_hubPage() found.', hubPage_key
            ret = self.conn.smembers(hubPage_key)
        else:
            print '[info] get_hubPage() not found.', hubPage_key
        return ret

    def get_listPage_cnt(self, domain):
        cnt = 0
        domain_key = self.site_hub_pre % domain
        if self.conn.keys(domain_key):
            cnt = self.conn.scard(domain_key)

        return cnt


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class SiteListHandler(tornado.web.RequestHandler):
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
            domain = i[0]
            site = i[1]
            site_name = i[2]
            domain_cnt = db.get_listPage_cnt(domain)
            site_index_list.append([site, str(domain_cnt), site_name])

        print '[info] SiteListJsonHandler get() draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search
        # pprint(site_index_list)

        j = json.dumps({"draw": draw,
                        "recordsTotal": g_recordsTotal,
                        "recordsFiltered": g_recordsFiltered,
                        'data': site_index_list})

        # pprint(j)
        self.write(j)


class HubPageHandler(tornado.web.RequestHandler):
    def get(self):
        global g_ListPages
        global g_site_url
        domain = ''
        topPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get', topPage
        db = DBDriver()
        domain = topPage_to_domain(topPage)
        g_ListPages = db.get_listPages(domain)
        g_site_url = topPage
        print '[info] HubPageHandler() get save to global', g_site_url, len(g_ListPages)

        self.render("hubPages.html", hubPages=g_ListPages)


class HubPage2Handler(tornado.web.RequestHandler):
    def get(self):
        hubPage = self.get_argument('hubPage', '')
        print '[info] HubPageHandler() get', hubPage

        draw = self.get_argument('draw', '')
        start = self.get_argument('start', '0')
        length = self.get_argument('length', '20')
        search = self.get_argument('search[value]', '')

        db = DBDriver()
        hubPages = list(db.get_listPages(hubPage))
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


class MatchHugPageHandler(tornado.web.RequestHandler):
    # def get(self):
    #     print '[info] MatchHugPageHandler() get'
    #     pprint(self.request.body_arguments)
    #     data = self.get_body_argument('data')
    #     pprint(data)
    #     self.write('ok')

    def post(self):
        db = DBDriver()
        resp_links = []
        print '[info] MatchHugPageHandler() post start.'

        # httpPost_XMLHttpRequest
        # para = self.request.body_arguments
        # print type(para)
        # pprint(para)
        # request_links = para['hrefList']
        # topPage = para['topPage']
        # print topPage, request_links

        # httpPost_ajax
        para = self.request.body_arguments
        topPage = para['topPage'][0]
        if topPage[-1] == '/':
            topPage = topPage[:-1]

        request_links = list(set(para['hrefList[]']))

        domain = topPage_to_domain(topPage)
        db_listPages = db.get_listPages(domain)

        for link in request_links:
            if link.find('http://') < 0:
                url = topPage + link
            else:
                url = link

            for lintPage in db_listPages:
                if lintPage == url:
                    resp_links.append(link)
                    break

        print '[info] MatchHugPageHandler() post end. recv:%d filter:%d' % (len(request_links), len(resp_links))
        # pprint(resp_links)
        self.write({'response': resp_links})


def signal_handler(signum, frame):
    tornado.ioloop.IOLoop.instance().stop()


signal.signal(signal.SIGINT, signal_handler)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            static_js_path=os.path.join(os.path.dirname(__file__), "static/js"),
            debug=True)

        handlers = [(r"/", MainHandler),
                    (r"/getSiteListJson", SiteListHandler),
                    (r"/getHubPage", HubPageHandler),
                    (r"/getHubPage2", HubPage2Handler),
                    (r"/matchHubpage", MatchHugPageHandler)]

        tornado.web.Application.__init__(self, handlers, **settings)


def init(search):
    # search = '42727'
    print '[info] init() search:', search
    global g_site_index_list, g_recordsTotal, g_recordsFiltered
    g_site_index_list = []

    db = DBDriver()
    l = db.get_domain_site()

    for (domain, site) in l.items():
        siteName = db.get_site_name(site)
        if search:
            if re.match(search, siteName, re.UNICODE):
                print '[info] init() matched.', siteName
                g_site_index_list.append([domain, site, siteName])
        else:
            g_site_index_list.append([domain, site, siteName])

    g_site_index_list.sort(reverse=False)
    g_recordsTotal = len(g_site_index_list)
    g_recordsFiltered = g_recordsTotal

    print('init complate!')


def main():
    # init('')

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
