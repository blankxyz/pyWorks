# encoding:utf-8
import datetime
import re
import copy

import redis
import arrow
import pymysql.cursors

'''

注意:exclude_list内部必须为字符串，不能是数字
'''

global_args = {
    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'news_time_hash_format': 'time_1_{0}_d{1}',
    'all_user_news_hash_format': 'time_value_1_{0}_d{1}',
    'all_hash_format': 'time_all_{0}_d{1}',  # 所有域名/配置时间差
    'config_url_format': 'timeout_{0}_config_id:{1}',  # 所有域名/配置时间差
    'news_user_zset': 'data_static_1_{0}:domain_id_value_dedup',  # 新闻对上用户查询
    'news_all_users_zset': 'data_static_1_{0}:domain_id_value',  # 新闻对上用户不去重
    'news_config_zset': 'data_static_1_{0}:config_id_value_dedup',  # 新闻对上配置查询

    'forums_user_zset': 'data_static_2_{0}:domain_id_value_dedup',  # 论坛对上用户查询
    'forums_all_users_zset': 'data_static_2_{0}:domain_id_value',  # 论坛对上用户不去重
    'forums_config_zset': 'data_static_2_{0}:config_id_value_dedup',  # 论坛对上配置查询
    'forums_time_hash_format': 'time_2_{0}_d{1}',  # 论坛对上用户时间差
    'forums_all_user_hash_format': 'time_value_2_{0}_d{1}',

    'all_domains_zset': 'data_static_{0}:domain_all',  # 所有域名
    'all_configs_zset': 'data_static_{0}:config_id_all',  # 所有域名

}
spider_con = redis.StrictRedis(host='192.168.16.223', port=6379, db=10)
spider_con_pipline = spider_con.pipeline()


def all_nums(zset_name_format, date, min1=1):
    '''
    查询配置或域名所有量
    :param zset_name_format:
    :param date:
    :param min1:
    :return:
    '''
    zset_name = zset_name_format.format(date)
    domains = spider_con.zrevrangebyscore(zset_name, max='+inf', min=min1)
    return domains


def all_nums_rank(time_hash, key_need):
    '''
    查询配置或域名所有量
    :param time_hash:
    :param key_need:
    :return:
    '''
    results = spider_con.hgetall(time_hash)
    domains = list(k for k, v in sorted(results.items(), key=lambda t: int(t[1].decode('utf-8')), reverse=True))
    domains_copy = copy.deepcopy(domains)
    for i in domains_copy:
        s = i.decode('utf-8')
        if re.search('^\d+$', s):
            if key_need == 'config':
                continue
            elif key_need == 'domain':
                domains.remove(i)
        else:
            if key_need == 'config':
                domains.remove(i)
            elif key_need == 'domain':
                continue
    return domains


def common_time_delta(date, time_hash_format, domains_org=None, zset_name_format='', exclude_list=''):
    '''
    [配置采集时间差页]
    数据
    {'domain': 'www.baidu.com',
     'total': 22, 876, 129,
     'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
             'd2': {'percent': '2.1%', 'cnt': 489652, 'width': '10.5'},
             'd3': {'percent': '3.3%', 'cnt': 748103, 'width': '16.5'},
             }
    },
    '''
    spider_con = redis.StrictRedis(host='192.168.16.223', port=6379, db=10)
    spider_con_pipline = spider_con.pipeline()
    zset_name = zset_name_format.format(date)
    if domains_org is None:
        domains = spider_con.zrevrangebyscore(zset_name, max='+inf', min=1, start=0, num=1000)
        # domains = spider_con.zrevrangebyscore(zset_name, max='+inf', min=1,)
    else:
        domains = domains_org

    ret = []
    WIDTH = 440

    for site in domains:
        for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2

            time_hash = time_hash_format.format(date, i)
            pipline_timedelta = spider_con_pipline.hget(time_hash, site)
    s = spider_con_pipline.execute()

    for i in range(0, len(domains)):
        try:
            site = domains[i]
        except Exception:
            break
        data = dict()
        total = 0
        time_deltas = s[i * 9:(i + 1) * 9]
        for k in range(1, 10):
            time_level = 'd' + str(k)
            data[time_level] = dict()
            time_delta = time_deltas[k - 1]
            if time_delta is not None:
                data[time_level]['cnt'] = int(time_delta)
            else:
                data[time_level]['cnt'] = 0

            total = total + data[time_level]['cnt']

            data[time_level]['percent'] = ''
            data[time_level]['width'] = ''

        if total:  # total != 0
            for j in range(1, 10):
                time_level = 'd' + str(j)
                p = data[time_level]['cnt'] / total
                data[time_level]['percent'] = '{:.2f}'.format(p * 100) + '%'
                # data[time_level]['width'] = '{:.2f}'.format(WIDTH * p)
                data[time_level]['width'] = ''

        if type(site) is bytes:
            site = str(site, encoding='utf-8')

        # if domains_org is None:
        #     # 如果不是查询，排除已经记录的域名或配置
        #     if site not in exclude_list:
        #         ret.append({
        #             'domain': site,
        #             'total': '{:,}'.format(total),
        #             'data': data
        #         })
        # else:
        #     # 如果是查询，不进行排除
        #     ret.append({
        #         'domain': site,
        #         'total': '{:,}'.format(total),
        #         'data': data
        #     })

        if site not in exclude_list:
            ret.append({
                'domain': site,
                'total': '{:,}'.format(total),
                'data': data
            })
    return ret


