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
    f = open("output.txt", 'a')
    for url in urllist:
        result = (format % url)
        f.write(result)
    f.close()


pages = 10
for i in range(1, pages):
    html = getHtml("https://www.youtube.com/results?search_query=lion+king&lclk=short&filters=short&page=%s" % i)
    getUrl(html)
    i += 1