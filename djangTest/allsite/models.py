# coding=utf-8
from django.db import models

# Create your models here.


from mongoengine import *
from djangTest.settings import DBNAME, DBHOST, ALLSITE_TAB

# connect(DBNAME, host='127.0.0.1', username='root', password='1234')
connect(DBNAME, host=DBHOST, )


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
