#!/usr/bin/env python
#  coding=utf-8

# def parse(self, response):
#     pipe = self.url_db.pipeline()
#     for i in xrange(self.limits):
#         # pipe.rpoplpush(self.key_urls, self.key_urls)
#         pipe.rpop(self.key_urls)
#     resp = []
#     url_list = []
#     try:
#         urls = pipe.execute()
#     except:
#         urls = []
#     page_urls = [url for url in urls if url is not None]
#     for url in page_urls:
#         self.url_dic[url] = 0
#         url_new = "http://www.kuwo.cn/album/%s" % url
#         req = {
#             'url': 'asdas',
#             'method': 'GET',
#             'proxies': {
#                 'http': 'socks5://127.0.0.1:1080',
#                 'https': 'socks5://127.0.0.1:1080',
#             }
#         }
#         url_list.append(req)
#     return (url_list, None, None)

import urllib2
import socket
import pycurl
import traceback

DOWNLOADED_FILE = '1.txt'
url = "http://www.youtube.com"
socket.setdefaulttimeout(300)
crl = pycurl.Curl()
crl.setopt(pycurl.URL, url)
# crl.setopt(pycurl.FOLLOWLOCATION, 1)
crl.setopt(pycurl.PROXY, "47.90.16.137:60120")
crl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
crl.setopt(pycurl.PROXYUSERPWD, "Zhxg-ss-2016")

outfile = file(DOWNLOADED_FILE, 'wb')
crl.setopt(pycurl.WRITEFUNCTION, outfile.write)
try:
    print 'perform'
    ret = crl.perform()
    print 'perform'
except Exception, e:
    traceback.print_exc()]


HCODE = crl.getinfo(crl.HTTP_CODE)
if HCODE == 200:
    print "down file succeful"
elif HCODE == 404:
    print "file not find"
else:
    print "unknow error", HCODE

outfile.close()
crl.close()
