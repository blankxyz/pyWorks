#!/usr/bin python
# coding=utf-8

import os.path
import json
import datetime
import re
import signal
import requests
import redis
import pymongo
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
from tornado.options import define, options

REDIS_SERVER = 'redis://127.0.0.1/10'
MONGODB_SERVER = '127.0.0.1' # '192.168.187.4'
MONGODB_PORT = 27017  #'37017'

define("port", default=5000, help="run on the given port", type=int)

# sns_info_list =
# {"12404766082711236659":
# "{u'snsId': u'12404766082711236659',
# u'timestamp': 1478763351,
# u'authorId': u'wxid_6oeldtzws22c22',
# u'comments':
# [{u'content': u'[\\u60a0\\u95f2][\\u60a0\\u95f2]',
#   u'authorName': u'jfvznumur',
#   u'isCurrentUser': True,
#   u'authorId': u'wxid_komia980lnkq12'
# }],
# u'content': u'\\u897f\\u6e56\\u9001\\u522b',
# u'authorName': u'\\u671d\\u9633',
# u'isCurrentUser': False,
# u'likes': [{u'userName': u'jfvznumur', u'isCurrentUser': True, u'userId': u'wxid_komia980lnkq12'}],
# 'db_patch': '75a5f0857d53_1479088651.45',
# u'mediaList': [u'http://mmsns.qpic.cn/mmsns/PFPUMLY8F77ibkrGrBsiaxaUocjELU14XXSwVyf8ibBcCJAno7eiaIlib3VFGAgiaVqTVXibLrsiapYiabcs/0'],
# u'rawXML':
# u'<TimelineObject>
#   <id><![CDATA[12404766082711236659]]></id>
#   <username><![CDATA[wxid_6oeldtzws22c22]]></username>
#   <createTime><![CDATA[1478763351]]></createTime>
#   <contentDescShowType>0</contentDescShowType>
#   <contentDescScene>0</contentDescScene>
#   <private><![CDATA[0]]></private>
#   <contentDesc><![CDATA[\\u897f\\u6e56\\u9001\\u522b]]></contentDesc>
#   <contentattr><![CDATA[0]]></contentattr>
#   <sourceUserName></sourceUserName>
#   <sourceNickName></sourceNickName>
#   <statisticsData></statisticsData>
#   <location poiClickableStatus =  \"0\"  poiClassifyId =  \"\"  poiScale =  \"0\"  longitude =  \"0.0\"  city =  \"\"
#   poiName =  \"\"  latitude =  \"0.0\"  poiClassifyType =  \"0\"  poiAddress =  \"\" ></location><ContentObject>
#   <contentStyle><![CDATA[1]]></contentStyle><title></title><description></description><contentUrl></contentUrl>
#   <mediaList><media><id><![CDATA[12404766083001757752]]></id><type><![CDATA[2]]></type>
#   <title></title><description></description><private><![CDATA[0]]></private>
#   <url type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/PFPUMLY8F77ibkrGrBsiaxaUocjELU14XXSwVyf8ibBcCJAno7eiaIlib3VFGAgiaVqTVXibLrsiapYiabcs/0]]></url>
#   <thumb type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/PFPUMLY8F77ibkrGrBsiaxaUocjELU14XXSwVyf8ibBcCJAno7eiaIlib3VFGAgiaVqTVXibLrsiapYiabcs/150]]></thumb>
#   <size height =  \"854.0\"  width =  \"640.0\"  totalSize =  \"94467.0\" ></size></media></mediaList></ContentObject>
#   <actionInfo></actionInfo></TimelineObject>'}",

amap_key = '0c7fb71b2e13546416337666cd406db3'  # 高德地图JavaScriptAPI key 220.249.18.226
baidu_map_key = 'e9ospC88hj5iHoI9xUabaHFYAEiFXlRa'


# logger = LogFormatter()

class Util(object):
    @staticmethod
    def calc_distance((Lng_A, Lat_A), (Lng_B, Lat_B)):
        '''
            Lat_A = 32.060255, Lng_A = 118.796877  # 南京
            Lat_B = 39.904211, Lng_B = 116.407395  # 北京
            Lat_A 纬度A, Lng_A 经度A
            Lat_B 纬度B, Lng_B 经度B
            distance 距离(km)
        '''
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
        if str_x_y != 'None' and str_x_y:
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
        # t = datetime.datetime.utcfromtimestamp(timestamp)
        t = datetime.datetime.utcfromtimestamp(timestamp)
        if now > t:
            # print str(now - t)
            num_str = re.match(re.compile(r"(\d+)\s[a-z]+"), str(now - t)).group(1)
            return num_str + u'天前'
        else:
            return u'未知时间'


