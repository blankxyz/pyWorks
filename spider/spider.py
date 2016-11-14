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
import copy
import urllib
import urllib2
import traceback
#from datetime import datetime
import datetime
import pprint
from collections import defaultdict

import log
import util
import setting
import downloader
#import htmlparser
from dedup import dedup

import myreadability

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

        #duanyifei add begin on 2016-05-27
        #数据总数不为0标志
        self.has_total_data = 0
        #详情页解析数据记录
        self.detail_page_record_list = []
        #函数执行异常记录
        self.exceptions_info_list = []
        #类型检查失败信息记录
        self.field_type_failed_record = []
        #url格式错误信息记录
        self.url_format_error_record = defaultdict(list)
        #字段类型预定义
        self.field_type_dic = self.get_field_type()
        #配置监测数据入库地址
        self.config_monitor_data_db = setting.CONFIG_MONITOR_DATA_DB
        #配置监测开关
        self.config_monitor = setting.CONFIG_MONITOR
        #duanyifei add end on 2016-05-27



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
            except Exception as e:
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
        except Exception as e:
            j_data = '{}'
            log.logger.error("post_data is %s; exception: %s"%(str(post_data),e))
        p_data = {"data":j_data}
        e_data = urllib.urlencode(p_data)

        try:
            response = urllib2.urlopen(url, e_data, timeout=15).read()
        except Exception as e:
            log.logger.info("send_cmd_to(): url:%s, Exception:%s"%(url, e))
            return []
        if not response:
            return []
