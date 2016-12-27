#coding:utf8
# from django.shortcuts import render

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from appWeibo.serializers import UserSerializer
from rest_framework.response import Response
import re
import redis
import datetime
import ssdb
import requests
import json
from collections import defaultdict
import cPickle as pickle


server_host = '192.168.132.93:8000'
#server_host = 'localhost:8000'

_list = list

def transform_time_str(timestamp):
    h = timestamp / 3600
    m = timestamp % 3600 / 60
    s = timestamp % 60
    return "%s:%s:%s"%(h,m,s)

class LogKey(object):
    def __init__(self, key):
        self.datetime = None
        self.flag = ''
        self.key = key
        self.parse_key()
    
    def parse_key(self):
        if re.search('^(\d+_\d+_\d+_\d+)-', self.key):
            self.datetime = datetime.datetime.strptime(re.search('^(\d+_\d+_\d+_\d+)-', self.key).group(1), "%Y_%m_%d_%H")
        elif re.search('^(\d+_\d+_\d+)-', self.key):
            self.datetime = datetime.datetime.strptime(re.search('^(\d+_\d+_\d+)-', self.key).group(1), "%Y_%m_%d")
        else:
            pass
        self.flag = self.key.split('-')[-1]
        return

class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    redisWeiboHost = '192.168.187.56'

    def list(self, request):
        redisWeibo = redis.StrictRedis(host=self.redisWeiboHost, port=6379, db=5)
        pipe = redisWeibo.pipeline()
        
        uids = request.query_params
        uids = uids.get('uids')
        uids = uids.split(',')
        
        for item in uids:
            pipe.hget('h_uids_info',item)
        info = pipe.execute()

        querysets = []
        for i,item in enumerate(info):
            uid = uids[i]
            if item:
                li = item.split('#')
                status_count = int(li[0]) if len(li)>0 else -1
                timestamp = int(li[1]) if len(li)>1 else -1
                lid = int(li[2]) if len(li)>2 else -1
                querysets.append({
                    'uid': uid,
                    'status_count':status_count,
                    'timestamp':timestamp,
                    'lid':lid
                })
            else:
                querysets.append({
                    'uid': uid,
                    'status_count':-1,
                    'timestamp':-1,
                    'lid':-1
                })
        return Response(querysets)
        

class ListViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    redisWeiboHost = '192.168.187.56'
    ssdbHost = '192.168.110.85'
    def list(self, request):
        redisWeibo = redis.StrictRedis(host = self.redisWeiboHost, port = 6379, db = 5)
        ssdbWeibo = ssdb.SSDB(host = self.ssdbHost, port = 8888)

        pipe = redisWeibo.pipeline()
        
        querysets = defaultdict(dict)
        names = ['l_uids_hot_60d','l_uids_hot_zombie','l_uids_10d','l_uids_60d']#,'list_weibo_uids_zombie']
        
        for key in names:
            pipe.llen(key)
        info = pipe.execute()
        
        for key, num in zip(names, info):
            querysets[key].update({'size':num})
        
        zombie_num = ssdbWeibo.qsize('list_weibo_uids_zombie')
        querysets['list_weibo_uids_zombie'].update({'size':zombie_num})
        
        zombie_num = ssdbWeibo.qsize('list_weibo_uids_real_zombie')
        querysets['list_weibo_uids_real_zombie'].update({'size':zombie_num})        
        
        
        names = ['l_uids_hot_60d','l_uids_hot_zombie','l_uids_10d','l_uids_60d','list_weibo_uids_zombie', 'list_weibo_uids_real_zombie']
        for key in names:
            key += '_log'
            pipe.lrange(key, 0, -1)
        info = pipe.execute()
        for id, key, time_list in zip(range(len(names)), names, info):
            if not time_list:
                time_list = [0]
            interval = map(lambda x,y: int(x) - int(y), time_list[:-1], time_list[1:])
            last_date = datetime.datetime.fromtimestamp(int(time_list[0])).strftime("%Y-%m-%d %H:%M:%S")
            querysets[key].update({
                               "interval":interval,
                               "id":id,
                               "last_date":str(last_date),
                                })
        return Response(querysets)
    

    def getListLog(self,pipe,lid,date = None):
        if not date:
            date = datetime.datetime.today()
        field = "%s_%s_%s-update_count_%s"%(date.year, date.month, date.day,lid)
        pipe.hget('h_log',field)

