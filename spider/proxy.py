#!/usr/bin/env python
# coding:utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved

'''
文件名：proxy.py
功能：获取可用http代理

代码历史：
2014-02-26：庞 威  代码编写
'''
import re
import os
import time
import random
import urllib2
import requests

import redis

#import db
import log
import setting
import htmlparser

#duanyifei add begin on 2016-03-21
cur_path = os.path.dirname(__file__)
proxy_dir = os.path.join(cur_path, "proxy")
if not os.path.exists(proxy_dir):
    os.mkdir(proxy_dir)
#duanyifei add end on 2016-03-21

def get_proxy_ip(count):
    '''
    功能：获取代理IP
    '''
    conn, cursor = db.GetMysqlCursor("proxy")
    
    cursor.execute("select ip, port from proxy_server where status=1 and ping<0.1 order by rand() limit %d"%count)
    
    result_tuple = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return [ (ip, port) for ip, port in result_tuple]


#duanyifei add begin on 2016-03-21
def get_proxy(url=None):
    '''
    从目标url获取代理信息;
    默认代理文件为 http://192.168.84.4/proxy.txt
    默认count代表取出代理数目,暂未使用
    '''
    url = url or getattr(setting, "PROXY_URL", "http://192.168.84.4/proxy.txt")

    update_interval = getattr(setting, "PROXY_UPDATE_INTERVAL", 300)
    
    if url.startswith('redis://'):
        proxies = get_proxy_from_redis(url)
    elif url.startswith('http://'):
        file_name = os.path.join(cur_path, 'proxy', url.split("/")[-1])
        if not os.path.exists(file_name):
            #文件不存在更新
            update_proxy_file(url, file_name)
        elif time.time() - os.stat(file_name).st_mtime > update_interval:
            #文件过期更新
            update_proxy_file(url, file_name)
        else:
            pass
        with open(file_name, 'r') as f:
            proxies = f.readlines()
    return [ item.split() for item in proxies]

def update_proxy_file(proxy_url, file_name):
    try:
        response = urllib2.urlopen(proxy_url)
    except Exception,e:
        log.logger.error("proxy.py: get_proxy(url=%s), %s"%(proxy_url, e))
        return False
    with open(file_name, 'w') as f:
        f.write(response.read())
    log.logger.debug("update proxy file  %s successful"%file_name)
    return True
#duanyifei add end on 2016-03-21


def get_anoymous_proxy_from_website():
    url_fmt = "http://www.xici.net.co/nn/%s"
    
    re_ip_post = re.compile('''<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>''')
    re_scheme = re.compile('''<td>(http|https)</td>''', re.I)
    proxies = set()
    
    db = redis.StrictRedis.from_url("redis://192.168.100.15/3")
    
    for page_no in xrange(1,5):
        url = url_fmt%page_no
        resp = requests.get(url)
        html_body = resp.content
        
        pos = 0
        while 1:
            m = re_ip_post.search(html_body, pos)
            if m:
                ip = m.group(1)
                port = m.group(2)
                pos = m.end()
                #print "%s : %s"%(ip, port)
            else:
                print "finshed"
                break
            m = re_scheme.search(html_body, pos)
            if m:
                scheme = m.group(1)
                #print pro
                pos = m.end()
            proxy = "%s    %s  %s"%(scheme, ip, port)
            proxies.add(proxy)
            print proxy
    
    pipe = db.pipeline()
    for proxy in proxies:
        pipe.sadd('high_anonymous_proxy', proxy)
    try:
        db.delete('high_anonymous_proxy')
        pipe.execute()
    except Exception, e:
        print e
    
    return proxies

def get_proxy_from_redis(redis_db):
    db = redis.StrictRedis.from_url(redis_db)
    proxies = []
    try:
        proxies = db.smembers('high_anonymous_proxy')
    except Exception, e:
        print e
    return proxies
    
if __name__ == "__main__":
    proxies = get_proxy('http://192.168.84.4/proxy_100ms.txt')
#     proxies = get_proxy('redis://192.168.100.15/3')
    for item in proxies:
        print item
#     print "len:", len(proxies)
# #
#     proxies = get_anoymous_proxy_from_website()
#     print "len(proxies): ", len(proxies)

#     proxies = get_high_anonymous_proxy()
#     for item in proxies:
#         print item
#     print "len:", len(proxies)
