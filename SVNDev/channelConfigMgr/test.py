#!/usr/bin/env python
# coding:utf8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：channel_spider.py
功能：  频道爬虫

代码历史：
2017-03-29：段毅飞，创建代码
'''

import re
import imp
import copy
import json
import time
import datetime
import traceback
from urlparse import urljoin, urlparse
from collections import defaultdict

import redis
import chardet
import pymongo
import requests
import tldextract

import log
import spider
import setting
import htmlparser
from dedup import dedup


def get_urls(data=None, list_url=None, precise_xpath_list=[], region_xpath_list=[], ends=[], detail_keywords=[],
             list_keywords=[], detail_regexs=[], list_regexs=[], keep_params=False, **kwargs):
    """
    @precise_xpath_list
        精准xpath列表
    @region_xpath_list
        详情页url所在位置区块 xpath
    @keep_params
        是否保留url中的参数 ?后面的
    @ends
        详情页url结尾字符串
    @detail_keywords
        详情页url中应该包含的字符串 任意一个存在即可
    @list_keywords
        反向过滤 列表页url中存在的字符串 任意一个存在即可
    @detail_regexs
        详情页url应该匹配的正则
    @list_regexs
        列表页url应该匹配的正则
    """

    def is_match(url, rules, typ='str'):
        if typ == 'str':
            for rule in rules:
                if rule in url:
                    return True
        elif typ == 'regex':
            for rule in rules:
                if re.search(rule, url):
                    return True
        return False

    urls = []
    list_url_domain = tldextract.extract(list_url).domain
    a_data_list = []
    title_urls = {}

    # 精准xpath列表
    for precise_xpath in precise_xpath_list:
        # if "@href" not in precise_xpath:
        # precise_xpath = precise_xpath + "/@href"
        a_data_list.extend(data.xpathall(precise_xpath))

    if not a_data_list:
        # 区块
        for region_xpath in region_xpath_list:
            a_data_list.extend(data.xpath(region_xpath).xpathall("//a"))
        if not a_data_list:
            a_data_list = data.xpathall("//a")
        # 文本长度过滤
        for a_data in a_data_list:
            title = a_data.text().decode("utf8")
            if len(title) < 8:
                continue
            a_url = a_data.xpath("//@href").text().strip()
            title_urls[a_url] = title
            urls.append(a_url)
    else:
        for item in a_data_list:
            a_url = item.xpath("//@href").text().strip()
            title = item.text().strip()
            title_urls[a_url] = title
            urls.append(a_url)

    # 是否保留参数
    if not keep_params:
        urls = [x.split("?")[0] for x in urls if x]
    # 去锚参数
    urls = [x.split("#")[0] for x in urls if x]
    # 补全url
    urls = [urljoin(list_url, x) for x in urls if x]
    # 去掉首页
    urls = [x for x in urls if urlparse(x).path.strip("/")]
    # 判断顶级域名
    urls = [x for x in urls if tldextract.extract(x).domain == list_url_domain]
    # 判断结尾
    if ends:
        urls = [x for x in urls if x.split("?")[0].endswith(tuple(ends)) or x.endswith(tuple(ends))]
    # detail_strs 判断
    if detail_keywords:
        urls = [x for x in urls if is_match(x, detail_keywords)]
    # list_strs 判断
    if list_keywords:
        urls = [x for x in urls if not is_match(x, list_keywords)]
    # detail_regexs 判断
    if detail_regexs:
        urls = [x for x in urls if is_match(x, detail_regexs, "regex")]
    # list_regexs 判断
    if list_regexs:
        urls = [x for x in urls if not is_match(x, list_regexs, "regex")]
    for url in title_urls.keys():
        if url not in urls:
            title_urls.pop(url)
    return {"urls": urls, "title_urls": title_urls}


def get_d(seconds):
    d = ""
    if seconds <= 60:
        d = "d1"
    elif seconds <= 120:
        d = "d2"
    elif seconds <= 300:
        d = "d3"
    elif seconds <= 900:
        d = "d4"
    elif seconds <= 1800:
        d = "d5"
    elif seconds <= 3600:
        d = "d6"
    elif seconds <= 7200:
        d = "d7"
    elif seconds <= 14400:
        d = "d8"
    else:
        d = "d9"
    return d


class MySpider(spider.Spider):
    ''''''

    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(self,
                               proxy_enable,
                               proxy_max_num,
                               timeout=timeout,
                               cmd_args=cmd_args)

        # 网站名称
        self.siteName = ""
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信 07 视频、99搜索引擎
        self.info_flag = "01"

        # 入口地址列表
        self.start_urls = [None]
        self.encoding = 'utf8'
        self.site_domain = ''
        self.conn = redis.StrictRedis.from_url("redis://spider-test-db-1.istarshine.net.cn/8")
        self.task_key_list = ["list_channel_spider_task_test",
                              "list_channel_spider_task"]
        self.test_task_key = "list_channel_spider_task_test"
        self.task_key = ""
        self.limits = 1
        self.dedup_uri = None
        self.dedup_dict = {}
        self.test_hash_channel_urls_info_key = "hash_channel_spider_result_test"
        self.test_result_key = "list_channel_spider_result_test_%s"

        # mongo日志
        self.mongo_conn = pymongo.MongoClient("spider-test-db-1.istarshine.net.cn", 37017)

        # 任务记录 默认每次运行仅一个任务
        self.json_task = {}
        # 时间差记录
        self.channel_timedelta = defaultdict(lambda: defaultdict(int))
        # 代码错误记录
        self.code_error_list = []

    def before_stoped(self, **kwargs):
        if not self.json_task:
            return
        # 测试不记录日志
        if self.task_key == self.test_task_key:
            return
        log_data = kwargs.get("log_data", {})
        # 增加代码错误记录
        log_data.update({"code_error": self.code_error_list[:5]})
        # 抛弃不必要字段
        if not self.code_error_list:
            self.json_task.pop("code", "")
        #
        log_data.update(self.json_task)
        #
        channel_url = self.json_task.get("url")
        if not channel_url:
            return
        today_str = time.strftime("%Y-%m-%d")
        timedelta_str = "timedelta_%s" % today_str
        # 运行日志入库
        db = self.mongo_conn['channelspider']
        db['log'].update({"channel_url": channel_url},
                         {
                             "$set": {"channel_url": channel_url},
                             "$push": {
                                 "run_log": {
                                     "$each": [log_data],
                                     "$slice": -1000
                                 },
                             },
                         },
                         upsert=True
                         )
        # 时间差信息入库
        for channel_url, timedelta in self.channel_timedelta.items():
            if not channel_url:
                continue
            db['log'].update({"channel_url": channel_url},
                             {
                                 "$set": {"channel_url": channel_url},
                                 "$inc": {
                                     "%s.%s" % (timedelta_str, key): value for key, value in timedelta.items()
                                 },
                             },
                             upsert=True
                             )
        #
        return

    def is_dedup(self, dedup_uri, url):
        urldedup = self.dedup_dict.get(dedup_uri, None)
        if not urldedup:
            urldedup = dedup.Dedup("/".join(dedup_uri.split("/")[:-1]), dedup_uri.split("/")[-1])
            self.dedup_dict[dedup_uri] = urldedup
        return urldedup.is_dedup(url)

    def handle_callback(self, json_task):
        code = json_task.get("code", "")
        if not code:
            log.logger.error("没有 code 代码")
            return {}
        module = imp.new_module("channel_spider")
        try:
            exec code.encode("utf8") in module.__dict__
        except Exception as e:
            log.logger.exception(e)
            return {}
        json_task.update({"parse_detail": module.parse_detail})
        return json_task

    def test_result_to_db(self, result, json_task):
        result = copy.deepcopy(result)
        config_id = json_task.get("config_id")
        channel_url = json_task.get("url")
        for post in result:
            url = post.get("url")
            post.update({
                "channel_title": json_task.get("title_urls").get(url),
                "channel_url": channel_url,
                "ctime": post.get("ctime", datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S"),
                "gtime": post.get("gtime", datetime.datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S"),
            })
        result = [json.dumps(post) for post in result]
        self.conn.lpush(self.test_result_key % config_id, *result)
        return 1

    def statistic_timedelta(self, channel_url, d):
        self.lock.acquire()
        last_count = self.channel_timedelta[channel_url][d]
        last_count += 1
        self.channel_timedelta[channel_url][d] = last_count
        self.lock.release()
        return

    def get_encoding(self, response):
        detect_encoding = chardet.detect(response.content)
        return detect_encoding.get("encoding")

    def get_start_urls(self, data=None):
        '''
        返回start_urls
        '''
        start_urls = []
        pipe = self.conn.pipeline()
        for task_key in self.task_key_list:
            for i in range(self.limits):
                pipe.rpop(task_key)
            tasks = pipe.execute()
            tasks = [x for x in tasks if x]
            if tasks:
                break
        self.task_key = task_key
        for task in tasks:
            try:
                json_task = json.loads(task)
            except Exception as e:
                continue
            self.json_task = copy.deepcopy(json_task)
            json_task = self.handle_callback(json_task)
            if not json_task:
                continue
            url = json_task.get("url", "")
            if not url:
                continue
            info_flag = json_task.get("info_flag", "")
            if not info_flag:
                continue
            request = {
                "url": url,
                "meta": json_task,
            }
            # 测试不加代理
            if self.task_key == self.test_task_key:
                request.update({"proxies": None})
            start_urls.append(request)

        if not start_urls:
            time.sleep(10)
        return start_urls

    def parse(self, response=None, url=None):
        """
        默认爬虫入口页分析函数；
        返回格式为(url_list,  callback, next_page_url)
            其中，url_list：表示当前data中分析出的url列表；如果没有url，改值为[]
            参数callback: 表示url_list中网页的分析函数；
            如果url_list中的值为详情页url，callback=None;
            该函数的返回值为同样为( url_list, callback, next_page_url)
        参数next_page_url: 下一页要分析的url，如果不翻页，该值为 None
        """
        url_list = []
        request = url
        list_url = request.get("url")
        json_task = request.get("meta")
        dedup_uri = json_task.get("dedup_uri")
        crawl_rules = json_task.get("crawl_rules", {})
        if not response:
            self.conn.lpush(self.task_key, json.dumps(request.get("meta")))
            return (url_list, None, None)
        encoding = json_task.get("channel_encoding")
        try:
            if not encoding:
                encoding = self.get_encoding(response)
            response.encoding = encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception as e:
            log.logger.error("parse(): %s" % e)
            return (url_list, None, None)
        #
        title_urls = {}
        try:
            urls_info = get_urls(data=data, list_url=list_url, **crawl_rules)
            url_list = urls_info.get("urls")
            title_urls = urls_info.get("title_urls")
        except Exception as e:
            log.logger.exception(e)
        #
        # 去重
        url_list = [url for url in url_list if not self.is_dedup(dedup_uri, url)]
        #
        json_task.pop("code", "")
        # 增加列表页标题
        json_task.update({"title_urls": title_urls})
        #
        url_list = [{"url": url, "meta": json_task} for url in url_list]
        # 测试不加代理
        if self.task_key == self.test_task_key:
            for request in url_list:
                request.update({"proxies": None})
            # 测试中间结果记录
            self.conn.hset(self.test_hash_channel_urls_info_key, list_url, json.dumps(title_urls))
        return (url_list, None, None)

    def parse_detail_page(self, response=None, url=None):
        '''
        详细页解析
        '''
        request = url
        json_task = request.get("meta")
        url = request.get("url", "")
        encoding = json_task.get("detail_encoding")
        callback = json_task.get("parse_detail", None)
        data_db = json_task.get("data_db", "")
        result = []
        _result = []
        try:
            if not encoding:
                encoding = self.get_encoding(response)
            response.encoding = encoding
            unicode_html_body = response.text
            data = htmlparser.Parser(unicode_html_body)
        except Exception as e:
            log.logger.error("parse_detail_page(): %s" % e)
            # 测试结果入库
            if self.task_key == self.test_task_key:
                result = [{
                    "url": url,
                    "error": "下载失败"
                }]
                self.test_result_to_db(result, json_task)
            return None
        # 解析函数错误信息
        error = ""

        if callback:
            try:
                _result = callback(self, response=response, url=request, data=data)
            except Exception as e:
                log.logger.exception(e)
                _result = []
                error = traceback.format_exc()
                self.code_error_list.append({"url": url, "error": error})

        if not isinstance(_result, list):
            _result = [_result]

        gtime = datetime.datetime.utcnow()
        for post in _result:
            siteName = post.get("siteName", "")
            if not siteName:
                siteName = json_task.get("siteName", "")
            if not isinstance(siteName, str):
                siteName = siteName.encode("utf8")
            channel = post.get("channel", "")
            if not channel:
                channel = json_task.get("channel", "")
            if not isinstance(channel, str):
                channel = channel.encode("utf8")
            post.update({
                "channel": channel,
                "gtime": gtime,
                "siteName": siteName,
                "data_db": data_db,
                "info_flag": json_task.get("info_flag", ""),
            })
            result.append(post)
            # 统计时间差
            try:
                ctime = post.get("ctime")
                gtime = post.get("gtime")
                d = get_d((gtime - ctime).total_seconds())
                self.statistic_timedelta(json_task.get("url", ""), d)
            except Exception as e:
                log.logger.exception(e)

        if self.task_key == self.test_task_key:
            if error and (not result):
                result = [{
                    "url": url,
                    "error": error
                }]
            self.test_result_to_db(result, json_task)
            result = []
        return result


if __name__ == '__main__':
    spider = MySpider()
    spider.proxy_enable = False
    spider.init_dedup()
    spider.init_downloader()

    # ------------ get_start_urls() ----------
    # urls = spider.get_start_urls()
    # for url in urls:
    #     print url

    # ------------ parse() ----------
    # url = 'http://tieba.baidu.com/f?kw=%C4%CF%D1%F4'
    # resp = spider.download(url)
    # urls, fun, next_url = spider.parse(resp)
    # for url in urls:
    #     print url

    # ------------ parse_detail_page() ----------
    url = ''
    resp = spider.download(url)
    res = spider.parse_detail_page(resp, url)
    for item in res:
        for k, v in item.iteritems():
            print k, v