class DailyRecordViewSet(viewsets.ViewSet):
    redisWeibo = redis.StrictRedis.from_url("redis://192.168.187.55:6379/15")
    def list(self, request):
        result = []
        now = datetime.datetime.now()
        oneday = datetime.timedelta(days=1)
        for i in range(60):
            result.append({"date":now.strftime("%Y-%m-%d"),
                           "num":self.redisWeibo.hget(now.strftime("%Y%m%d"), "weibo.com")})
            now = now - oneday
        return Response(result)

class LogViewSet(viewsets.ViewSet):
    redisWeiboHost = '192.168.187.56'
    key_log = 'h_log'
    key_old_log = 'h_log_old'
    def list(self, request):
        
        def _hmget(conn, keys):
            result = {}
            if not keys:
                return result
            values = conn.hmget(self.key_log, *keys)
            old_keys = []
            #先从最新日志中取
            for key, value in zip(keys, values):
                if not value:
                    old_keys.append(key)
                else:
                    result.update({key:int(value)})
            #从3天前日志中取
            if old_keys:
                values = conn.hmget(self.key_old_log, *old_keys)
                for key, value in zip(old_keys, values):
                    result.update({key:int(value) if value else 0})
            return result
        
        def get_log_name(max_days, is_hour=True, flags=[], prefix=''):
            date = datetime.datetime.today()
            oneday = datetime.timedelta(days=1)            
            keys = []
            for i in range(max_days):
                for flag in flags:
                    if is_hour:
                        for hour in range(24):
                            key = '{date.year}_{date.month}_{date.day}_{hour}-{prefix}{flag}'.format(**{"date":date, "hour":hour, "flag":flag, "prefix":prefix})
                            keys.append(key)
                    else:
                        key = '{date.year}_{date.month}_{date.day}-{prefix}{flag}'.format(**{"date":date, "flag":flag, "prefix":prefix})
                        keys.append(key)
                date = date - oneday
            return keys
        
        def get_queryset(max_days, is_hour=True, flags=[], prefix='', dict_level=1, description='', is_flag=True):
            '''
            @max_days   控制取出日志的时间
            @is_hour    控制取出日志是按照小时还是日期取
            @flags      日志键名标志， 一般有多个
            @prefix     日志键名前缀
            @dict_level 数据格式嵌套深度
            @description
            @is_flag    控制数据汇总的时候按照flag还是小时
            '''
            keys = get_log_name(max_days, is_hour=is_hour, flags=flags, prefix=prefix)
            result = _hmget(redisWeibo, keys)
            keys = [LogKey(key) for key in keys]
            if dict_level == 0:
                querysets = defaultdict(int)
                for key in keys:
                    querysets[str(key.datetime.date())] += result.get(key.key)
            if dict_level == 1:
                querysets = defaultdict(lambda : defaultdict(int))
                for key in keys:
                    querysets[str(key.datetime.date())]['total'] += result.get(key.key)
                    if is_flag:
                        querysets[str(key.datetime.date())][str(key.flag)] += result.get(key.key)
                    else:
                        querysets[str(key.datetime.date())][str(key.datetime.hour)] += result.get(key.key)
            querysets = {'data': querysets, 'description': description}
            return querysets
        
        redisWeibo = redis.StrictRedis.from_url("redis://%s:6379/5"%self.redisWeiboHost)
        
        if not request.query_params:
            querysets = {
                "update":"http://%s/log?type=update&days=3"%server_host,
                "page":"http://%s/log?type=page&days=3"%server_host,
                "get_page":"http://%s/log?type=get_page&days=3"%server_host,
                "success_page":"http://%s/log?type=success_page&days=3"%server_host,
                "empty_page":"http://%s/log?type=empty_page&days=3"%server_host,
                "retry_page":"http://%s/log?type=retry_page&days=3"%server_host,
                "api":"http://%s/log?type=api&days=3"%server_host,
                "new":"http://%s/log?type=new&days=3"%server_host,
                "new2":"http://%s/log?type=new2&days=3"%server_host,
                "special_push":"http://%s/log?type=special_push&days=3"%server_host,
                "valide":"http://%s/log?type=valide&days=3"%server_host,
                "wyq_weibo_count":"http://%s/log?type=wyq_weibo_count&days=3"%server_host,
                "queue_length":"http://%s/log?type=queue_length&days=3"%server_host,
                "analyze_page":"http://%s/log?type=analyze_page&days=3"%server_host,
                "discard_weibo":"http://%s/log?type=discard_weibo&days=3"%server_host,
                "topic_weibo_comment":"http://%s/log?type=topic_weibo_comment&days=3"%server_host,
                "api_fail_count":"http://%s/log?type=api_fail_count&days=3"%server_host,
                "longtext_count":"http://%s/log?type=longtext_count&days=3"%server_host,
                         }
            return Response(querysets)
        
        _type = request.query_params.get('type')
        max_days = request.query_params.get('days')
        max_days = int(max_days) if max_days else 5
        #max_days = max_days if max_days < 10 else 10
        
        querysets = None
        if _type == 'update':
            '''?type=update&days=2'''
            flags = ['update_count_0','update_count_1','update_count_2','update_count_3','update_count_4', 'update_count_5']
            querysets = get_queryset(max_days, flags=flags, description=u'探测到发帖总量', dict_level=1)
        
        if _type == 'page':
            '''?type=page&days=2'''
            flags = ['page_count_0','page_count_1','page_count_2','page_count_3','page_count_4', 'page_count_5']
            querysets = get_queryset(max_days, flags=flags, description=u'探测到发帖总页码', dict_level=1, is_flag=False)

        if _type == 'success_page':
            '''?type=success_page&days=2'''
            flags = ['success_page_count']
            querysets = get_queryset(max_days, flags=flags, description=u'下载成功页面数', dict_level=1, is_flag=False)
        
        if _type == 'longtext_count':
            '''?type=longtext_count&days=2'''
            flags = ['longtext_count']
            querysets = get_queryset(max_days, flags=flags, description=u'longtext_count', dict_level=1, is_flag=False)

        if _type == 'empty_page':
            '''?type=empty_page&days=2'''
            flags = ['empty_page_count']
            querysets = get_queryset(max_days, flags=flags, description=u'下载成功页面中空白页面数', dict_level=1, is_flag=False)

        if _type == 'retry_page':
            '''?type=retry_page&days=2'''
            flags = ['retry_page_count']
            querysets = get_queryset(max_days, flags=flags, description=u'下载失败重试页面数', dict_level=1, is_flag=False)

        if _type == 'get_page':
            '''?type=get_page&days=2'''
            flags = ['get_page_count']
            querysets = get_queryset(max_days, flags=flags, description=u'取到页面数', dict_level=1, is_flag=False)
                
        if _type == 'api':
            '''?type=api&days=2'''
            flags= ['l_uids_new', 'l_uids_candidate', 'l_new_uids_validated', 'l_uids_10d', 'l_uids_60d', 'list_weibo_uids_zombie', 'list_weibo_uids_real_zombie', 'l_uids_hot_60d', 'l_uids_hot_zombie', 
                    'comment', 'comment_detect', 'repost_detect', 'comment_topic', 'lost_detect']
            querysets = get_queryset(max_days, flags=flags, prefix='api_use_count_', description=u'api使用记录', dict_level=1)
        if _type == 'api_fail_count':
            flags = ['api_fail_count']
            querysets = get_queryset(max_days, flags=flags, description=u'api失败次数记录', dict_level=1, is_flag=False)            
        if _type == 'new':
            '''?type=new&days=2'''
            flags = ['new_uid']
            querysets = get_queryset(max_days, flags=flags, is_hour=False, description=u'新帐号发现 第一策略', dict_level=0)
        
        if _type == 'new2':
            '''?type=new2&days=2'''
            flags = ['new_1_day_uid']
            querysets = get_queryset(max_days, flags=flags, description=u'新帐号发现 第二策略', dict_level=1, is_flag=False)

        if _type == 'special_push':
            '''?type=special_push&days=2'''
            flags = ['special_push_count']
            querysets = get_queryset(max_days, flags=flags, description=u'特殊帐号 push', dict_level=1, is_flag=False)

        if _type == 'valide':
            '''?type=valide&days=2'''
            flags = ['valide']
            querysets = get_queryset(max_days, flags=flags, description=u'valide微博数量', dict_level=1, is_flag=False)
            
        if _type == 'wyq_weibo_count':
            '''?type=valide&days=2'''
            flags = ['wyq_weibo_count']
            querysets = get_queryset(max_days, flags=flags, description=u'微舆情微博数量', dict_level=1, is_flag=False)        
        
        if _type == 'discard_weibo':
            flags = ['discard_weibo_count']
            querysets = get_queryset(max_days, flags=flags, description=u'丢弃微博数量微博数量', dict_level=1, is_flag=False)
        
        if _type == 'queue_length':
            '''?type=valide&days=2'''
            queue_name = request.query_params.get('name')
            querysets = {}
            description=u'采集队列长度'
            flags = ['l_uids_10d', 'l_uids_60d', 'l_uids_hot_60d', 'l_uids_hot_zombie', 'l_uids_hot_special', 'l_uids_special', 'list_weibo_uids_zombie', 'l_uids_candidate', 'l_uids_new', 'list_weibo_uids_real_zombie']
            for flag in flags:
                if not queue_name:
                    pass
                else:
                    if flag != queue_name:
                        continue
                temp_querysets = get_queryset(max_days, flags=[flag], dict_level=1, is_flag=False, prefix='queue_length_')
                data = temp_querysets.get('data')
                querysets.update({flag:data})
            querysets = {'data':querysets, 'description':description}
            
        if _type == 'analyze_page':
            all_page = requests.get('http://%s/log?type=page&days=%s'%(server_host, max_days)).json()
            get_page = requests.get('http://%s/log?type=get_page&days=%s'%(server_host, max_days)).json()
            success_page = requests.get('http://%s/log?type=success_page&days=%s'%(server_host, max_days)).json()
            empty_page = requests.get('http://%s/log?type=empty_page&days=%s'%(server_host, max_days)).json()
            retry_page = requests.get('http://%s/log?type=retry_page&days=%s'%(server_host, max_days)).json()
            push_page = requests.get('http://%s/log?type=special_push&days=%s'%(server_host, max_days)).json()
            querysets = defaultdict(dict)
            for date in all_page['data'].keys():
                for hour in range(24):
                    hour = str(hour)
                    querysets[date][hour] = {
                        'all':all_page['data'][date][hour],
                        'get':get_page['data'][date][hour],
                        'success':success_page['data'][date][hour],
                        'empty':empty_page['data'][date][hour],
                        'retry':retry_page['data'][date][hour],
                        'push':push_page['data'][date][hour],
                    }
                    querysets[date][hour].update({
                        "all+push-success":querysets[date][hour]['all'] + querysets[date][hour]['push'] - querysets[date][hour]['success']
                    })
            querysets = {'data': querysets, 'description': ''}
        
        if _type == 'topic_weibo_comment':
            flags = ['topic_weibo_count']
            querysets = get_queryset(max_days, flags=flags, description=u'topic_weibo_comment 微博数量', dict_level=1, is_flag=False)
        
        return Response(querysets)

