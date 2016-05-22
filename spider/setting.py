#encoding=utf8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：setting.py
功能：爬虫多线程运行配置文件；从配置文件spider.cfg读取配置选项和值

代码历史：
2014-03-15：庞 威，创建代码
'''
import os
import ConfigParser


config = ConfigParser.ConfigParser()
_cur_path = os.path.dirname(__file__)
config.read(_cur_path + '/spider.conf')

#for section in config.sections():
#    globals().update(config.items())

#threading
PROCESS_NUM = config.getint('threading', 'process_num')
CRAWLER_MODE = config.get('threading', 'crawler_mode')
LIST_PAGE_THREAD_NUM = config.getint('threading', 'list_page_thread_num')
DETAIL_PAGE_THREAD_NUM = config.getint('threading', 'detail_page_thread_num')
DATA_QUEUE_THREAD_NUM = config.getint('threading', 'data_queue_thread_num')

#http
PROXY_ENABLE = config.getboolean('http', 'proxy_enable')
PROXY_MAX_NUM = config.getint('http', 'proxy_max_num')
PROXY_AVAILABLE = config.getint('http', 'available_proxy_num')
PROXY_URL = config.get('http', 'proxy_url')
COMPRESSION = config.getboolean('http', 'compression')
HTTP_TIMEOUT = config.getint('http', 'http_timeout')
COOKIE_ENABLE = config.getboolean('http', 'cookie_enable')
#duanyifei add begin on 2016-03-21
try:
    PROXY_UPDATE_INTERVAL = config.getint('http', 'proxy_update_interval')
except:
    PROXY_UPDATE_INTERVAL = 300
#duanyifei add end on 2016-03-21

#spider
SPIDER_ID = config.get('spider', 'spider_id')
GET_SPIDER_CONFIG_FROM = config.get('spider', 'get_spider_config_from')
SEND_CRAWL_RESULT_TO = config.get('spider', 'send_crawl_result_to')
GET_SPIDER_PARAM_FROM = config.get('spider', 'get_spider_param_from')
EXIT_TIMEOUT = config.getint('spider', 'exit_timeout')
LIST_DETAIL_INTERVAL = config.getint('spider', 'list_detail_interval')
DATA_ENCODING = config.get('spider', 'data_encoding')
REPEAT_TIMES = config.getint('spider', 'repeat_times')
SHOW_DATA = config.getboolean('spider', 'show_data')
try:
    ADSL_ID = config.getint('spider', 'adsl_id')
except:
    ADSL_ID = -1

#dedup
DEDUP_URI = config.get('dedup', 'dedup_uri')
DEDEUP_KEY = config.get('dedup', 'dedup_key')


#daemon_app
STDIN_PATH = config.get('daemon_app', 'stdin_path')
STDOUT_PATH = config.get('daemon_app', 'stdout_path')
STDERR_PATH = config.get('daemon_app', 'stderr_path')
PIDFILE_PATH = config.get('daemon_app', 'pidfile_path')
PIDFILE_TIMEOUT = config.getint('daemon_app', 'pidfile_timeout')


#data_queue
SPIDER_DATA_DB = config.get('data_db', 'spider_data_db')
SPIDER_LOG_DB = config.get('data_db', 'spider_log_db')
CRAWLER_LIST_DATA = config.get('data_db', 'crawler_list_data')


#pangwei add begin on 2016-03-14
import platform

def get_windows_localip():
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())#这个得到本地ip
    return local_ip

def get_linux_localip():
    import socket
    import fcntl
    import struct

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip  =  socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915, struct.pack('256s', "eth0"[:15]))[20:24])
    
    return local_ip

def get_localip():
    local_ip = ""
    try:
        if  platform.system() == "Windows":
            local_ip =  get_windows_localip()
        else:
            local_ip =  get_linux_localip()
    except Exception, e:
        local_ip = ""
    return local_ip

SPIDER_IP = get_localip()

#pangwei add end on 2016-03-14


if __name__ == "__main__":
    print 'LIST_PAGE_THREAD_NUM', type(LIST_PAGE_THREAD_NUM), LIST_PAGE_THREAD_NUM
    print 'GET_SPIDER_CONFIG_FORM', type(GET_SPIDER_CONFIG_FROM), GET_SPIDER_CONFIG_FROM
    print 'PROXY_ENABLE', type(PROXY_ENABLE), PROXY_ENABLE
    print 'PROXY_URL', type(PROXY_URL), PROXY_URL
    print 'DEDUP_URI', type(DEDUP_URI), DEDUP_URI
    print 'DEDEUP_KEY', type(DEDEUP_KEY), DEDEUP_KEY
    print 'CRAWLER_DATA', type(SPIDER_DATA_DB), SPIDER_DATA_DB
    print 'EXIT_TIMEOUT', type(EXIT_TIMEOUT), EXIT_TIMEOUT
    print 'LIST_DETAIL_INTERVAL', type(LIST_DETAIL_INTERVAL), LIST_DETAIL_INTERVAL
    print 'DATA_ENCODING', type(DATA_ENCODING), DATA_ENCODING
    print 'REPEAT_TIMES', type(REPEAT_TIMES), REPEAT_TIMES
    print 'SEND_CRAWL_RESULT_TO', type(SEND_CRAWL_RESULT_TO), SEND_CRAWL_RESULT_TO
    
    print 'ADSL_ID', type(ADSL_ID), ADSL_ID
    print 'SPIDER_IP', type(SPIDER_IP), SPIDER_IP
