#!/usr/bin/env python
# coding=utf-8

import os.path
import json
import datetime
import re
import signal
import requests
import redis

from pprint import pprint
import tornado.locale
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

REDIS_SERVER = 'redis://127.0.0.1/10'

define("port", default=5000, help="run on the given port", type=int)

# sns_info_list1 = [
#     {u'snsId': u'12381551676090822951',
#      u'timestamp': 1475995978,
#      u'authorId': u'v1_e2e2690b7fa86dde01c3325fe797ae0d3a5a67d040e5aefc7406d71841621eae80b62c10d501e75f43cf10973d0a4fa3@stranger',
#      u'comments': [],
#      u'content': u'\\u795d\\u54e5\\u4eec\\u59d0\\u4eec\\u670b\\u53cb\\u4eec\\u91cd\\u9633\\u8282\\u5feb\\u4e50\\uff01',
#      u'authorName': u'\\u6f14\\u660e',
#      u'isCurrentUser': False,
#      u'likes': [],
#      'db_patch': '75a5f0857d53_1479168323.39',
#      u'mediaList': [
#          u'http://mmsns.qpic.cn/mmsns/WD4FduqfeKKAbJsmFI6IFrknR3ManjhZqjQxlGJibwvNzbmWzVPbTL3ricnzYhjFp3ZmYiaZKz5yyE/0'
#      ],
#      u'rawXML': u'<TimelineObject>'
#                 u'<id><![CDATA[12381551676090822951]]></id>
#                 <username> <![CDATA[v1_e2e2690b7fa86dde01c3325fe797ae0d3a5a67d040e5aefc7406d71841621eae80b62c10d501e75f43cf10973d0a4fa3 @ stranger]] >
#                 </username>
#                 <createTime> <![CDATA[1475995978]]></createTime>
#                 <contentDescShowType>0</contentDescShowType>
#                 <contentDescScene>0</contentDescScene>
#                 <private><![CDATA[0]]></private>
#                 <contentDesc><![CDATA[\\u795d\\u54e5\\u4eec\\u59d0\\u4eec\\u670b\\u53cb\\u4eec\\u91cd\\u9633\\u8282\\u5feb\\u4e50\\uff01]]></contentDesc>
#                 <contentattr><![CDATA[0]]></contentattr>
#                 <sourceUserName></sourceUserName>
#                 <sourceNickName></sourceNickName>
#                 <statisticsData></statisticsData>
#                 <location poiClickableStatus = \"0\"  " \
#                     poiClassifyId =  \"\"  " \
#                     poiScale =  \"0\"  " \
#                     longitude =  \"0.0\"  " \
#                     city =  \"\"  " \
#                     poiName =  \"\"  " \
#                     latitude =  \"0.0\"  " \
#                     poiClassifyType =  \"0\"  " \
#                     poiAddress =  \"\">" \
#                 </location>
#                 <ContentObject>
#                 <contentStyle><![CDATA[1]]></contentStyle><title></title><description></description><contentUrl></contentUrl><mediaList><media><id><![CDATA[12381551676468113677]]></id><type><![CDATA[2]]></type><title></title><description></description><private><![CDATA[0]]></private><url type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/WD4FduqfeKKAbJsmFI6IFrknR3ManjhZqjQxlGJibwvNzbmWzVPbTL3ricnzYhjFp3ZmYiaZKz5yyE/0]]></url><thumb type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/WD4FduqfeKKAbJsmFI6IFrknR3ManjhZqjQxlGJibwvNzbmWzVPbTL3ricnzYhjFp3ZmYiaZKz5yyE/150]]></thumb><size height =  \"488.0\"  width =  \"650.0\"  totalSize =  \"41895.0\" ></size></media></mediaList></ContentObject><actionInfo></actionInfo></TimelineObject>'}

amap_key = '0c7fb71b2e13546416337666cd406db3'  # 高德地图JavaScriptAPI key 220.249.18.226
baidu_map_key = 'e9ospC88hj5iHoI9xUabaHFYAEiFXlRa'


class Util(object):
    def convert_str_xy_to_x_y(self, str_x_y):
        '''
        Args:
            str_x_y: '39.983424_116.322987'
        Returns:
            (x,y)
        '''
        (x, y) = (None, None)
        if str_x_y != 'None' and str_x_y != '':
            x = str_x_y.split('_')[0]
            y = str_x_y.split('_')[1]
        return (x, y)

    def convert_xy_to_address(self, str_x_y):
        '''
        Args:
            str_x_y: '39.983424_116.322987'
        Returns:
            '北京市海淀区中关村大街27号1101-08室'
        '''
        address = None
        (x, y) = self.convert_str_xy_to_x_y(str_x_y)
        if x:
            url = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&' \
                  'location=%s,%s&output=json&pois=0&ak=%s' % (x, y, baidu_map_key)
            response = requests.get(url)
            content = response.content[len('renderReverse&&renderReverse('):-1]
            j = json.loads(content)
            address = j['result']['sematic_description']

        return address

    def time_min(self, ago_time_str):
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

        print ret_time.strftime("%Y-%m-%d %H:%M:%S")
        return ret_time