#        print "--reponse--,",response
        try:
            data = json.loads(response)
        except Exception as e:
            log.logger.info("send_cmd_to.json.load(): exception: %s; url:%s"%(e,url))
            return []
        return data

    def request_callback(self, request):
        '''
         需要处理特殊的request，例如header
        '''
        return request

    def download(self, request, func_name=None, **kwargs):
        '''
        '''
        kwargs.update(self.request_headers)
        
        response = None

        url = request.get('url') if isinstance(request, dict) else request

        if isinstance(url, basestring):
            newurl_lower = url.lower().strip()
            if (newurl_lower.startswith('http://') or
                    newurl_lower.startswith('https://') or
                    newurl_lower.startswith('ftp://')):
                response = self.downloader.download(request, **kwargs)
            else:
                log.logger.info("-- config_id:%s ; url not start with http/https/ftp: %s"%(self.config_id, url))
                self.url_format_error_record[func_name].append(url)
        else:
            log.logger.error("-- config_id:%s ; url not instance of basestring or dict: %s"%(self.config_id, url))
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
                
                
                # duanyifei begin 2016-5-23
                # 错误严重级别代码
                # 默认最低  0
                default_level = '0'
                # 一般  1
                general_level = '1'
                # 肯定  2
                serious_level = '2'

                # 错误分类 error_reason
                # 1. 字段解析失败比例高
                # 2. 连续下载失败
                # 3. 总数连续为0
                # 4. 详情页异常
                # 5. 返回值字段检查失败
                # 6. url格式错误

                error_level = default_level
                error_reason = defaultdict(dict)
                # 指定监控或者debug模式下 收集配置运行信息
                if self.config_monitor or self.debug:

                    # 字段解析失败比例处理
                    for k,v in self.failed_info.iteritems():
                        num = len(v)
                        per = num * 1.0 / self.new_data_num
                        if per > 0.8 and self.new_data_num > 10:
                            error_level = serious_level
                            error_reason['1'].update({k:"{}/{}/{}".format(num, self.new_data_num, self.total_data_num)})
                    # 总数连续为0 增加总数不为0标志判断
                    if self.total_data_num == 0 and not self.has_total_data:
                        error_level = general_level
                        error_reason['3'].update({"total_data_num":self.total_data_num})
                    # 连续下载失败
                    elif self.download_failed_num == self.new_data_num and self.new_data_num > 5:
                        error_level = general_level
                        error_reason['2'].update({"download_failed_num":self.download_failed_num,
                                                "new_data_num":self.new_data_num
                                                })
                    #异常处理
                    if self.exceptions_info_list:
                        error_level = serious_level
                        exc_urls = defaultdict(list)
                        exc_format = {}
                        for exc_dic in self.exceptions_info_list:
                            e_name = exc_dic['e_name']
                            url = exc_dic['url']
                            if url:
                                exc_urls[e_name].append(url)
                            format_exc = exc_dic['detail']
                            exc_format[e_name] = format_exc

                        for e_name, format_exc in exc_format.iteritems():
                            error_reason['4'].update({
                                e_name:{
                                    'urls':exc_urls.get(e_name, []),
                                    'exc_info':format_exc,
                                }
                                })

                    # 字段类型检查失败
                    if self.field_type_failed_record:
                        error_level = serious_level
                        for idx,err in enumerate(self.field_type_failed_record):
                            error_reason['5'].update({str(idx):err})

                    # url格式错误处理
                    if self.url_format_error_record:
                        error_level = serious_level
                        error_reason['6'].update(self.url_format_error_record)
                    # duanyifei end 2016-5-23
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
                            'siteName':self.siteName,
                            'job_id': self.job_id,
                            #duanyifei 2016-5-23
                            'detail_page_record_list':self.detail_page_record_list,
                            'error_level':error_level,
                            'error_reason':dict(error_reason),
                            #duanyifei 2016-5-23
                            }
                #
                util.save_log(self.log_db, str(self.config_id), response)
                #保存监控信息到mongodb  指定监控并且非debug模式生效
                if self.config_monitor and not self.debug:
                    util.save_monitor_log(self.config_monitor_data_db, response)
                    log.logger.info(u"config_runing_info is saved !!!")

                #打印爬虫日志信息
                if self.debug:
                    for k,v in response.iteritems():
                        if isinstance(v, (basestring, int, float)):
                            print "%s : %s"%(k, v)
                        else:
                            if k in ('detail_page_record_list', ):
                                limits = 10
                                print "%s :" % ( k ), u"总数 {} 最大显示条数 {}".format(len(v), limits)
                                v = v[:limits]
                                print " %s" % ( pprint.pformat(v) )
                            else:
                                print "%s : \n %s"%(k, pprint.pformat(v))

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
                    except Exception as e:
                        log.logger.info("send crawl result to %s failed: %s"%(url,e))
                #
                self.job_event.set()
            #    
            self.lock.release()
            return True
        return False

    # duanyifei 2016-5-23
    def save_parse_detail_info(self, result):
        '''
        参数result为解析页面返回值
        此函数作用为记录页面返回值解析错误的字段

        错误定义:
            字符串字段返回值为空
            visitCount, replyCount 返回值为-1
            ctime和gtime相差 1s 内

        '''
        if not result:
            return True
        result = copy.deepcopy(result)
        if not isinstance(result, list):
            log.logger.error('parse_detail_page() error: return value is not list or dict')
            return True
        new_result = []
        g_c = datetime.timedelta(seconds=1)
        for post in result:
            if not post:
                continue
            url = post.get('url')

            dic = {'url':url}

            ctime, gtime = post.get('ctime'), post.get('gtime')
            # duanyifei 2016/10/26 add  判断 ctime 是否存在
            if not ctime or ctime.microsecond != 0:
                dic.update({'ctime':str(ctime)})
                self.failed_info['ctime'].append("%s : %s"%('ctime', url))

            for k,v in post.iteritems():
                error_flag = 0
                k = str(k)
                if k == 'url':
                    pass
                elif isinstance(v, datetime.datetime):
                    continue
                elif isinstance(v, str):
                    if not v:
                        error_flag = 1
                elif k in ('visitCount', 'replyCount'):
                    if isinstance(v, list):
                        count = v[0].get('count')
                    else:
                        count = v
                    if count < 0:
                        v = count
                        error_flag = 1
                else:
                    continue
                if error_flag:
                    dic.update({k:v})
            if len(dic.keys()) > 1:
                new_result.append(dic)
        self.detail_page_record_list += new_result
        return True

    def get_field_type(self):
        basestring_type_list = ['url']
        str_type_list = ['title', 'content', 'author', 'source', 'siteName', 'channel', 'html', 'summary']
        datetime_type_list = ['ctime', 'gtime']
        list_type_list = ['video_urls', 'pic_urls']
        list_or_int_type_list = ['visitCount', 'replyCount']
        dic = dict()
        dic.update({}.fromkeys(basestring_type_list, basestring))
        dic.update({}.fromkeys(str_type_list, str))
        dic.update({}.fromkeys(datetime_type_list, datetime.datetime))
        dic.update({}.fromkeys(list_type_list, list))
        dic.update({}.fromkeys(list_or_int_type_list, (list, int)))
        return dic


    def check_detail_field(self, post):
        '''对详情页返回值字段类型进行检查'''
        # 指定监控或者debug模式下进行检查 
        # if not self.config_monitor and not self.debug:
        #     return True
        flag = True
        error = {}
        for k,v in post.iteritems():
            if k in self.field_type_dic.keys():
                should_type = self.field_type_dic.get(k)
                if not isinstance(v, should_type):
                    flag = False
                    if k == 'url':
                        error.update({'url_type':str(type(v))})
                    else:
                        error.update({k:str(type(v))})
                    if self.debug:
                        log.logger.error(util.RR(k)+u" TYPE ERROR, should be {}, but found ".format(should_type)+util.RR("{}".format(type(v))))
                    else:
                        log.logger.error(u"{} TYPE ERROR, should be {}, but found {}".format(k, self.field_type_dic.get(k), type(v)))
        if not flag:
            url = post.get('url', '')
            error.update({'url':url})
            self.field_type_failed_record.append(error)
        return flag
    # duanyifei 2016-5-23

    # duanyifei 2016/10/24 add
    def add_retweeted_source(self, response, result=[]):
        if response is None:
            return result
        
        retweeted_source = ''
        try:
            doc = myreadability.Document(response.content)
            if hasattr(doc, 'source'):
                retweeted_source = doc.source
        except Exception as e:
            log.logger.error(u"add_retweeted_source() error: %s"%e)
            log.logger.exception(e)
        # 没有抽到 直接返回
        if not retweeted_source:
            return result

        if isinstance(result, dict):
            result = [result]
        result = copy.deepcopy(result)
        
        for post in result:
            if 'retweeted_source' not in post:
                post.update({'retweeted_source':retweeted_source})
        return result
    #

    def parse_detail_by_url(self, request=None):
        '''
        参数url指向一个详情页，下载并分析该页面详情；并统计分析结果；
        返回值为一个二元元组；第一个值表示所有详情页是否下载解析完毕，第二个值表示是否有下一页要抓取；
        '''
        request = copy.deepcopy(request)
        url = request.get('url') if isinstance(request, dict) else request
        next_urls = []
        
        result = {}
        parse_success = True
        
        response = self.download(request, func_name='parse')
        try:
            result = self.parse_detail_page(response, request)
        except Exception as e:
            # duanyifei 2016-5-24
            e_detail = traceback.format_exc()
            if self.debug:
                print util.R(e_detail)
            else:
                log.logger.error(e_detail)
            exc_dic = {'detail':e_detail, 'url':url, 'e_name':util.get_type_str(e)}
            self.exceptions_info_list.append(exc_dic)
            # duanyifei 2016-5-24
            parse_success = False
        # 下载网页失败
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
                result = [result]
            if isinstance(result, list):
                new_result = []
                for item in result:
                    if isinstance(item, dict):
                        if 'url' not in item:
                            item.update({'url':url})
                        # 值存在检查
                        for key, value in item.items():
                            if not value:
                                parse_success = False
