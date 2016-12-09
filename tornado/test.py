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


class DBDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.geojson_path = 'export/json'

    def geojson_import(self, city):
        fd = open(self.geojson_path+city+'.json', 'r')
        j = fd.read()
        pp = json.loads(j)
        # pprint(pp)
        fd.close()

def main():
    db = DBDriver()
    db.patch_address()


if __name__ == "__main__":
    main()
