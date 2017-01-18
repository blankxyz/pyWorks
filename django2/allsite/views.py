# coding=utf-8
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from models import User
from pprint import pprint

import pymongo
from django.http import HttpResponse,HttpResponseServerError
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
        ret = []
        cond = {'name':{'$regex':search}}
        cnt = self.site_cn_all.find(cond).count()
        l = self.site_cn_all.find(cond).sort("hubPageCnt", pymongo.DESCENDING).limit(length).skip(start)
        for info in l:
            ret.append([info['site'], info['hubPageCnt'], info['name']])

        # pprint(ret)
        return (ret, cnt)

    def get_hubPageList(self, start, length, search):
        ret = []
        cond = {'name':{'$regex':search}}
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

#----------------------------------------------------------------------------------------------------------
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


def index(req):
    username = req.COOKIES.get('username', '')
    return render_to_response('index.html', {'username': username})


def allsite(req):
    username = req.COOKIES.get('username', '')
    return render_to_response('domainlist.html', {'username': username})


def domainlist(req):
    return render_to_response('domainlist.html')

def hubPageList(req):
    return render_to_response('hubPageList.html')

def detailPageList(req):
    return render_to_response('detailPageList.html')

def newDomainList(req):
    return render_to_response('newDomainList.html')