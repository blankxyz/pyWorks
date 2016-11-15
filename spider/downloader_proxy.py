#!/usr/bin/env python
# coding:utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：downloader.py
功能：该模块实现网页下载； 
　　　目前实现的功能有：
　　　　　随机切换代理
      支持　content-encoding：　gzip　deflate
      retry
      redirect
代码历史：
2014-02-27：庞  威，代码创建
'''

import time
import copy
import random
import logging

import requests

import log
import proxy
import setting
import util

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.ERROR)

class Downloader(object):
    '''下载器'''
    def __init__(self, proxy_enable=setting.PROXY_ENABLE, 
                 proxy_max_num=setting.PROXY_MAX_NUM, 
                 available_proxy=setting.PROXY_AVAILABLE,
                 proxy_url=setting.PROXY_URL,
                 cookie_enable=setting.COOKIE_ENABLE, 
                 timeout=setting.HTTP_TIMEOUT):
        super(Downloader, self).__init__()
        self.cookie_enable = cookie_enable
        self.proxy_enable = proxy_enable
        User_Agent = setting.USER_AGENT
        self.headers = {"Accept":"text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
                        "User-Agent":User_Agent,
                        }
        if self.proxy_enable:
            self.proxy_manager = ProxyManager(proxy_max_num, available_proxy, proxy_url)
        if timeout > 120 or timeout <= 0:
            self.timeout = 30
        else:
            self.timeout = timeout
        #
        self.session = requests.Session()
        a = requests.adapters.HTTPAdapter(pool_connections=available_proxy,
                                          pool_maxsize=proxy_max_num,
                                          max_retries=0)
        self.session.mount('http://', a)

    def init_proxy_success(self):
        """
        返回初始化代理结果，成功返回True,失败返回False;
        """
        if self.proxy_enable:
            if self.proxy_manager.proxy_queue.qsize() > 0:
                return True
        return False
    
    @retry(Exception)
    def _download(self, request, **kwargs):
        request = copy.deepcopy(request)
        url = request.get('url') if isinstance(request, dict) else request
        response = None
#        print  "downloading ...", url
        if self.proxy_enable:
            #proxy_type, proxy_host = self.proxy_manager.get_proxy()
            proxy_item = self.proxy_manager.get_proxy()
            proxy_type, proxy_host = proxy_item.get_proxy()
            if proxy_host is not None:
                proxy = "%s://%s"%(proxy_type, proxy_host)
                proxies = {proxy_type: proxy}
            else:
                proxies = None
        else:
            proxies = None

        try:
            timeout = gevent.Timeout(self.timeout+1)
            timeout.start()
            try:
                if 'proxies' not in kwargs:
                    kwargs.update(proxies=proxies)

                kwargs.update({
                    'stream':True,
                    'timeout':self.timeout,
                    })

                default_method = 'POST' if 'data' in kwargs else 'GET'

                keep_status_code = 0

                if isinstance(request, dict):
                    try:
                        if request.get('meta', {}).get('keep_status_code', False):
                            keep_status_code = 1
                    except:
                        pass
                    method = request.get('method')
                    default_method = method if method is not None else default_method
                    for key in ('url', 'meta', 'method', 'func_name'):
                        if key in request:
                            request.pop(key)
                    kwargs.update(request)

                r = self.session.request(default_method, url, **kwargs)

                if r.status_code not in (200, 404, 410):
                    log.logger.warning(u"调试信息 下载返回码 %s  请注意"%util.BB(r.status_code))
                    if not keep_status_code:
                        r.raise_for_status()
                elif r.status_code in (404, 410):
                    log.logger.warning(u"调试信息 下载返回码 %s  请注意"%util.BB(r.status_code))
                
                #
                response = r
                response.content
                #保存当前代理
                if self.proxy_enable:
                    self.proxy_manager.put_proxy(proxy_item)
                try:
                    response.proxies = kwargs.get('proxies')
                except Exception as e:
                    log.logger.error(u"response对象增加代理属性失败 %s"%e)
            except requests.exceptions.Timeout, e:
                raise e
            except requests.exceptions.RequestException as e:
                raise e
            except Exception as e:
                raise e
            else:
                r.close()
        except gevent.Timeout, e:
            #print "--**-- gevent.Timeout"
            raise requests.exceptions.Timeout
        except requests.exceptions.RequestException as e:
            #print "--**-- RequestException", e
            raise e
        except Exception as e:
            raise e
        finally:
            timeout.cancel()
        
        return response

    def download(self, request, **kwargs):
        headers = kwargs.get('headers',{})
        self.headers.update(headers)
        kwargs.update(headers=self.headers)
        response = None
        try:
            response = self._download(request, **kwargs)
        except gevent.Timeout, e:
            #log.logger.debug("gevent.Timeout: %s : %s"%(url, str(e)))
            #print 'gevent.Timeout: ', str(e)
            pass
        except requests.exceptions.Timeout, e:
            #log.logger.debug(" requests.Timeout: %s : %s;"%(str(e), url))
            #print 'requests.Timeout', str(e)
            pass
        except requests.exceptions.RequestException as e:
            #log.logger.debug("requests.RequestException: %s : %s"%(e, url))
            #print 'RequestException', str(e)
            pass
        except Exception as e:
            #log.logger.debug("download %s failed; reason: %s"%(url, e))
            #print 'Exception: ', str(e)
            pass
        #print len(response)
        return response


if __name__ == '__main__':
#     item = ProxyItem('http', '192.168.1.1:80', 2)
#     print item.is_valid()
#     print item.get_proxy()
#     
#     print item.is_valid()
#     print item.get_proxy()
#     
#     print item.is_valid()
#     print item.get_proxy()
#     pm = ProxyManager(2,2)
#     
#     p = pm.get_proxy()
#     print p.get_proxy()
#      
#     proxy_item = ProxyItem('http', '112.84.130.13:80', 2)
#     pm.put_proxy(proxy_item)
# 
#     proxy_item = ProxyItem('http', '112.84.130.13:80', 2)
#     pm.put_proxy(proxy_item)
#     p = pm.get_proxy()
#     print p.get_proxy()
#     
#     p = pm.get_proxy()
#     print p.get_proxy()
#     
#     p = pm.get_proxy()
#     print p.get_proxy()
#     
#     p = pm.get_proxy()
#     print p.get_proxy()
    
#     urls = ["http://tieba.baidu.com/p/2650465863", 'http://tieba.baidu.com/p/2245454220', 'http://tieba.baidu.com/p/3022141148']*2
#     d = Downloader(True, 3,3, timeout=2)
#     
#     from gevent import pool
#     pool = pool.Pool(6)
#     t1 = time.time()
#     for url in urls:
#         pool.spawn(d.download, url)
#     pool.join()
#     print "gevent.pool: ", time.time() - t1
    
#     t1 = time.time()
#     jobs = [gevent.spawn(d.download, url) for url in urls]
#     gevent.joinall(jobs)
#     print "gevent.spawn: ", time.time() - t1

#     from gevent import threadpool
#     t1 = time.time()
#     pool = threadpool.ThreadPool(6)
#     for url in urls:
#         pool.spawn(d.download, url)
#     pool.join()
#     print "thread: ", time.time() - t1
#    url = 'http://bbs.jztele.com/thread-3575106123-1-1.html'
    url = 'http://bbs.tianya.cn'
#     header = {'Accept':'*/*',
#               'User-Agent':'python-requests/2.2.1 CPython/2.7.6 Windows/7'}
    d = Downloader(False,  timeout=20)
    response = d.download(url)
    print type(response.status_code)
    print response.status_code
    # print response.text
#     print response.request.headers
    
#     import requests
#     headers = {"Accept":"text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8",
#     "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0",
#     "Referer":"http://www.0595bbs.cn/forum-61-1.html?order=createdat",
#     "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3"
#     }
#     proxies = {'http':'http://111.206.81.248:80'}
#     response = requests.get(url, headers=headers)
# #    response = requests.get(url)
#     
#     print response.text
# #     print response.request.headers
# #     print response.request.url
#     print response.url
