#!/usr/bin/env python
# coding:utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：parser.py
功能：解析网页信息，提取相应数据，支持连贯操作，并自动识别时间和url等

接口调用范例：
     print "测试xpath========================================"
    num = Parser("<?xml version=\"1.0\" encoding=\"UTF-8\"?><html><data>12341234</data><time>5分钟前</time></html>").xpath(".//data/text()").int()
    print num
    
    items = Parser("<data>1</data><data>2</data>").xpathall(".//data/text()")
    for item in items:
        print item.int()
        
    print "测试regex========================================="
        
    num = Parser("123412341324abcd").regex("([12]+)").int()
    print num
    
    for item in Parser("123412341324abcd").regexall("([12]+)"):
        print item.int()
        
    print "测试连贯操作=========================================="
    num = Parser("<data>1234.1234abc</data>").xpath("//data/text()").regex("([\d\.]+)").float()
    print num
    
    print "测试时间===================================================="
    print Parser("01月03日 11:16").datetime()
    print Parser("29分钟前").datetime()
    print Parser("今天 15:42").datetime()
    print Parser("2013-11-11 13:52:35").datetime()

    print "测试URL==================================================="
    url = Parser(r"/a.html?b=3&a=4&c=1234134", "http://www.baidu.com/ab/").url()
    print url


