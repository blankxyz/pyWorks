#!/usr/bin python
# coding=utf-8

import os.path
import json
import datetime
import re
import signal
import urllib
import urlparse
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


class Util(object):
    @staticmethod
    def get_domain(url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        domain = netloc
        if 'www.' in netloc:
            domain = netloc[len('www.'):]

        return domain

    def convert_path_to_rule(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''

        split_path = path.split('/')

        new_path_list = []
        for p in split_path:
            regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', regex)
            new_path_list.append(self.convert_regex_format(regex))

        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

    def convert_regex_format(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
        '''
        ret = ''
        digit = '\d'
        word = '[a-zA-Z]'
        cnt = 0
        pos = 0
        temp = ''
        while pos <= len(rule):
            if rule[pos:pos + len(digit)] == digit:
                if temp.find(digit) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (digit, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (word, cnt)
                pos = pos + len(word)
            elif pos == len(rule):
                ret = ret + temp
                break
            else:
                ret = ret + temp + rule[pos]
                temp = ''
                cnt = 0
                pos = pos + 1
        return ret


class DBDriver(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url('redis://192.168.174.130/12')
        self.hash_cn_domain_site = 'hash_cn_domain_site'  # 网站域名: 首页地址
        self.hash_cn_site_name = 'hash_cn_site_index'  # 首页地址: 网站名字
        self.hash_cn_domain_site_name = 'hash_cn_domain_site_name'  # 网站域名: {首页地址, 网站名字}
        self.set_cnn_hub_urls = 'set_cnn_hub_urls'  # 所有的列表页
        self.site_hub_pre = 'set_%s_hub'  # site_域名_hub 某个域名下的列表页

    def get_domain_site(self):
        return self.conn.hgetall(self.hash_cn_domain_site)

    def get_site_name(self, site):
        return self.conn.hget(self.hash_cn_site_name, site)

    def get_all_domain_site_name(self):
        ret = []
        l = self.conn.hgetall(self.hash_cn_domain_site_name)
        # pprint(l)
        for (domain, site_name) in l.items():
            site_name = eval(site_name)
            ret.append([domain, site_name['site'], site_name['name']])

        return ret

    def get_listPages(self, domain):
        ret = []
        hubPage_key = self.site_hub_pre % domain

        if self.conn.keys(hubPage_key):
            print '[info] get_hubPage() found.', hubPage_key
            ret = self.conn.smembers(hubPage_key)
        else:
            print '[info] get_hubPage() not found.', hubPage_key

        if ret:
            ret = list(ret)
            ret.sort(reverse=True)
        return ret

    def get_listPage_cnt(self, domain):
        cnt = 0
        domain_key = self.site_hub_pre % domain
        if self.conn.keys(domain_key):
            cnt = self.conn.scard(domain_key)

        return cnt

    def add_hubpage(self, domain, hubPage):
        hubPage_key = self.site_hub_pre % domain
        self.conn.sadd(hubPage_key, hubPage)

    def delete_hubpage(self, domain, hubPage):
        hubPage_key = self.site_hub_pre % domain
        self.conn.srem(hubPage_key, hubPage)


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

        # init(search)

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
        domain = Util.get_domain(topPage)
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


        # content.js:  data:JSON.stringify({'hrefList':hrefs,'topPage':topPage}),
        # d = json.loads(self.request.body)
        # print 'json.loads(self.request.body)', d
        # topPage = d['topPage']
        # request_links = list(set(d['hrefList']))

        # httpPost_ajax
        para = self.request.body_arguments
        topPage = para['topPage'][0]
        if topPage[-1] == '/':
            topPage = topPage[:-1]

        print '[info] MatchHugPageHandler() post start.', topPage

        request_links = list(set(para['hrefList[]']))

        domain = Util.get_domain(topPage)
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

        print '[info] MatchHugPageHandler() post end. [url-recv] %d [url-filter] %d' % (
            len(request_links), len(resp_links))
        # pprint(resp_links)
        self.write({'response': resp_links})


class HubPageEditer(tornado.web.RequestHandler):
    def post(self):
        # action = self.get_argument('action')
        # hubPage = self.get_argument('hubPage')
        print '[info] HubpageEditer() post'
        d = json.loads(self.request.body)
        pprint(d)

        hubPage = d['hubPage']
        action = d['action']

        domain = Util.get_domain(hubPage)
        print '[info] HubpageEditer() post', action, hubPage, domain

        db = DBDriver()

        if action == 'add':
            db.add_hubpage(domain, hubPage)

        if action == 'delete':
            db.delete_hubpage(domain, hubPage)

        self.write({'response': action + ' ' + hubPage + ' ok!'})


class UrlFinder(tornado.web.RequestHandler):
    def post(self):
        resp_links = []
        d = json.loads(self.request.body)
        pprint(d)
        url = d['url']
        links = d['links']

        util = Util()
        regex = util.convert_path_to_rule(url)
        new_regex = re.sub(r'\d+', '1,', regex)

        for link in links:
            if re.match(new_regex, link, re.U):
                resp_links.append(link)

        print '[info] UrlFinder() post', url, '>>>', new_regex
        print len(links), links, '>>>', len(resp_links), resp_links
        self.write({'regex': new_regex, 'links': resp_links})


class HubPageEditerRestAPI(tornado.web.RequestHandler):
    def get(self):
        print '[info] HubpageEditerRestAPI get'
        self.write({'response': 'ok'})

    def delete(self, url):
        print '[info] HubpageEditerRestAPI delete'
        self.set_status(204)
        self.write({'response': url})

    def put(self, url):
        print '[info] HubpageEditerRestAPI put'
        self.set_status(201)
        self.write({'response': url})


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
                    (r"/matchHubPage", MatchHugPageHandler),
                    (r"/editHubPage", HubPageEditer),
                    (r"/urlFinder", UrlFinder)]
        # (r'/hubpage$', HubpageEditerRestAPI),
        # (r'/hubpage/{url}', HubpageEditerRestAPI),
        # (r'/hubpage/(<url>)/(edit)$', HubpageEditerRestAPI)
        # ]

        tornado.web.Application.__init__(self, handlers, **settings)


def init(search):
    # search = '42727'
    print '[info] init() search:', search
    global g_site_index_list, g_recordsTotal, g_recordsFiltered
    g_site_index_list = []

    db = DBDriver()
    # l = db.get_domain_site()
    #
    # for (domain, site) in l.items():
    #     siteName = db.get_site_name(site)
    #     g_site_index_list.append([domain, site, siteName])
    g_site_index_list = db.get_all_domain_site_name()

    g_site_index_list.sort(reverse=False)
    g_recordsTotal = len(g_site_index_list)
    g_recordsFiltered = g_recordsTotal

    print('[info] init complate!')


def main():
    init('')

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
