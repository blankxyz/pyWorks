#!/usr/bin python
# coding=utf-8

import pymongo
import json
from pprint import pprint


class MongodbDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient('192.168.187.4', 37017)
        self.db = self.client.wx_sns_data
        self.sns_info = self.db.sns_info

    def patch_address(self):
        return None

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
        fd = open('./static/js/wx_lbs_info.js', 'w')
        fd.write('var weixin_lbs_info =  [\n')
        cnt = 0
        for i in l:
            print(i['snsId'])
            if i['rawXML']['TimelineObject'].has_key('location'):
                x = i['rawXML']['TimelineObject']['location']['@longitude']
                y =  i['rawXML']['TimelineObject']['location']['@latitude']
                fd.write('''    {"lng_lat": ["''' + y + '''", "''' + x + '''"], "name": "location%d"},\n''' % cnt)
                cnt = cnt + 1
        fd.write('];\n')
        fd.close()

def main():
    mongo = MongodbDriver()
    # mongo.search_sns_info()
    mongo.make_time_loacation()

if __name__ == "__main__":
    main()
