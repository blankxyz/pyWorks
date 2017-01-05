from mongoengine import *


DBNAME = 'allsite_db'
DBHOST = '127.0.0.1'
ALLSITE_TAB= 'site_cn_all'

connect(DBNAME)

class SiteList(Document):
    site = StringField(max_length=120, required=True)
    domain = StringField(max_length=120, required=True)
    hubPageCnt = IntField(default=0, required=True)
    name = StringField(max_length=120, required=True)
    crawltime = DateTimeField(required=False)
    city = StringField(max_length=120, required=False)
    meta = {
        'collection': 'site_cn_all'
    }


for e in SiteList.objects.all():
    print e["site"], e["domain"], e["hubPageCnt"]