class RedisViewSet(viewsets.ViewSet):
    redisWeiboHost = '192.168.187.56'
    def list(self, request):
        redisWeibo = redis.StrictRedis.from_url("redis://%s:6379/5"%self.redisWeiboHost)
        info = redisWeibo.info()
        return Response(info)

class SpiderViewSet(viewsets.ViewSet):
    redisWeiboHost = '192.168.187.56'
    def list(self, request):
        redisWeibo = redis.StrictRedis.from_url("redis://%s:6379/5"%self.redisWeiboHost)
        _type = request.query_params.get('type')
        if not request.query_params:
            querysets = {
                "direct":"http://%s/spider?type=direct"%server_host,
                         }
            return Response(querysets)
        result = None
        if _type == 'direct':
            result = []
            spider_list = redisWeibo.zrange('z_spider_log', 0, -1, withscores=True)
            spider_id_list = [x[0] for x in spider_list]
            spider_config_list = redisWeibo.hmget('h_log_spider_config', *spider_id_list)
            for spider, config in zip(spider_list, spider_config_list):
                config = pickle.loads(config)
                proxy = config.get('http', 'proxy_url')
                result.append({
                    "spider_id":spider[0] + '-' + proxy.split('/')[-1].strip(".txt").strip('proxy'),
                    "num":spider[1],
                    "proxy":proxy,
                     })
                result.sort(key=lambda x: x['num'])
        return Response(result)
