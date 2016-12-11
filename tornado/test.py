#!/usr/bin python
# coding=utf-8

import pymongo
import json
from pprint import pprint
import requests

REDIS_SERVER = 'redis://127.0.0.1/10'
MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'


class DBDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.geojson_path = 'static/json/'
        self.db = self.client.wx_sns_data
        self.city_info = self.db.city_info
        self.db_patch_location = self.db.db_patch_location
        self.db_patch_geo = self.db.db_patch_geo

    def geojson_import(self, city):
        fd = open(self.geojson_path + city + '.json', 'r')
        j = fd.read()
        pp = eval(j)
        fd.close()

        for i in pp['features']:
            # pprint(i)
            self.city_info.insert(i)

    def get_polygon(self, district):
        l = self.city_info.find_one({'properties.name': district})
        return l['geometry']['coordinates'][0]

    def conver_to_geojson(self):
        s = set()
        l = self.db_patch_location.find()
        cnt = 0
        for i in l:
            cnt = cnt + 1
            longitude = 0.0
            latitude = 0.0
            k = str(i['db_patch'])
            if i['location'] != 'None' and i['location'] != '':
                longitude = float(str(i['location'].split('_')[1]))
                latitude = float(str(i['location'].split('_')[0]))
                if longitude != float(0.0) and longitude > latitude:
                    s.add((longitude, latitude))
                    print 'cnt:', cnt
                    # v = {"coordinate": {"longitude": longitude, "latitude": latitude},
                    #      "driver": str(k.split('_')[0]),
                    #      "time": str(k.split('_')[1])}

        for (longitude, latitude) in s:
            pprint({
                'loc': {'type': "Point", 'coordinates': [longitude, latitude]},
                'name': "point",
                'category': "Driver"
            })
            self.db_patch_geo.insert({
                'loc': {'type': "Point", 'coordinates': [longitude, latitude]},
                'name': "point",
                'category': "Driver"
            })

        # self.db_patch_geo.ensureIndex({'loc': '2dsphere'})

    def find_driver(self, district):
        polygon = self.get_polygon(district)
        print polygon
        l = self.db_patch_geo.find(
            {'loc': {'$geoWithin': {'$box': [[110.000000, 30.000000], [120.000000, 40.000000]]}}})

        for i in l:
            pprint(i)

    def find_test(self):
        l = self.db_patch_geo.find({'coordinate': {'$nearSphere': [116.310815, 39.981343]}})
        for i in l:
            pprint(i)


def main():
    db = DBDriver()
    # db.geojson_import('beijing')
    # db.conver_to_geojson()
    db.find_driver('海淀区')
    # db.find_test()


if __name__ == "__main__":
    main()
