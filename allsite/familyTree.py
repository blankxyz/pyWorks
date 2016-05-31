# -*- coding: utf-8 -*-
import re
import urllib2
import urlparse

g_family_list = []
domain = "sina.com.cn"
homepage = "http://www.sina.com.cn/"
detailPageSuffixes = ['html', 'shtml', '...']

def getTagsOnlyPage(url):
    resp = urllib2.urlopen(url).read().decode('gbk').encode('utf-8')
    # resp = 'a classcheckBtn hrefjavascriptvoid>'
    print resp
    filter = re.sub(r'\<a([\d\w\W]*?)\>', '', resp, re.M|re.U)
    print filter
# 找到详情页由上而下倒推父节点
# http://ka.sina.com.cn/index/mmo/0-0-0-17-0-0-0/2 url
# http://ka.sina.com.cn/index/mmo/0-0-0-17-0-0-0/  同上
# http://ka.sina.com.cn/index/mmo/  同上
# http://ka.sina.com.cn/index/ 父节点
def addFamilyTree(detailUrl):
    regUrl = ''
    regStr = ''
    p_urls = detailUrl.spilt("\/")
    # todo urls结果为comment
    for url in p_urls:
        ret = urllib2.urlopen(url)
        if ret.status == '200':
            cnt = 0
            preLink = ''
            links = getLinksWithoutFamilyList(url)
            for link in links:
                if isSameParent(link, preLink):
                    cnt = cnt + 1
                if cnt >= 3:  # same page count more then 3page
                    regStr = "[\d][\w\W]"  # todo
                    regUrl = url + regStr
                    break
                else:
                    regUrl = url
                    preLink = link

            g_family_list.append(regUrl)
    return


def filterUrlsBySameParent(urls, parentUrl):
    parent = ''
    return parent


def findChilds(parentUrl):
    urls = getLinksWithoutFamilyList(parentUrl)
    # urls = filterUrlsBySameParent(urls, parentUrl)
    for url in urls:
        if isListPage(url):
            findChilds(url)
        else:
            addFamilyTree(url)
    return


def isSameParent(urlone, urltwo):
    if not isListPage(urlone):
        return False
    else:
        # todo page is similarity
        return True


def isListPage(url):

    return True


def getLinksWithoutFamilyList(url):
    links = []
    for link in links:
        if domain in urlparse.urlparse(url).netloc and url not in g_family_list:  # todo
            links.append(url)
    return links


def homeStart():
    findChilds(homepage)
    return



if __name__ == '__main__':
    url = 'http://data.house.sina.com.cn/mc/'
    # homeStart()
    getTagsOnlyPage(url)
