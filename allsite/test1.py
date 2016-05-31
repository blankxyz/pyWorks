# coding:utf-8

import time
import urllib2
import urlparse

from bs4 import BeautifulSoup

#url = "http://freebuf.com/"
#domain = "freebuf.com"
url="http://www.sohu.com"
domain="sohu.com"
deep = 0
tmp = ""
sites = set()
visited = set()


# local = set()
def get_local_pages(url, domain):
    global deep
    global sites
    global tmp
    repeat_time = 0
    urls = set()

    # 防止url读取卡住
    while True:
        try:
            time.sleep(1)
            resp = urllib2.urlopen(url=url, timeout=3)
            break
        except:
            print "error@urlopen"
            time.sleep(1)
            repeat_time = repeat_time + 1
            if repeat_time == 5:
                return

    soup = BeautifulSoup(resp.read())
    tags = soup.findAll(name='a')
    for tag in tags:
        try:
            href = tag['href']
        except:
            print "error@tag['href']"
            continue
        print '1)parse tag[\'href\']:', href
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(href)
        print '2)urlparse:', (scheme, netloc, path, params, query, fragment)
        # 处理相对路径url
        if scheme is "" and netloc is "":
            print u'[start]处理相对路径'
            url_obj = urlparse.urlparse(resp.geturl())
            href = url_obj['scheme'] + "://" + url_obj['netloc'] + url_obj['path'] + href
            # 保持url的干净
            href = href[:8] + href[8:].replace('//', '/')
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(href)
            # 这里不是太完善，但是可以应付一般情况
            if '../' in path:
                paths = path.split('/')
                for i in range(len(paths)):
                    if paths[i] == '..':
                        paths[i] = ''
                        if paths[i - 1]:
                            paths[i - 1] = ''
                    tmp_path = ''
                    for p in paths:
                        if p == '':
                            continue
                        tmp_path = tmp_path + '/' + p
                    href = href.replace(p, tmp_path)
            print u"[end]处理相对路径" + href

        if 'http' not in scheme:
            print "[error] Bad href：" , href.encode('ascii')
            print format('-' * 60)
            continue

        if scheme is "" and netloc is not "":
            print "[error] Bad href: " , href
            print format('-' * 60)
            continue

        if domain not in netloc:
            print "[error] Bad href: " , href
            print format('-' * 60)
            continue

        new_url = href
        if new_url not in sites:
            print "3)the new_url is: " , new_url
            print format('-'*60)
            urls.add(new_url)

    return urls  # dfs算法遍历全站


def dfs(urls):
    # 无法获取新的url说明遍历完成，即可结束dfs
    if urls is set():
        return

    global url
    global domain
    global sites
    global visited
    sites = set.union(sites, urls)
    for url in urls:
        if url not in visited:
            print "Visiting", url
            visited.add(url)
            pages = get_local_pages(url, domain)
            dfs(pages)
    print "success"


if __name__ == '__main__':
    pages = get_local_pages(url, domain)
    # dfs(pages)
    for i in sites:
        print i
