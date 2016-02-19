# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import socket
import sys
import io

socket.setdefaulttimeout(30)

def getHtml(url):
    page = 1
    url = 'http://www.qiushibaike.com/hot/page/' + str(page)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
    headers = { 'User-Agent' : user_agent }
    try:
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        #print response.read()
        content = response.read()
        pattern = re.compile('<div.*?author">.*?<a.*?<img.*?>(.*?)</a>.*?<div.*?'+
                                 'content">(.*?)<!--(.*?)-->.*?</div>(.*?)<div class="stats".*?class="number">(.*?)</i>')
        items = re.findall(r'div.*?content">(.*?)<!--(.*?)-->', content, re.U|re.S)
        #print items
        for item in items:
            print item[0].decode('utf-8').encode('utf-8'), item[1]

    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason

def getImg(html):
    imglist = re.findall(r"title=(.*?)style", html, re.U|re.S)
    #print imglist

    x = 0
    for imgurl in imglist:
        print imgurl
        #urllib.urlretrieve(imgurl,'%s')
        x+=1
    else:
        print 'this is over'

#--------------test--------------------
url="http://localhost:5000/statusChange"
#url="http://hr.baicgroup.com.cn/blogon"
html = getHtml(url)
#print getImg(html)
