#!/usr/bin python
# coding=utf-8

import pymongo
import json
from pprint import pprint
import requests

REDIS_SERVER = 'redis://127.0.0.1/10'
MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'

# local_flg 0: 附近的人  2：朋友圈
FRIENDS_FLG = 2
AROUND_FLG = 0

amap_key = '0c7fb71b2e13546416337666cd406db3'  # 高德地图JavaScriptAPI key 220.249.18.226
# baidu_map_key = 'e9ospC88hj5iHoI9xUabaHFYAEiFXlRa'
baidu_map_key = '4119853f8e9c07a0eeaf89352b2c795d'


class Util(object):
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


class MongodbDriver(object):
    def __init__(self):
        self.util = Util()
        self.client = pymongo.MongoClient('127.0.0.1')
        self.db = self.client.wx_sns_data
        self.sns_info = self.db.sns_info
        self.sns_info_patch = self.db.sns_info_patch

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
                    print cnt, i['snsId'], addressComponent
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
                                                    "street": street})

            cnt = cnt + 1


def main():
    mongo = MongodbDriver()
    mongo.patch_address()


if __name__ == "__main__":
    main()
