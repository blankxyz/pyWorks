# coding:utf-8
import urllib
from bs4 import BeautifulSoup
import re


def get_all_url(url):
    urls = []
    web = urllib.urlopen(url)


    soup = BeautifulSoup(web.read())
    tags_a = soup.findAll(name='a', attrs={'href': re.compile("^https?://")})
    try:
        for tag_a in tags_a:
            urls.append(tag_a['href'])
            # return urls
    except:
        pass
    return urls

def get_local_urls(url):
    local_urls = []
    urls = get_all_url(url)
    for _url in urls:
        ret = _url
        if 'freebuf.com' in ret.replace('//', '').split('/')[0]:
            local_urls.append(_url)
    return local_urls


def get_remote_urls(url):
    remote_urls = []
    urls = get_all_url(url)
    for _url in urls:
        ret = _url
        if "freebuf.com" not in ret.replace('//', '').split('/')[0]:
            remote_urls.append(_url)
    return remote_urls


def __main__():
    url = 'http://freebuf.com/'
    rurls = get_remote_urls(url)
    print "--------------------remote urls-----------------------"
    f=open('get_remote_urls.log','w')
    for ret in rurls:
        print ret
#        f.write(ret)
    f.close()

    print "---------------------localurls-----------------------"
    urls = get_local_urls(url)
    f = open('get_local_urls.log', 'w')
    for ret in urls:
        print ret
 #       f.write(ret)
    f.close()

if __name__ == '__main__':
    __main__()
