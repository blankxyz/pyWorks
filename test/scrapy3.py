# -*- coding: utf-8 -*-
import urllib2
import cookielib
import urllib
import Image
import cStringIO
from pytesser.pytesser import *
import re
import os

# UnicodeEncodeError: 'ascii' codec can't encode character.
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

cookieJar = cookielib.MozillaCookieJar()
cookieSupport = urllib2.HTTPCookieProcessor(cookieJar)
# 调试用
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
opener = urllib2.build_opener(cookieSupport, httpsHandler)
urllib2.install_opener(opener)

loginPage = "http://zhuzhou2013.feixuelixm.teacher.com.cn/IndexPage/Index.aspx"
# 要post的url
LoginUrl = "http://zhuzhou2013.feixuelixm.teacher.com.cn/GuoPeiAdmin/Login/Login.aspx"

# 手动输入验证码
# verifyCodeUrl = "http://zhuzhou2013.feixuelixm.teacher.com.cn/GuoPeiAdmin/Login/ImageLog.aspx"
# file = urllib2.urlopen(verifyCodeUrl)
# pic= file.read()
# path = "code.jpg"
# #img = cStringIO.StringIO(file) # constructs a StringIO holding the image  AttributeError: addinfourl instance has no attribute 'seek'
# localPic = open(path,"wb")
# localPic.write(pic)
# localPic.close()
# print "please  %s,open code.jpg"%path
# text =raw_input("input code :")
# im = Image.open(path)
# text =image_to_string(im)
# print text

# using pytesser to passer the verify code。
verifyCodeUrl = "http://zhuzhou2013.feixuelixm.teacher.com.cn/GuoPeiAdmin/Login/ImageLog.aspx"
file = urllib2.urlopen(verifyCodeUrl).read()
img = cStringIO.StringIO(file)  # constructs a StringIO holding the image  AttributeError: addinfourl instance has no attribute 'seek'
im = Image.open(img)
text = image_to_string(im)
print "verifyCodeUrl:", text

cookies = ''
for index, cookie in enumerate(cookieJar):
    # print '[',index, ']';
    # print cookie.name;
    # print cookie.value;
    # print "###########################"
    cookies = cookies + cookie.name + "=" + cookie.value + ";"
print "###########################"
cookie = cookies[:-1]
print "cookies:", cookie

# username = "7879954564555664"
# password = "12313164"

username = "430223198809308045"
password = "56961888"

# post date: copy from httpFox
postData = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '/wEPDwUKLTcyMzEyMTY2Nw8WAh4LTG9naW5lZFBhZ2UFEExvZ2luZWRQYWdlLmFzcHgWAmYPZBYCZg8PZBYGHgV0aXRsZQUg55So5oi35ZCNL+WtpuS5oOeggS/ouqvku73or4Hlj7ceB29uZm9jdXMFEGNoZWNrSW5wdXQodGhpcykeBm9uYmx1cgUNcmVzdG9yZSh0aGlzKWQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFC0ltZ2J0bkxvZ2luckJjpNhrusWhtPuT33UJ1dBUkvw=',
    'txtUserName': username,
    'txtPassWord': password,
    'txtCode': text,
    'ImgbtnLogin.x': 44,
    'ImgbtnLogin.y': 14,
    'ClientScreenWidth': 1180
}

# post header copy: from httpFox
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-cn,en-us;q=0.8,zh;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'zhuzhou2013.feixuelixm.teacher.com.cn',
    'Cookie': cookies,
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:29.0) Gecko/20100101 Firefox/29.0',
    'Referer': 'http://zhuzhou2013.feixuelixm.teacher.com.cn/GuoPeiAdmin/Login/Login.aspx',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length' :473,
    'Connection': 'Keep-Alive'
}

# 合成post数据
data = urllib.urlencode(postData)
print "post data:", data

request = urllib2.Request(LoginUrl, data, headers)
try:
    response = urllib2.urlopen(request)
    # cur_url =  response.geturl()
    # print "cur_url:",cur_url
    status = response.getcode()
    print status
except  urllib2.HTTPError, e:
    print e.code

# 将响应的网页打印到文件中，方便自己排查错误
# 必须对网页进行解码处理
f = response.read().decode("utf8")
outfile = open("rel_ip.txt", "w")
print >> outfile, "%s" % (f)

info = response.info()
print info

# test for login success,if LoginedPage.aspx are loaded.
testUrl = "http://zhuzhou2013.feixuelixm.teacher.com.cn/GuoPeiAdmin/Login/LoginedPage.aspx"
try:
    response = urllib2.urlopen(testUrl)
except  urllib2.HTTPError, e:
    print e.code

# 因为后面要从网页查找字符来验证登陆成功与否，所以要保证查找的字符与网页编码相同，否则无非得到正确的结论。建议用英文查找,如css中的 id， name 之类的。
f = response.read().decode("utf8").encode("utf8")
outfile = open("out_ip.txt", "w")
print >> outfile, "%s" % (f)

# 在返回的网页中，查找“你好” 两个字符，因为只有登陆成功后才有两个字，找到了即表示登陆成功。建议用英文
tag = '你好'.encode("utf8")
if re.search(tag, f):
    print 'Logged in successfully!'
else:
    print 'Logged in failed, check result.html file for details'

response.close()
