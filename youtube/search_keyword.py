# coding:utf-8

import re
import urllib


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html


def getUrl(html):
    reg = r"(?<=a\shref=\"/watch).+?(?=\")"
    urlre = re.compile(reg)
    urllist = re.findall(urlre, html)
    format = "https://www.youtube.com/watch%s\n"
    f = open("search_keyword.txt", 'a')
    for url in urllist:
        result = (format % url)
        f.write(result)
    f.close()


pages = 2
for i in range(1, pages):
    #china+beijing&lclk=short&filters=short
    print i
    html = getHtml("https://www.youtube.com/results?search_query=china+beijing&page=%s" % i)
    getUrl(html)
    i += 1