# coding=utf-8
import time, datetime
import pymongo
import redis
import locale
from pprint import pprint
import json
from copy import deepcopy

# MONGODB_SERVER = '127.0.0.1'
# MONGODB_PORT = 27017
# REDIS_SERVER = 'redis://127.0.0.1/15'

MONGODB_SERVER = '192.168.16.223'
MONGODB_PORT = 37017

MONGODB_SERVER_DIRECT = '192.168.149.39'
MONGODB_PORT_DIRECT = 37017

REDIS_SERVER = 'redis://192.168.187.55/15'

CONFIG_ID = '37556'  # 全站爬虫配置ID

OK_PERCENT = 0.8

UNKOWN = '未知'


class RedisDriver(object):
    def __init__(self):
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)

    def get_crawlTimePart(self):
        '''
        [主控面板] 采集时间差（today）
        '''
        ret = []
        day = datetime.datetime.now().strftime('%Y%m%d')
        crawlTime_hset_key = day + '_cfgid_td'
        cfg_id = CONFIG_ID + '_d'
        for i in range(1, 10):
            cnt = self.conn.hget(crawlTime_hset_key, cfg_id + str(i))
            if cnt:
                ret.append(int(cnt))
            else:
                ret.append(0)
        return ret

    def get_crawlTimeList(self):
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
        ret = []
        days = []
        WIDTH = 440

        for i in range(31):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            days.append(day.strftime('%Y%m%d'))

        for d in days:
            data = dict()
            total = 0
            for i in range(1, 10):
                j = (self.conn.hget(d + '_cfgid_td', CONFIG_ID + '_d' + str(i)))
                data['d' + str(i)] = dict()
                if j:
                    data['d' + str(i)]['cnt'] = int(j)
                else:
                    data['d' + str(i)]['cnt'] = 0

                total = total + data['d' + str(i)]['cnt']

                data['d' + str(i)]['percent'] = ''
                data['d' + str(i)]['width'] = ''

            if total:  # total != 0
                for i in range(1, 10):
                    p = data['d' + str(i)]['cnt'] / total
                    data['d' + str(i)]['percent'] = '{:.2f}'.format(p * 100) + '%'
                    data['d' + str(i)]['width'] = '{:.2f}'.format(WIDTH * p)

            ret.append({
                'date': time.strftime('%Y-%m-%d', time.strptime(d, '%Y%m%d')),
                'total': '{:,}'.format(total),
                'data': data
            })

        return ret

    def get_crawlUsed(self):
        '''
        [主控面板] 采集入库统计（一周）
        '''
        days = []
        all_list = []
        used_list = []
        keys = []

        for i in range(6, -1, -1):  # 一周7天时间差(6,5,4,3,2,1,0)
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            days.append(day.strftime('%m-%d'))
            keys.append(day.strftime('%Y%m%d') + '_cfgid_stat')

        for k in keys:
            all_v = self.conn.hget(k, CONFIG_ID + '_all')
            if all_v:
                all_list.append(int(all_v))
            else:
                all_list.append(0)

            used_v = self.conn.hget(k, CONFIG_ID + '_user')
            if used_v:
                used_list.append(int(used_v))
            else:
                used_list.append(0)

        return days, all_list, used_list


class MongoDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)

        self.allsite_db = self.client.allsite

        self.date_domain_num = self.allsite_db.date_domain_num
        self.domain_info = self.allsite_db.domain_info

        self.hub_info = self.allsite_db.hub_info
        self.hub_static = self.allsite_db.hub_static

        self.detail_info = self.allsite_db.detail_info

        self.crawl_data_stat = self.allsite_db.crawl_data_stat

        self.client_direct = pymongo.MongoClient(MONGODB_SERVER_DIRECT, MONGODB_PORT_DIRECT)
        self.direct_db_name = self.client_direct.database_names()[-1]
        self.direct_db = self.client_direct.get_database(self.direct_db_name)

    # domain
    def get_domain_info_list_cnt(self, search, times):
        '''
        [域名管理画面] 数据件数
        '''
        cond = dict()
        cond['domain'] = {'$regex': search}

        if times == 'today':
            today = datetime.date.today()
            timestamp = time.mktime(today.timetuple())
            cond['found_time'] = {'$gte': timestamp}

        cnt = self.domain_info.find(cond).count()

        return cnt

    def get_domain_info_list(self, search, times, skip_num, page_num):
        '''
        [域名管理画面] 数据
        '''
        ret = []
        cond = dict()
        cond['domain'] = {'$regex': search}

        if times == 'today':
            today = datetime.date.today()
            timestamp = time.mktime(today.timetuple())
            cond['found_time'] = {'$gte': timestamp}

        l = self.domain_info.find(cond).skip(skip_num).limit(page_num)  # .sort({"hub_num": -1})
        for info in l:
            siteName = ''
            if 'name' in info and info['name']:
                siteName = info['name']
            else:
                if 'search_engine_name' in info:
                    names = dict()
                    d = info['search_engine_name']
                    for (k, v) in d.items():
                        if isinstance(v, int):  # 去掉 非int型数据
                            names[k] = v

                    siteName, _ = sorted(names.items(), key=lambda x: x[1], reverse=True)[0]

            searchEngine = {'sogou': 0, 'baidu': 0, 'so': 0}
            if 'search_engine' in info:
                if 'baidu' in info['search_engine']:
                    searchEngine['baidu'] = info['search_engine']['baidu']
                if 'sogou' in info['search_engine']:
                    searchEngine['sogou'] = info['search_engine']['sogou']
                if 'so' in info['search_engine']:
                    searchEngine['so'] = info['search_engine']['so']

            ret.append({'url': info['domain'],
                        'hubPageCnt': info['hub_num'] if 'hub_num' in info else 0,
                        'siteName': siteName,
                        'source': info['source'] if 'source' in info else '',
                        'searchEngine_sogou': searchEngine['sogou'],
                        'searchEngine_so': searchEngine['so'],
                        'searchEngine_baidu': searchEngine['baidu'],
                        'tag': UNKOWN})

        return ret

    def get_domain_cnt(self, opt):
        '''
        [主控面板] 域名总数 时序列表
        '''
        info = self.date_domain_num.find_one()
        info.pop('_id')

        # 日期时间表
        days = sorted(info.keys())
        days = [day[5:] for day in days]  # 从YYYY-mm-dd中截取mm-dd

        # 合计总数
        totalCnt = sorted(info.values())

        # 日增数
        daysCnt = []
        j = totalCnt[0]
        for i in totalCnt:
            daysCnt.append(i - j)
            j = i

        interval = 0  # echarts数据显示间隔

        if (opt == "week"):
            return days[-7:], daysCnt[-7:], totalCnt[-7:], interval

        if (opt == "month"):
            return days[-31:], daysCnt[-31:], totalCnt[-31:], interval

        if (opt == "year"):
            interval = int(len(days) / 30)
            return days[-365:], daysCnt[-365:], totalCnt[-365:], interval

    def get_newDomain_cnt(self):
        '''
        [主控面板] 今日新增域名 总数
        '''
        today = datetime.date.today()
        timestamp = time.mktime(today.timetuple())
        ret = self.domain_info.find({'found_time': {'$gte': timestamp}}).count()
        return ret

    def set_domain_info(self, domain, siteName):
        ret = self.domain_info.update({'domain': domain}, {'$set': {'name': siteName}})
        # print(ret)
        return (ret['nModified'] == 1)

    # hubPage
    def get_hubPage_info_list_cnt(self, search):
        '''
        [列表展示页] 数据件数
        '''
        cond = dict()
        cond['url'] = {'$regex': search}
        cond['possibility'] = {'$exists': True}
        cnt = self.hub_info.find(cond).count()

        return cnt

    def get_hubPage_info_list(self, search, skip_num, page_num):
        '''
        [列表展示页] 数据
        '''
        ret = []
        cond = dict()
        cond['url'] = {'$regex': search}
        cond['possibility'] = {'$exists': True}

        seconds = self.get_hubPage_scanPeriod()
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        # possibility 探测周期
        l = self.hub_info.find(cond).sort('possibility', pymongo.ASCENDING).skip(skip_num).limit(page_num)
        for info in l:
            if 'crawled_num' in info:
                crawled_num = info['crawled_num']
            else:
                crawled_num = 0

            if today in info:
                crawled_num_today = info[today]
            else:
                crawled_num_today = 0

            if today + '_user' in info:
                user_num_today = info[today + '_user']
            else:
                user_num_today = 0

            possibility = info['possibility']
            if possibility and seconds:
                period = seconds / possibility
                h = int(period / (60 * 60))
                m = int((period - (60 * 60) * h) / 60)
                s = int(period - (60 * 60) * h - 60 * m)
                period_str = "{0}小时{1}分{2}秒".format(h, m, s)
            else:
                period_str = UNKOWN

            ret.append({'url': info['url'],
                        'crawled_num': crawled_num,
                        'crawled_num_today': crawled_num_today,
                        'user_num_today': user_num_today,
                        'period': period_str})

        return ret

    def get_hubPage_sum(self):
        '''
        [主控面板] 频道总数
        '''
        ret = []
        # aggregate（聚类函数） 不分组 '_id':'' 使用 $sum
        l = self.domain_info.aggregate([{'$group': {'_id': '', 'hubPage_sum': {'$sum': '$hub_num'}}}])
        for info in l:
            ret.append(info)

        return ret[0]['hubPage_sum']

    def get_hubPage_scanPeriod(self):
        '''
        [主控面板] 扫描周期（秒）
        '''
        seconds = 0
        info = self.hub_static.find_one({'name': 'hub_finish_list'})
        if info:
            d = datetime.datetime.fromtimestamp(info['hub_finish_list'][-1]) - \
                datetime.datetime.fromtimestamp(info['hub_finish_list'][-2])
            seconds = d.total_seconds()

        return seconds

    def get_hubPage_remainQueue(self):
        '''
        [主控面板] 频道探测速度-残留队列数量
        '''
        times = []
        cnt_list = []

        t = int(datetime.datetime.now().strftime('%H'))
        for i in range(t - 23, t + 1):
            if i >= 0:
                times.append(i)
            else:
                times.append((i + 24) * -1)

        info = self.hub_static.find_one({'name': 'hub_schedule_num'})  # 20min扫描一次
        size = len(info['hub_schedule_num'])
        for i in range(size - 1, size - 3 * 24 - 1, -3):  # 20min扫描一次,间隔3次为1小时，取最近的24小时
            if i < 0:
                cnt_list.append(0)  # 没有扫描值
            else:
                cnt_list.append(info['hub_schedule_num'][i])

        return times, cnt_list[::-1]

    def get_hubPage_rank(self):
        '''
        [主控面板] 频道采集量排名（top10）
        '''
        hubPageUrl = []
        hubPageCrawledNum = []

        l = self.hub_info.find({'crawled_num': {'$exists': True}}).sort('crawled_num', pymongo.DESCENDING).limit(10)
        for info in l:
            hubPageUrl.append(info['url'])
            hubPageCrawledNum.append(info['crawled_num'])

        return hubPageUrl, hubPageCrawledNum

    # detail
    def get_detail_direct_cnt(self, day):
        '''
        [详情展示页] 数据件数
        '''
        cond = dict()

        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        zero_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hour, minutes=minute)
        cond['gtime'] = {'$gte': zero_time}
        cond['compare_info.content'] = {'$exists': True}
        cnt = self.detail_info.find(cond).count()

        return cnt

    def parse_select_cond(self, search, hubPage, select_cond):
        '''
        [详情展示页] '_titleNG_contentNG_sourceNG_ctimeNG' -> mongodb find({cond})
           选择条件： _(固定分隔符) + field(title,content,source,ctime) + OK/NG（正误分类）
        '''
        cond = dict()
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        zero_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hour, minutes=minute)
        cond['gtime'] = {'$gte': zero_time}
        cond['url'] = {'$regex': search}
        if hubPage:
            cond['hub_url'] = hubPage

        if not select_cond:
            cond['compare_info.content'] = {'$exists': True}

        elif 'all' in select_cond:
            if select_cond == '_allOK':
                for field in ['title', 'content', 'source', 'ctime']:
                    cond['compare_info.' + field] = {'$gte': OK_PERCENT}
            else:
                cond['$or'] = []
                for field in ['title', 'content', 'source', 'ctime']:
                    cond['$or'].append({'compare_info.' + field: {'$lt': OK_PERCENT}})

        else:
            select_cond_list = select_cond.split('_')
            select_cond_list.remove('')
            for c in select_cond_list:
                field = c[:-2]
                status = c[-2:]
                cond['compare_info.' + field] = {'$gte': OK_PERCENT} if status == 'OK' else  {'$lt': OK_PERCENT}

        print('[info] parse_select_cond()', cond)
        return cond

    def get_detail_info_list_cnt(self, search, hubPage, select_cond):
        '''
        [详情展示页] 今日数据件数
        '''
        cond = self.parse_select_cond(search, hubPage, select_cond)
        all_cnt = self.detail_info.find(cond).count()

        title_ok_cond = cond.copy()
        if 'titleOK' in select_cond:
            title_ok_cnt = all_cnt
        elif 'titleNG' in select_cond:
            title_ok_cnt = 0
        else:
            title_ok_cond['compare_info.title'] = {'$gte': OK_PERCENT}
            title_ok_cnt = self.detail_info.find(title_ok_cond).count()

        content_ok_cond = cond.copy()
        if 'contentOK' in select_cond:
            content_ok_cnt = all_cnt
        elif 'contentNG' in select_cond:
            content_ok_cnt = 0
        else:
            content_ok_cond['compare_info.content'] = {'$gte': OK_PERCENT}
            content_ok_cnt = self.detail_info.find(content_ok_cond).count()

        source_ok_cond = cond.copy()
        if 'sourceOK' in select_cond:
            source_ok_cnt = all_cnt
        elif 'sourceNG' in select_cond:
            source_ok_cnt = 0
        else:
            source_ok_cond['compare_info.source'] = {'$gte': OK_PERCENT}
            source_ok_cnt = self.detail_info.find(source_ok_cond).count()

        ctime_ok_cond = cond.copy()
        if 'ctimeOK' in select_cond:
            ctime_ok_cnt = all_cnt
        elif 'ctimeNG' in select_cond:
            ctime_ok_cnt = 0
        else:
            ctime_ok_cond['compare_info.ctime'] = {'$gte': OK_PERCENT}
            ctime_ok_cnt = self.detail_info.find(ctime_ok_cond).count()

        all_cond = cond.copy()
        if 'NG' in select_cond:
            all_ok_cnt = 0
        else:
            all_cond['compare_info.title'] = {'$gte': OK_PERCENT}
            all_cond['compare_info.content'] = {'$gte': OK_PERCENT}
            all_cond['compare_info.source'] = {'$gte': OK_PERCENT}
            all_cond['compare_info.ctime'] = {'$gte': OK_PERCENT}
            all_ok_cnt = self.detail_info.find(all_cond).count()

        return all_cnt, all_ok_cnt, title_ok_cnt, content_ok_cnt, source_ok_cnt, ctime_ok_cnt

    def get_detail_info_list(self, search, hubPage, select_cond, skip_num, page_num):
        '''
        [详情展示页] 今日数据
        '''
        # select_cond : '_titleNG_contentNG_sourceNG_ctimeNG'

        ret = []
        cond = self.parse_select_cond(search, hubPage, select_cond)

        l = self.detail_info.find(cond).sort('url', pymongo.ASCENDING).skip(skip_num).limit(page_num)
        for info in l:
            all_ok = False
            tt = info['compare_info']
            if tt['title'] > OK_PERCENT and tt['content'] > OK_PERCENT \
                    and tt['source'] > OK_PERCENT and tt['ctime'] > OK_PERCENT:
                all_ok = True

            d = self.direct_db.item.find_one({'url': info['url']})
            ret.append({'url': info['url'],
                        'hub_url': info['hub_url'],
                        'channel': info['channel'],
                        'title': info['title'],
                        'content': info['content'],
                        'source': info['source'],
                        'ctime': info['ctime'],
                        'all_ok': all_ok,
                        'compare_title': info['compare_info']['title'] * 100,
                        'compare_content': info['compare_info']['content'] * 100,
                        'compare_source': info['compare_info']['source'] * 100,
                        'compare_ctime': info['compare_info']['ctime'] * 100,

                        "direct_config_id": d['config_id'],
                        "direct_title": d['title'],
                        "direct_content": d['content'],
                        "direct_source": d['retweeted_source'] if 'retweeted_source' in d else '',
                        "direct_ctime": d['ctime']
                        })

        print('[info] get_detail_info_list() cond:', cond, len(ret))
        return ret

    def get_detail_list_top100(self):
        '''
        [主控面板] 详情页Top100
        '''
        ret = []

        l = self.detail_info.find().sort('gtime', pymongo.DESCENDING).limit(100)
        for info in l:
            ret.append({'url': info['url']})

        return ret

    def get_detail_total_cnt(self):
        '''
        [主控面板] 详情页统计数（累计）
        '''
        total_cnt = self.detail_info.find().count()

        return total_cnt

    def get_detail_today_cnt(self):
        '''
        [主控面板] 详情页统计数（今日）
        '''
        day = datetime.datetime.now().strftime('%Y%m%d')
        h = str(int(datetime.datetime.now().strftime('%H')))
        info = self.crawl_data_stat.find_one({'date': day})
        return info['data'][h]['all'], info['data'][h]['user']

    def get_detail_3dayDiff(self):
        '''
        [主控面板] 采集统计（24小时）
        '''
        beforeYesterday = [0] * 24
        by = datetime.datetime.now() - datetime.timedelta(days=2)
        by_info = self.crawl_data_stat.find_one({'config_id': CONFIG_ID, 'date': by.strftime('%Y%m%d')})
        if by_info:
            h = sorted([int(i) for i in by_info['data'].keys()])
            for i in h:
                if i != min(h):
                    beforeYesterday[i] = by_info['data'][str(i)]['all'] - by_info['data'][str(i - 1)]['all']

        yesterday = [0] * 24
        y = datetime.datetime.now() - datetime.timedelta(days=1)
        y_info = self.crawl_data_stat.find_one({'config_id': CONFIG_ID, 'date': y.strftime('%Y%m%d')})
        if y_info:
            h = sorted([int(i) for i in y_info['data'].keys()])
            for i in h:
                if i != min(h):
                    yesterday[i] = y_info['data'][str(i)]['all'] - y_info['data'][str(i - 1)]['all']

        today = []
        t = datetime.datetime.now()
        t_info = self.crawl_data_stat.find_one({'config_id': CONFIG_ID, 'date': t.strftime('%Y%m%d')})
        if t_info:
            h = sorted([int(i) for i in t_info['data'].keys()])
            for i in h:
                if i != min(h):
                    today.append(t_info['data'][str(i)]['all'] - t_info['data'][str(i - 1)]['all'])

        return today, yesterday, beforeYesterday

    def get_detail_dialog_info(self, url):
        a = self.detail_info.find_one({'url': url})
        d = self.direct_db.item.find_one({'url': url})

        info = {"title": a['title'],
                "content": a['content'],
                "source": a['source'],
                "ctime": a['ctime'],
                "title_ok": a['compare_info']['title'] > OK_PERCENT,
                "content_ok": a['compare_info']['content'] > OK_PERCENT,
                "source_ok": a['compare_info']['source'] > OK_PERCENT,
                "ctime_ok": a['compare_info']['ctime'] > OK_PERCENT,

                "direct_config_id": d['config_id'],
                "direct_title": d['title'],
                "direct_content": d['content'],
                "direct_source": d['retweeted_source'] if 'retweeted_source' in d else '',
                "direct_ctime": d['ctime']
                }

        return info


if __name__ == '__main__':
    r = RedisDriver()
    # pprint(r.get_crawlTimePart())

    db = MongoDriver()
    # print(db.get_detail_allsiteCrawledInfo('http://www.nmgepb.gov.cn/tslm/hbqk/201604/P020160407567525989498/index.html'))
    # db.get_detail_list('', '_titleNG_contentOK_sourceOK_ctimeNG', skip_num=0, page_num=100)
    # db.get_detail_list('', '_allNG', skip_num=0, page_num=100)
    # print(db.get_detail_direct_cnt(''))
    url = 'http://binzhou.sdchina.com/show/4045048.html'
    pprint(db.get_detail_dialog_info(url))
