#!/usr/bin/env python
# coding:utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：spider.py
功能：该模块实现爬出抓取的基本功能；负责初始化爬虫参数值； 

代码历史：
2014-02-07：贺伟刚，创建代码框架
2014-02-26：庞  威，代码补充
'''
import gevent.lock
import gevent.event

from gevent import monkey
monkey.patch_all()

import json
import time
import urllib
import urllib2
#from datetime import datetime
import datetime
from collections import defaultdict

import log
import util
import setting
import downloader
#import htmlparser
from dedup import dedup

INIT_PROXY_FAILED = 0
INVALID_URL = 1
DOWNLOAD_FAILED = 1
PARSE_LIST_FAILED = 2
PARSE_DETAIL_FAILED = 3

class Spider(object):
    """docstring for Spider"""
    def __init__(self, proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        super(Spider, self).__init__()
        #是否使用代理
#        self.proxy_enable = getattr(cmd_arg, 'PROXY_ENABLE', None) or proxy_enable
        cmd_proxy = getattr(cmd_args, 'PROXY_ENABLE', None)
        self.proxy_enable = cmd_proxy if cmd_proxy is not None else proxy_enable
        #每个代理最多连续重复使用次数
        self.proxy_max_num =  getattr(cmd_args, 'PROXY_MAX_NUM', None) or proxy_max_num
        #
        self.timeout =  getattr(cmd_args, 'HTTP_TIMEOUT', None) or timeout
#        self.downloader = downloader.Downloader(self.proxy_enable, self.proxy_max_num, timeout=self.timeout)
        #本次采集开始时间
        self.start_time = datetime.datetime.utcnow()
        #本次采集结束时间
        self.end_time = None
        #本次采集到的数据总数
        self.total_data_num = 0
        #本次采集去重后得到的新数据条数
        self.new_data_num = 0
        #解析成功的数据数目
        self.parsed_success_num = 0
        #解析失败的数据数目
        self.parsed_failed_num = 0
        #下载失败的数据数目
        self.download_failed_num = 0
        #
        self.lock = gevent.lock.RLock()
        self.parse_list_page_finish = False
        self.job_event = gevent.event.Event()
        #错误信息列表；每一项格式为(error_code, error_info)
        #error_code: 0： 获取代理失败； 1：下载失败； 2：解析数据失败
        self.error_info = []
        self.failed_info = defaultdict(list)
        self.parse_failed = {}
        self.worker_id = ""
        self.config_id = ""
        self.config_name = ""
        self.job_id = ""
        self.last_crawl_time = None
        self.spider_id = ""
        #采集入口url
        self.start_urls = []
        self.max_interval = datetime.timedelta(days=1)
        #类别码，01=新闻,02=论坛,03=博客,0401=新浪微博,0402=腾讯微博
        self.info_flag = '02'
        self.siteName = ''
        #代理文件地址
        self.proxy_url = setting.PROXY_URL
        #去重库地址
        self.dedup_uri = setting.DEDUP_URI
        self.dedup_key = setting.DEDEUP_KEY
        #
        self.detail_page_queue = None
        #抓取数据入库地址
        self.data_db = setting.SPIDER_DATA_DB
        #日志信息入库地址
        self.log_db = setting.SPIDER_LOG_DB
        self.request_headers = {}
        #调试模式标志位
        self.debug = getattr(cmd_args, 'debug', False)
        if self.debug:
            print "spider: proxy_enable:", self.proxy_enable
            print "spider: proxy_max_num:", self.proxy_max_num
            print "spider: timeout:", self.timeout
            print "spider: data_db:", self.data_db
            print "spider: log_db:", self.log_db
            #print "spider: dedup_uri:", self.dedup_uri
            #print "spider: dedup_key:", self.dedup_key
#        self.init_dedup()
#        self.init_downloader()

    def init_downloader(self):
        """
        初始化downloader
        """
        self.downloader = downloader.Downloader(self.proxy_enable, 
                                                self.proxy_max_num, 
                                                proxy_url=self.proxy_url,
                                                timeout=self.timeout)

    def init_dedup(self):
        """
        初始化去重库
        """
        if self.dedup_uri is not None and self.dedup_key is not None:
            try:
                self.urldedup = dedup.Dedup(self.dedup_uri, self.dedup_key)
            except Exception, e:
                log.logger.error("init dedup failed: %s; dedup: %s"%(e, self.dedup_uri))
        else:
            self.urldedup = None
    
    def increase_total_data_num(self):
        """
        设置采集总数
        """
        self.lock.acquire()
        self.total_data_num += 1
        self.lock.release()
    
    def increase_new_data_num(self):
        """
        设置新数据总数
        """
        self.lock.acquire()
        self.new_data_num += 1
        self.lock.release()
    
    def increase_parsed_success_num(self):
        """
        解析成功数目加1
        """
        self.lock.acquire()
        self.parsed_success_num += 1
        self.lock.release()
    
    def increase_parsed_failed_num(self):
        """
        解析失败数目加1
        """
        self.lock.acquire()
        self.parsed_failed_num += 1
        self.lock.release()
    
    def increase_download_failed_num(self):
        """
        下载失败数目加1
        """
        self.lock.acquire()
        self.download_failed_num += 1
        self.lock.release()
    
    def set(self):
        """
        设置列表页解析已完成标志位为True
        """
        self.parse_list_page_finish = True
    
    def is_set(self):
        """
        列表页解析工作是否已结束
        """
        return self.parse_list_page_finish
    
    def set_config_id(self, config_id):
        self.config_id = config_id

    def set_worker_id(self, worker_id):
        self.worker_id = worker_id
    
    def set_job_id(self, job_id):
        self.job_id = job_id

    def set_data_queue(self, queue):
        self.crawler_data_queue = queue

    def set_detail_page_queue(self, queue):
        self.detail_page_queue = queue

    def set_spider_id(self, spider_id):
        self.spider_id = spider_id

    def set_config_name(self, config_name):
        self.config_name = config_name

    def get_start_urls(self, data=None):
        '''
        返回start_urls
        '''
        return self.start_urls

    def send_update_cmd(self, data=None):
        """
        抓取结束后更新数据库
        """
        pass

    def send_cmd_to(self, url, post_data):
        """
                抓取结束后更新数据库
        """
        if not url:
            return []
#        print "--- url is: ", url
#        print " --- post_data is:", post_data
        try:
            j_data = json.dumps(post_data)
        except Exception, e:
            j_data = '{}'
            log.logger.error("post_data is %s; exception: %s"%(str(post_data),e))
        p_data = {"data":j_data}
        e_data = urllib.urlencode(p_data)

        try:
            response = urllib2.urlopen(url, e_data, timeout=15).read()
        except Exception, e:
            log.logger.info("send_cmd_to(): url:%s, Exception:%s"%(url, e))
            return []
        if not response:
            return []
#        print "--reponse--,",response
        try:
            data = json.loads(response)
        except Exception, e:
            log.logger.info("send_cmd_to.json.load(): excepiton: %s; url:%s"%(e,url))
            return []
        return data

    def request_callback(self, request):
        '''
         需要处理特殊的request，例如header
        '''
        return request

    def download(self, url, **kwargs):
        '''
        '''
        #kwargs = self.request_headers
        kwargs.update(self.request_headers)
        
        response = None
        if isinstance(url, basestring):
            newurl_lower = url.lower().strip()
            if (newurl_lower.startswith('http://') or
                    newurl_lower.startswith('https://') or
                    newurl_lower.startswith('ftp://')):
                response = self.downloader.download(url, **kwargs)
            else:
                log.logger.info("-- config_id:%s ; url not start with http/https/ftp: %s"%(self.config_id, url))
        return response

    def check_url_list(self, url_list, url):
        """
        判断参数url_list是否为空，如果为空，记为列表页解析错误;
        参数url表示当前页地址；url_list是从url网页中解析出来的结果；
        """
        if not url_list:
            pass
            #self.error_info.append((PARSE_LIST_FAILED, 'PARSE_LIST_FAILED: no item in page:%s'%url))

    def spider_finished(self):
        '''
        判断本次抓取所有工作是否结束；如果是，发送本次爬取结果统计信息；
        '''
        """
        判断本次抓取所有工作是否结束；如果是，发送本次爬取结果统计信息；
        """
        if self.parse_list_page_finish:
            self.lock.acquire()
            if self.new_data_num == (self.parsed_success_num + 
                                     self.parsed_failed_num + 
                                     self.download_failed_num ):
                #
                if self.new_data_num > self.download_failed_num:
                    for key, value in self.parse_failed.iteritems():
                        if value:
                            self.error_info.append((PARSE_DETAIL_FAILED, "PARSE_DETAIL_FAILED; parse %s failed; "%key))
                            for err in self.failed_info[key]:
                                self.error_info.append((PARSE_DETAIL_FAILED, err))
                #
                response = {'start_time':time.mktime(self.start_time.timetuple()), 
                            'end_time':time.mktime(datetime.datetime.utcnow().timetuple()),
                            'total_data_num': self.total_data_num,
                            'new_count': self.new_data_num,
                            'parse_success_num': self.parsed_success_num,
                            'parse_failed_num': self.parsed_failed_num,
                            'download_failed_num': self.download_failed_num,
                            'spider_id': self.spider_id,
                            'worker_id': self.worker_id,
                            'config_id': self.config_id,
                            'config_name':self.config_name,
                            'job_id': self.job_id,
                            }
                #
                util.save_log(self.log_db, str(self.config_id), response)
                
                #打印爬虫日志信息
                if self.debug:
                    for k, v in response.iteritems():
                        print "%s : %s"%(k, v)
                #
                url = getattr(setting, "SEND_CRAWL_RESULT_TO", "")
                if self.error_info and url:
                    error_response = {
                                      'spider_id':self.spider_id,
                                      'config_id':self.config_id,
                                      'config_name':self.config_name,
                                      'error_info':self.error_info
                                      }
                    j_data = json.dumps(error_response)
                    data = {"crawl_result": j_data}
                    e_data = urllib.urlencode(data)
                    try:
                        urllib2.urlopen(url, e_data, timeout=15)
                    except Exception, e:
                        log.logger.info("send crawl result to %s failed: %s"%(url,e))
                #
                self.job_event.set()
            #    
            self.lock.release()
            return True
        return False


    def parse_detail_by_url(self, url=None):
        '''
        参数url指向一个详情页，下载并分析该页面详情；并统计分析结果；
        返回值为一个二元元组；第一个值表示所有详情页是否下载解析完毕，第二个值表示是否有下一页要抓取；
        '''
        next_urls = []
        if not url:
            return False, next_urls
        
        result = {}
        parse_success = True
        
        response = self.download(url)
        try:
            result = self.parse_detail_page(response, url)
        except Exception, e:
            parse_success = False
        #下载网页失败
        if result is None:
            self.increase_download_failed_num()
#            self.error_info.append((DOWNLOAD_FAILED, "DOWNLOAD_FAILED; url:%s"%url))
            log.logger.info("DOWNLOAD_FAILED; url:%s"%url)
            res = self.spider_finished()
            return res, next_urls
        
        if not result:
            parse_success = False
        else:
            if isinstance(result, dict):
                for key, value in result.items():
                    if not value:
                        parse_success = False
#                        self.error_info.append((PARSE_DETAIL_FAILED, "PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(key, url)))
                        log.logger.info("PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(key, url))
                        #字段解析失败监测；当字段解析失败时，将其存入parse_failed，key为字段名;
                        if self.parse_failed.get(key, True):
                            self.parse_failed[key] = True
                            self.failed_info[key].append("%s : %s"%(key, url))
                    else:
                        #解析成功，将该字段对应的值设为False
                        self.parse_failed[key] = False
            elif isinstance(result, list):
                for item in result:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if not value:
                                parse_success = False
#                                self.error_info.append((PARSE_DETAIL_FAILED, "PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(key, url)))
                                log.logger.info("PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(key, url))
                                if self.parse_failed.get(key, True):
                                    self.parse_failed[key] = True
                                    self.failed_info[key].append("%s : %s"%(key, url))
                            else:
                                self.parse_failed[key] = False
        if parse_success:
            self.increase_parsed_success_num()
        else:
            self.increase_parsed_failed_num()
        #save data to db by data_queue
        res = {'url':url, 'config_id':self.config_id, 
               'info_flag':self.info_flag, 'siteName':self.siteName,
               'data_db':self.data_db, 'spider_id':getattr(setting, 'SPIDER_IP', self.spider_id)}
        #标题解析成功时将该数据入库，否则丢弃;
        if isinstance(result, dict):
            #获取下一页url
            next_urls = result.pop('next_urls', [])
            #更新返回信息
            if result.get('title', ''):
                res.update(result)
                self.crawler_data_queue.put(res)
                #
                if self.debug or getattr(setting, 'SHOW_DATA', False):
                    print util.B('\n {}'.format('###########################'))
                    for k, v in res.iteritems():
                        print '{:>10.10} : {}'.format(k,v)
        elif isinstance(result, list):
            new_result = []
            for item in result:
                if isinstance(item, dict):
                    next_urls = item.pop('next_urls', [])
                    if item.get('title', ''):
                        res1 = res.copy()
                        res1.update(item)
                        new_result.append(res1)
                        #
                        if self.debug or getattr(setting, 'SHOW_DATA', False):
                            print util.B('\n {}'.format('###########################'))
                            for k, v in res1.iteritems():
                                print '{:>10.10} : {}'.format(k,v)
            if new_result:
                self.crawler_data_queue.put(new_result)
        #
        for url in next_urls:
            self.increase_new_data_num()
        #
        res = self.spider_finished()
        #
        return res, next_urls


if __name__ == "__main__":
    error_response = {
                      'spider_id':'12',
                      'config_id':'34',
                      'config_name':'test',
                      'error_info':[(3, 'error1'), (3, '234')]
                      }
    j_data = json.dumps(error_response)
    data = {"crawl_result": j_data}
    e_data = urllib.urlencode(data)
    url = "http://192.168.110.24/task.php"
    try:
        resp = urllib2.urlopen(url, e_data, timeout=15)
    except Exception, e:
        log.logger.info("send crawl result to %s failed: %s"%(url,e))
        print "failed"
    else:
        print resp.read()
        print "ok"