def custom_time_delta(date, time_hash_format, domains_org, d1, d2):
    '''
    [配置采集时间差页]
    数据
    {'domain': 'www.baidu.com',
     'total': 22, 876, 129,
    'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
             'd2': {'percent': '2.1%', 'cnt': 489652, 'width': '10.5'},
             'd3': {'percent': '3.3%', 'cnt': 748103, 'width': '16.5'},
             }
    },
    '''
    domains = domains_org

    data = dict()
    for site in domains:
        for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
            time_hash = time_hash_format.format(date, i)
            pipline_timedelta = spider_con_pipline.hget(time_hash, site)
    s = spider_con_pipline.execute()

    for i in range(0, len(domains)):
        try:
            site = domains[i]
        except Exception:
            break
        data[site] = 0
        time_deltas = s[i * 9:(i + 1) * 9]
        for k in range(d1, d2):
            time_delta = time_deltas[k - 1]
            if time_delta is not None:
                data[site] += int(time_delta)
            else:
                continue
    return data


def custom_all_sums(time_hash_format, key_need, date, d1, d2):
    domains = []
    for j in range(d1, d2):
        time_hash1 = time_hash_format.format(date, j)
        domains1 = all_nums_rank(time_hash1, key_need)
        domains += domains1
    domains = list(set(domains))
    result = custom_time_delta(date, time_hash_format, domains, d1, d2)
    domains = list()
    for i, v in sorted(result.items(), key=lambda k: int(k[1]), reverse=True):
        domains.append(i)
    return {'domains': domains, 'nums': result}


def time_delta_history(date_begin, date_end, domain, time_delta_hash_format):
    '''
    [单个配置或域名采集时间差历史]
    数据
    {'date': '2017-3-4',
     'total': 22, 876, 129,
    'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
             'd2': {'percent': '2.1%', 'cnt': 489652, 'width': '10.5'},
             'd3': {'percent': '3.3%', 'cnt': 748103, 'width': '16.5'},
             }
    },
    '''
    date_list = []

    for i in arrow.Arrow.span_range('day', date_begin, date_end):
        date = i[1].format('YYYY-MM-DD')
        date_list.append(date)

    for i in date_list:
        for j in range(1, 10):
            # time_1_2017-03-24_d4
            time_delta_hash_name = time_delta_hash_format.format(i, j)
            spider_con_pipline.hget(time_delta_hash_name, domain)
    time_delta_result = spider_con_pipline.execute()

    ret = []
    WIDTH = 440
    for i in range(len(date_list) - 1, -1, -1):
        date = date_list[i]
        data = dict()
        total = 0
        time_deltas = time_delta_result[i * 9:(i + 1) * 9]
        for k in range(1, 10):
            time_level = 'd' + str(k)
            data[time_level] = dict()
            time_delta = time_deltas[k - 1]
            if time_delta is not None:
                data[time_level]['cnt'] = int(time_delta)
            else:
                data[time_level]['cnt'] = 0

            total = total + data[time_level]['cnt']

            data[time_level]['percent'] = ''
            data[time_level]['width'] = ''

        if total != 0:  # total != 0
            for j in range(1, 10):
                time_level = 'd' + str(j)
                p = data[time_level]['cnt'] / total
                data[time_level]['percent'] = '{:.2f}'.format(p * 100) + '%'
                # data[time_level]['width'] = '{:.2f}'.format(WIDTH * p)
                data[time_level]['width'] = ''

            ret.append({
                'domain': date,
                'total': '{:,}'.format(total),
                'data': data
            })
    return ret


# 获取所有时间差数据
def all_deltas(time_hash1, key_need, date, exclude_list):
    '''
    [所有采集时间差页]
    数据
    {'date': '2017-03-23',
     'total': 22, 876, 129,
    'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
             'd2': {'percent': '2.1%', 'cnt': 489652, 'width': '10.5'},
             'd3': {'percent': '3.3%', 'cnt': 748103, 'width': '16.5'},
             }
    },
    '''
    spider_con = redis.StrictRedis(host='192.168.16.223', port=6379, db=10)
    spider_con_pipline = spider_con.pipeline()

    for i in range(1, 10):
        # 时间差hash time_1_2017-03-24_d2
        time_hash = time_hash1.format(date, i)
        spider = spider_con_pipline.hgetall(time_hash, )

    all_times = spider_con_pipline.execute()
    if all_times.count({}) == 9:
        delta_all = dict()
        delta_all['date'] = date
        delta_all['total'] = 0
        data = dict()
        for i in range(1, 10):
            time_level = 'd' + str(i)
            data[time_level] = {'percent': 0, 'cnt': 0, 'width': 0}
        delta_all['data'] = data
        return delta_all

    all_ds = list()
    for i in all_times:
        i_deltas = list()
        for k, v in i.items():
            s = k.decode('utf-8')
            if re.search('^\d+$', s) and s not in exclude_list:
                if key_need == 'config':
                    i_deltas.append(v)
                else:
                    continue
            elif s not in exclude_list:
                if key_need == 'domain':
                    i_deltas.append(v)
                else:
                    continue
        all_ds.append(i_deltas)

    WIDTH = 440
    data = dict()
    total = 0
    for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
        time_level = 'd' + str(i)
        data[time_level] = dict()
        sum_num = 0
        for k in all_ds[i - 1]:
            sum_num += int(k)
        total += sum_num
        data[time_level]['cnt'] = sum_num

    delta_all = dict()
    for k, i in data.items():
        p = i['cnt'] / total
        i['percent'] = '{:.2f}'.format(p * 100) + '%'
        # i['width'] = '{:.2f}'.format(WIDTH * p)
        i['width'] = ''

    delta_all['date'] = date
    delta_all['total'] = total
    delta_all['data'] = data
    return delta_all


