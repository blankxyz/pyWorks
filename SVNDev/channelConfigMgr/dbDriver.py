# coding=utf-8
from pprint import pprint
import os, time, datetime
import pymongo
import redis
import json
import copy

from .setting import REDIS_SERVER, MONGODB_SERVER, MONGODB_PORT


# REDIS_SERVER = 'redis://127.0.0.1/8'
# MONGODB_SERVER = '192.168.16.223'
# MONGODB_PORT = 37017

# MONGODB_SERVER = '127.0.0.1'
# MONGODB_PORT = 27017


class RedisDriver(object):
    def __init__(self):
        self._conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.task_pre = "hash_channel_spider:"
        self.spider_60_hash_key = "hash_channel_spider:60"
        self.spider_300_hash_key = "hash_channel_spider:300"
        self.spider_900_hash_key = "hash_channel_spider:900"
        self.test_key = "list_channel_spider_task_test"
        self.test_url_result_key = 'hash_channel_spider_result_test'
        self.test_result_pre = 'list_channel_spider_result_test_'
        self.info_flag_options_hash_key = 'hash_options:info_flag'
        self.dedup_uri_options_hash_key = 'hash_options:dedup_uri'
        self.data_db_options_hash_key = 'hash_options:data_db'

    def get_task_draw(self):
        cnt_list = []
        task_list = ['60', '300', '900']
        for task in task_list:
            cnt = self._conn.hlen(self.task_pre + task)
            cnt_list.append(cnt)
        return cnt_list, task_list

    def init_options(self):
        INFO_FLAG_OPTIONS = [
            {'text': '新闻', 'value': '01'},
            {'text': '论坛', 'value': '02'},
            {'text': '博客', 'value': '03'},
            {'text': '新浪微博', 'value': '0401'},
            {'text': '腾讯微博', 'value': '0402'},
            {'text': '平煤', 'value': '05'},
            {'text': '微信', 'value': '06'},
            {'text': '视频', 'value': '07'},
            {'text': '长微博', 'value': '08'},
            {'text': 'APP', 'value': '09'},
            {'text': '评论', 'value': '10'},
            {'text': '搜索', 'value': '99'}
        ]
        for i in INFO_FLAG_OPTIONS:
            self._conn.hset(self.info_flag_options_hash_key, i['text'], i['value'])

        DEDUP_URI_OPTIONS = [
            {'text': '贴吧', 'value': 'redis://redis-dupweibo-1.istarshine.net.cn:6379/0/tieba_dedup'},
            {'text': '微博', 'value': 'redis://redis-dupweibo-1.istarshine.net.cn:6379/0/sina_dedup'},
            {'text': '行业', 'value': 'redis://redis-dupweibo-1.istarshine.net.cn:6379/0/industry_dedup'},
            {'text': '腾讯微博', 'value': 'redis://redis-dupweibo-1.istarshine.net.cn:6379/0/qq_dedup'},
            {'text': '秘书', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/dedup'},
            {'text': '海外', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/oversea_dedup'},
            {'text': '话题', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/topic_dedup'},
            {'text': '全站', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/allsite_dedup'},
            {'text': '问答', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/ask_dedup'},
            {'text': '行业汽车', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/car_dedup'},
            {'text': '行业金融', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/money_dedup'},
            {'text': '行业旅游', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/travel_dedup'},
            {'text': '政策', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/policy_dedup'},
            {'text': '招标', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/bidding_dedup'},
            {'text': '外文', 'value': 'redis://redis-dupurl-1.istarshine.net.cn:6379/0/foreignlang_dedup'}
        ]
        for i in DEDUP_URI_OPTIONS:
            self._conn.hset(self.dedup_uri_options_hash_key, i['text'], i['value'])

        DATA_DB_OPTIONS = [
            {'text': '腾讯微博', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/qq_data'},
            {'text': '贴吧', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/tieba_data'},
            {'text': '微博', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/sina_data'},
            {'text': '行业', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/industry_data'},
            {'text': '秘书', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/data'},
            {'text': '海外', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/oversea_data'},
            {'text': '话题', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/topic_data'},
            {'text': '全站', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/allsite_data'},
            {'text': '问答', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/ask_data'},
            {'text': '行业汽车', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/car_data'},
            {'text': '行业金融', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/money_data'},
            {'text': '行业旅游', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/travel_data'},
            {'text': '政策', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/policy_data'},
            {'text': '招标', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/bidding_data'},
            {'text': '外文', 'value': 'redis://redis-collectioncache-1.istarshine.net.cn:6379/3/foreignlang_data'}
        ]
        for i in DATA_DB_OPTIONS:
            self._conn.hset(self.data_db_options_hash_key, i['text'], i['value'])

    ################## 测试 ########################
    def set_test(self, info):
        self._conn.lpush(self.test_key, json.dumps(info))
        return True

    def remove_test_url_result(self, channnel_url):
        self._conn.hdel(self.test_url_result_key, channnel_url)
        return True

    def remove_test_result(self, config_id):
        self._conn.delete(self.test_result_pre + str(config_id))
        return True

    def get_test_result_by_url(self, config_id, detail_url):
        ret = ''
        cnt = self._conn.llen(self.test_result_pre + str(config_id))
        for i in range(cnt):
            l = self._conn.lindex(self.test_result_pre + str(config_id), i)
            info = json.loads(l.decode('utf8'))
            if info['url'] == detail_url:
                ret = info
                break

        return ret

    def get_test_result_detail_url(self, searchChannel, searchTitle):
        ret = []
        v = self._conn.hget(self.test_url_result_key, searchChannel)
        if v:
            l = json.loads(v.decode('utf8'))
            for k, v in l.items():
                if searchTitle:
                    if v.find(searchTitle) >= 0:
                        ret.append({'url': k, 'channel_title': v})
                    else:
                        continue
                else:
                    ret.append({'url': k, 'channel_title': v})

        return ret

    def get_test_result(self, config_id, channel_url):
        ret = []
        cnt = self._conn.llen(self.test_result_pre + str(config_id))
        for i in range(cnt):
            l = self._conn.lindex(self.test_result_pre + str(config_id), i)
            info = json.loads(l.decode('utf8'))
            if info['channel_url'] == channel_url:
                ret.append(info)
        # print('get_try_result:', info, msg)
        return ret

    ################## 运行任务 ########################
    def set_task(self, info, interval):
        self.remove_test_url_result(info['url'])
        self.remove_test_result(info['config_id'])

        if interval == '1':
            key = self.spider_60_hash_key
        elif interval == '5':
            key = self.spider_300_hash_key
        else:  # '15'
            key = self.spider_900_hash_key

        self._conn.hset(key, info['url'], json.dumps(info))
        return True

    def remove_task(self, url):
        info = None
        for i in ['60', '300', '900']:
            key = self.task_pre + i
            info = self._conn.hget(key, url)
            if info:
                self._conn.hdel(key, url)
                break

        # print('remove_task:', url, info)
        return json.loads(info.decode('utf8')) if info else None


class MongoDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self._db = self.client.channelspider
        self.channel = self._db.channel
        self.config = self._db.config
        self.log = self._db.log
        self.router = self._db.router
        self.info_flag = self._db.info_flag

    def get_status_draw(self):
        cnt_list = []
        status_list = ['待测试', '测试中', '运行中']
        for status in status_list:
            cnt = self.channel.find({'status': status}).count()
            cnt_list.append(cnt)
        return cnt_list, status_list

    ############ 主控面板 ##################
    def get_domain_cnt(self):
        cnt = len(self.channel.distinct('domain'))
        return cnt

    def get_channels_cnt(self):
        cnt = self.channel.count()
        return cnt

    def get_info_flag_draw(self):
        cnt_list = []
        flag_list = ['新闻', '论坛', '博客', '新浪微博', '腾讯微博', '平煤', '微信', '视频', '长微博', 'APP', '评论', '搜索']
        for flag in flag_list:
            cnt = self.channel.find({'info_flag': flag}).count()
            cnt_list.append(cnt)
        return cnt_list, flag_list

    ############ Domain Tree ##################
    def all_domain_tree(self):
        root = {'name': '全部域名', 'children': []}
        domains = []
        l = self.channel.find()
        for i in l:
            domains.append(i['domain'])

        domains = list(set(domains))
        for domain in domains:
            domain_childrens = []
            configs = self.channel.find({'domain': domain})
            for config in configs:
                config_childrens = []
                config_id = config['config_id']
                channels = self.channel.find({'config_id': config_id})
                for channel in channels:
                    children = {'name': channel['url']}
                    config_childrens.append(children)

                children = {'name': '配置ID:' + str(config_id), 'children': config_childrens}
                domain_childrens.append(children)

            children = {'name': domain, 'children': domain_childrens}
            root['children'].append(children)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(BASE_DIR, 'static') + '\\files\\domainTree.json'

        fd = open(file_path, 'w')
        fd.write(json.dumps(root))
        fd.close()
        return root

    ############ 频道管理 ##################
    def get_channel_search_cnt(self, search):
        cond = dict()
        if search:
            cond['url'] = {'$regex': search}

        cnt = self.channel.find(cond).count()
        return cnt

    def get_channel_list(self, search, skip_num, page_size):
        ret = []
        cond = dict()
        if search:
            cond['url'] = {'$regex': search}

        l = self.channel.find(cond).sort([('update_ts', pymongo.DESCENDING)]).skip(skip_num).limit(page_size)
        for info in l:
            info.pop('_id')  # json编码error ObjectId('5812bedd6fce0d8637532ef1') is not JSON serializable
            # info['update_ts'] = datetime.datetime.fromtimestamp(info['update_ts']).strftime("%Y-%m-%d %H:%M:%S")
            ret.append(info)

        return ret

    def get_channel_info(self, url):
        cond = dict()
        cond['url'] = url

        info = self.channel.find_one(cond)
        if info:
            info.pop('_id')  # json编码error ObjectId('5812bedd6fce0d8637532ef1') is not JSON serializable

        return info

    def set_channel_info(self, info):
        ret = self.channel.update({'url': info['url']}, {"$set": info}, upsert=True)
        return ret

    def set_channel_info_status(self, url, status):
        ret = self.channel.update({'url': url}, {"$set": {'status': status}})
        return ret

    def remove_channel_info(self, url):
        ret = self.channel.remove({'url': url})
        return ret

    ################## 配置管理 ########################
    def get_config_search_cnt(self, delete_flag, config_id, domain):
        cond = {'delete': delete_flag}
        if domain:
            cond['domain'] = {'$regex': domain}
        if config_id != -1:
            cond['config_id'] = config_id

        # print('get_config_search_cnt', cond)
        cnt = self.config.find(cond).count()
        return cnt

    def get_config_list(self, delete_flag, config_id, domain, skip_num, page_size):
        # print('[info] get_config_list start.', config_id, domain)
        ret = []
        cond = {'delete': delete_flag}
        if domain:
            cond['domain'] = {'$regex': domain}
        if config_id != -1:  # -1 等价于 None
            cond['config_id'] = config_id

        l = self.config.find(cond).sort([('config_id', pymongo.DESCENDING)]).skip(skip_num).limit(page_size)
        for info in l:
            info.pop('_id')  # json编码error ObjectId('5812bedd6fce0d8637532ef1') is not JSON serializable
            info.pop('code')  # binary
            # info['channel_cnt'] = len(self.get_config_use_channels(info['config_id']))
            ret.append(info)

        # print('[info] get_config_list end.', ret)
        return ret

    def get_config_code(self, config_id):
        # print('[info] get_config_code start.', config_id)
        cond = dict()
        cond['config_id'] = config_id
        info = self.config.find_one(cond)
        # print('[info] get_config_code end.', info)
        if info and isinstance(info['code'], bytes):
            return info['code'].decode('utf8')
        else:
            return info['code'] if info else '无'

    def get_config_info(self, config_id):
        # print('[info] get_config_info start.', config_id)
        cond = dict()
        cond['config_id'] = config_id

        info = self.config.find_one(cond)
        if info: info.pop('_id')  # json编码error ObjectId('5812bedd6fce0d8637532ef1') is not JSON serializable

        # print('[info] get_config_info end.', info)
        return info

    def set_config_info(self, info):
        # $inc
        if info['config_id'] == -1:
            m = self.config.aggregate([{'$group': {'_id': '', 'max_id': {'$max': '$config_id'}}}])
            for i in m:
                info['config_id'] = i['max_id'] + 1

        info['delete'] = False
        ret = self.config.update({'config_id': info['config_id']}, {"$set": info}, upsert=True)
        return ret, info['config_id']

    def remove_config_info(self, config_id):
        self.channel.update({'config_id': config_id}, {'$set': {'config_id': -1}}, multi=True)
        ret = self.config.update({'config_id': config_id}, {'$set': {'delete': True}})
        # ret = self.config.remove({'config_id': config_id})
        return ret

    def recovery_config_info(self, config_id):
        ret = self.config.update({'config_id': config_id}, {'$set': {'delete': False}})
        return ret

    def get_config_use_channels(self, config_id):
        ret = []
        cond = dict()
        if config_id != -1:
            cond['config_id'] = config_id

        l = self.channel.find(cond)
        for info in l:
            ret.append(info['url'])

        return ret

    def get_channelInfo_by_configId(self, config_id):
        ret = []
        if config_id == -1:
            return ret

        cond = dict()
        cond['config_id'] = config_id
        l = self.channel.find(cond)
        for info in l:
            info.pop('_id')
            ret.append(info)

        return ret

    ################## 运行Log ########################
    def get_runResult_list(self, channel_url, skip_num, page_size):
        ret = []
        i = 0
        # (int(page) - 1) * PAGE_SIZE, PAGE_SIZE
        info = self.log.find_one(
            {'channel_url': channel_url},
            {"run_log": {"$slice": [skip_num, page_size]}}
        )
        if info:
            info.pop('_id')
            for log in info['run_log']:
                log['run_log_idx'] = log['start_time']
                log['start_time'] = datetime.datetime.fromtimestamp(log['start_time']).strftime("%Y-%m-%d %H:%M:%S")
                log['end_time'] = datetime.datetime.fromtimestamp(log['end_time']).strftime("%Y-%m-%d %H:%M:%S")
                log['delta_time'] = ''
                log['code_error_flag'] = '有' if 'code_error' in log and log['code_error'] else '无'
                ret.append(log)

        return ret

    def get_runResult_search_cnt(self, channel_url):
        l = self.log.aggregate([
            {'$match': {'channel_url': channel_url}},
            {'$project': {'cnt': {'$size': '$run_log'}}}
        ])
        for info in l:
            return info['cnt']
        else:
            return 0

    def get_runError_info(self, channel_url, run_log_idx, code_error_idx):
        info = self.log.find_one({'channel_url': channel_url})
        code = ""
        cnt = 0
        if info:
            code = info['run_log'][run_log_idx]['code']
            l = info['run_log'][run_log_idx]['code_error']
            cnt = len(l)
            _, d = divmod(code_error_idx, cnt)
            info = l[d]

        return info, code, cnt

    ################## 路由管理 ########################
    def get_timedelta_list(self, channel_url):
        '''
        [采集时间差页] 数据
        {'date': '2017-02-10',
         'total': 22,876,129,
         'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
                  'd2': {'percent': '2.1%', 'cnt': 489652, 'width': '10.5'},
                  'd3': {'percent': '3.3%', 'cnt': 748103, 'width': '16.5'},
                  'd4': {'percent': '9.3%', 'cnt': 2135519, 'width': '46.5'},
                  'd5': {'percent': '0%', 'cnt': 0, 'width': '0'},
                  'd6': {'percent': '20.7%', 'cnt': 4736320, 'width': '103.5'},
                  'd7': {'percent': '31.6%', 'cnt': 7231528, 'width': '158'},
                  'd8': {'percent': '7.8%', 'cnt': 1774018, 'width': '39'},
                  'd9': {'percent': '4.3%', 'cnt': 993639, 'width': '21.5'}
                  }
         },
        '''
        WIDTH = 440
        ret = []
        info = self.log.find_one({'channel_url': channel_url})
        if info:
            info.pop('_id')
        else:
            return ret

        days = []
        for i in range(30, -1, -1):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            days.append(day.strftime('%Y-%m-%d'))

        for day in days:
            if 'timedelta_' + day in info:
                data = dict()
                total = 0
                for i in range(1, 10):  # d1 - d9
                    if 'd' + str(i) in info['timedelta_' + day]:
                        cnt = info['timedelta_' + day]['d' + str(i)]
                    else:
                        cnt = 0

                    data['d' + str(i)] = dict()
                    data['d' + str(i)]['cnt'] = cnt
                    data['d' + str(i)]['percent'] = ''
                    data['d' + str(i)]['width'] = ''
                    total = total + cnt

                for i in range(1, 10):  # d1 - d9
                    p = data['d' + str(i)]['cnt'] / total
                    data['d' + str(i)]['percent'] = '{:.2f}'.format(p * 100) + '%'
                    data['d' + str(i)]['width'] = '{:.2f}'.format(WIDTH * p)

                ret.append({
                    'date': day,
                    'total': '{:,}'.format(total),
                    'data': data
                })

        return ret

    ################## 路由管理 ########################
    def get_router_list(self):
        ret = []
        l = self.router.find().sort([('name', pymongo.DESCENDING)])

        for info in l:
            info.pop('_id')
            ret.append(info)

        return ret

    def set_router(self, info):
        ret = self.router.update({'name': info['name']}, {'$set': info}, upsert=True)
        return ret

    def remove_router(self, name):
        ret = self.router.remove({'name': name})
        return ret

    def translate_to_redis(self, info):
        '''
        转换画面文字（info_flag，去重库，入库地址）为定义值
        '''
        if 'redis' in info['data_db']:  # 不需要翻译
            return info

        rds_info = copy.deepcopy(info)

        # info_flag
        f = self.info_flag.find_one({'name': info['info_flag']})
        rds_info['info_flag'] = f['value']

        i = self.router.find_one({'name': info['data_db']})  # mongoDB里只有router，没有dedup_uri和data_db
        rds_info['dedup_uri'] = i['dedup']
        rds_info['data_db'] = i['data_db']

        items = ['precise_xpath_list', 'region_xpath_list', 'ends', 'detail_keywords',
                 'list_keywords', 'detail_regexs', 'list_regexs']
        for item in items:
            new_list = []
            for expr in rds_info['crawl_rules'][item]:
                if expr:
                    new_list.append(expr)

            rds_info['crawl_rules'][item] = new_list

        return rds_info


if __name__ == '__main__':
    # r = RedisDriver()
    # r.init_options()

    db = MongoDriver()
    db.all_domain_tree()
    # pprint(db.get_channel_search_cnt(''))
