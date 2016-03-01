# -*- coding: utf-8 -*-
import urllib2
import cookielib
import urllib
import socket
import cStringIO
import re
import os
from bs4 import BeautifulSoup

socket.setdefaulttimeout(30)
# UnicodeEncodeError: 'ascii' codec can't encode character.
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

url = 'http://cpquery.sipo.gov.cn/txnPantentInfoList.do?inner-flag:open-type=window&inner-flag:flowno=1457270946639'
queryUrl = 'http://cpquery.sipo.gov.cn/txnQueryBibliographicData.do?select-key:shenqingh=2014202071967&select-key:gonggaobj=1&select-key:backPage=http%3A%2F%2Fcpquery.sipo.gov.cn%2FtxnQueryOrdinaryPatents.do%3Fselect-key%3Ashenqingh%3D2014202071967%26select-key%3Azhuanlimc%3D%26select-key%3Ashenqingrxm%3D%26select-key%3Azhuanlilx%3D%26select-key%3Ashenqingr_from%3D%26select-key%3Ashenqingr_to%3D%26inner-flag%3Aopen-type%3Dwindow%26inner-flag%3Aflowno%3D1457276172123&inner-flag:open-type=window&inner-flag:flowno=1457276286289'
cookieFile = 'cookie.txt'


def saveCookies():
    cookie = cookielib.MozillaCookieJar(cookieFile)
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    response = opener.open(url)
    for item in cookie:
        print 'Name = ' + item.name
        print 'Value = ' + item.value
    cookie.save(ignore_discard=True, ignore_expires=True)


def readCookies():
    cookie = cookielib.MozillaCookieJar(cookieFile)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    result = opener.open(url)
    cookie.save(ignore_discard=True, ignore_expires=True)
    response = opener.open(queryUrl)
    fp = open("cpquery.html", 'w')
    fp.write(response.read())
    fp.close()


def grepHtml(url):
    soup = BeautifulSoup(open('cpquery.html'))
    #  < span title = "实审请求视撤失效" name = "record_zlx:anjianywzt" >
    content = soup.findAll(attrs={"name":"record_zlx:anjianywzt"})
    print content
    #print content[0].title
#    print text.decode('utf-8').encode('utf-8'), item[1]

# --------------test--------------------
saveCookies()
readCookies()
html = grepHtml(url)
