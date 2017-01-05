# coding=utf-8
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from models import SiteList
from pprint import pprint
from djangTest.settings import DBNAME, DBHOST, ALLSITE_TAB
import datetime
import re
import pymongo
from django.http import HttpResponse
from django.http import JsonResponse
import json
# Create your views here.
import time

MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'


class DBDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.allsite_db
        self.site_cn_all = self.db.site_cn_all

    def get_site_cn_all(self, start, length, search):
        print start, length, search
        ret = []
        if
        cond = re.compile(search)
        cnt = self.site_cn_all.find(cond).count()
        l = self.site_cn_all.find(cond).sort("hubPageCnt", pymongo.DESCENDING).limit(length).skip(start)
        for info in l:
            ret.append([info['site'], info['hubPageCnt'], info['name']])

        # pprint(ret)
        return (ret, cnt)


def index(request):
    print 'index start .........'

    draw = request.GET.get('draw')
    start = request.GET.get('start')
    length = request.GET.get('length')
    search = request.GET.get('search[value]')

    start = int(start)
    length = int(length)
    end = start + length
    print '[info] get() draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search

    db = DBDriver()
    (ret, cnt) = db.get_site_cn_all(start, length, search)
    # pprint({"draw": draw,
    #         "recordsTotal": cnt,
    #         "recordsFiltered": cnt,
    #         'data': ret})

    # 等效于 json.dumps()
    output = JsonResponse({"draw": draw,
                           "recordsTotal": cnt,
                           "recordsFiltered": cnt,
                           'data': ret})

    print 'index end ........'
    # return render(request, 'index.html', context={'SiteList': ret})
    # return HttpResponse(output, content_type="application/json")
    return HttpResponse(output, content_type='application/json; charset=UTF-8')
