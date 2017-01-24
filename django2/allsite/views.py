# coding=utf-8
from django.shortcuts import render
import random
# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from models import User
from pprint import pprint
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

import pymongo
from django.http import HttpResponse, HttpResponseServerError
from django.http import JsonResponse
import json
# Create your views here.
import time

MONGODB_SERVER = '127.0.0.1'  # '192.168.187.4'
MONGODB_PORT = 27017  # '37017'

domain_cnt = 0
hubPage_cnt = 0
detail_cnt = 0
new_doamin_cnt = 0


class DBDriver(object):
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.client.allsite_db
        self.site_cn_all = self.db.site_cn_all

    def get_site_cn_all(self, start, length, search):
        ret = []
        cond = {'name': {'$regex': search}}
        cnt = self.site_cn_all.find(cond).count()
        l = self.site_cn_all.find(cond).sort("hubPageCnt", pymongo.DESCENDING).limit(length).skip(start)
        for info in l:
            ret.append([info['site'], info['hubPageCnt'], info['name']])

        # pprint(ret)
        return (ret, cnt)

    def get_hubPageList(self, start, length, search):
        ret = []
        cond = {'name': {'$regex': search}}
        cnt = self.site_cn_all.find(cond).count()
        l = self.site_cn_all.find(cond).sort("hubPageCnt", pymongo.DESCENDING).limit(length).skip(start)
        for info in l:
            ret.append([info['site'], info['hubPageCnt'], info['name']])

        # pprint(ret)
        return (ret, cnt)


def sitelistJson(request):
    print '[info] sitelistJson start.'

    draw = request.GET.get('draw')
    start = request.GET.get('start')
    length = request.GET.get('length')
    search = request.GET.get('search[value]')

    start = int(start)
    length = int(length)
    end = start + length
    print '[info] sitelistJson draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search

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

    print '[info] sitelistJson end.'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def hubPageListJson(request):
    print '[info] hubPageListJson start.'

    draw = request.GET.get('draw')
    start = request.GET.get('start')
    length = request.GET.get('length')
    search = request.GET.get('search[value]')

    start = int(start)
    length = int(length)
    end = start + length
    print '[info] hubPageListJson draw:', draw, 'start:', start, 'length:', length, 'end:', end, 'search:', search

    db = DBDriver()
    (ret, cnt) = db.get_hubPageList(start, length, search)
    # pprint({"draw": draw,
    #         "recordsTotal": cnt,
    #         "recordsFiltered": cnt,
    #         'data': ret})

    # 等效于 json.dumps()
    output = JsonResponse({"draw": draw,
                           "recordsTotal": cnt,
                           "recordsFiltered": cnt,
                           'data': ret})

    print '[info] hubPageListJson end.'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


# ----------------------------------------------------------------------------------------------------------
class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', widget=forms.PasswordInput())


def regist(req):
    print '[info] regist start.'
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            print '[info] regist username: %s,password: %s.' % (username, password)
            # 添加到数据库
            User.objects.create(username=username, password=password)
            # return HttpResponse('regist success!!')
            return HttpResponseRedirect('/allsite/login/')
    else:
        uf = UserForm()

    print '[info] regist end.'
    return render_to_response('regist.html', {'uf': uf}, context_instance=RequestContext(req))


def login(req):
    print '[info] login start.'
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            print '[info] login username: %s, password: %s' % (username, password)
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                response = HttpResponseRedirect('/allsite/index/')
                # 将username写入浏览器cookie,失效时间为3600
                response.set_cookie('username', username, 60)
                print '[info] login success.'
                return response
            else:
                print '[info] login failure.'
                return HttpResponseRedirect('/allsite/login/')
    else:
        uf = UserForm()

    print '[info] login end.'
    return render_to_response('login.html', {'uf': uf}, context_instance=RequestContext(req))


def logout(req):
    response = HttpResponse('logout')
    response.delete_cookie('username')
    return response

# @csrf_exempt
@ensure_csrf_cookie
def index(req):
    username = req.COOKIES.get('username', '')
    result = {}
    result['domain_total'] = 15222
    return render_to_response('index.html', {'result': result})


def allsite(req):
    username = req.COOKIES.get('username', '')
    return render_to_response('domainlist.html', {'username': username})


def domainlist(req):
    return render_to_response('domainlist.html')


def hubPageList(req):
    return render_to_response('hubPageList.html')


def detailList(req):
    return render_to_response('detailList.html')


