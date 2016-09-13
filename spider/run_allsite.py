#!/usr/bin/env python
# coding:utf8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：run.py
功能：爬虫多线程执行文件

代码历史：
2014-02-07：贺伟刚，创建代码框架
2014-02-26：庞  威  代码补充
'''
import gevent.pool
import gevent.queue
import gevent.event
from gevent import threadpool
from gevent import monkey
# monkey.patch_all()

import sys
import imp
import json
import time
import signal
import random
import urllib2
import requests
import traceback

import log
import util
import setting

# 全局Event变量，用于退出时线程间同步
eventExit = None
# 命令行参数对象，保存从命令行中得到的参数
cmd_args = None


def load_module(url, spider_id=None, worker_id=None, name='spider', add_to_sys_modules=0):
    '''
    动态加载py模块。url为要加载的模块地址，支持http, ftp及本地操作；
    参数name是加载后的模块名称，不能使包的形式， 因此，name='spider.sina'是不允许的；
    参数add_to_sys_modules=1表示将新建模块加入到sys.module; 设置为0则表示不加入；
    '''
    newurl_lower = url.lower()
    if newurl_lower.startswith("http://") or newurl_lower.startswith("https://"):
        # url = url%(spider_id, worker_id)
        try:
            url = url % (spider_id, worker_id)
            #            data = urllib2.urlopen(url, timeout=15).read()
            data = requests.get(url, timeout=15).content
        except Exception as e:
            log.logger.error("run.py:load_module(): url:%s, Exception:%s" % (url, e))
            return (None, None)
        # print '---**--- content: ', data
        try:
            data = json.loads(data)
        except Exception as e:
            log.logger.error("json.load() failed; excepiton: %s; url:%s" % (e, url))
            return (None, None)
        try:
            config = data.pop('config_content', '').encode('utf-8')
        except Exception as e:
            log.logger.error("config_content.encode('utf8') failed; excepiton: %s" % e)
            return (None, None)
        if not config:
            return (None, None)
        try:
            code = compile(config, '', 'exec')
        except Exception as e:
            log.logger.error("-- compile failed --; config_id:%s; excepiton: %s" % (data.get('config_id', '-1'), e))
            return (None, None)

        module = imp.new_module(name)
        try:
            exec code in module.__dict__
        except Exception as e:
            log.logger.error("-- exec code in module.__dict__ failed --; config_id:%s; excepiton: %s" % (
            data.get('config_id', '-1'), e))
            return (None, None)
        if add_to_sys_modules:
            sys.modules[name] = module
        return (data, module)

    elif newurl_lower.startswith("file://"):
        if not newurl_lower.startswith("file:///"):
            url = "file:///%s" % url
        try:
            data = urllib2.urlopen(url).read()
        except Exception as e:
            log.logger.error("run.py:load_module(): url:%s, Exception:%s" % (url, e))
            return (None, None)
        #
        config = data
        try:
            code = compile(config, '', 'exec')
        except Exception as e:
            log.logger.error("-- compile failed --; config_id:%s; excepiton: %s" % (data.get('config_id', '-1'), e))
            return (None, None)

        module = imp.new_module(name)
        try:
            exec code in module.__dict__
        except Exception as e:
            log.logger.error("-- exec code in module.__dict__ failed --; config_id:%s; excepiton: %s" % (
            data.get('config_id', '-1'), e))
            return (None, None)
        if add_to_sys_modules:
            sys.modules[name] = module
        return ({}, module)

    else: # for allsite redis task call
        import redis
        # url = 'redis://127.0.0.1/14'
        conn = redis.StrictRedis.from_url(url)
        task_manager_key = 'task_manager'  # 任务管理
        task_list = conn.hgetall(task_manager_key)
        for k, v in task_list.iteritems():
            status = eval(v).get('status')
            if status == 'todo':  # 提取状态为待运行：todo
                config = eval(v).get('config_content')
                try:
                    code = compile(config, '', 'exec')
                except Exception as e:
                    log.logger.error("-- compile failed --; config_id:%s; excepiton: %s" % e)
                    # print '[error]run_task_one() error', e
                    return (None, None)

                module = imp.new_module('allsite_spider')
                try:
                    exec code in module.__dict__
                except Exception as e:
                    # print '[error]run_task_one() error', e
                    log.logger.error("-- exec code in module.__dict__ excepiton: %s" % e)
                    return (None, None)

                # 修改状态为运行中：start
                conn.hdel(task_manager_key, k)
                v = {'config_content':config,'status':'start'}
                conn.hset(task_manager_key, k, v)
                break

        else:
            log.logger.error("-- task_manager not found: %s" % url)
            # print '[error]run_task_one() not found task_manager'
            return (None, None)

        if add_to_sys_modules:
            sys.modules[name] = module
        return ({}, module)


def get_detail_page_urls(spider, urls, func, detail_job_queue):
    """
    根据该列表urls中的入口地址，分析获取详情页信息，将获取的详情页url放到详情页抓取任务队列中;
    方法相当于数的遍历；
    参数func表示参数urls说指向的网页分析函数；返回值为(list_urls, callback, next_page_url)
    其中，list_urls表示从当前页分析得到的url列表， callback表示list_urls网页的分析函数，next_page_url
    表示从当前页分析出的下一页地址，如果不分析下一页信息，改值为None
    参数detail_job_queue表示详情页队列； 分析出来的详情页信息将会放入此队列中；
    """
    if func is not None:
        if urls:
            for request in urls:
                url = request.get('url') if isinstance(request, dict) else request
                print 'downloading  list page ...', url
                response = spider.download(request, func_name='get_start_urls')
                #                if response is None:
                #                    log.logger.error("download page failed; url is:%s"%url)
                #                    continue
                # data = getattr(response, 'unicode_body', '')
                # data = htmlparser.Parser(data, response=response)
                # list_urls, callback, next_page_url = func(data)
                try:
                    list_urls, callback, next_page_url = func(response)
                except Exception as e:
                    e_detail = traceback.format_exc()
                    if getattr(cmd_args, 'debug', None):
                        log.logger.exception(util.R(e_detail))
                    exc_dic = {'detail': e_detail, 'url': url, 'e_name': util.get_type_str(e)}
                    spider.exceptions_info_list.append(exc_dic)
                    list_urls, callback, next_page_url = [], None, None
                    log.logger.error("-- %s , config_id: %s, exception: %s" % (func, spider.config_id, e))
                # 判断列表解析结果是否为空或有错误
                spider.check_url_list(list_urls, url)
                # print "---***---", func
                get_detail_page_urls(spider, list_urls, callback, detail_job_queue)
                if next_page_url is not None:
                    get_detail_page_urls(spider, [next_page_url], func, detail_job_queue)
    else:
        if urls is None:
            urls = []
            log.logger.error("-- urls is None, config_id: %s " % (spider.config_id))
        for request in urls:
            url = request.get('url') if isinstance(request, dict) else request
            if not isinstance(url, basestring):
                continue
            spider.increase_total_data_num()
            #            global urldedup
            if spider.urldedup is not None:
                try:
                    if not spider.urldedup.is_dedup(url):
                        detail_job_queue.put((spider, request))
                        spider.increase_new_data_num()
                        if getattr(cmd_args, 'debug', None):
                            if isinstance(request, dict):
                                print " *** new detail url is:", url, request
                            else:
                                print " *** new detail url is:", url
                except Exception as e:
                    print e
            else:
                detail_job_queue.put((spider, request))
                spider.increase_new_data_num()
                if getattr(cmd_args, 'debug', None):
                    if isinstance(request, dict):
                        print " *** new detail url is:", url, request
                    else:
                        print " *** new detail url is:", url


def list_page_thread(eventExit, detail_job_queue, name, crawler_data_queue):
    '''
    列表页工作线程，不断向任务服务器获取配置脚本
    '''
    while 1:
        if eventExit.isSet():
            print "---***--- list threads finished !!!"
            break
        else:
            data, mod = load_module(setting.GET_SPIDER_CONFIG_FROM,
                                    setting.SPIDER_ID, name)
            if mod is not None:
                repeat_times = getattr(setting, 'REPEAT_TIMES', 1)
                while repeat_times > 0:
                    if eventExit.isSet():
                        break

                    global cmd_args
                    try:
                        spider = mod.MySpider(cmd_args=cmd_args)
                        spider.set_data_queue(crawler_data_queue)
                        spider.set_detail_page_queue(detail_job_queue)
                        spider.init_dedup()
                        spider.init_downloader()
                    except Exception as e:
                        log.logger.error("-- init spider failed; config_id: %s , %s" % (data.get("config_id", ''), e))
                        repeat_times -= 1
                        continue

                    if data is not None:
                        job_id = str(data.get("job_id", '-1')).encode('utf-8')
                        config_id = str(data.get("config_id", '')).encode('utf-8') or "%s" % setting.SPIDER_ID
                        config_name = str(data.get("savename", '')).encode('utf-8')
                        spider.set_job_id(job_id)
                        spider.set_config_id(config_id)
                        spider.set_config_name(config_name)
                        spider.set_spider_id(setting.SPIDER_ID)
                        spider.set_worker_id(name)
                        limit = data.get("limit", 1)
                        post_data = {'spider_id': setting.SPIDER_ID,
                                     'worker_id': name,
                                     'config_id': config_id,
                                     'limit': limit,
                                     }
                    try:
                        start_urls = spider.get_start_urls(post_data)
                    except Exception as e:
                        start_urls = []
                        exc_dic = {'detail': traceback.format_exc(), 'url': '', 'e_name': util.get_type_str(e)}
                        spider.exceptions_info_list.append(exc_dic)
                        log.logger.error("-- get_start_urls failed; config_id: %s , %s" % (config_id, e))
                    # 根据start_urls中的入口url获取下一列表页url及详情页url
                    # 将得到的详情页url放到detail_job_queue中
                    get_detail_page_urls(spider, start_urls, spider.parse,
                                         detail_job_queue)
                    # 设置列表页解析结束标志
                    spider.set()
                    # 如果没有新帖子信息，直接返回；
                    res = spider.spider_finished()
                    # 等待详情页解析线程结束
                    spider.job_event.wait()
                    #                    while not spider.job_event.is_set():
                    #                        gevent.sleep(0.1)
                    # print " ---*** list end *** "
                    if res:
                        del spider

                    repeat_times -= 1

                if getattr(cmd_args, 'debug', None):
                    eventExit.set()
                    # eventExit.set()
            else:
                time.sleep(1.0)


def detail_page_thread(eventExit, job_queue):
    '''
    详细页下载线程; 当任务队列发生Empty异常时，如果eventExit设置为True，则退出；
    '''
    while 1:
        try:
            # print " --- job_queue --- : ",job_queue.qsize()
            spider, request = job_queue.get(True, 1)
            log.logger.debug('-----job_queue----qsize: %s' % job_queue.qsize())
        except Exception as e:
            if eventExit.isSet():
                # if job_queue.empty():
                break
            # print "---- detail queue empty  ------ "
            continue
        result, next_urls = spider.parse_detail_by_url(request)
        if next_urls:
            for url in next_urls:
                job_queue.put((spider, url))
        if result:
            del spider
        job_queue.task_done()


def data_queue_thread(eventExit, crawler_data_queue):
    """
    """
    # 默认数据保存地址
    uri = setting.SPIDER_DATA_DB
    other_data_queue_sender = {}
    try:
        data_queue_sender = util.from_url(uri)
    except Exception as e:
        log.logger.error("init data_queue_sender failed: %s , %s" % (uri, e))
        raise e
    while 1:
        try:
            # print " --- crawler_data_queue :",crawler_data_queue.qsize()
            data = crawler_data_queue.get(True, 1)
        except Exception as e:
            if eventExit.isSet():
                data_queue_sender.close()
                for key in other_data_queue_sender.keys():
                    other_data_queue_sender[key].close()
                break
            # print "--- crawler_data_queue  empty *** "
            continue

        if not data:
            continue

        if isinstance(data, dict):
            if 'data_db' not in data:
                try:
                    data_queue_sender.send(data)
                except Exception as e:
                    log.logger.error("data_queue_sender.send() failed: %s , %s" % (uri, e))
                    continue
            else:
                data_db = data.pop('data_db')
                if data_db in other_data_queue_sender:
                    try:
                        other_data_queue_sender[data_db].send(data)
                    except Exception as e:
                        log.logger.error("other_data_queue_sender failed: %s, %s" % (data_db, e))
                        continue
                else:
                    try:
                        other_sender = util.from_url(data_db)
                        other_data_queue_sender[data_db] = other_sender
                        other_sender.send(data)
                    except Exception as e:
                        log.logger.error("init other_sender failed: %s, %s" % (e, data_db))
                        continue

        elif isinstance(data, list):
            from collections import defaultdict
            data_list = defaultdict(list)
            for item in data:
                data_db = item.pop('data_db', None)
                if data_db is not None:
                    data_list[data_db].append(item)

            for data_db, data in data_list.iteritems():
                if data_db in other_data_queue_sender:
                    try:
                        other_data_queue_sender[data_db].send(data)
                    except Exception as e:
                        log.logger.error("other_data_queue_sender failed: %s, %s" % (data_db, e))
                        continue
                else:
                    try:
                        other_sender = util.from_url(data_db)
                        other_data_queue_sender[data_db] = other_sender
                        other_sender.send(data)
                    except Exception as e:
                        log.logger.error("init other_sender failed: %s, %s" % (e, data_db))
                        continue

        crawler_data_queue.task_done()


def run_spider():
    """
    爬虫多线程执行主体函数
    """
    monkey.patch_all()

    global eventExit

    #    eventExit = gevent.event.Event()

    signal.signal(signal.SIGTERM, stop_spider)

    crawler_mode = setting.CRAWLER_MODE
    counter = 0
    if crawler_mode == 'threading':
        #
        import Queue
        import threading
        eventExit = threading.Event()
        detail_job_queue = Queue.Queue()
        crawler_data_queue = Queue.Queue()

        list_thread_pool = []
        counter = 0
        for _ in range(setting.LIST_PAGE_THREAD_NUM):
            time.sleep(random.random())
            counter += 1
            list_thread = threading.Thread(target=list_page_thread,
                                           args=(eventExit, detail_job_queue, counter, crawler_data_queue))
            list_thread.start()
            list_thread_pool.append(list_thread)

        interval = getattr(setting, 'LIST_DETAIL_INTERVAL', 60)
        time.sleep(interval)

        detail_page_thread_pool = []
        for _ in range(setting.DETAIL_PAGE_THREAD_NUM):
            detail_thread = threading.Thread(target=detail_page_thread, args=(eventExit, detail_job_queue))
            detail_thread.start()
            detail_page_thread_pool.append(detail_thread)

        data_queue_thread_pool = []
        for _ in range(setting.DATA_QUEUE_THREAD_NUM):
            data_thread = threading.Thread(target=data_queue_thread, args=(eventExit, crawler_data_queue))
            data_thread.start()
            data_queue_thread_pool.append(data_thread)
    else:
        #
        eventExit = gevent.event.Event()
        detail_job_queue = gevent.queue.JoinableQueue()
        crawler_data_queue = gevent.queue.JoinableQueue()
        #
        list_thread_pool = gevent.pool.Pool(setting.LIST_PAGE_THREAD_NUM)
        detail_page_thread_pool = gevent.pool.Pool(setting.DETAIL_PAGE_THREAD_NUM)
        data_queue_thread_pool = gevent.pool.Pool(1)

        for _ in xrange(setting.LIST_PAGE_THREAD_NUM):
            time.sleep(random.random())
            counter += 1
            list_thread_pool.spawn(list_page_thread, eventExit, detail_job_queue, counter, crawler_data_queue)

        interval = getattr(setting, 'LIST_DETAIL_INTERVAL', 60)
        time.sleep(interval)

        for _ in range(setting.DETAIL_PAGE_THREAD_NUM):
            detail_page_thread_pool.spawn(detail_page_thread, eventExit, detail_job_queue)

        for _ in range(setting.DATA_QUEUE_THREAD_NUM):
            data_queue_thread_pool.spawn(data_queue_thread, eventExit, crawler_data_queue)

    eventExit.wait()
    #    signal.pause()
    try:
        exit_timeout = getattr(setting, 'EXIT_TIMEOUT', 300)
        timeouter = gevent.Timeout(exit_timeout)
        timeouter.start()

        if crawler_mode == 'threading':
            for thread in list_thread_pool:
                thread.join()
            for thread in detail_page_thread_pool:
                thread.join()
            for thread in data_queue_thread_pool:
                thread.join()
        else:
            list_thread_pool.join()
            detail_page_thread_pool.join()
            data_queue_thread_pool.join()

    except gevent.Timeout, e:
        log.logger.debug("internal timeout triggered: %s" % e)
    finally:
        timeouter.cancel()

    log.logger.info("---***--- all work finished!!!")


#    print "---***--- All work finished!!!"
# 通知Thread 可以退出了，放到服务stop函数中，当前线程是一直工作，没有退出
# eventExit.set()

def stop_spider(signum, frame):
    """
    结束爬虫所有线程；立即结束获取配置线程；抓取详情页线程需完成detail_job_queue队列中所有任务才能退出；
    """
    global eventExit
    eventExit.set()
    print " ---***--- stop_spider() called !!! "


def web_interface():
    '''
    '''
    import bottle
    from bottle import route, run, error

    @error(404)
    def error404(error):
        return '404'

    @route('/status')
    def status():
        return '1'

    run(host='')


def multi_process_runner():
    """
    多进程模式
    """
    import multiprocessing

    process_pool = []

    def stop_process(signum, frame):
        for p in process_pool:
            p.terminate()

    signal.signal(signal.SIGTERM, stop_process)

    for _ in xrange(getattr(setting, 'PROCESS_NUM', 2)):
        p = multiprocessing.Process(target=run_spider)
        p.start()
        process_pool.append(p)

    for p in process_pool:
        p.join()
    print "---***--- All work finished!!!"


class App(object):
    """
    该类定义了守护进程中的执行对象
    """

    def __init__(self):
        self.stdin_path = setting.STDIN_PATH
        self.stdout_path = setting.STDOUT_PATH
        self.stderr_path = setting.STDERR_PATH
        self.pidfile_path = setting.PIDFILE_PATH
        self.pidfile_timeout = setting.PIDFILE_TIMEOUT

    def run(self):
        """
        守护进程中执行体
        """
        #        run_spider()
        multi_process_runner()

    def stop(self):
        """
        守护进程结束前执行动作；
        """
        stop_spider()


def reset_setting_config(args):
    """
    """
    if args:
        # 指定配置文件时, list_thread_num 设置为  1
        config_url = getattr(args, 'GET_SPIDER_CONFIG_FROM', '')
        if config_url:
            config_url = config_url.lower()
            if not config_url.startswith('http') or not config_url.startswith('https'):
                args.LIST_PAGE_THREAD_NUM = 1
                args.LIST_DETAIL_INTERVAL = 1
        #
        for key, value in args.__dict__.iteritems():
            if value is not None:
                # print "%s : %s"%(key, value)
                if key in setting.__dict__:
                    print "before: ", key, setting.__dict__[key]
                    setting.__dict__[key] = value
                    print "after: %s: %s" % (key, value)


def main():
    """
    """
    import argsparser

    global cmd_args
    cmd_args = argsparser.cmd_parse()
    #    print "cmd_args: ", cmd_args
    reset_setting_config(cmd_args)

    if cmd_args.start:
        from daemon import runner
        sys.argv[1] = 'start'
        app = App()
        daemon_runner = runner.DaemonRunner(app)
        daemon_runner.daemon_context.files_preserve = [log.fp.stream, log.std.stream]
        daemon_runner.do_action()
    elif cmd_args.stop:
        from daemon import runner
        sys.argv[1] = 'stop'
        app = App()
        daemon_runner = runner.DaemonRunner(app)
        daemon_runner.daemon_context.files_preserve = [log.fp.stream, log.std.stream]
        daemon_runner.do_action()
    elif cmd_args.debug:
        run_spider()
    else:
        argsparser.print_usage()


if __name__ == "__main__":
    #    app = App()
    #    daemon_runner = runner.DaemonRunner(app)
    #    daemon_runner.daemon_context.files_preserve = [log.fp.stream, log.std.stream]
    #    daemon_runner.do_action()
    #     import cProfile
    #     cProfile.run('run_spider()')

    #    run_spider()
    #    multi_process_runner()
    main()