class RedisDriver(object):
    def __init__(self):
        self.util = Util()
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.weixin_sns_info_hset_key = 'hash_weixin_snsinfo'
        self.weixin_info_hset_patch_key = 'weixin_info_hset_patch_key'  # patch address
        self.weixin_time_location_hset_key = 'hash_weixin_s_time_location'

    def patch_address(self):
        l = self.conn.hgetall(self.weixin_sns_info_hset_key)
        for k, v in l.items():
            # print v
            sns_info = json.loads(v)
            sns_info['poi_address'] = ''
            if sns_info['db_patch']:
                str_x_y = self.conn.hget(self.weixin_time_location_hset_key, sns_info['db_patch'])
                if str_x_y:
                    address = self.util.convert_xy_to_address(str_x_y)
                    print str_x_y, '>>>>', address
                    sns_info['poi_address'] = address

            self.conn.hset(self.weixin_info_hset_patch_key, k, sns_info)

    # def get_all_sns_info(self):
    #     sns_info_list = []
    #     l = self.conn.hgetall(self.weixin_info_hset_patch_key)
    #     for k, v in l.items():
    #         sns_info_list.append(eval(v))
    #
    #     return sns_info_list

    def get_authors(self):
        authors = []
        l = self.conn.hgetall(self.weixin_info_hset_patch_key)
        for k, v in l.items():
            sns_info = eval(v)
            author = sns_info["authorName"]
            authors.append(author)

        return list(set(authors))

    def search_sns_info(self, ago_time='', authors=[], has_pic='', x_y='', distance=''):
        '''
        Args:
            ago_time: '1 hour' or '2 minutes'
            authors: list type
            has_pic: 'on'
            x_y: '116.316405_39.977629' 目标位置
            distance: km   距目标位置的距离要求（ xxx km以内）
        Returns:
            符合要求的 sns_info_list
        '''
        util = Util()
        sns_info_list = []
        l = self.conn.hgetall(self.weixin_info_hset_patch_key)
        for k, v in l.items():
            author_flg = False
            time_flg = False
            pic_flg = False
            distance_flg = False

            sns_info = eval(v)
            author = sns_info["authorName"]
            ctime = sns_info["timestamp"]
            media_list = sns_info["mediaList"]
            sns_info["ago_days"] = Util.convert_ago_time_to_days(ctime)
            # print datetime.datetime.utcfromtimestamp(ctime), self.util.time_min(ago_time)

            if not authors or author in authors:
                author_flg = True
            if not ago_time.strip() or datetime.datetime.utcfromtimestamp(ctime) >= \
                    datetime.datetime.strptime(ago_time, "%Y-%m-%d"):
                time_flg = True
            if has_pic == 'off' or (has_pic == 'on' and len(media_list)) > 0:
                pic_flg = True

            if not distance:
                distance_flg = True
            else:
                sns_info_y_x = self.conn.hget(self.weixin_time_location_hset_key, sns_info['db_patch'])
                (x, y) = util.convert_str_xy_to_x_y(x_y)
                (sns_info_y, sns_info_x) = util.convert_str_xy_to_x_y(sns_info_y_x)
                if x and sns_info_x:
                    d = util.calc_distance((x, y), (sns_info_x, sns_info_y))
                    print u'采集地:', sns_info_y_x, u'选取地:', x_y, u'相距：', d, u'限定：', distance
                    if d <= int(distance):
                        distance_flg = True

            # print author_flg, time_flg, pic_flg, distance_flg
            if author_flg and time_flg and pic_flg and distance_flg:
                sns_info_list.append(sns_info)

        return sns_info_list

    def get_weixin_cnt(self):
        return self.conn.hlen(self.weixin_sns_info_hset_key)

    def make_time_loacation(self):
        # var weixin_lbs_info =  [
        #   {"lnglat": ["116.418757", "39.917544"], "name": "东城区"},
        #   {"lnglat": ["116.366794", "39.915309"], "name": "西城区"},
        #   {"lnglat": ["116.486409", "39.921489"], "name": "朝阳区"},
        # ];
        l = self.conn.hvals(self.weixin_time_location_hset_key)
        fd = open('./static/js/weixin_lbs_info.js', 'w')
        fd.write('var weixin_lbs_info =  [\n')
        cnt = 0
        for i in l:
            if i != 'None' and i != '':
                x = i.split('_')[0]
                y = i.split('_')[1]
                fd.write('''    {"lng_lat": ["''' + y + '''", "''' + x + '''"], "name": "location%d"},\n''' % cnt)
                cnt = cnt + 1
        fd.write('];\n')
        fd.close()


class MongodbDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.wx_sns_data
        self.sns_info = self.db.sns_info

    # def patch_address(self):
    #     return None

    def get_authors(self):
        authors = []
        l = self.sns_info.find().sort("authorName")
        for sns_info in l:
            author = sns_info["authorName"]
            authors.append(author)

        return list(set(authors))

    def search_sns_info(self, ago_time='', authors='', has_pic='', x_y='', distance=''):
        sns_info_list = []
        # l = self.sns_info.find({'$or': [{"authorName": authors}, {"timestamp": {'$gte', ago_time}}]}).sort("timestamp")
        l = self.sns_info.find().sort("timestamp")
        for sns_info in l:
            sns_info_list.append(sns_info)
        # for k, v in l.items():
        #     pic_flg = False
        #
        #     sns_info = eval(v)
        #     media_list = sns_info["mediaList"]
        #     sns_info["ago_days"] = '3 day'
        #
        #     if has_pic == 'off' or (has_pic == 'on' and len(media_list)) > 0:
        #         pic_flg = True
        #
        #     if pic_flg:
        #         sns_info_list.append(sns_info)

        return sns_info_list

    def get_weixin_cnt(self):
        return self.sns_info.find().count()

    def make_time_loacation(self):
        # var weixin_lbs_info =  [
        #   {"lnglat": ["116.418757", "39.917544"], "name": "东城区"},
        #   {"lnglat": ["116.366794", "39.915309"], "name": "西城区"},
        #   {"lnglat": ["116.486409", "39.921489"], "name": "朝阳区"},
        # ];
        l = self.sns_info.find()
        fd = open('./static/js/weixin_lbs_info.js', 'w')
        fd.write('var weixin_lbs_info =  [\n')
        cnt = 0
        for i in l:
            print(i['snsId'])
            if i['rawXML']['TimelineObject'].has_key('location'):
                x = i['rawXML']['TimelineObject']['location']['@longitude']
                y = i['rawXML']['TimelineObject']['location']['@latitude']
                fd.write('''    {"lng_lat": ["''' + y + '''", "''' + x + '''"], "name": "location%d"},\n''' % cnt)
                cnt = cnt + 1
        fd.write('];\n')
        fd.close()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title=u"微信采集展示",
            header_text=u"微信数据展示")


class FriendsHandler(tornado.web.RequestHandler):
    def get(self):
        # db = RedisDriver()
        db = MongodbDriver()
        print 'get--------------------start'
        authors_list = db.get_authors()
        # pprint(authors_list)

        sns_info_list = db.search_sns_info()
        # pprint(sns_info_list)
        print 'get--------------------start'
        self.render(
            "friends.html",
            page_title=u"微信信息采集结果",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list,
            authors_list=authors_list)

    def post(self):
        # db = RedisDriver()
        db = MongodbDriver()
        ago_time = self.get_argument('ago_time', '')
        authors = self.get_arguments('authors')
        pic_flg = self.get_argument('pic_flg', 'off')
        x_y = self.get_argument('x_y', '')
        distance = self.get_argument('distance', '')
        print '-------------------------------   post  ----------------------------------- '
        print 'ago_time: ', ago_time, 'authors: ', authors, 'pic_flg: ', pic_flg, 'x_y: ', x_y, 'distance: ', distance
        print '-------------------------------   post  ----------------------------------- '
        authors_list = db.get_authors()
        # pprint(authors_list)

        sns_info_list = db.search_sns_info(ago_time, authors, pic_flg, x_y, distance)
        # pprint(sns_info_list)

        self.render(
            "friends.html",
            page_title=u"微信朋友圈",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list,
            authors_list=authors_list)


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


class AroundHandler(tornado.web.RequestHandler):
    def get(self):
        # db = RedisDriver()
        db = MongodbDriver()
        print 'get--------------------start'
        authors_list = db.get_authors()
        # pprint(authors_list)

        sns_info_list = db.search_sns_info()
        # pprint(sns_info_list)
        print 'get--------------------start'
        self.render(
            "around.html",
            page_title=u"微信周围的人",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list,
            authors_list=authors_list)

    def post(self):
        db = RedisDriver()
        ago_time = self.get_argument('ago_time', '')
        authors = self.get_arguments('authors')
        pic_flg = self.get_argument('pic_flg', 'off')
        x_y = self.get_argument('x_y', '')
        distance = self.get_argument('distance', '')
        print '-------------------------------   post  ----------------------------------- '
        print 'ago_time: ', ago_time, 'authors: ', authors, 'pic_flg: ', pic_flg, 'x_y: ', x_y, 'distance: ', distance
        print '-------------------------------   post  ----------------------------------- '
        authors_list = db.get_authors()
        # pprint(authors_list)

        sns_info_list = db.search_sns_info(ago_time, authors, pic_flg, x_y, distance)
        # pprint(sns_info_list)

        self.render(
            "around.html",
            page_title=u"微信周围的人",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list,
            authors_list=authors_list)


class SnsInfoModule(tornado.web.UIModule):
    def render(self, sns_info):
        return self.render_string(
            "modules/sns_info.html",
            sns_info=sns_info,
        )

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
            (r"/convert_xy_to_address", Manager),
            (r"/(weixin_lbs_info\.js)", tornado.web.StaticFileHandler, dict(path=settings['static_js_path'])),
            (r"/(authors\.js)", tornado.web.StaticFileHandler, dict(path=settings['static_js_path'])),
            (r"/around", AroundHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    # db = RedisDriver()
    db =MongodbDriver()
    # db.make_time_loacation()

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def patch_address():
    redis_db = RedisDriver()
    redis_db.patch_address()


def test():
    redis_db = RedisDriver()
    pprint(redis_db.get_authors())


if __name__ == "__main__":
    # test()
    # patch_address()
    main()