def all_deltas_rank(date, delta, time_hash_format, exclude_list, key_need):
    time_hash = time_hash_format.format(date, delta)
    domains = all_nums_rank(time_hash, key_need)
    zset = global_args['news_config_zset']  # 暂时没有作用
    time_deltas = common_time_delta(date=date, zset_name_format=zset, time_hash_format=time_hash_format,
                                    domains_org=domains, exclude_list=exclude_list)
    sum_search = dict()
    total = 0
    data = dict()
    for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
        time_level = 'd' + str(i)
        data[time_level] = dict()

    for single in time_deltas:
        total += int(''.join(single['total'].split(',')))

        for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
            time_level = 'd' + str(i)
            try:
                data[time_level]['cnt'] += single['data'][time_level]['cnt']
            except Exception:
                data[time_level]['cnt'] = single['data'][time_level]['cnt']
    if total != 0:
        for i in range(1, 10):
            time_level = 'd' + str(i)
            p = data[time_level]['cnt'] / total
            data[time_level]['percent'] = '{:.2f}'.format(p * 100) + '%'
            data[time_level]['width'] = ''
    sum_search['data'] = data
    sum_search['total'] = total
    return sum_search


# 获取相关分组（海外、巡查('89', '21')）的配置ID
def config_ids_get(gid_list):
    # yqht_connection = pymysql.connect(
    #     host='192.168.16.117',
    #     port=3306,
    #     user='spider',
    #     password='7881rtpb',
    #     db='yqht',
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor)

    yqht_connection = pymysql.connect(
        host='192.168.16.223',
        port=3306,
        user='root',
        password='zhxg_140101',
        db='yqht',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    yqht_cousor = yqht_connection.cursor()
    if len(gid_list) > 1:
        sql = 'select id from b_conf where gid in %s' % (gid_list,)
    if len(gid_list) == 1:
        sql = 'select id from b_conf where gid=%s' % (gid_list[0],)
    yqht_cousor.execute(sql)
    config_dicts = yqht_cousor.fetchall()
    yqht_connection.commit()
    yqht_cousor.close()
    yqht_connection.close()
    config_ids = []
    for i in config_dicts:
        config_ids.append(str(i['id']))
    return config_ids


# 配置url查询
def config_url(date, config_id):
    time_hash_format = global_args['config_url_format']
    time_hash = time_hash_format.format(date, config_id)
    domains = spider_con.lrange(time_hash, start=0, end=-1)
    return domains


    # def for_user_timedelta(date, domains=None):
    #     '''
    #     新闻，域名，对上用户
    #     :return:
    #     '''
    #     #
    #     # zset_name_format = global_args['news_user_zset']
    #     return common_time_delta(date, global_args['news_time_hash_format'], domains,)
    #
    #
    # def all_user_timedelta(date, domains=None):
    #     '''
    #     新闻，域名，所有用户
    #     :return:
    #     '''
    #     # time_value_1_2017-03-24_d1
    #     # zset_name_format = global_args['news_all_users_zset']
    #     return common_time_delta(date, global_args['all_user_news_hash_format'], domains)
    #
    #
    # def for_config_timedelta(date, domains=None):
    #     '''
    #     新闻，配置，对上用户
    #     :return:
    #     '''
    #     # data_static_1_2017-03-24:config_id_value_dedup
    #     # zset_name_format = global_args['news_config_zset']
    #     return common_time_delta(date, global_args['news_time_hash_format'], domains,)
    #
    #
    # def all_domains_timedelta(date, domains=None):
    #     '''
    #     域名，所有
    #     :return:
    #     '''
    #     # data_static_2017-04-07:domain_all
    #     # zset_name_format = global_args['all_domains_zset']
    #     return common_time_delta(date, global_args['all_hash_format'], domains)
    #
    #
    # def all_configs_timedelta(date, domains=None):
    #     '''
    #     域名，所有
    #     :return:
    #     '''
    #     # data_static_2017-04-07:domain_all
    #     # zset_name_format = global_args['all_configs_zset']
    #     return common_time_delta(date, global_args['all_hash_format'], domains)


    # 时间历史查询
