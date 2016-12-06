#!/usr/bin python
# coding=utf-8

import os.path
import json
import datetime
import re
import signal
import urllib
import requests
import redis
import pymongo
import time
from math import *

import tornado.autoreload
from pprint import pprint
import tornado.locale
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.log import LogFormatter
import tornado.web
from tornado.escape import json_encode
from tornado.options import define, options

# import ConfigParser
#
# config = ConfigParser.ConfigParser()
# if len(config.read('./user_conf.ini')) == 0:
#     print '[error] cannot read the config file.'
#     exit(-1)
# else:
#     print '[info] read the config file.'
#
# USER_AREA = config.get('user', 'user_area')
# print '[info] user area is :', USER_AREA

REDIS_SERVER = 'redis://127.0.0.1/10'
MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'

# local_flg 0: 附近的人  2：朋友圈
FRIENDS_FLG = 2
AROUND_FLG = 0
PAGE_NUM = 10

define("port", default=5000, help="run on the given port", type=int)

amap_key = '0c7fb71b2e13546416337666cd406db3'  # 高德地图JavaScriptAPI key 220.249.18.226
# baidu_map_key = 'e9ospC88hj5iHoI9xUabaHFYAEiFXlRa'
baidu_map_key = '4119853f8e9c07a0eeaf89352b2c795d'


# logger = LogFormatter()

class Util(object):
    @staticmethod
    def calc_distance((Lng_A, Lat_A), (Lng_B, Lat_B)):
        '''
            Lng_A = 118.796877, Lat_A = 32.060255  # 南京
            Lng_B = 116.407395, Lat_B = 39.904211  # 北京
            Lat_A 纬度A, Lng_A 经度A
            Lat_B 纬度B, Lng_B 经度B
            distance 距离(km)
        '''
        print '[info] calc_distance() ', (Lng_A, Lat_A), (Lng_B, Lat_B)
        ra = 6378.140  # 赤道半径 (km)
        rb = 6356.755  # 极半径 (km)
        flatten = (ra - rb) / ra  # 地球扁率
        rad_lat_A = radians(float(Lat_A))
        rad_lng_A = radians(float(Lng_A))
        rad_lat_B = radians(float(Lat_B))
        rad_lng_B = radians(float(Lng_B))
        pA = atan(rb / ra * tan(rad_lat_A))
        pB = atan(rb / ra * tan(rad_lat_B))
        xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
        c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
        c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
        dr = flatten / 8 * (c1 - c2)
        distance = ra * (xx + dr)
        return distance
        # print('(Lat_A, Lng_A)=({0:10.3f},{1:10.3f})'.format(Lat_A, Lng_A))
        # print('(Lat_B, Lng_B)=({0:10.3f},{1:10.3f})'.format(Lat_B, Lng_B))
        # print('Distance={0:10.3f} km'.format(distance))

    def convert_str_xy_to_x_y(self, str_x_y):
        '''
        Args:
            str_x_y: '116.322987_39.983424','116.322987,39.983424'
        Returns:
            str type (x,y)
        '''
        (x, y) = (None, None)
        if str_x_y != u'None' and len(str_x_y) > 0:
            sp = '_' if '_' in str_x_y else ','
            x = str_x_y.split(sp)[0]
            y = str_x_y.split(sp)[1]
            # logger.format('convert_str_xy_to_x_y() %s %s %s' % (str_x_y, x, y))
        return (x, y)

    def convert_xy_to_address(self, str_x_y):
        '''
        Args:
            str_x_y: '39.983424_116.322987'
        Returns:
            '北京市海淀区中关村大街27号1101-08室'
        '''
        address = u'位置信息不明'
        (x, y) = self.convert_str_xy_to_x_y(str_x_y)
        if x:
            url = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&' \
                  'location=%s,%s&output=json&pois=0&ak=%s' % (x, y, baidu_map_key)

            # logger.format('[info] convert_xy_to_address() %s' % url)
            response = requests.get(url)
            content = response.content[len('renderReverse&&renderReverse('):-1]
            j = json.loads(content)
            address = j['result']['sematic_description']

        return address

    def convert_xy_to_addressComponent(self, str_x_y):
        '''
        Args:
            str_x_y: '39.983424_116.322987'
        Returns:
                "addressComponent": {
                                      "country": "中国",
                                      "country_code": 0,
                                      "province": "北京市",
                                      "city": "北京市",
                                      "district": "海淀区",
                                      "adcode": "110108",
                                      "street": "中关村大街",
                                      "street_number": "27号1101-08室",
                                      "direction": "附近",
                                      "distance": "7"
                                    },
        '''
        addressComponent = {"country": "",
                            "country_code": 0,
                            "province": "",
                            "city": "",
                            "district": "",
                            "adcode": "",
                            "street": "",
                            "street_number": "",
                            "direction": "",
                            "distance": ""
                            }
        (x, y) = self.convert_str_xy_to_x_y(str_x_y)
        if x:
            url = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&' \
                  'location=%s,%s&output=json&pois=0&ak=%s' % (x, y, baidu_map_key)

            # logger.format('[info] convert_xy_to_address() %s' % url)
            response = requests.get(url)
            content = response.content[len('renderReverse&&renderReverse('):-1]
            j = json.loads(content)
            addressComponent = j['result']['addressComponent']

        return addressComponent

    @staticmethod
    def time_min(ago_time_str):
        '''
        Args:
            ago_time_str: 例：'1 hour' or '2 minutes'
        Returns:
            计算XX时间之前的结果
        '''
        ret_time = datetime.datetime.now()
        if ago_time_str is None:
            return ret_time

        num_str = re.match(re.compile(r"(\d+)\s[a-zA-Z]+"), ago_time_str)
        if num_str:
            num = int(num_str.group(1))
            if 'second' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(seconds=num))
            if 'minute' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(minutes=num))
            if 'hour' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(hours=num))
            if 'day' in ago_time_str:
                ret_time = (ret_time - datetime.timedelta(days=num))

        # print ret_time.strftime("%Y-%m-%d %H:%M:%S")
        return ret_time

    @staticmethod
    def convert_ago_time_to_days(timestamp):
        now = datetime.datetime.now()
        t = datetime.datetime.utcfromtimestamp(timestamp)
        if now > t:
            num_str = re.match(re.compile(r"(\d+)\s[a-z]+"), str(now - t)).group(1)
            return num_str + u'天前'
        else:
            return u'未知时间'

    def get_loginUser(self):
        return 'admin'


