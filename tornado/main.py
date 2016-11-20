#!/usr/bin/env python
# coding=utf-8

import os.path
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

define("port", default=8000, help="run on the given port", type=int)

sns_info_list1 = [
    {
        "title": "微信朋友圈",
        "subtitle": "腾讯微信",
        "image": "/static/images/collective_intelligence.gif",
        "author": "Toby Segaran",
        "date_added": 1310248056,
        "date_released": "August 2007",
        "isbn": "978-0-596-52932-1",
        "description": "<p>微信朋友圈指的是腾讯微信上的一个社交功能，于微信4.0版本2012年4月19日更新时上线，用户可以通过朋友圈发表文字</p>"
    },
    {
        "title": "微信4.0",
        "subtitle": "微信4.0",
        "image": "/static/images/restful_web_services.gif",
        "author": "Leonard Richardson, Sam Ruby",
        "date_added": 1311148056,
        "date_released": "May 2007",
        "isbn": "978-0-596-52926-0",
        "description": "<p>You've built web sites that can be used by humans. But can you also build web sites that are usable by machines? That's where the future lies, and that's what this book shows you how to do. Today's web service technologies have lost sight of the simplicity that made the Web successful. This book explains how to put the &quot;Web&quot; back into web services with REST, the architectural style that drives the Web.</p>"
    },
    {
        'isbn': '12406114522407964940',
        'date_added': 1478924098,
        "date_released": "May 2007",
        'authorId': 'v1_1e4d3d1ca549abd4fff001da72255d05ec7831619f942df082f81219f72b8dee175ee6ab8dfbc9b3956fdb21323646a9@stranger',
        'comments': [],
        'title': u'\u8c01\u5bb6\u6709\u72d7\u72d7\u672c\u4eba\u60f3\u8981\u9886\u517b\u4e00\u53ea\u6700\u9ad8\u662f\u6cf0\u8fea',
        'subtitle': 'subtitle',
        'author': u'\u5ff5\u5fc6',
        'description': u'\u8c01\u5bb6\u6709\u72d7\u72d7\u672c\u4eba\u60f3\u8981\u9886\u517b\u4e00\u53ea\u6700\u9ad8\u662f\u6cf0\u8fea',
        'isCurrentUser': False,
        'likes': [],
        'db_patch': '75a5f0857d53_1479168323.39',
        'image': 'http://mmsns.qpic.cn/mmsns/ibhzWy4ibIEpB7DLyLtl4xCf7LBqwicgMlDVV6hqrrwRbuAHYcWEdIs4KObIHcNqEWfY8LkaUdJkEs/0',
        'image11': '/static/images/1.jpeg',
        'rawXML': '<TimelineObject><id><![CDATA[12406114522407964940]]></id><username><![CDATA[v1_1e4d3d1ca549abd4fff001da72255d05ec7831619f942df082f81219f72b8dee175ee6ab8dfbc9b3956fdb21323646a9@stranger]]></username><createTime><![CDATA[1478924098]]></createTime><contentDescShowType>0</contentDescShowType><contentDescScene>0</contentDescScene><private><![CDATA[0]]></private><contentDesc><![CDATA[\\u8c01\\u5bb6\\u6709\\u72d7\\u72d7  \\u672c\\u4eba\\u60f3\\u8981\\u9886\\u517b\\u4e00\\u53ea\\u6700\\u9ad8\\u662f\\u6cf0\\u8fea  [\\u6109\\u5feb][\\u6109\\u5feb][\\u6109\\u5feb]\\u82b1\\u94b1\\u7684\\u4e5f\\u884c[\\u594b\\u6597][\\u594b\\u6597][\\u594b\\u6597]]]></contentDesc><contentattr><![CDATA[0]]></contentattr><sourceUserName></sourceUserName><sourceNickName></sourceNickName><statisticsData></statisticsData><location poiClickableStatus =  \"0\"  poiClassifyId =  \"\"  poiScale =  \"0\"  longitude =  \"0.0\"  city =  \"\"  poiName =  \"\"  latitude =  \"0.0\"  poiClassifyType =  \"0\"  poiAddress =  \"\" ></location><ContentObject><contentStyle><![CDATA[1]]></contentStyle><title></title><description></description><contentUrl></contentUrl><mediaList><media><id><![CDATA[12406114522560663831]]></id><type><![CDATA[2]]></type><title></title><description></description><private><![CDATA[0]]></private><url type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/ibhzWy4ibIEpB7DLyLtl4xCf7LBqwicgMlDVV6hqrrwRbuAHYcWEdIs4KObIHcNqEWfY8LkaUdJkEs/0]]></url><thumb type =  \"1\" ><![CDATA[http://mmsns.qpic.cn/mmsns/ibhzWy4ibIEpB7DLyLtl4xCf7LBqwicgMlDVV6hqrrwRbuAHYcWEdIs4KObIHcNqEWfY8LkaUdJkEs/150]]></thumb><size height =  \"1280.0\"  width =  \"960.0\"  totalSize =  \"102469.0\" ></size></media></mediaList></ContentObject><actionInfo></actionInfo></TimelineObject>'
    }
]


class RedisDriver(object):
    def __init__(self):
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.weixin_info_hset_key = 'hash_weixin_snsinfo'

    def get_all_sns_info(self):
        sns_info_list = []
        l = self.conn.hgetall(self.weixin_info_hset_key)
        for k, v in l.items():
            sns_info_list.append(eval(v))
        return sns_info_list

    def get_weixin_cnt(self):
        return self.conn.hlen(self.weixin_info_hset_key)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/search/", SearchHandler),
            (r"/discussion/", DiscussionHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"SnsInfo": SnsInfoModule},
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title=u"微信采集展示",
            header_text=u"微信数据展示",
        )


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        redis_db = RedisDriver()
        sns_info_list = redis_db.get_all_sns_info()
        # pprint(sns_info_list)
        # pprint(eval(sns_info_list[0])['content'])
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


def main():
    tornado.locale.set_default_locale('zh_CN')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