class RedisDriver(object):
    def __init__(self):
        self.util = Util()
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.weixin_info_hset_key = 'hash_weixin_snsinfo'
        self.weixin_info_hset_patch_key = 'weixin_info_hset_patch_key'  # patch address
        self.weixin_time_location_hset_key = 'hash_weixin_s_time_location'

    def patch_address(self):
        l = self.conn.hgetall(self.weixin_info_hset_key)
        for k, v in l.items():
            sns_info = eval(v)
            sns_info['poi_address'] = ''
            if sns_info['db_patch']:
                str_x_y = self.conn.hget(self.weixin_time_location_hset_key, sns_info['db_patch'])
                if str_x_y:
                    address = self.util.convert_xy_to_address(str_x_y)
                    print str_x_y, '>>>>', address
                    sns_info['poi_address'] = address

            self.conn.hset(self.weixin_info_hset_patch_key, k, sns_info)

    def get_all_sns_info(self):
        sns_info_list = []
        l = self.conn.hgetall(self.weixin_info_hset_patch_key)
        for k, v in l.items():
            sns_info_list.append(eval(v))

        return sns_info_list

    def search_sns_info(self, ago_time, authors):
        '''
        Args:
            ago_time_str: '1 hour' or '2 minutes'
            authors: 'tom,jerry'
        Returns:
        '''
        authors = authors.sprit(',')
        sns_info_list = []
        l = self.conn.hgetall(self.weixin_info_hset_patch_key)
        for k, v in l.items():
            author_flg = False
            time_flg = False
            sns_info = eval(v)
            author = sns_info["authorName"]
            ctime = sns_info["timestamp"]
            if len(authors) == 0 or author in authors:
                author_flg = True
            if ago_time is '' or ctime <= self.util.time_min(ago_time):
                time_flg = True

            if author_flg and time_flg:
                sns_info_list.append(sns_info)

        return sns_info_list

    def get_weixin_cnt(self):
        return self.conn.hlen(self.weixin_info_hset_key)

    def make_time_loacation(self):
        # var citys =  [
        #   {"lnglat": ["116.418757", "39.917544"], "name": "东城区"},
        #   {"lnglat": ["116.366794", "39.915309"], "name": "西城区"},
        #   {"lnglat": ["116.486409", "39.921489"], "name": "朝阳区"},
        # ];
        l = self.conn.hvals(self.weixin_time_location_hset_key)
        fd = open('./static/js/timeLocation.js', 'w')
        fd.write('var citys =  [\n')
        cnt = 0
        for i in l:
            if i != 'None' and i != '':
                x = i.split('_')[0]
                y = i.split('_')[1]
                fd.write('''    {"lnglat": ["''' + y + '''", "''' + x + '''"], "name": "location%d"},\n''' % cnt)
                cnt = cnt + 1
        fd.write('];\n')
        fd.close()


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
            (r"/search", SearchHandler),
            (r"/(timeLocation\.js)", tornado.web.StaticFileHandler, dict(path=settings['static_js_path'])),
            (r"/discussion", DiscussionHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title=u"微信采集展示",
            header_text=u"微信数据展示")


class SearchHandler(tornado.web.RequestHandler):
    def __init__(self):
        self.util = Util()
        self.redis_db = RedisDriver()

    def get(self):
        sns_info_list = self.redis_db.get_all_sns_info()
        # pprint(sns_info_list)
        # pprint(eval(sns_info_list[0])['content'])
        self.render(
            "search_result.html",
            page_title=u"微信信息采集结果",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list[:300])

    def post(self):
        print(self.request.remote_ip)
        time_range = self.get_argument('time', '')
        authors = self.get_argument('authors', '')
        ago_time = self.util.time_min(time_range)
        sns_info_list = self.redis_db.search_sns_info(ago_time, authors)
        self.render(
            "search_result.html",
            page_title=u"微信信息采集结果",
            header_text=u"采集结果展示",
            sns_info_list=sns_info_list)


class DiscussionHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "discussion.html",
            page_title="Burt's Books | Discussion",
            header_text="Talkin' About Books With Burt",
            comments=[
                {
                    "user": "Alice",
                    "text": "I can't wait for the next version of Programming Collective Intelligence!"
                },
                {
                    "user": "Burt",
                    "text": "We can't either, Alice.  In the meantime, be sure to check out RESTful Web Services too."
                },
                {
                    "user": "Melvin",
                    "text": "Totally hacked ur site lulz <script src=\"http://melvins-web-sploits.com/evil_sploit.js\"></script><script>alert('RUNNING EVIL H4CKS AND SPL0ITS NOW...');</script>"
                }
            ]
        )


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


def main():
    redis_db = RedisDriver()
    redis_db.make_time_loacation()

    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def test():
    # util = Util()
    # print util.convert_xy_to_address('39.983424_116.322987')
    redis_db = RedisDriver()
    # pprint(redis_db.get_all_sns_info())
    redis_db.patch_address()


if __name__ == "__main__":
    main()
    # test()
