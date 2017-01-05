from pprint import pprint
import pymongo

MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'


class DBDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.allsite_db
        self.site_cn_all = self.db.site_cn_all

    def get_site_cn_all(self):
        return self.site_cn_all.find()


print 'index start .........'
d = DBDriver()
l = d.get_site_cn_all()
for info in l[:20]:
    print info['site']