class SessionManager(object):
    def __init__(self):
        util = Util()
        self.userId = util.get_loginUser()

        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.around_snsId_hset_key = '_around_snsId_hset'
        self.around_pages_hset_key = '_around_pages_hset'
        self.around_current = 'around_current'  # index

        self.friends_snsId_hset_key = '_friends_snsId_hset'
        self.friends_pages_hset_key = '_friends_pages_hset'
        self.friends_current = 'friends_current'  # index

    def set_around_result(self, snsInfo_list):
        print 'set_around_result', len(snsInfo_list)
        snsId_list = [snsInfo['snsId'] for snsInfo in snsInfo_list]

        if self.conn.exists(self.userId + self.around_snsId_hset_key):
            self.conn.delete(self.userId + self.around_snsId_hset_key)

        i = 1
        for snsId in snsId_list:
            self.conn.hset(self.userId + self.around_snsId_hset_key, i, snsId)
            i = i + 1

        self.conn.hset(self.userId + self.around_pages_hset_key, self.around_current, 1)

    def get_around_result(self, action):
        snsId_list = []
        current = self.conn.hget(self.userId + self.around_pages_hset_key, self.around_current)
        current = int(current)
        total = self.conn.hlen(self.userId + self.around_snsId_hset_key)
        print 'action:', action, 'current:', current, 'total:', total

        start = current
        end = current + PAGE_NUM - 1

        if total <= PAGE_NUM:  # 不足1页
            start = 1
            end = total
        else:
            if action == 'frist':
                start = 1
                end = total if total < PAGE_NUM else PAGE_NUM

            if action == 'next':
                if current + PAGE_NUM >= total:  # 已经是末页
                    start = current
                    end = total
                else:
                    start = current + PAGE_NUM
                    end = start + PAGE_NUM - 1
                    if start <= total and total <= end:
                        end = total

            if action == 'pre':
                if current == 1:  # 已经是首页
                    start = 1
                    end = PAGE_NUM
                else:
                    start = current - PAGE_NUM
                    end = start + PAGE_NUM - 1

            if action == 'last':
                start = 1 if total < PAGE_NUM else (total - (total % PAGE_NUM) + 1)
                end = total

        self.conn.hset(self.userId + self.around_pages_hset_key, self.around_current, start)

        print 'start:', start, 'end:', end
        for i in range(start, end + 1):
            snsId_list.append(self.conn.hget(self.userId + self.around_snsId_hset_key, i))

        return snsId_list

    def get_around_result_cnt(self):
        return self.conn.hlen(self.userId + self.around_snsId_hset_key)

    def get_around_result_currentPage(self):
        return self.conn.hget(self.userId + self.around_pages_hset_key, self.around_current)

    def set_friends_result(self, snsInfo_list):
        snsId_list = [snsInfo['snsId'] for snsInfo in snsInfo_list]

        if self.conn.exists(self.userId + self.friends_snsId_hset_key):
            self.conn.delete(self.userId + self.friends_snsId_hset_key)
        i = 1
        for snsId in snsId_list:
            self.conn.hset(self.userId + self.friends_snsId_hset_key, i, snsId)
            i = i + 1

        self.conn.hset(self.userId + self.friends_pages_hset_key, self.friends_current, 1)

    def get_friends_result(self, action):
        snsId_list = []
        current = self.conn.hget(self.userId + self.friends_pages_hset_key, self.friends_current)
        current = int(current)
        total = self.conn.hlen(self.userId + self.friends_snsId_hset_key)
        print 'get_friends_result()', 'action:', action, 'current:', current, 'total:', total

        start = current
        end = current + PAGE_NUM - 1

        if total <= PAGE_NUM:  # 不足1页
            start = 1
            end = total
        else:
            if action == 'first':
                start = 1
                end = total if total < PAGE_NUM else PAGE_NUM

            if action == 'next':
                if current + PAGE_NUM >= total:  # 已经是末页
                    start = current
                    end = total
                else:
                    start = current + PAGE_NUM
                    end = start + PAGE_NUM - 1
                    if start <= total and total <= end:
                        end = total

            if action == 'pre':
                if current == 1:  # 已经是首页
                    start = 1
                    end = PAGE_NUM
                else:
                    start = current - PAGE_NUM
                    end = start + PAGE_NUM - 1

            if action == 'last':
                start = 1 if total < PAGE_NUM else (total - (total % PAGE_NUM) + 1)
                end = total

        self.conn.hset(self.userId + self.friends_pages_hset_key, self.friends_current, start)

        print 'get_friends_result()', 'start:', start, 'end:', end
        for i in range(start, end + 1):
            snsId_list.append(self.conn.hget(self.userId + self.friends_snsId_hset_key, i))

        return snsId_list

    def get_friends_result_cnt(self):
        return self.conn.hlen(self.userId + self.friends_snsId_hset_key)

    def get_friends_result_currentPage(self):
        return self.conn.hget(self.userId + self.friends_pages_hset_key, self.friends_current)


