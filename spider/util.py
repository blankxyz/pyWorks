#!/usr/bin/env python
# coding:utf-8


#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：util.py
功能：工具函数文件 

代码历史：
2014-02-27：庞  威，代码创建
'''
import os
import re
import sys
import time
import copy
import datetime
import urlparse

try:
    import ujson as json
except ImportError:
    import json
import requests
import redis

from lxml.html.clean import Cleaner

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None): return text

import log

def get_current_file_path():
    '''
    获取当前文件所在路径
    '''
    path = os.path.dirname(os.path.abspath(sys.path[0]))
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def is_re_match(pattern, string):
    '''
    '''
    m = re.match(pattern, string)
    if m is None:
        return False
    return True

def is_variable(v):
    '''
    '''
    try:
        type (eval(v))
    except:
        return False
    else:
        return True

def get_one_result(pattern, string):
    try:
        result_tuple = re.compile(pattern).findall(string)
    except Exception:
        return None
    if len(result_tuple)>0:
        return result_tuple[0]
    else:
        return None
    
def get_one_result_c(p, string):
    try:
        result_tuple =p.findall(string)
    except Exception:
        return None
    if len(result_tuple)>0:
        return result_tuple[0]
    else:
        return None
    
def TimeDeltaYears(years, from_date=None):
    if from_date is None:
        from_date = datetime.datetime.now()
    try:
        return from_date.replace(year=from_date.year + years)
    except:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year+years)

def filter_style_script(text):
    '''去除注释 style script'''
    html_cleaner = Cleaner(scripts=True, javascript=True, comments=True, style=True,
                    links=False, meta=False, page_structure=False, processing_instructions=False,
                    embedded=False, frames=False, forms=False, annoying_tags=False, remove_tags=None,
                    remove_unknown_tags=False, safe_attrs_only=False)
    text = html_cleaner.clean_html(text)
    return text

def clear_special_xpath(data, xp):
    '''
    删除指定 xpath 数据
    仅作用于 htmlparser.Parser 对象
    '''
    data = copy.deepcopy(data)
    result = data._root.xpath(xp)
    for i in result:
        i.getparent().remove(i)
    return data


class MysqlPipeline(object):
    """
    """
    def __init__(self, uri):
        """
        """
        try:
            import MySQLdb
        except ImportError:
            print "no module MySQLdb found"
        
        parsed = urlparse.urlparse(uri)
        host = parsed.hostname
        port = parsed.port or 3306
        user = parsed.username
        passwd = parsed.password
        
        db, table = parsed.path.strip('/').split('.')
        conn = MySQLdb.connect(
                                host=host,
                                port=port,
                                user=user,
                                passwd=passwd,
                                db=db,
                                charset='utf8'
                             )
        self.conn = conn
        self.table = table
        self.cursor = conn.cursor()
    
    def send(self, data):
        """
        向数据库发送数据；
        """
        fields = []
        values = []
        for k, v in data.iteritems():
            fields.append(k)
            values.append(v)
        
        if self.conn:
            try:
                self.cursor.execute("""INSERT INTO %s(%s) VALUES (%s) """%(self.table, ','.join(fields), values))
                self.conn.commit()
            except Exception as e:
                log.logger.exception(e)
                return False
            else:
                return True
    
    def close(self):
        """
        """
        self.cursor.close()
        self.conn.close()
        self.cursor = self.conn = None


class MongoPipeline(object):
    """
    """
    def __init__(self, uri):
        """
        连接到monogodb数据库
        """
        import pymongo
        parsed = pymongo.uri_parser.parse_uri(uri)
        database = parsed['database']
        collection = parsed['collection']
        host, port = parsed['nodelist'][0]

        self.conn = pymongo.MongoClient(host=host, port=port)
        if database:
            self.db = self.conn[database]
        else:
            self.db = None
        if database and collection:
            self.collection = self.db[collection]
        else:
            self.collection = None
        #print "i am in mongodb", self.collection
        
    def send(self, data):
        """
        """
        try:
            if self.collection:
#                self.collection.save(data)
                self.collection.insert(data)
        except Exception as e:
            log.logger.exception(e)
            return False
        return True
    
    def close(self):
        """
        """
        self.conn.close()
        self.conn = None


class RedisPipeline(object):
    """
    连接到redis数据库
    """
    def __init__(self, uri):
        """
        """
#         import redis
#         self.db = redis.StrictRedis.from_url(uri)
        import data_buffer
        self.db = data_buffer.create(uri)
        
    def send(self, data):
        """
        """
        if isinstance(data, dict):
            try:
                self.db.push(data)
            except Exception as e:
                return False
            return True
        elif isinstance(data, list):
            try:
                self.db.pushall(data)
            except Exception as e:
                return False
            return True
    
    def close(self):
        """
        """
#        self.db.close()
        self.db = None

class DataQueuePipeline(object):
    """
    操作data_queue的对象
    """
    def __init__(self, uri):
        """
        """
        import data_queue
        
        url = urlparse.urlparse(uri)
        host = url.hostname
        port = url.port or 27017
        try:
            path = url.path.strip('/')
            i = path.index('.')
        except Exception:
            self.db = path
        else:
            self.db = path[:i]
            self.collection = path[i+1:]
            print self.db, self.collection
        
        try:
            self.data_queue_sender =  data_queue.Deliver(data_queue.opt.PUSH)
            self.data_queue_sender.connect(host, port)
        except Exception as e:
            log.logger.error("init data_queue_sender failed: %s"%e)
            raise e
        #print host, port
        
    def send(self, data):
        """
        """
        if self.db and self.collection:
            return self.data_queue_sender.send({'db':self.db,
                                                 'collection':self.collection,
                                                 'data':data})
        else:
            return self.data_queue_sender.send(data)
    
    def close(self):
        """
        """
        self.data_queue_sender.close()

#mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
def from_url(uri):
    """
    以uri形式连接数据库，并返回相应可以操作数据库的对象
    """
    if uri.startswith('zmq://'):
        
        return DataQueuePipeline(uri)
    
    elif uri.startswith('mongodb://'):
        
        return MongoPipeline(uri)
    
    elif uri.startswith('mysql://'):
        
        return MysqlPipeline(uri)
    
    elif uri.startswith('redis://'):
        return RedisPipeline(uri)
    else:
        raise Exception('unknow uri <{}>'.format(uri))

    return None

def get_type_str(instance):
    '''获取实例的类型名字'''
    m = re.search("\'([^\']+)", repr(type(instance)))
    return m.group(1).split('.')[-1] if m else ''


def utc_datetime(data):
    '''
    把data转换为日期时间，时区为东八区北京时间，能够识别：今天、昨天、5分钟前等等，如果不能成功识别，则返回datetime.datetime.utcnow()
    '''
    dt = None
    utc_dt = None
    #2013年8月15日 22:46
    if re.search(r'''\s*(\d+)年(\d+)月(\d+)日\s+(\d+):(\d+)\s*''',data):
        dt = datetime.datetime.strptime(data, "%Y年%m月%d日 %H:%M")
    #11秒前
    elif re.search("(\d+)秒前", data):
        minutes = int(re.findall("(\d+)秒前", data)[0])
        dt = datetime.datetime.now() - datetime.timedelta(seconds=minutes)
        str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
    #29分钟前
    elif re.search("(\d+)分钟前", data):
        minutes = int(re.findall("(\d+)分钟前", data)[0])
        dt = datetime.datetime.now() - datetime.timedelta(seconds=minutes*60)
        str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
    #2小时前
    elif re.search("(\d+)小时前", data):
        hours = int(re.findall("(\d+)小时前", data)[0])
        dt = datetime.datetime.now() - datetime.timedelta(hours=hours)
        str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")
    #2天前
    elif re.search("(\d+)天前", data):
        days = int(re.search("(\d+)天前", data).group(1))
        dt = datetime.datetime.now() - datetime.timedelta(days=days)
        str_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d %H:%M:%S")

    #01月03日 11:16
    elif re.match("\s*(\d+)月(\d+)日\s+(\d+)[:：]+(\d+)\s*", data):
        dt = TimeDeltaYears(datetime.date.today().year - 1900, datetime.datetime.strptime(data, "%m月%d日 %H:%M"))

    #2014年5月11日
    elif re.search("\s*(\d+)年(\d+)月(\d+)日", data):
        m = re.search("\s*(\d+)年(\d+)月(\d+)日", data)
        try:
            dt = datetime.datetime.strptime("{}-{}-{}".format(m.group(1), m.group(2), m.group(3)), "%Y-%m-%d")
        except:
            dt = datetime.datetime.strptime("{}-{}-{}".format(m.group(1), m.group(2), m.group(3)), "%y-%m-%d")

    #5月11日
    elif re.search("\s*(\d+)月(\d+)日", data):
        m = re.search("\s*(\d+)月(\d+)日", data)
        dt = TimeDeltaYears(datetime.date.today().year - 1900, datetime.datetime.strptime("{}-{}".format(m.group(1), m.group(2)), "%m-%d"))
    #今天 15:42  今天15:42 
    elif re.search("今天\s*(\d+):(\d+)", data):
        days = datetime.date.today() - datetime.date(1900, 1, 1)
        m = re.search("今天\s*(\d+):(\d+)", data)
        dt = datetime.datetime.strptime('{}:{}'.format(m.group(1), m.group(2)), "%H:%M")  + datetime.timedelta(days=days.days)

    #昨天 15:42
    elif re.search("昨天\s*(\d+):(\d+)", data):
        days = datetime.date.today()- datetime.timedelta(days=1) - datetime.date(1900, 1, 1)
        m = re.search("昨天\s*(\d+):(\d+)", data)
        dt = datetime.datetime.strptime('{}:{}'.format(m.group(1), m.group(2)), "%H:%M")  + datetime.timedelta(days=days.days)

    #前天  10:41
    elif re.search("前天\s*(\d+):(\d+)", data):
        days = datetime.date.today()- datetime.timedelta(days=2) - datetime.date(1900, 1, 1)
        m = re.search("前天\s*(\d+):(\d+)", data)
        dt = datetime.datetime.strptime('{}:{}'.format(m.group(1), m.group(2)), "%H:%M")  + datetime.timedelta(days=days.days)

    elif re.match("\s*(\d+)[-/](\d+)[-/](\d+)\s+(\d+):(\d+):(\d+)\s*",  data): #2013-11-11 13:52:35 #2013/11/11 13:52:35
        data = re.sub('/', '-', data)
        try:
            dt = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        except:
            dt = datetime.datetime.strptime(data, "%y-%m-%d %H:%M:%S")
    
    elif re.match("\s*(\d+)[-/](\d+)[-/](\d+)\s+(\d+):(\d+)\s*",  data): #2013-11-11 13:52 #2013/11/11 13:52
        data = re.sub('/', '-', data)
        try:
            dt = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
        except:
            dt = datetime.datetime.strptime(data, "%y-%m-%d %H:%M")
    
    #7/3
    elif re.match("\s*(\d+[/-]\d+)", data):
        year = datetime.datetime.now().year
        m = re.compile("(\d+)[/-](\d+)").search(data)
        month = int(m.group(1))
        day = int(m.group(2))
        dt = datetime.datetime(year,month, day)
    else:
        log.logger.debug("错误，datetime，没有解析成功, %s"%data)
        return datetime.datetime.utcnow()
     
    utc_dt = dt - datetime.timedelta(seconds=28800)
    return utc_dt

def R(x):
    return colored(x, 'red',    attrs=['bold'])
def G(x):
    return colored(x, 'green',  attrs=['dark', 'bold'])
def B(x):
    return colored(x, 'blue',   attrs=['bold'])
def Y(x):
    return colored(x, 'yellow', attrs=['dark', 'bold'])

def RR(x):
    return colored(x, 'white', 'on_red',    attrs=['bold'])
def GG(x):
    return colored(x, 'white', 'on_green',  attrs=['dark', 'bold'])
def BB(x):
    return colored(x, 'white', 'on_blue',   attrs=['bold'])
def YY(x):
    return colored(x, 'white', 'on_yellow', attrs=['dark', 'bold'])


def save_log(uri, key, data):
    try:
        conn = redis.StrictRedis.from_url(uri)
        data = json.dumps(data)
        conn.lpush(key, data)
        conn.ltrim(key, 0, 999)
    except Exception as e:
        log.logger.exception(e)
    return 

def save_monitor_log(uri, data):
    #duanyifei 2016-5-23
    try:
        data = copy.deepcopy(data)
        data.update({"config_id":int(data['config_id'])})
        mongo_client = from_url(uri)
        mongo_client.send(data)
    except Exception as e:
        log.logger.exception(e)
        log.logger.error(data)
        log.logger.error(u"保存模版监测信息失败")
    #duanyifei 2016-5-23
    return

def fromtimestamp(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp)) - datetime.timedelta(hours=8)


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num
    
def mid_to_url(midint):
    '''
    '''
    midint = str(midint)[::-1]
    size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
    result = []
    for i in range(size):
        s = midint[i * 7: (i + 1) * 7][::-1]
        s = base62_encode(int(s))
        s_len = len(s)
        if i < size - 1 and len(s) < 4:
            s = '0' * (4 - s_len) + s
        result.append(s)
    result.reverse()
    return ''.join(result)

def url_to_mid(url):
    '''
    '''
    url = str(url)[::-1]
    size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))

conn_pool = redis.ConnectionPool(host='192.168.110.130', port=6379, db=3)
connection = redis.StrictRedis(connection_pool=conn_pool)

def get_keywords(key_start, limits, connection=connection, key_keywords=None):
    '''
    '''
    if key_keywords is None:
        key_keywords = 'all_user_keywords'
    
    start = connection.get(key_start)
    if start is None:
        start = 0
    else:
        start = int(start)
    
    len = connection.llen(key_keywords)
    if len == 0:
        return []
#    elif len == 1:
#        return [connection.lindex(key_keywords, 0)]
    
    if start >= len:
        start = 0
        new_start = (start + limits) % len
        end = new_start - 1
        connection.set(key_start, new_start)
        return connection.lrange(key_keywords, start, end)
    else:
        if start + limits <= len:
            new_start = (start + limits) % len
            end = new_start - 1
            connection.set(key_start, new_start)
            return connection.lrange(key_keywords, start, end)
        elif start + limits <= 2 * len:
            new_start = (start + limits) % len
            end = new_start - 1
            connection.set(key_start, new_start)
            return connection.lrange(key_keywords, start, -1) + connection.lrange(key_keywords, 0, end)
        else:
            return connection.lrange(key_keywords, start, -1)


def canonicalize_url(url, keep_fragment=True):
    """
    规范化url:对url中的query字段重新排序，
    避免http://xxx.com/123.html?b=1&a=3和http://xxx.com/123.html?a=3&b=1作为两个url存在
    """
    import urllib
    uri = urlparse.urlsplit(url)
    query_args = urlparse.parse_qsl(uri.query,True)
    query_args.sort()
    query_args = urllib.urlencode(query_args)
    if keep_fragment:
        return urlparse.urlunsplit((uri.scheme, uri.netloc, uri.path, query_args, uri.fragment))
    else:
        return urlparse.urlunsplit((uri.scheme, uri.netloc, uri.path, query_args, ''))


def get_verify_code(img_name, type, url='http://192.168.100.108/vcode/test.php'):
    '''
    获取验证图片中的信息,如果获取验证信息成功，将该图片删除
    img_name:图片名称，包含路径信息
    '''
    verify_code = ''
    if os.path.exists(img_name):
        #url = "http://192.168.2.79/dama2_http_api_demo/test.php"
        #url = "http://192.168.100.112/vcode/test.php"
        #url = 'http://192.168.100.108/vcode/test.php'
        with open(img_name, 'rb') as f:
            content = f.read()
            data = {
                "code":content,
                "type":type,
                }
            try:
                resp = requests.post(url, data)
                verify_code = resp.content
                print "---resp:", verify_code
            except Exception as e:
                log.logger.error("--get_verify_code() : %s"%e)
        #if verify_code and verify_code != 'EEEF':
        # try:
        #     os.remove(img_name)
        # except:
        #     pass
    return verify_code


def retry(ExceptionToCheck, tries=3, delay=1, backoff=1):
    """
    函数重试装饰器
    参数ExceptionToCheck表示当该异常发生时，重新下载该网页
    参数tries表示最大重试次数
    参数delay表示初始等待重试间隔
    参数backoff表示时间间隔系数；每重试一次，时间间隔乘以该参数
    """
    def deco_retry(func):
        def wrapper(self, *args, **kwargs):
            mtries, mdelay = tries, delay
            count = 0
            while mtries > 0:
                try:
                    count += 1
                    kwargs.get('retries',{}).update({'count':count})
                    return func(self, *args, **kwargs)
                except ExceptionToCheck, e:
                    #print "%s, Retrying in %d seconds..."%(str(e), mdelay)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
                    lastException = e
            #print "exception : %s"%lastException
            raise lastException
        return wrapper # true decorator
    return deco_retry

@retry(Exception, 3, 2)
def _get_proxy_by_adsl(adsl_id=None, config_id=None):
    '''
    '''
    proxy = ''
    if adsl_id and config_id:
        proxy_url = "http://192.168.67.51:8080/proxy/get?adsl_id=%s&config_id=%s"%(adsl_id, config_id)
        try:
            resp = requests.get(proxy_url, timeout=15)
            proxy = resp.content
        except Exception as e:
            #print "--get_proxy_by_mid(mid=%s, sid=%s) failed: %s"%(mid, sid, e)
            raise e
        if not proxy:
            raise ValueError
    return proxy

def get_proxy_by_adsl(adsl_id, config_id):
    '''
    '''
    try:
        resp = _get_proxy_by_adsl(adsl_id, config_id)
    except Exception as e:
        log.logger.error("--get_proxy_by_adsl(adsl_id=%s, config_id=%s) failed: %s"%(adsl_id, config_id, e))
        resp = ''
    return resp

def release_proxy_by_adsl(adsl_id, config_id=None):
    '''
    '''
    try:
        url = "http://192.168.67.51:8080/proxy/release?adsl_id=%s&config_id=%s"%(adsl_id, config_id)
        resp = requests.get(url)
        return resp.content
    except:
        pass
    return '0'

def scp_img(src='', name='', dest='http://192.168.70.60/img.php', retries=3):
    '''
    send image to dest host
    '''
    if src:
        while retries>0:
            retries -= 1
            try:
                if not name:
                    name = os.path.basename(src)
                content = ''
                with open(src, 'rb') as f:
                    content = f.read()
                data = {
                    'name':name,
                    'content':content,
                }
                #print "name: ", name
                resp = requests.post(dest, data)
                print resp.content
                resp = json.loads(resp.content)
                if resp.get('path', ''):
                    return resp
            except Exception as e:
                log.logger.error("--scp_img failed: src:%s, Exception:%s"%(src, e))
                print "--scp_img() failed: %s"%e
    return {}


if __name__ == "__main__":
#    print is_re_match("aa", "oooooo")
#     print TimeDeltaYears(1)
#     uri = "mongodb://192.168.110.9/data.ba_names"
#     sender = from_uri(uri)
#     data = {'url':'pangwei', 'status':1}
#     res = sender.send(data)
#     sender.close()
#     print res
    #redis
#     uri = "redis://127.0.0.1:6379/0/dtianya"
#     uri = 'redis://192.168.100.15/4/data'
#     sender = from_url(uri)
#     import time
#     start = time.time()
#     data = {
#             'title':'title',
#             'content':'content',
#             'url':'http//www.python.org/p/123456',
#             'ctime':datetime.datetime(2014,8,14,01, 01),
#             'gtime':datetime.datetime(2014,8,14,06, 18),
#             'source':'pw',
#             'info_flag':'02',
#             'siteName':'hello'
#             }
# #     for i in xrange(10000):
# #         res = sender.send({'id':i})
#     res = sender.send(data)
#     sender.close()
#     print res
#     print "costs : ", time.time() - start

    #data queue
#     uri = "zmq://192.168.110.10:45000/data.ba_names"
#     try:
#         sender = from_uri(uri)
#         res = sender.send({'url':'pangwei', 'ctime':datetime.datetime.utcnow()})
#     except Exception as e:
#         print e
#     else:
#         sender.close()
#     print res

#     uri = "zmq://192.168.110.10:45000/data.tieba"
#     try:
#         sender = from_uri(uri)
#         res = sender.send({'config_id':'pangwei', 'job_id':1})
#     except Exception as e:
#         print e
#     else:
#         sender.close()
#     print res


#     uri = "zmq://192.168.100.7:10000"
#     data = {'info_flag':'02', 'config_id':1, 
#             'source':'pangwei', 'siteName':'baidu', 'channel':'pangwei',
#             'title':'hello', 'content':'asfdasdf---***---asdf',
#             'url':'http://www.baidu.com',
#             'ctime':datetime.datetime.utcnow(),
#             'gtime':datetime.datetime.utcnow()
#             }
#     try:
#         sender = from_url(uri)
#         res = sender.send(data)
#         print res
#     except Exception as e:
#         print e
#     else:
#         sender.close()
#     print res
#     pass
    
#     uri = 'redis://192.168.110.110/8'
# #     save_log(uri, '345', {'config_id':345})
#     save_log(uri, '345', {'config_id':345})
#     save_log(uri, '345', {'config_id':346})
#     save_log(uri, '345', {'config_id':347})
#     mid = '3743906829572599'
#     key = mid_to_url(mid)
#     print "key: ", key
#     import cPickle as pickle
#     uri = 'redis://192.168.100.15/4'
#     conn = redis.StrictRedis.from_url(uri)
#     d_s = conn.rpop('weibo')
#     print "dumps: ", d_s
#     l_s = pickle.loads(d_s)
#     print "loads: ", l_s
    
#     print url_to_mid('CzthYDMNb')
#     print url_to_mid('Czrnc70x4')
# #    print mid_to_url('C6eFSxwfT')
#    url = 'http://www.baidu.com/p?c=3&a=1####0_1'
    #url = 'http://bbs.tianya.cn/post-828-254117-1.shtml####0_1'
#    print canonicalize_url(url)
    
    #print get_verify_code('d:\\temp\\genimg.jpg', 62, 'kronus', 'zhxg130809')
#    print get_verify_code('d:\\tmp\\qq.jpg', 19)
    
    #print os.path.abspath(sys.path[0])
#     resp = get_proxy_by_adsl(6, 1)
#     proxy = resp
#     if proxy:
#         print "---: ", proxy, type(proxy), json.loads(proxy)
#     else:
#         print "--not proxy"
    # t = time.time()
    # print '--start .....'
    print  scp_img("E:\\eclipse\\spider\\spider\\success_img\\1.jpg")
    # print '---stop .... , total costs:', time.time() - t

    #
#     url = 'http://data.auto.sina.com.cn/hello?b=1&a=2#abc'
#     print canonicalize_url(url, False)
