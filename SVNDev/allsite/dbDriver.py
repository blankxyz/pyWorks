# coding=utf-8
from pprint import pprint
import time, datetime
import pymongo
import redis
import json

from django.utils import html as django_html  # .remove_tags(value, tags)

# from .setting import CONFIG_ID, REDIS_SERVER, MONGODB_SERVER, MONGODB_PORT, MONGODB_SERVER_DIRECT, MONGODB_PORT_DIRECT, \
#     OK_PERCENT, UNKOWN

MONGODB_SERVER = '192.168.16.223'
MONGODB_PORT = 37017

MONGODB_SERVER_DIRECT = '192.168.149.39'
MONGODB_PORT_DIRECT = 37017

REDIS_SERVER = 'redis://192.168.187.55/15'
REDIS_COMMENTS_SERVER = 'redis://192.168.16.223/8'

CONFIG_ID = '37556'  # 全站爬虫配置ID

OK_PERCENT = 0.8

UNKOWN = '未知'


class RedisDriver(object):
    def __init__(self):
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.conn_comments = redis.StrictRedis.from_url(REDIS_COMMENTS_SERVER)

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

    # -------- 评论采集 -------------------------------------
    def get_commentsQueueSize(self):
        # "qq", "toutiao", "ifeng", "163", "tianya", "sina"
        ret = []
        ret.append(self.conn_comments.llen('comment_task:qq'))
        ret.append(self.conn_comments.llen('comment_task:toutiao'))
        ret.append(self.conn_comments.llen('comment_task:ifeng'))
        ret.append(self.conn_comments.llen('comment_task:163'))
        ret.append(self.conn_comments.llen('comment_task:tianya'))
        ret.append(self.conn_comments.llen('comment_task:sina'))
        return ret


class MongoDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.allsite_db = self.client.allsite
        self.date_domain_num = self.allsite_db.date_domain_num
        self.domain_info = self.allsite_db.domain_info
        self.hub_info = self.allsite_db.hub_info
        self.hub_static = self.allsite_db.hub_static
        self.detail_info = self.allsite_db.detail_info
        self.detail_likeness = self.allsite_db.detail_likeness
        self.detail_manual_correct = self.allsite_db.detail_manual_correct
        self.crawl_data_stat = self.allsite_db.crawl_data_stat

        self.comment_db = self.client.NewsComments
        self.comment = self.comment_db.comment

    def get_domain_info_list_cnt(self, search, times):
        '''
        [域名管理画面] 数据件数
        '''
        cond = dict()
        if search:
            cond['domain'] = {'$regex': search}

        if times == 'today':
            today = datetime.date.today()
            timestamp = time.mktime(today.timetuple())
            cond['found_time'] = {'$gte': timestamp}

        cnt = self.domain_info.find(cond).count()

        return cnt

    def get_domain_info_list(self, search, times, skip, page_size):
        '''
        [域名管理画面] 数据
        '''
        ret = []
        cond = dict()
        if search:
            cond['domain'] = {'$regex': search}

        if times == 'today':
            today = datetime.date.today()
            timestamp = time.mktime(today.timetuple())
            cond['found_time'] = {'$gte': timestamp}

        l = self.domain_info.find(cond).sort('found_time', pymongo.DESCENDING).skip(skip).limit(page_size)
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

            source = info['source'] if 'source' in info else UNKOWN
            if source == 'manual_added':
                source_name = '手工添加'
            elif source == 'cross_domain_link':
                source_name = '交叉搜索'
            elif source == 'baidu':
                source_name = '百度'
            elif source == 'sogou':
                source_name = '搜狗'
            elif source == 'so':
                source_name = '360'
            else:
                source_name = UNKOWN

            ret.append({'url': info['domain'],
                        'hubPageCnt': info['hub_num'] if 'hub_num' in info else 0,
                        'siteName': siteName,
                        'source': source_name,
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
        return (ret['nModified'] == 1)

    def get_hubPage_info_list_cnt(self, search, quick_flg=False):
        '''
        [列表展示页] 数据件数
        '''
        # print('[info] get_hubPage_info_list_cnt start...')
        cond = dict()
        if search:
            cond['url'] = {'$regex': search}
        if quick_flg:
            cond['quick'] = True

        cond['possibility'] = {'$exists': True}
        cnt = self.hub_info.find(cond).count()
        # print('[info] get_hubPage_info_list_cnt end.')
        return cnt

    def get_hubPage_info_list(self, search, skip, page_size, quick_flg=False):
        '''
        [列表展示页] 数据
        '''
        ret = []
        seconds = self.get_hubPage_scanPeriod()
        today = datetime.datetime.today().strftime('%Y-%m-%d')

        cond = dict()
        if search:
            cond['url'] = {'$regex': search}
        if quick_flg:
            cond['quick'] = True
        # cond['possibility'] = {'$exists': True}

        # possibility 探测周期
        l = self.hub_info.find(cond).sort('possibility', pymongo.DESCENDING).skip(skip).limit(page_size)
        for info in l:
            if 'name' in info:
                names = info['name']
                name, _ = sorted(names.items(), key=lambda x: x[1], reverse=True)[0]
            else:
                name = ''
            if 'period' in info:
                period = info['period']
            else:
                period = 15

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

            if 'possibility' in info:
                possibility = info['possibility']
            else:
                possibility = 0

            if possibility and seconds:
                p = seconds / possibility
                h = int(p / (60 * 60))
                m = int((p - (60 * 60) * h) / 60)
                s = int(p - (60 * 60) * h - 60 * m)
                period_str = "{0}小时{1}分{2}秒".format(h, m, s)
            else:
                period_str = UNKOWN

            ret.append({'url': info['url'],
                        'name': name,
                        'period': period,
                        'crawled_num': crawled_num,
                        'crawled_num_today': crawled_num_today,
                        'user_num_today': user_num_today,
                        'period_str': period_str})

        return ret

    def set_hubPage_info(self, url, name, period):
        print("[info] set_hubPage_info", url, name, period)
        ret = self.hub_info.update({'url': url},
                                   {"$set": {'url': url, 'period': period, 'quick': True, 'name': {name: 10000}}},
                                   upsert=True)
        print("[info] set_hubPage_info", ret)
        return ret

    def remove_hubPage_info(self, url):
        cnt = self.hub_info.remove({'url': url})
        return cnt

    def get_hubPage_sum(self):
        '''
        [主控面板] 频道总数
        '''
        ret = []
        # aggregate（聚类函数） 不分组 '_id':'' 使用 $sum
        # l = self.domain_info.aggregate([{'$group': {'_id': '', 'hubPage_sum': {'$sum': '$hub_num'}}}])
        cnt = self.hub_info.count()
        return cnt

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

    def parse_select_cond(self, search, hubPage, select_cond, day='today'):
        '''
        [详情展示页]
            select_cond: '_titleNG_contentNG_sourceNG_ctimeNG' -> mongodb find({cond})
            选择条件： _(固定分隔符) + field(title,content,source,ctime) + OK/NG（正误分类）
            day: 20170102 or today
        '''
        cond = dict()
        if hubPage:
            cond['hub_url'] = hubPage

        if day == 'today':
            hour = datetime.datetime.now().hour
            minute = datetime.datetime.now().minute
            time0 = datetime.datetime.utcnow() - datetime.timedelta(hours=hour, minutes=minute)
        else:
            time0 = datetime.datetime.strptime(day, "%Y%m%d") - datetime.timedelta(hours=8)

        time24 = time0 + datetime.timedelta(hours=24, minutes=0, seconds=0)

        cond['gtime'] = {'$gte': time0, '$lt': time24}

        if search:
            cond['url'] = {'$regex': search}

        if not select_cond:
            cond['compare_info.content'] = {'$exists': True}

        elif 'all' in select_cond:
            if select_cond == '_allOK':
                for field in ['source', 'ctime', 'title', 'content']:
                    cond['compare_info.' + field] = {'$gte': OK_PERCENT}
            else:
                cond['$or'] = []
                for field in ['source', 'ctime', 'title', 'content']:
                    cond['$or'].append({'compare_info.' + field: {'$lt': OK_PERCENT}})

        else:
            select_cond_list = select_cond.split('_')
            select_cond_list.remove('')
            for c in select_cond_list:
                field = c[:-2]
                status = c[-2:]
                cond['compare_info.' + field] = {'$gte': OK_PERCENT} if status == 'OK' else  {'$lt': OK_PERCENT}

        # print('[info] parse_select_cond()',select_cond, cond)
        return cond

    def get_detail_search_cnt(self, search, hubPage, select_cond, day='today'):
        '''
        [详情展示页] 查询结果件数（今日）
        '''
        cond = self.parse_select_cond(search, hubPage, select_cond, day)
        all_cnt = self.detail_info.find(cond).count()
        # print("[info] get_detail_all_cnt", all_cnt)
        return all_cnt

    def get_detail_part_ok_cnt(self, search, hubPage, selected_cond, selected_cnt, part, day='today'):
        '''
        [详情展示页] 查询结果件数（今日） 各项目正误统计
         selected_cond： 已选数据集的前提条件  '[_title[OK|NG]|_content[OK|NG]|_source[OK|NG]|_ctime[OK|NG]]'
                        or '_allOK' or '_allNG'
         selected_cnt：已选数据集的件数
         part: 'title','content','source','ctime','all'
         Returns: 部分条件正确的件数
        '''
        if selected_cond == '_allOK':
            return selected_cnt
        if selected_cond == '_allNG':
            return 0

        cond = self.parse_select_cond(search, hubPage, selected_cond, day)
        if part == 'all':
            all_ok_cond = cond.copy()
            if 'NG' in selected_cond:
                all_ok_cnt = 0
            else:  # 'OK'
                all_ok_cond['compare_info.title'] = {'$gte': OK_PERCENT}
                all_ok_cond['compare_info.content'] = {'$gte': OK_PERCENT}
                all_ok_cond['compare_info.source'] = {'$gte': OK_PERCENT}
                all_ok_cond['compare_info.ctime'] = {'$gte': OK_PERCENT}
                # print('[info] get_detail_part_cnt all_ok_cond', all_ok_cond)
                all_ok_cnt = self.detail_info.find(all_ok_cond).count()
            return all_ok_cnt
        else:  # 'title','content','source','ctime'
            part_ok_cond = cond.copy()
            if part + 'OK' in selected_cond:
                part_ok_cnt = selected_cnt
            elif part + 'NG' in selected_cond:
                part_ok_cnt = 0
            else:
                part_ok_cond['compare_info.' + part] = {'$gte': OK_PERCENT}
                # print('[info] get_detail_part_cnt part_ok_cond', part_ok_cond)
                part_ok_cnt = self.detail_info.find(part_ok_cond).count()
            return part_ok_cnt

    def get_detail_info_list(self, search, hubPage, select_cond, skip, page_size):
        '''
        [详情展示页] 今日数据
        '''
        # select_cond : '_titleNG_contentNG_sourceNG_ctimeNG'
        ret = []
        cond = self.parse_select_cond(search, hubPage, select_cond)

        l = self.detail_info.find(cond).sort('gtime', pymongo.ASCENDING).skip(skip).limit(page_size)
        for info in l:
            all_ok = False
            tt = info['compare_info']
            if tt['title'] >= OK_PERCENT and tt['content'] >= OK_PERCENT \
                    and tt['source'] >= OK_PERCENT and tt['ctime'] >= OK_PERCENT:
                all_ok = True

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
                        })

        # print('[info] get_detail_info_list() cond:', len(ret), cond)
        return ret

    def get_detail_likeness_list(self, start, end, skip, page_size):
        ret = []
        cond = dict()
        if start and end:
            t_s = datetime.datetime.strptime(start, '%Y%m%d')
            t_e = datetime.datetime.strptime(end, '%Y%m%d')
            cond = {'$gte': t_s, 'lte': t_e}

        l = self.detail_likeness.find(cond).sort('date', pymongo.DESCENDING).skip(skip).limit(page_size)
        for info in l:
            info.pop('_id')
            ret.append(info)

        return ret

    def get_detail_list_top100(self, search, skip, page_size):
        '''
        [主控面板] 详情页Top100
        '''
        ret = []
        cond = dict()
        if search:
            cond['url'] = {'$regex': search}

        l = self.detail_info.find(cond).sort('gtime', pymongo.DESCENDING).skip(skip).limit(page_size)
        for info in l:
            a = []
            a.append(info['url'])
            ret.append(a)

        return ret

    def get_detail_total_cnt(self):
        '''
        [主控面板] 详情页统计数（累计）
        '''
        total_cnt = self.detail_info.count()
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
        [主控面板] 采集统计（3天24小时）
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

    def get_doamin_search_category_cnt(self):
        '''
        [主控面板] 域名发现方式分类
        '''
        manual_added_cnt = self.domain_info.find({'source': 'manual_added'}).count()
        cross_domain_link_cnt = self.domain_info.find({'source': 'cross_domain_link'}).count()
        engine_baidu_cnt = self.domain_info.find({'source': 'baidu'}).count()
        engine_sogou_cnt = self.domain_info.find({'source': 'sogou'}).count()
        engine_so_cnt = self.domain_info.find({'source': 'so'}).count()
        engine_sum = engine_baidu_cnt + engine_sogou_cnt + engine_so_cnt
        # print(manual_added_cnt, cross_domain_link_cnt, engine_sum, engine_baidu_cnt, engine_sogou_cnt, engine_so_cnt)
        return manual_added_cnt, cross_domain_link_cnt, engine_sum, engine_baidu_cnt, engine_sogou_cnt, engine_so_cnt

    def get_detail_correct_info(self, url):
        cond = dict()
        cond['url'] = url
        info = self.detail_manual_correct.find_one(cond)
        return info

    def get_detail_dialog_info(self, url):
        # print("[info] get_detail_dialog_info start...", url)
        info = dict()
        # 全站采集结果
        allsite = self.detail_info.find_one({'url': url})
        info['title'] = allsite['title']
        # info['content'] = allsite['content']
        info['content'] = django_html.remove_tags(allsite['content'],
                                                  "header img br p div strong font span a li ul b em i tr td")
        info['source'] = allsite['source']
        info['ctime'] = allsite['ctime']
        # 对比结果
        info['title_ok'] = allsite['compare_info']['title'] >= OK_PERCENT
        info['content_ok'] = allsite['compare_info']['content'] >= OK_PERCENT
        info['source_ok'] = allsite['compare_info']['source'] >= OK_PERCENT
        info['ctime_ok'] = allsite['compare_info']['ctime'] >= OK_PERCENT
        # 直采结果
        client_direct = pymongo.MongoClient(MONGODB_SERVER_DIRECT, MONGODB_PORT_DIRECT)
        db_names = client_direct.database_names()
        db_names = [name for name in db_names if 'spider' in name]
        # num = None
        # for i, name in enumerate(db_names):
        #     if name[-1] != str(i + 1):
        #         num = i - 1
        # direct_db = client_direct.get_database(db_names[num])
        direct_info = None
        for db_name in db_names:
            direct_db = client_direct.get_database(db_name)
            cnt = direct_db.item.find({'url': url}).count()
            if cnt > 0:
                l = direct_db.item.find({'url': url})
                for d in l:
                    direct_json = json.loads(d['data'])
                    if direct_json['config_id'] != CONFIG_ID:
                        direct_info = direct_json
                break

        info['direct_config_id'] = direct_info['config_id'] if direct_info else UNKOWN
        info['direct_title'] = direct_info['title'] if direct_info else UNKOWN
        info['direct_content'] = direct_info['content'] if direct_info else UNKOWN
        info['direct_source'] = direct_info['retweeted_source'] \
            if direct_info and 'retweeted_source' in direct_info else UNKOWN
        info['direct_ctime'] = datetime.datetime.fromtimestamp(direct_info['ctime']).strftime('%Y-%m-%d %H:%M:%S') \
            if direct_info else UNKOWN

        # 手工判定结果
        info['correct_title'] = UNKOWN
        info['correct_content'] = UNKOWN
        info['correct_source'] = UNKOWN
        info['correct_ctime'] = UNKOWN
        c = self.get_detail_correct_info(url)
        if c:
            correct = c['correct']
            info['correct_title'] = 'ok' if correct['title'] == True else 'ng'
            info['correct_content'] = 'ok' if correct['content'] == True else 'ng'
            info['correct_source'] = 'ok' if correct['source'] == True else 'ng'
            info['correct_ctime'] = 'ok' if correct['ctime'] == True else 'ng'

        # print("[info] get_detail_dialog_info end.", info)
        return info

    def getMatchDetailUrls(self, links):
        # print("[info] getMatchDetailUrls start.", links)
        ret = []
        l = self.detail_info.find({'url': {'$in': links}})
        for info in l:
            ret.append(info['url'])

        # print("[info] getMatchDetailUrls end.", ret)
        return ret

    def save_detail_correctInfo(self, info):
        info['update'] = datetime.datetime.today()
        info['editor'] = 'admin'
        one = self.detail_manual_correct.find_one({'url': info['url']})
        if one:
            info['_id'] = one['_id']
            self.detail_manual_correct.save(info)
            return 'update'
        else:
            self.detail_manual_correct.insert(info)
            return 'insert'

    def get_detail_correct_list(self, url, user, start, end):
        ret = []
        cond = dict()
        if url:
            cond['url'] = {'$regex': url}
        if user:
            cond['editor'] = user

        if start and end:
            t_s = datetime.datetime.strptime(start + ' 00:00:01', '%Y-%m-%d %H:%M:%S')
            t_e = datetime.datetime.strptime(end + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            cond['update'] = {'$gte': t_s, '$lte': t_e}

        # print(cond)
        l = self.detail_manual_correct.find(cond).sort('update', pymongo.DESCENDING)
        for info in l:
            ret.append(info)

        return ret

    # -------- 评论采集 -------------------------------------
    def get_comments_search_cnt(self, search):
        cond = dict()
        if search:
            cond['post_url'] = {'$regex': search}

        cnt = self.comment.find(cond).count()
        return cnt

    def get_commentInfo_list(self, search, skip_num, page_size):
        ret = []
        cond = dict()
        if search:
            cond['post_url'] = {'$regex': search}

        # print(cond)
        # l = self.comment.find(cond).sort('url',pymongo.ASCENDING).skip(skip_num).limit(page_size)
        l = self.comment.find(cond).skip(skip_num).limit(page_size)
        for info in l:
            # ret.append([info['post_url'], info['area'], info['content'], info['source'], info['ctime'],
            #             info['gtime'], info['shareCount'], info['up_count'], info['down_count']])
            ret.append(info)

        return ret


if __name__ == '__main__':
    r = RedisDriver()
    # pprint(r.get_crawlTimePart())

    db = MongoDriver()
    # print(db.get_detail_allsiteCrawledInfo('http://www.nmgepb.gov.cn/tslm/hbqk/201604/P020160407567525989498/index.html'))
    # db.get_detail_list('', '_titleNG_contentOK_sourceOK_ctimeNG', skip_num=0, page_num=100)
    # db.get_detail_list('', '_allNG', skip_num=0, page_num=100)
    # print(db.get_hubPage_info_list('', 10, 20))
    # print(db.get_detail_direct_cnt(''))
    # url = 'http://www.cqcb.com/reading/2017-03-05/267950_pc.html'
    url = 'http://www.babytree.com/ask/detail/37328235'
    pprint(db.get_detail_dialog_info(url))
    # _setDetailLikeness('20170306')
    # pprint(db.get_detail_likeness_list('', '', 0, 100))
    # pprint(db.get_commentInfo_list('', 0, 20))