def dashBoardCnt(request):
    # print 'dashBoardCnt start.........'
    global domain_cnt
    global hubPage_cnt
    global detail_cnt
    global new_doamin_cnt

    domain_cnt = 12345
    hubPage_cnt = 23456
    detail_cnt = 34567890
    new_doamin_cnt = 4567

    domain_cnt = domain_cnt + random.randint(1, 10)
    hubPage_cnt = hubPage_cnt + random.randint(80, 100)
    detail_cnt = detail_cnt + random.randint(500, 1000)
    new_doamin_cnt = new_doamin_cnt + random.randint(1, 10)

    output = JsonResponse({"domain_cnt": domain_cnt,
                           "hubPage_cnt": hubPage_cnt,
                           "detail_cnt": detail_cnt,
                           'new_doamin_cnt': new_doamin_cnt})

    # print 'dashBoardCnt end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageRank(request):
    print 'drawHubPageRank start.........'

    # draw = request.GET.get('draw')
    # start = request.GET.get('start')
    # length = request.GET.get('length')
    # search = request.GET.get('search[value]')

    arr = [50000, 42000, 36000, 20000, 10000, 9000, 8000, 6000, 3000, 2000]

    output = JsonResponse({"hubPageRank": arr})

    print 'drawHubPageRank end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDomainRank(request):
    print 'drawDomainRank start.........'

    arr1 = [10000, 12000, 16000, 10000, 8000, 4000, 4000, 3000, 1000, 500]
    arr2 = [30000, 22000, 16000, 20000, 10000, 9000, 8000, 6000, 10000, 1000]
    output = JsonResponse({"domainRankUsed": arr1, "domainRankUnUsed": arr2})

    print 'drawDomainRank end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageTrend(request):
    print 'drawHubPageTrend start.........'

    arr1 = [120, 132, 133, 134, 150, 200, 210, 220, 232, 233, 235, 260,
            261, 262, 277, 278, 280, 290, 310, 330, 340, 350, 380]
    period = 20.2

    output = JsonResponse({"hubPageTrend": arr1, "period": period})

    print 'drawHubPageTrend end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDetailTrend(request):
    print 'drawDetailTrend start.........'

    beforeYesterday = [90, 132, 133, 134, 150, 200, 210, 220, 232, 233, 235, 260, 261, 262, 277, 278, 280, 290, 310,
                       330, 340, 350, 360, ]
    yesterday = [90, 142, 143, 144, 180, 220, 230, 250, 282, 273, 295, 290, 291, 292, 287, 291, 290, 292, 320, 330,
                 340, 350, 370, ]
    today = [90, 162, 173, 184, 180, 220, 260, 270, 332, 333, 335, 360, 361, 362, 377, 378, 380, 390, 410, 430, 440,
             450, 470, ]

    output = JsonResponse({"beforeYesterday": beforeYesterday, "yesterday": yesterday, "today": today})

    print 'drawDetailTrend end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawCrawlTimePart(request):
    print 'drawCrawlTimePart start.........'
    data = {}
    data['0-1'] = 0
    data['1-2'] = 0
    data['2-5'] = 10
    data['5-15'] = 20
    data['15-30'] = 20
    data['30-60'] = 30
    data['60-120'] = 30
    data['120-240'] = 40
    data['>240'] = 20

    output = JsonResponse(data)

    print 'drawCrawlTimePart end ........'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')

# @csrf_exempt
@ensure_csrf_cookie
def drawNewDomain(request):
    print 'drawNewDomain start *************************'
    timeList = []
    domainCnt = []
    print 'drawNewDomain', request.POST

    if request.POST.has_key('opt'):
        opt = request.POST['opt']
        print 'drawNewDomain', opt

        if (opt == "day"):
            timeList = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
                        "17", "18", "19", "20", "21", "22", "23", "24"]
            domainCnt = [500, 420, 360, 200, 500, 600, 800, 500, 420, 360, 700, 500, 400, 600, 500, 420, 360,
                         200, 500, 600, 400, 500, 420, 360]

        if (opt == "week"):
            timeList = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            domainCnt = [500, 420, 360, 500, 700, 900, 800]

        if (opt == "month"):
            timeList = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
                        "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]
            domainCnt = [500, 420, 360, 200, 500, 600, 800, 500, 420, 360, 700, 500, 400, 600, 500, 420, 360,
                         200, 500, 600, 400, 500, 420, 360, 100, 150, 400, 600, 500, 420, 360]
    else:
        timeList = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        domainCnt = [500, 420, 360, 500, 700, 900, 800]

    output = JsonResponse({'timeList': timeList, 'domainCnt': domainCnt})
    print 'drawNewDomain end *************************'
    return HttpResponse(output, content_type='application/json; charset=UTF-8')