class DBDriver(object):
    def __init__(self):
        self.util = Util()
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.wx_sns_data
        self.sns_info = self.db.sns_info
        self.lbs_info = self.db.lbs_info
        self.users = self.db.users
        self.authorId_name = self.db.authorId_name
        self.db_patch_location = self.db.db_patch_location  # drivers
        self.sns_info_patch = self.db.sns_info_patch

    def patch_address(self):
        l = self.sns_info.find({"localFlag": AROUND_FLG})
        cnt = 0
        for i in l:
            if i['rawXML']['TimelineObject'].has_key('location'):
                x = i['rawXML']['TimelineObject']['location']['@latitude']
                y = i['rawXML']['TimelineObject']['location']['@longitude']
                if x != '0.0':
                    str_x_y = x + '_' + y
                    addressComponent = self.util.convert_xy_to_addressComponent(str_x_y)

                    snsId = i['snsId']
                    country = addressComponent['country']
                    province = addressComponent['province']
                    city = addressComponent['city']
                    district = addressComponent['district']
                    adcode = addressComponent['adcode']
                    street = addressComponent['street']

                    self.sns_info_patch.insert({"snsId": snsId,
                                                "country": country,
                                                "province": province,
                                                "city": city,
                                                "district": district,
                                                "adcode": adcode,
                                                "street": street,
                                                "latitude": x,
                                                "longitude": y})
            cnt = cnt + 1

    def get_friends(self):
        authors = []
        l = self.authorId_name.find().sort("authorName")
        for sns_info in l:
            author = sns_info["authorName"]
            authors.append(author)

        authors.sort()

        return authors

    def get_friendsId_by_name(self, authorName_list):
        db = DBDriver()
        friendsId_list = []
        for authorName in authorName_list:
            if authorName:
                authorId_name = db.authorId_name.find_one({"authorName": authorName})
                friendsId_list.append(authorId_name['authorId'])

        return friendsId_list

    def get_around(self):
        authors = []
        l = self.lbs_info.find({"localFlag": AROUND_FLG}).sort("authorName")
        for sns_info in l:
            author = sns_info["authorName"]
            authors.append(author)

        return list(set(authors))

    def get_address_form_patch(self, (x, y)):
        poi_address = u'地点未知'
        l = self.sns_info_patch.find_one({"longitude": x,
                                          "latitude": y})
        if l and l['street']:
            poi_address = l['city'] + u' · ' + l['district'] + l['street']

        return poi_address

    def patch_agoDays_address(self, sns_info):
        ctime = sns_info["timestamp"]
        ago_days = Util.convert_ago_time_to_days(ctime)

        poi_address = u'未知地点'
        if sns_info['rawXML']['TimelineObject'].has_key('location'):
            sns_info_x = sns_info['rawXML']['TimelineObject']['location']['@longitude']
            sns_info_y = sns_info['rawXML']['TimelineObject']['location']['@latitude']
            if sns_info_x != '0.0':
                poi_address = sns_info['rawXML']['TimelineObject']['location']['@poiName']
                if not poi_address:
                    poi_address = self.get_address_form_patch((sns_info_x, sns_info_y))

        return (ago_days, poi_address)

    def friends_sns_info(self, friends='', timeStart='', timeEnd='',
                         hasPic='', hasLikes='', hasComments=''):
        # local_flg 0: 附近的人  2：朋友圈
        sns_info_list = []
        cond = {}

        friendsId_list = self.get_friendsId_by_name(friends)
        if friendsId_list:
            cond['authorId'] = {"$in": friendsId_list}

        if timeStart:
            st = int(time.mktime(time.strptime(timeStart + ' 00:00:00', "%Y-%m-%d %H:%M:%S")))
        else:
            st = int(time.mktime(time.strptime('1971-01-01' + ' 00:00:00', "%Y-%m-%d %H:%M:%S")))

        if timeEnd:
            et = int(time.mktime(time.strptime(timeEnd + ' 23:59:59', "%Y-%m-%d %H:%M:%S")))
        else:
            et = int(time.mktime(time.strptime('2046-01-01' + ' 23:59:59', "%Y-%m-%d %H:%M:%S")))

        cond['timestamp'] = {"$gte": st, "$lte": et}

        if hasPic == 'true':
            cond['mediaList.0'] = {"$exists": 1}  # len(mediaList) >= 0

        if hasLikes == 'true':
            cond['likes.0'] = {"$exists": 1}

        if hasComments == 'true':
            cond['comments.0'] = {"$exists": 1}

        print '[info] friends cond is:'
        pprint(cond)

        l = self.sns_info.find(cond).sort("timestamp", pymongo.DESCENDING)
        for sns_info in l:
            (ago_days, poi_address) = self.patch_agoDays_address(sns_info)
            sns_info['ago_days'] = ago_days
            sns_info['poi_address'] = poi_address
            sns_info_list.append(sns_info)

        print '[info] friends post result is:', len(sns_info_list)
        return sns_info_list

    def around_sns_info(self, timeStart='', timeEnd='', author=[], x_y='', distance='', hasPic=''):
        # local_flg 0: 附近的人  2：朋友圈
        sns_info_list = []
        db_patch_list = []  # 符合距离要求的db_patch
        cond = {}

        if timeStart:
            st = int(time.mktime(time.strptime(timeStart + ' 00:00:00', "%Y-%m-%d %H:%M:%S")))
        else:
            st = int(time.mktime(time.strptime('1971-01-01' + ' 00:00:00', "%Y-%m-%d %H:%M:%S")))

        if timeEnd:
            et = int(time.mktime(time.strptime(timeEnd + ' 23:59:59', "%Y-%m-%d %H:%M:%S")))
        else:
            et = int(time.mktime(time.strptime('2046-01-01' + ' 23:59:59', "%Y-%m-%d %H:%M:%S")))

        cond['timestamp'] = {"$gte": st, "$lte": et}

        if author and author[0] != 'all':
            cond['authorName'] = {"$in": author}

        if distance:
            (x, y) = self.util.convert_str_xy_to_x_y(x_y)
            db_list = self.db_patch_location.find()
            for db in db_list:
                (db_y, db_x) = self.util.convert_str_xy_to_x_y(db['location'])
                if db_x and float(db_x) != 0.0:
                    d = self.util.calc_distance((x, y), (db_x, db_y))
                    print u'选取地', (x, y), u'限定', distance, u'采集地', (db_x, db_y), u'相距', d
                    if d <= float(distance):
                        db_patch_list.append(db['db_patch'])

            cond['db_patch'] = {"$in": db_patch_list}

        if hasPic:
            cond['mediaList.0'] = {"$exists": 1}  # len(mediaList) >= 0

        print '[info] around post cond:'
        pprint(cond)

        info_list = self.lbs_info.find(cond).sort("timestamp", pymongo.DESCENDING)  # .skip(10 * skip_page).limit(10)

        for sns_info in info_list:
            (ago_days, poi_address) = self.patch_agoDays_address(sns_info)
            sns_info['ago_days'] = ago_days
            sns_info['poi_address'] = poi_address
            sns_info_list.append(sns_info)

        print '[info] around post result:', len(sns_info_list)
        return sns_info_list

    def get_drivers(self):
        return self.db_patch_location.find()

    def get_users(self):
        return self.users.find()

    def get_aroundInfo_list_by_snsId(self, snsId_list):
        aroundInfo_list = []
        l = self.sns_info.find({'snsId': {'$in': snsId_list}}).sort("timestamp", pymongo.DESCENDING)
        for sns_info in l:
            (ago_days, poi_address) = self.patch_agoDays_address(sns_info)
            sns_info['ago_days'] = ago_days
            sns_info['poi_address'] = poi_address
            aroundInfo_list.append(sns_info)

        return aroundInfo_list

    def get_friendsInfo_list_by_snsId(self, snsId_list):
        lbsInfo_list = []
        l = self.lbs_info.find({'snsId': {'$in': snsId_list}}).sort("timestamp", pymongo.DESCENDING)
        for sns_info in l:
            (ago_days, poi_address) = self.patch_agoDays_address(sns_info)
            sns_info['ago_days'] = ago_days
            sns_info['poi_address'] = poi_address
            lbsInfo_list.append(sns_info)

        return lbsInfo_list

    def get_loginUser_area(self):
        area_list = []
        user = self.util.get_loginUser()
        if user == 'admin':
            area_list = [{"province": "all", "city": "all", "district": "all"}]
        else:
            l = self.users.find({'userName': user})
            for i in l:
                area_list.append({"province": i['province'], "city": i['city'], "district": i['district']})

        return area_list

    def make_userArea_point_js(self):
        '''
            area : {"province": "北京市", "city": "北京市", "district": "海淀区"}
            var weixin_lbs_info =  [
                {"lnglat": ["116.418757", "39.917544"], "name": "东城区"},
                {"lnglat": ["116.366794", "39.915309"], "name": "西城区"},
                {"lnglat": ["116.486409", "39.921489"], "name": "朝阳区"},
            ];
        '''
        area = self.get_loginUser_area()
        # if locations[0]['province'] == 'all': # admin
        l = self.db_patch_location.find()

        fd = open('./static/js/lbsInfo.js', 'w')  # 不能使用‘_’作为文件名
        fd.write('var lbsInfo =  [\n')
        for i in l:
            location = i['location']
            if location != u'None':
                (y, x) = self.util.convert_str_xy_to_x_y(location)
                if x and float(x):
                    fd.write('''    {"lnglat": ["''' + x + '''", "''' + y + '''"], "name": "''' +
                             i['db_patch'] + '''"},\n''')
        fd.write('];\n')
        fd.close()

    def make_userArea_outline_js(self):
        '''
            area : {"province": "北京市", "city": "北京市", "district": "海淀区"}
            var userArea =  "朝阳区";
        '''
        area = self.get_loginUser_area()
        fd = open('./static/js/userArea.js', 'w')  # 不能使用‘_’作为文件名
        fd.write('''var userArea = "''' + area[0]['district'] + '''";\n''')
        fd.close()


