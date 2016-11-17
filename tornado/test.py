#!/usr/bin/env python
# -*- coding:utf-8 -*-


from datetime import timedelta
from bs4 import BeautifulSoup
from tornado.httpclient import AsyncHTTPClient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import ioloop, gen, queues
import pycurl

proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
           'Connection': 'keep-alive',
           'Cookie': 'PREF=f1=1222&cvdm=list',  # must be set 'list'
           'Host': 'www.youtube.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
           }
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='

def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)

@gen.coroutine
def fetch(url):
    print('fetcing', url)
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    http_request = HTTPRequest(
        url,
        prepare_curl_callback=prepare_curl_socks5,
        proxy_host="localhost",
        proxy_port=1080
    )
    response = yield AsyncHTTPClient().fetch(http_request,raise_error=False)
    # http_header = {
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'}
    # http_request = HTTPRequest(url=url, method='GET', headers=http_header,
    #                            connect_timeout=200, request_timeout=60, proxy_host="127.0.0.1",proxy_port=1080)
    # http_client = HTTPClient()
    # http_response = http_client.fetch(http_request)

    raise gen.Return(response)


_q = queues.Queue()


@gen.coroutine
def run():
    try:
        url = yield _q.get()
        res = yield fetch(url)
        html = res.body
        soup = BeautifulSoup(html)
        print(str(soup.find('title')))
    finally:
        _q.task_done()


@gen.coroutine
def worker():
    while not _q.empty():
        yield run()


@gen.coroutine
def main():
    for i in range(73000, 73100):  # 放100个链接进去
        # url = "http://www.jb51.net/article/%d.htm" % i
        url = PRE_SEARCH_URL + 'china'
        yield _q.put(url)
    for _ in range(100):  # 模拟100个线程
        worker()
    yield _q.join(timeout=timedelta(seconds=300))


if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(main)