代码历史：
2014-01-29：贺伟刚 ，创建代码框架
2014-02-07：贺伟刚，实现代码
'''

import re
from lxml import etree
import datetime, time
import urlparse
import urllib
import log
import util


bad_attrs = ['width', 'height', 'style', '[-a-z]*color', 'background[-a-z]*', 'on*']
single_quoted = "'[^']+'"
double_quoted = '"[^"]+"'
non_space = '[^ "\'>]+'
htmlstrip = re.compile("<" # open
    "([^>]+) " # prefix
    "(?:%s) *" % ('|'.join(bad_attrs),) + # undesirable attributes
    '= *(?:%s|%s|%s)' % (non_space, single_quoted, double_quoted) + # value
    "([^>]*)"  # postfix
    ">"        # end
, re.I)

def clean_attributes(html):
    while htmlstrip.search(html):
        html = htmlstrip.sub('<\\1\\2>', html)
    return html


class Parser():
    '''
    解析数据类，支持连贯操作
    '''
    def __init__(self, data=None, url=None, encoding="utf8", response=None):
        '''
        初始化，data 为页面源码；response就是requests库中的response对象
        '''
        self.response = response
        if url is None and response is not None:
            try:
                self.m_url = response.request.url
            except:
                pass
        else:
            self.m_url = url
        
        if encoding == "utf8":
            self.data = data
        else:
            self.data = data.decode(encoding).encode("utf8")
        
        self.encoding = encoding
        
        if data:
            self._root = etree.HTML(data)
            if self.m_url is not None:
                try:
                    self._root.make_links_absolute(self.m_url, resolve_base_href=True)
                except:
                    pass
        else:
            self._root = None
        
    def xpath(self, xp, default=""):
        '''
        用xpath，解析data，Parser类实例，用于连贯操作，如果没有解析成功，则返回默认结果
        '''
        
        try:
#            result = etree.HTML(self.data).xpath(xp)
            result = self._root.xpath(xp)
        except Exception, e:
            try:
                url = self.response.request.url
            except:
                url = ''
            log.logger.debug(util.R("异常：xpath 解析错误: xp is %s; exception:%s; url:%s"%(xp, e, url)))
            return Parser(default)
        
        if len(result)>0:
            data = result[0]
            return Parser(etree.tostring(data, method="html")) if isinstance(data, etree._Element) else Parser(data)
        else:
            try:
                url = self.response.request.url
            except:
                url = ''
            log.logger.debug(util.BB("xpath 解析无结果: %s; url: %s"%(xp, url)))
            return Parser(default)
            
        
    def xpathall(self,xp):
        '''
        返回多个结果，list方式
        '''
        try:
#            result = etree.HTML(self.data).xpath(xp)
            result = self._root.xpath(xp)
        except Exception, e:
            try:
                url = self.response.request.url
            except:
                url = ''
            log.logger.debug(util.R("异常：xpathall 解析错误， xp is %s; exception: %s; url: %s"%(xp, e, url)))
            return []
        
        if len(result)>0:
            return[ Parser(etree.tostring(data, method="html")) if isinstance(data, etree._Element) else Parser(data) for data in result]
        else:
            try:
                url = self.response.request.url
            except:
                url = ''
            log.logger.debug(util.BB("xpathall 解析无结果:  %s;  url: %s"%(xp, url)))
            return []
    
    def regex(self, reg, default=""):
        '''
        用正则解析data，没有解析成功，则抛出异常，支持连贯操作
        注意：一次只能解析出一个字段
        '''
        try:
            result = re.compile(reg).findall(self.data)
        except Exception, e:
            try:
                url = self.response.request.url
            except:
                url = ''
            if isinstance(reg, unicode):
                reg = reg.encode('utf8')
            log.logger.debug(util.R("异常：regex 解析错误，%s; reg:%s;  url: %s"%(e, reg, url)))
            return Parser(default)
        
        if len(result)>0:
            return Parser(result[0])
        else:
            try:
                url = self.response.request.url
            except:
                url = ''
            if isinstance(reg, unicode):
                reg = reg.encode('utf8')
            log.logger.debug(util.BB("regex 解析无结果; reg:%s; url:%s"%(reg, url)))
            return Parser(default)
        
    def regexall(self, reg):
        '''
        返回list方式的多个结果
        '''
        try:
            result = re.compile(reg).findall(self.data)
        except Exception, e:
            try:
                url = self.response.request.url
            except:
                url = ''
            if isinstance(reg, unicode):
                reg = reg.encode('utf8')
            log.logger.debug(util.R("异常：regexall 解析错误: %s; url: %s; exception: %s"%(reg, url, e)))
            return []
        
        if len(result)>0:
            return [ Parser(data) for data in result]
        else:
            try:
                url = self.response.request.url
            except:
                url = ''
            if isinstance(reg, unicode):
                reg = reg.encode('utf8')
            log.logger.debug(util.BB("regexall 解析无结果:%s ;  url: %s"%(reg, url)))
            return []
        
    def strip(self):
        '''
        删除空格等，等效于python的strip()函数，只是支持连贯操作
        '''
        try:
            data = self.data.strip()
            data = re.sub(r'(&#160;)+$', '', data)
        except Exception, e:
            log.logger.debug("异常：strip错误，%s"%e)
            return Parser(self.data)
        
        return Parser(data)
    
    def __repr__(self):
        '''
        重载操作符，用于显示%s
        '''
        return self.str()
#        return self.str(self.data)
      
    def str(self, encoding="utf8"):
        '''
        把data转为字符串，默认返回utf8编码，解析出来结果是多个，例如xpath，则只是提取一个，如果是多个，需要用tuple()处理
        '''
        return self.data.encode(encoding)

    def text(self, encoding="utf8"):
        '''
        提取data代表的标签内的text，默认返回utf8编码;与str()函数的不同之处在于，该函数操作在基于html文档的etree element之上；
        而str()函数只是对文本内容进行编码
        '''
        if self._root is not None:
            return etree.tostring(self._root,  encoding=encoding,  method='text')
        else:
            return ''.encode(encoding)
    
    def html(self, encoding="utf8"):
        '''
        '''
        if self._root is not None:
            return etree.tostring(self._root,  encoding=encoding, method='html')
        else:
            return ''.encode(encoding)
    
    def cleaned_html(self, encoding="utf8"):
        '''
        '''
        if self._root is not None:
            return etree.tostring(self._root,  encoding=encoding, method='html')
            return clean_attributes(etree.tostring(self._root,  encoding=encoding, method='html'))
        else:
            return ''.encode(encoding)
        
    
    def int(self,default=-1):
        '''
        把data转为整数，如果不全是数字，例如：123abc，则抛出异常
        '''
        result = default
        try:
            result = int(self.data)
        except Exception, e:
            log.logger.debug("异常：int转换错误,%s"%e)
            return default
        
        return result
    
    def float(self, default=0.0):
        '''
        把data转为浮点，如果转换不成功，则抛出异常
        '''
        result = default
        try:
            result = float(self.data)
        except Exception, e:
            log.logger.debug("异常：float转换错误，%s"%e)
            return default
        return result
    
    def datetime(self):
        '''
        把data转换为日期时间，时区为东八区北京时间，能够识别：今天、昨天、5分钟前等等，如果不能成功识别，则返回None
        '''
        dt = None
        utc_dt = None
        if re.match("\s*(\d+)月(\d+)日\s+(\d+)[:：]+(\d+)\s*", self.data): #01月03日 11:16
            
            dt = util.TimeDeltaYears(datetime.date.today().year - 1900, datetime.datetime.strptime(self.data, "%m月%d日 %H:%M"))
        if re.match("\s*(\d+)-(\d+)\s+(\d+)[:：]+(\d+)\s*", self.data): #01-03 11:16
            
            dt = util.TimeDeltaYears(datetime.date.today().year - 1900, datetime.datetime.strptime(self.data, "%m-%d %H:%M"))
        #29分钟前 
        elif re.search("(\d+)秒前", self.data): #10秒前 
            seconds = int(re.findall("(\d+)秒前", self.data)[0])
            dt = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
            str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
        #29分钟前 
        elif re.search("(\d+)分钟前", self.data): #29分钟前 
            minutes = int(re.findall("(\d+)分钟前", self.data)[0])
            dt = datetime.datetime.now() - datetime.timedelta(seconds=minutes*60)
            str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
        #1小时前 
        elif re.search("(\d+)小时前", self.data):
            hours = int(re.search("(\d+)小时前", self.data).group(1))
            dt = datetime.datetime.now() - datetime.timedelta(hours=hours)
            str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
        #2天前 
        elif re.search("(\d+)天前", self.data):
            days = int(re.search("(\d+)天前", self.data).group(1))
            dt = datetime.datetime.now() - datetime.timedelta(days=days)
            str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
            
        elif re.match("今天\s*(\d+):(\d+)", self.data): #今天 15:42 
            days = datetime.date.today() - datetime.date(1900, 1, 1)
            dt = datetime.datetime.strptime(self.data, "今天 %H:%M")  + datetime.timedelta(days=days.days)
            
        elif re.match("\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)\s*", self.data): #2013-11-11 13:52:35
            try:
                dt = datetime.datetime.strptime(self.data, "%Y-%m-%d %H:%M:%S")
            except:
                dt = datetime.datetime.strptime(self.data, "%y-%m-%d %H:%M:%S")
        
        elif re.match("\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+)\s*", self.data): #2013-11-11 13:52
            try:
                dt = datetime.datetime.strptime(self.data, "%Y-%m-%d %H:%M")
            except :
                dt = datetime.datetime.strptime(self.data, "%y-%m-%d %H:%M")
        
        elif re.match("\s*(\d+)/(\d+)/(\d+)\s+(\d+):(\d+)\s*",  self.data): #2013/11/11 13:52
            dt = datetime.datetime.strptime(self.data, "%Y/%m/%d %H:%M")
        
        elif re.match("\s*(\d+)-(\d+)-(\d+)", self.data): #2013-11-11
            dt = datetime.datetime.strptime(self.data, "%Y-%m-%d")
        
        else:
            log.logger.debug(util.BB("错误，datetime，没有解析成功, 匹配内容: %s "%self.data))
            dt = datetime.datetime.now()
         
        utc_dt = dt - datetime.timedelta(seconds=28800)
        return utc_dt
       
    def url(self,  remove_param=False):
        '''
        把data转换为标准的url格式，如果url有参数，则按照升序重新排列，防止url相同，但是参数顺序不同而造成的url不同的识别错误，
        例如http://xxx.com/123.html?b=1&a=3，则返回http://xxx.com/123.html?a=3&b=1；
        如果remove_param=True，则删除参数，例如http://xxx.com/123.html?b=1&a=3，则返回为http://xxx.com/123/html；
        如果是相对路径，例如123.html，则返回绝对路径：http://xxx.com/123.html，并识别/123.html,则为http://xxx.com/123.html
        注意：识别url需要在__init__中设置url参数，否则无法识别相对路径的Url
        '''
        
        result = ""
        
        uri = urlparse.urlsplit(self.data)
        #对参数进行排序，名字升序
        query = urlparse.parse_qsl(uri.query,True)
        query.sort()
        query = urllib.urlencode(query)
        
        if uri.netloc == "":
            #没有域名
            result = urlparse.urljoin(self.m_url, urlparse.urlunsplit((uri.scheme, uri.netloc, uri.path, query, uri.fragment)))
        else:
            result =  urlparse.urlunsplit((uri.scheme, uri.netloc, uri.path, query, uri.fragment))
            
        return result

    def replace(self, pattern, repl, count=0):
        """
        将data中满足规则pattern的元素替换为字符串repl; 
        参数count表示替换发生的最大次数；必须为非负整数；默认为0,表示替换所有符合条件的元素；
        """
        try:
            result = re.compile(pattern).sub(repl, self.data, count)
        except Exception, e:
            log.logger.debug("异常：replace 替换错误，%s"%e)
            return self
        
        return Parser(result)
    
    def delete(self, pattern, count=0):
        """
        删除data中符合规则pattern的元素；参数count同sub
        """
        try:
            result = re.compile(pattern).sub("", self.data, count)
        except Exception, e:
            log.logger.debug("异常: delete 删除出现错误: %s"%e)
            return self
        
        return Parser(result)

    def urls(self, base_url, domains=None, regex=None):
        """
        找出所有的有效url;
        参数base_url代表url前缀，用来生成绝对url; 参数domains指允许的url域；regex是一个正则表达式，用来过滤url;
        """
        try:
            result = etree.HTML(self.data).xpath("//a/@href | //iframe/@src")
        except Exception, e:
            log.logger.debug("异常：xpath 解析错误， %s"%e)
            return []
        #去重
        urls_set = set(result)
        
        if regex is not None:
            reg = re.compile(regex, re.U)
        urls = []
        for url in urls_set:
            if regex is not None:
                try:
                    res = reg.findall(url)
                except Exception,e:
                    log.logger.debug("异常：findall in urls() 解析错误， %s"%e)
                    continue
                if res:
                    url = res[0]
                else:
                    continue
            if str(url).startswith("/"):
                if base_url is not None:
                    url = base_url + url
                    urls.append(url)
                elif self.m_url is not None:
                    url = self.m_url + url
                    urls.append(url)
                else:
                    continue
            elif url.startswith("http://") or url.startswith("https://"):
                uri = urlparse.urlsplit(url)
                if domains is not None:
                    if uri.netloc and uri.netloc in domains:
                        urls.append(url)
                else:
                    urls.append(url)
        return urls
    
    def utcnow(self):
        return datetime.datetime.utcnow()
    
    def fromtimestamp(self):
        return datetime.datetime.fromtimestamp(float(self.data)) - datetime.timedelta(hours=8)
    
if __name__ == "__main__":

#    测试用例，每个用例都要测试到
#     print "测试xpath========================================"
#     num = Parser("<?xml version=\"1.0\" encoding=\"UTF-8\"?><html><data>12341234</data><time>5分钟前</time></html>").xpath(".//data/text()").int()
#     print num
#     
#     items = Parser("<data>1</data><data>2</data>").xpathall(".//data/text()")
#     for item in items:
#         print item.int()
#         
#     print "测试regex========================================="
#         
#     num = Parser("123412341324abcd").regex("([12]+)").int()
#     print num
#     
#     for item in Parser("123412341324abcd").regexall("([12]+)"):
#         print item.int()
#         
#     print "测试连贯操作=========================================="
#     num = Parser("<data>1234.1234abc</data>").xpath("//data/text()").regex("([\d\.]+)").float()
#     print num
#     
#     print "测试时间===================================================="
    print Parser("10秒前").datetime()
    print Parser("08-18 13:00").datetime()
    print Parser("14-08-18 13:00:12").datetime()
    print Parser("2天前").datetime()
#     print Parser().utcnow()
#     print "测试URL==================================================="
#     url = Parser(r"/a.html?b=3&a=4&c=1234134", "http://www.baidu.com/ab/").url()
#     print url

#     data = "<html>welcome 123 to the 456 world 789 of 110 python</html>"
#     print 'data is: ', data
#     #测试
#     reg = r"\d+"
#     res = Parser(data)
#       
#     res1 = res.replace(reg, "*", count=2)
#     print 'res1 : ', res1.str()
#     #delete操作
#     res = Parser(data)
#     print 'res2 : ', res.delete("\d+", 1).str()
#     print 'res2 : ', res.replace("\d+", '', 1).str()
#     
#     #测试错误替换
#     reg = r"\w+ (\d+"
#     res4 = res.replace(reg, "*")
#     print 4, res4.str()
#     res5 = res.delete(reg)
#     print 5, res5.str()
#     url = Parser(r"/a.html?b=3&c=1234134&a=4", "http://www.baidu.com/ab/").url()
#     print url
#     url = Parser(r"/a.html?b=3&a=4&c=1234134", "http://www.baidu.com/ab/").url()
#     print url
#     import urllib2
#     url = "http://tieba.baidu.com/f/index/forumpark?pcn=%C8%CB%CE%C4%D7%D4%C8%BB&pci=0&ct=1&rn=20&pn=1"
#     data = urllib2.urlopen(url).read().decode('gbk')
#     data = Parser(data)
#     title = data.xpath("//title/text()")
#     print 'title: ', title.str()
# #    divs = data.xpathall(".//*[@id='ba_list']/div/a/@href")
#     divs = data.xpathall(".//*[@id='ba_list']/div")
#     if divs:
#         for div in divs:
#             href = div.xpath("//a/@href").str()
#             ba_name = div.xpath("//p[@class='ba_name']/text()")
# #            href = div.str()
#             print "href is", href
#             print "ba_name is", ba_name.str()
# 
#     items = Parser("<data>1</data><data>2</data>").xpathall(".//data/text()")
#     for item in items:
#         print 'item:', item.int()

#     import requests
#     url = 'http://tieba.baidu.com/p/3070746920'
# #    url = 'http://tieba.baidu.com/f?kw=%D6%A3%D6%DD'
#     response = requests.get(url)
#     data = response.text
#     data1 = Parser(data, response=response)
#     title = data1.xpath("//title").text()
#     
#     import time
#     t1 = time.time()
#     #xpath performace analysics
#     for _ in xrange(100):
#         data1 = Parser(data, response=response)
#         title = data1.xpath("//title")
#         ba_name = data1.xpath("//title/text()").regex(".*_(.*?)_.*")
#         content = data1.xpath("//cc/div")
#         reply_count = data1.xpath("//li[@class='l_reply_num']/span[1]/text()")
    #re performace analysics
#     for _ in xrange(1000):
#         title = re.compile('''<h1 .*?>(.*?)</h1>''').findall(data)
#         ba_name = re.compile('''<title>.*?_(.*?)_.*</title>''').findall(data)
#         content = re.compile('''<div id="post_content_\d+" .*?>(.*?)</div>''').findall(data)
#         reply_count = re.compile('''3px">(\d+)</span>''', re.U|re.M).findall(data)
#         print 'title :', title[0]
#         print 'content :', content[0]
#         print 'ba_name :', ba_name[0]
#         print 'reply_count :', reply_count[0]
#    print 'cost :', time.time() - t1
    
#     data1 = data1.delete("<!--")
#     title = data1.xpath("//title/text()").regex("(.*)_.*").text()
#     print title
#     posts = data1.xpathall("//a[@class='j_th_tit']")
#     for post in posts:
#         title = post.text()
#         print title