class Manager(tornado.web.RequestHandler):
    def get(self):
        print '[info]Manager get() start'
        util = Util()
        y_x = self.get_argument('y_x')
        address = util.convert_xy_to_address(y_x)
        # jsonStr = json.dumps(ret, sort_keys=True)
        print '[info]Manager get()', y_x, '->', address
        # self.write(json.dumps({'address': address}))
        self.write(address)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            title=u"微信采集展示")


class FriendsHandler(tornado.web.RequestHandler):
    def create_table(self, sns_info_list):
        html = '''
                <table id="sns_info_tab" class="table">
                <thead>
                <tr>
                    <th></th>
                    <th></th>
                </tr>
                </thead>
                <tbody>
                '''

        for sns_info in sns_info_list:
            html += '''
            <tr style="border: 1px;">
                <td>
                    <div class="sns_left" style="padding-top:0;">
                        <img src="static/images/weixin_logo.png" class="sns_author_logo img-rounded"/>
                    </div>
                </td>
                <td>
                    <div class="sns_right">
                        <div class="sns_author row clearfix">
                        ''' + sns_info["authorName"] + '''
                        </div>
                        <div class="sns_content row clearfix">
                            <small>''' + sns_info["content"] + '''</small>
                        </div>
                        <div class="pull-left sns_image_list row clearfix">'''
            # -----------------------------------------------------------------------------
            for url in sns_info["mediaList"]:
                html += '''<img src="http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=''' \
                        + url + '''" class="media img-rounded sns_image"/>'''

            html += '''</div>'''
            # -----------------------------------------------------------------------------
            html += '''<div class="sns_timeLocation row clearfix">
                        <h6><span class="glyphicon glyphicon-time"></span>'''
            html += sns_info["ago_days"]
            html += '''&nbsp;&nbsp;&nbsp;
                            <span class="glyphicon glyphicon-screenshot"></span>&nbsp;'''
            html += sns_info["poi_address"]
            html += ''' </h6>
                        </div>'''

            if len(sns_info["likes"]) > 0:
                html += '''<div class="sns_comments row clearfix">
                            <span class="glyphicon glyphicon-heart-empty"></span>'''
                for comment in sns_info["likes"]:
                    html += '''<small>&nbsp;&nbsp;'''
                    html += comment['userName']
                    html += '''</small>'''

                html += '''</div>'''

            if len(sns_info["comments"]) > 0:
                html += '''<div class="sns_comments row clearfix">'''
                for comment in sns_info["comments"]:
                    html += '''<h4>'''
                    html += comment['authorName']
                    html += ''':<small>&nbsp;&nbsp;'''
                    html += comment['content']
                    html += '''</small>'''
                    html += '''</h4>'''
                html += '''</div>'''

            html += '''</div>
                </td>
            </tr>'''

        # end for
        html += '''</tbody></table>'''
        return html

    def get(self):
        db = DBDriver()
        session = SessionManager()

        init_flg = self.get_argument('init', 'false')
        action = self.get_argument('action', '')

        print '------------------------------- Friends  get  ----------------------------------- '
        print  'init_flg: ', init_flg, 'action: ', action
        print '------------------------------- Friends  get  ----------------------------------- '
        friends_list = db.get_friends()
        if init_flg == 'true':  # init
            sns_info_list = db.friends_sns_info()
            session.set_friends_result(sns_info_list)
            total = session.get_friends_result_cnt()
            self.render("friends.html",
                        title=u"微信-朋友圈",
                        current=1,
                        total=total,
                        sns_info_list=sns_info_list[:PAGE_NUM],
                        friends_list=friends_list)
        else:
            snsId_list = session.get_friends_result(action)
            sns_info_list = db.get_aroundInfo_list_by_snsId(snsId_list)
            print 'get() sns_info_list:', len(sns_info_list)
            current = session.get_friends_result_currentPage()
            total = session.get_friends_result_cnt()
            html = self.create_table(sns_info_list)
            self.write({'currentPage': int(current) / PAGE_NUM + 1, 'total': total, 'html': html})

    def post(self):
        session = SessionManager()
        db = DBDriver()
        snsId_list = []

        friendsSel = self.get_arguments('friendsSel')

        timeStart = self.get_argument('timeStart', '')
        timeEnd = self.get_argument('timeEnd', '')
        hasPic = self.get_argument('hasPic', '')
        hasLikes = self.get_argument('hasLikes', '')
        hasComments = self.get_argument('hasComments', '')

        print '------------------------------- Friends  post  ----------------------------------- '
        print 'friendsSel: ', friendsSel
        print 'timeStart: ', timeStart, ' timeEnd:', timeEnd, 'hasPic: ', hasPic, ' hasLikes:', hasLikes, ' hasComments: ', hasComments
        print '------------------------------- Friends  post  ----------------------------------- '
        sns_info_list = db.friends_sns_info(friendsSel, timeStart, timeEnd, hasPic, hasLikes, hasComments)
        session.set_friends_result(sns_info_list)

        current = session.get_friends_result_currentPage()
        total = session.get_friends_result_cnt()
        html = self.create_table(sns_info_list[:PAGE_NUM])

        self.write({'currentPage': int(current) / PAGE_NUM + 1, 'total': total, 'html': html})


