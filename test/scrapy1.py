# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import socket
import cookielib

socket.setdefaulttimeout(30)

def saveCookies():
    #url = 'http://10.0.90.50:10080/Login.aspx'
    url = 'http://www.cnblogs.com/'
    #设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookie.txt'
    #声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = cookielib.MozillaCookieJar(filename)
    #利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
    handler = urllib2.HTTPCookieProcessor(cookie)
    #通过handler来构建opener
    opener = urllib2.build_opener(handler)
    #创建一个请求，原理同urllib2的urlopen
    response = opener.open(url)

    for item in cookie:
        print 'Name = '+item.name
        print 'Value = '+item.value
    #保存cookie到文件
    cookie.save(ignore_discard=True, ignore_expires=True)

def readCookies():
    #loginUrl = 'http://10.0.90.50:10080/Login.aspx'
    loginUrl = 'http://www.cnblogs.com'
    filename = 'cookie.txt'
    #声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    postdata = urllib.urlencode({
                'UserCodetxt':'yanqiang11.song',
                'PassWordtxt':'(Nttdata1)'
            })

    #模拟登录，并把cookie保存到变量
    result = opener.open(loginUrl, postdata)
    #保存cookie到cookie.txt中
    cookie.save(ignore_discard=True, ignore_expires=True)
    #利用cookie请求访问另一个网址，此网址是成绩查询网址
    logUrl = 'http://10.0.90.50:10080/KQSYS_ONL_17.aspx'
    #请求访问成绩查询网址
    response = opener.open(logUrl)

    fp = open("cnblogs.html", 'w')
    fp.write(response.read())
    fp.close()

def grepHtml(url):
    page = 1
    #url = 'http://www.qiushibaike.com/hot/page/' + str(page)
    url = 'http://passport.cnblogs.com/user/signin?ReturnUrl=http://i.cnblogs.com/EditDiary.aspx'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0'
    headers = { 'User-Agent' : user_agent }
    try:
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        #print response.read()
        content = response.read()
        pattern = re.compile('<div.*?author">.*?<a.*?<img.*?>(.*?)</a>.*?<div.*?'+
                                 'content">(.*?)<!--(.*?)-->.*?</div>(.*?)<div class="stats".*?class="number">(.*?)</i>')
        items = re.findall('div.*?content">(.*?)<!--(.*?)-->', content, re.U|re.S)
        for item in items:
            text = re.sub('<br/>','',item[0])
            #控制台输出转化为UTF-8编码
            print text.decode('utf-8').encode('utf-8'), item[1]

    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print u"连接失败原因：",e.reason

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
#url="http://hr.baicgroup.com.cn/blogon"
saveCookies()
#readCookies()
#html = grepHtml(url)
#print getImg(html)