#                                self.error_info.append((PARSE_DETAIL_FAILED, "PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(key, url)))
                                log.logger.info("PARSE_DETAIL_FAILED; parse %s failed; url:%s"%(util.RR(key), url))
                                if self.parse_failed.get(key, True):
                                    self.parse_failed[key] = True
                                    self.failed_info[key].append("%s : %s"%(key, url))
                            else:
                                self.parse_failed[key] = False
                        # 类型检查
                        if not self.check_detail_field(item):
                            parse_success = False
                            continue
                        new_result.append(item)
                result = new_result
        if parse_success:
            self.increase_parsed_success_num()
        else:
            self.increase_parsed_failed_num()
        # save data to db by data_queue
        res = {'url':url, 'config_id':self.config_id, 
               'info_flag':self.info_flag, 'siteName':self.siteName,
               'data_db':self.data_db, 'spider_id':getattr(setting, 'SPIDER_IP', self.spider_id)}

        g_c = datetime.timedelta(seconds=1)
        # 标题解析成功时将该数据入库，否则丢弃;
        if isinstance(result, dict):
            result = [result]
        if isinstance(result, list):
            new_result = []
            info_flag = 0
            try:
                info_flag = int(getattr(self, 'info_flag', 0))
            except Exception as e:
                log.logger.error(u"获取 info_flag error: %s, config_id: %s"%(e, self.config_id))
            if info_flag == 1 and result:
                # 2016/10/24 duanyifei add_retweeted_source
                try:
                    _result = self.add_retweeted_source(response, result)
                    if _result:
                        result = _result
                except Exception as e:
                    log.logger.error(u"add_retweeted_source() error: %s"%e)
                    log.logger.exception(e)
                # 2016/10/24 duanyifei add_retweeted_source
            for item in result:
                if isinstance(item, dict):
                    next_urls += item.pop('next_urls', [])
                    if item.get('title', ''):
                        res1 = res.copy()
                        res1.update(item)
                        new_result.append(res1)
                        #
                        if self.debug or getattr(setting, 'SHOW_DATA', False):
                            print util.B('\n {}'.format('###########################'))
                            ctime, gtime = res1.get('ctime'), res1.get('gtime')
                            time_error = 0
                            if gtime - ctime < g_c:
                                time_error = 1
                            for k, v in res1.iteritems():
                                if not v:
                                    print util.R('{:>10.10}'.format(k))+ ': {}'.format(v)
                                elif (k in ('ctime', ) and time_error):
                                    print util.R('{:>10.10}'.format(k))+ ': ' + util.RR('{}'.format(v))
                                else:
                                    print '{:>10.10} : {}'.format(k,v)
            
            if new_result:
                self.crawler_data_queue.put(new_result)

        # duanyifei 2016-5-23
        # 指定监控或者debug模式下 收集详情页错误字段信息
        if self.config_monitor or self.debug:
            try:
                self.save_parse_detail_info(result)
            except Exception as e:
                log.logger.exception(e)
        # duanyifei 2016-5-23
        
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
    except Exception as e:
        log.logger.info("send crawl result to %s failed: %s"%(url,e))
        print "failed"
    else:
        print resp.read()
        print "ok"