class AroundHandler(tornado.web.RequestHandler):
    def create_table(self, sns_info_list):
        html = '''
        <table id="sns_info_tab" class="table">
        <thead>
        <tr>
            <th></th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        '''

        for sns_info in sns_info_list:
            html += '''
            <tr style="border: 1px solid #ccc;">
                <td>
                    <div class="sns_left">
                        <img src="static/images/weixin_logo.png" class="sns_author_logo img-rounded"/>
                    </div>
                </td>
                <td>
                    <div class="sns_right">
                        <div class="sns_author row clearfix">
                        ''' + sns_info["authorName"] + '''
                        </div>
                        <div class="sns_content row clearfix">
                            <small>''' + sns_info["content"] + '''</small>
                        </div>
                        <div class="pull-left sns_image_list row clearfix">'''
            # -----------------------------------------------------------------------------
            for url in sns_info["mediaList"]:
                html += '''<img src="http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=''' \
                        + url + '''" class="media img-rounded sns_image"/>'''

            html += '''</div>'''
            # -----------------------------------------------------------------------------
            html += '''
                    <div class="sns_timeLocation row clearfix">
                        <h6><span class="glyphicon glyphicon-time"></span>&nbsp; ''' \
                    + sns_info["ago_days"] + '''&nbsp;&nbsp;&nbsp;
                        <span class="glyphicon glyphicon-screenshot"></span>&nbsp; ''' \
                    + sns_info["poi_address"] + '''
                        </h6>
                    </div>
                    '''
            # -----------------------------------------------------------------------------
            if len(sns_info["likes"]) > 0:
                html += '''
                    <div class="sns_comments row clearfix">
                        <span class="glyphicon glyphicon-heart-empty"></span>'''

            for comment in sns_info["likes"]:
                html += '''<small>&nbsp;&nbsp;''' + comment['userName'] + '''</small>'''

            html += '''</div>'''
            # -----------------------------------------------------------------------------
            if len(sns_info["comments"]) > 0:
                html += '''<div class="sns_comments row clearfix">'''
                for comment in sns_info["comments"]:
                    html += '''<h4>''' + comment['authorName'] + '''<small>&nbsp;&nbsp;''' + \
                            comment['content'] + '''</small></h4>'''
                html += '''</div>'''

            # -----------------------------------------------------------------------------
            html += '''</div>
                </td>
            </tr>'''
            # -----------------------------------------------------------------------------

        # end for
        html += '''</tbody></table>'''
        return html

    def get(self):
        db = DBDriver()
        session = SessionManager()

        init_flg = self.get_argument('init', 'false')
        action = self.get_argument('action', '')

        print '------------------------------- Around  get  -----------------------------------'
        print  'init_flg: ', init_flg, 'action: ', action
        print '------------------------------- Around  get  -----------------------------------'
        authors_list = db.get_around()
        if init_flg == 'true':  # init
            sns_info_list = db.around_sns_info()
            session.set_around_result(sns_info_list)
            total = session.get_around_result_cnt()
            self.render(
                "around.html",
                current=1,
                total=total,
                sns_info_list=sns_info_list[:PAGE_NUM],
                authors_list=authors_list)
        else:
            snsId_list = session.get_around_result(action)
            sns_info_list = db.get_friendsInfo_list_by_snsId(snsId_list)
            print 'sns_info_list:', len(sns_info_list)
            current = session.get_around_result_currentPage()
            total = session.get_around_result_cnt()
            html = self.create_table(sns_info_list)
            self.write({'currentPage': int(current) / PAGE_NUM + 1, 'total': total, 'html': html})

    def post(self):
        db = DBDriver()
        session = SessionManager()
        snsId_list = []

        timeStart = self.get_argument('timeStart', '')
        timeEnd = self.get_argument('timeEnd', '')
        authors = self.get_arguments('authors')
        hasPic = self.get_argument('hasPic', '')
        x_y = self.get_argument('x_y', '')
        distance = self.get_argument('distance', '')

        print '-------------------------------   post  ----------------------------------- '
        print 'timeStart:', timeStart, ' timeEnd: ', timeEnd, ' authors:', authors
        print 'hasPic:', hasPic, 'x_y:', x_y, ' distance:', distance
        print '-------------------------------   post  ----------------------------------- '
        sns_info_list = db.around_sns_info(timeStart, timeEnd, authors, x_y, distance, hasPic)
        session.set_around_result(sns_info_list)

        total = session.get_around_result_cnt()
        current = session.get_around_result_currentPage()
        html = self.create_table(sns_info_list[:PAGE_NUM])

        self.write({'currentPage': int(current) / PAGE_NUM + 1, 'total': total, 'html': html})


