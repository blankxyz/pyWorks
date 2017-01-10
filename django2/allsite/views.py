# coding=utf-8
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from models import User
from pprint import pprint


class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', widget=forms.PasswordInput())


def regist(req):
    print '[info] regist start.'
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            # 获得表单数据
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
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
                return response
            else:
                return HttpResponseRedirect('/allsite/login/')
    else:
        uf = UserForm()

    print '[info] login end.'
    return render_to_response('login.html', {'uf': uf}, context_instance=RequestContext(req))


# 登陆成功
def index(req):
    username = req.COOKIES.get('username', '')
    return render_to_response('index.html', {'username': username})


def logout(req):
    response = HttpResponse('logout')
    response.delete_cookie('username')
    return response
