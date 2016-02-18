# -*- coding: utf-8 -*-
import urllib
import re

def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    #print html
    return html

def getImg(html):
    imglist = re.findall(r"title=(.*?)style", html.decode('utf8'), re.U|re.S)
    #print imglist

    x = 0
    for imgurl in imglist:
        print imgurl
        #urllib.urlretrieve(imgurl,'%s')
        x+=1
    else:
        print 'this is over'

html = getHtml("http://localhost:5000/statusChange")

print getImg(html)