class DriversHandler(tornado.web.RequestHandler):
    def get(self):
        db = DBDriver()
        print '-------------------------------   get  -----------------------------------'
        drivers = db.get_drivers()
        users = db.get_users()
        print '-------------------------------   get  -----------------------------------'
        self.render(
            "drivers.html",
            page_title=u"微信-",
            header_text=u"采集结果展示",
            users=users,
            drivers=drivers)

    def post(self):
        pass


class UserManagerHandler(tornado.web.RequestHandler):
    def get(self):
        db = DBDriver()
        print '-------------------------------   get  -----------------------------------'
        drivers = db.get_drivers()
        users = db.get_users()
        print '-------------------------------   get  -----------------------------------'
        self.render(
            "userManager.html",
            page_title=u"微信-",
            header_text=u"采集结果展示",
            users=users)

    def post(self):
        db = DBDriver()

        userName = self.get_argument('userName', '')
        province = self.get_arguments('province')
        city = self.get_argument('city', '')
        district = self.get_argument('district', '')


class SnsInfoModule(tornado.web.UIModule):
    def render(self, sns_info):
        return self.render_string(
            "modules/sns_info.html",
            sns_info=sns_info)

    def css_files(self):
        return "css/search_result.css"

    def javascript_files(self):
        return "js/search_result.js"


def signal_handler(signum, frame):
    tornado.ioloop.IOLoop.instance().stop()


signal.signal(signal.SIGINT, signal_handler)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            static_js_path=os.path.join(os.path.dirname(__file__), "static/js"),
            ui_modules={"SnsInfo": SnsInfoModule},
            debug=True,
        )
        handlers = [
            (r"/", MainHandler),
            (r"/friends", FriendsHandler),
            (r"/around", AroundHandler),
            (r"/drivers", DriversHandler),
            (r"/users", UserManagerHandler),
            (r"/convert_xy_to_address", Manager),
            # (r"/(authors\.js)", tornado.web.StaticFileHandler, dict(path=settings['static_js_path'])),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    db = DBDriver()
    db.make_userArea_point_js()  # 控制前端采集点描绘
    db.make_userArea_outline_js()  # 控制前端行政区轮廓划分

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def patch_address():
    db = DBDriver()
    db.patch_address()


def test():
    db = DBDriver()
    pprint(db.get_friends())


if __name__ == "__main__":
    # test()
    # patch_address()
    main()
