# coding=utf-8

# Create your views here.
import json
from pprint import pprint
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django import forms
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response

from .dbDriver import RedisDriver
from .dbDriver import MongoDriver
from .dbDriver import CONFIG_ID

UNKOWN = '未知'
PAGE_NUM = 20


# @csrf_exempt
@ensure_csrf_cookie
def main(request):
    '''
    [主控面板画面]仅取得详情页Top100数据
    '''
    # print('main start...')
    db = MongoDriver()
    result = db.get_detail_list_top100()
    context = {
        'result': result
    }
    # print('main end.')
    return render(request, 'allsite/main.html', context)


class DomainListViewAPI(APIView):
    def get(self, request, format=None):
        search = ''
        times = ''
        page_num = 1
        db = MongoDriver()  # session
        cnt = db.get_domain_info_list_cnt(search, times)
        result = db.get_domain_info_list(search, times, (int(page_num) - 1) * PAGE_NUM, PAGE_NUM)

        return Response(result)

    def post(self, request, format=None):
        ret = {'ret': 'ok'}
        return Response(ret)


# [域名管理画面]
class DomainListView(TemplateView):
    queryset = []
    template_name = 'allsite/domainList.html'

    def _get_data(self, req):
        search = req.get('search', '')
        times = req.get('times', 'all')
        page_num = req.get('page', 1)

        db = MongoDriver()  # session
        cnt = db.get_domain_info_list_cnt(search, times)
        result = db.get_domain_info_list(search, times, (int(page_num) - 1) * PAGE_NUM, PAGE_NUM)
        paginator = Paginator(range(cnt), PAGE_NUM)
        index = paginator.page(page_num)
        context = {
            'index': index,
            'search': search,
            'all_cnt': '{:,}'.format(cnt),
            'result': result,
            'times': times
        }
        self.queryset = result
        return context

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self._get_data(request.POST)
        return render(request, self.template_name, context)


@login_required
def domainList(request):
    '''
    [域名管理画面]
    '''
    args = request.POST if request.method == 'POST' else request.GET
    print('[info] domainList()', request.method, args)
    search = args.get('search', '')
    times = args.get('times', 'all')
    page_num = args.get('page', 1)

    db = MongoDriver()
    cnt = db.get_domain_info_list_cnt(search, times)
    result = db.get_domain_info_list(search, times, (int(page_num) - 1) * PAGE_NUM, PAGE_NUM)

    # paginator = Paginator(result, PAGE_NUM)
    paginator = Paginator(range(cnt), PAGE_NUM)
    index = paginator.page(page_num)

    context = {
        'index': index,
        'search': search,
        'all_cnt': '{:,}'.format(cnt),
        'result': result,
        'times': times
    }
    # print('domainlist end.')
    return render(request, 'allsite/domainList.html', context)


def domainModify(request):
    '''
    [域名管理画面 - dialog] 域名修改
    '''
    # print('[info] domainModify start .....')
    print(request.POST)

    url = request.POST.get('url')
    siteName = request.POST.get('siteName')

    db = MongoDriver()
    ret = db.set_domain_info(domain=url, siteName=siteName)

    output = JsonResponse({"ret": ret})
    # print('[info] domainModify end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


@login_required
def hubPageList(request):
    '''
    [列表URL（频道）管理画面]
    '''
    if request.method == 'POST':
        print('[info] hubPageList POST: ', request.POST)
        search = request.POST.get('search', '')
        page_num = 1

    else:  # request.method == 'GET'
        print('[info] hubPageList GET: ', request.GET)
        search = request.GET.get('search', '')
        page_num = request.GET.get('page', 1)

    db = MongoDriver()
    cnt = db.get_hubPage_info_list_cnt(search)
    result = db.get_hubPage_info_list(search, (int(page_num) - 1) * PAGE_NUM, PAGE_NUM)

    paginator = Paginator(range(cnt), PAGE_NUM)
    index = paginator.page(page_num)

    context = {
        'search': search,
        'index': index,
        'all_cnt': '{:,}'.format(cnt),
        'result': result
    }
    return render(request, 'allsite/hubPageList.html', context)


@login_required
def detailList(request):
    '''
    [详细URL画面]
    '''
    if request.method == 'POST':
        print('[info] detailList POST: ', request.POST)
        search = request.POST.get('search', '')
        hubPage = ''
        select_cond = request.POST.get('selectCond', '')
        page_num = 1

    else:  # request.method == 'GET'
        print('[info] detailList GET: ', request.GET)
        search = request.GET.get('search', '')
        select_cond = request.GET.get('selectCond', '')
        hubPage = request.GET.get('hubPage', '')
        page_num = request.GET.get('page', 1)

    db = MongoDriver()
    all_cnt, all_ok_cnt, title_ok_cnt, content_ok_cnt, source_ok_cnt, ctime_ok_cnt = \
        db.get_detail_info_list_cnt(search, hubPage, select_cond)

    result = db.get_detail_info_list(search, hubPage, select_cond, (int(page_num) - 1) * PAGE_NUM, PAGE_NUM)
    paginator = Paginator(range(all_cnt), PAGE_NUM)
    index = paginator.page(page_num)

    context = {
        'allsite_config_id': CONFIG_ID,
        'search': search,
        'selectCond': select_cond,
        'index': index,
        'all_cnt': '{:,}'.format(all_cnt),
        'result': result,
        'all_ok_cnt': all_ok_cnt,
        'all_ng_cnt': all_cnt - all_ok_cnt,
        'title_ok_cnt': title_ok_cnt,
        'title_ng_cnt': all_cnt - title_ok_cnt,
        'content_ok_cnt': content_ok_cnt,
        'content_ng_cnt': all_cnt - content_ok_cnt,
        'source_ok_cnt': source_ok_cnt,
        'source_ng_cnt': all_cnt - source_ok_cnt,
        'ctime_ok_cnt': ctime_ok_cnt,
        'ctime_ng_cnt': all_cnt - ctime_ok_cnt,
    }
    return render(request, 'allsite/detailList.html', context)


def getDetailDialogInfo(request):
    '''
    [详细画面 - dialog] 获取全站采集内容
    '''
    # print('[info] getDetailDialogInfo start .....')
    print(request.POST)

    url = request.POST.get('url')
    db = MongoDriver()
    info = db.get_detail_dialog_info(url)
    output = JsonResponse(info)

    # print('[info] getDetailDialogInfo end.', info)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def crawlTimesMain(request):
    '''
    [采集时间差画面] 数据
    '''
    if request.method == 'POST':
        print('crawlTimesMain POST: ', request.POST)
        search = request.POST.get('search', '')

    else:  # request.method == 'GET'
        print('crawlTimesMain GET: ', request.GET)
        search = request.GET.get('search', '')

    result = [
        {'date': '2017-02-10',
         'total': 1999450 * 8,
         'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
                  'd2': {'percent': '2.1%', 'cnt': 1999450, 'width': '10.5'},
                  'd3': {'percent': '3.3%', 'cnt': 1999450, 'width': '16.5'},
                  'd4': {'percent': '9.3%', 'cnt': 1999450, 'width': '46.5'},
                  'd5': {'percent': '0%', 'cnt': 1999450, 'width': '0'},
                  'd6': {'percent': '20.7%', 'cnt': 1999450, 'width': '103.5'},
                  'd7': {'percent': '31.6%', 'cnt': 1999450, 'width': '158'},
                  'd8': {'percent': '7.8%', 'cnt': 1999450, 'width': '39'},
                  'd9': {'percent': '4.3%', 'cnt': 1999450, 'width': '21.5'}
                  }
         },
        {'date': '2017-02-11',
         'total': 1999450 * 8,
         'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': '43.5'},
                  'd2': {'percent': '2.1%', 'cnt': 1999450, 'width': '10.5'},
                  'd3': {'percent': '3.3%', 'cnt': 1999450, 'width': '16.5'},
                  'd4': {'percent': '9.3%', 'cnt': 1999450, 'width': '46.5'},
                  'd5': {'percent': '0%', 'cnt': 1999450, 'width': '0'},
                  'd6': {'percent': '20.7%', 'cnt': 1999450, 'width': '103.5'},
                  'd7': {'percent': '31.6%', 'cnt': 1999450, 'width': '158'},
                  'd8': {'percent': '7.8%', 'cnt': 1999450, 'width': '39'},
                  'd9': {'percent': '4.3%', 'cnt': 1999450, 'width': '21.5'}
                  }
         },
    ]

    r = RedisDriver()
    result = r.get_crawlTimeList()
    context = {
        'search': search,
        'result': result
    }
    return render(request, 'allsite/crawlTimes.html', context)


def dashBoardTopCnt(request):
    '''
    [主控面板] 顶端数字栏
    '''
    # print( 'dashBoardCnt start.........')
    db = MongoDriver()

    # 域名总数
    _, _, domain_total_cnt_list, _ = db.get_domain_cnt('week')

    # 频道总数
    hubPage_total_cnt = db.get_hubPage_sum()

    # 今日新增域名
    new_doamin_cnt = db.get_newDomain_cnt()

    # 详情页总数
    # detail_all_cnt = db.get_detail_total_cnt()

    # 详情页总数
    detail_today_all_cnt, detail_today_user_cnt = db.get_detail_today_cnt()
    detail_today_direct_cnt = db.get_detail_direct_cnt('today')

    detail_today_direct_per = 0
    detail_today_user_per = 0
    if detail_today_all_cnt:
        detail_today_direct_per = int(detail_today_direct_cnt / detail_today_all_cnt * 100)
        detail_today_user_per = int(detail_today_user_cnt / detail_today_all_cnt * 100)

    output = JsonResponse({"domain_cnt": '{:,}'.format(domain_total_cnt_list[-1]),
                           "hubPage_cnt": '{:,}'.format(hubPage_total_cnt),
                           "detail_today_all_cnt": '{:,}'.format(detail_today_all_cnt),
                           "detail_today_direct_cnt": '{:,}'.format(detail_today_direct_cnt),
                           "detail_today_direct_per": detail_today_direct_per,
                           "detail_today_user_cnt": '{:,}'.format(detail_today_user_cnt),
                           "detail_today_user_per": detail_today_user_per,
                           'new_doamin_cnt': '{:,}'.format(new_doamin_cnt)
                           })

    # print ('dashBoardCnt end ........')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageRank(request):
    '''
    [主控面板] 频道采集量排名
    '''
    # print( 'drawHubPageRank start.........')
    db = MongoDriver()
    hubPageUrl, hubPageCrawledNum = db.get_hubPage_rank()

    output = JsonResponse({"hubPageUrl": hubPageUrl, "hubPageCrawledNum": hubPageCrawledNum})

    # print( 'drawHubPageRank end ........')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDomainRank(request):
    '''
    [主控面板] 域名总数
    '''
    # print( 'drawDomainRank start.........')
    arr1 = [10000, 12000, 16000, 10000, 8000, 4000, 4000, 3000, 1000, 500]
    arr2 = [30000, 22000, 16000, 20000, 10000, 9000, 8000, 6000, 10000, 1000]
    output = JsonResponse({"domainRankUsed": arr1, "domainRankUnUsed": arr2})

    # print( 'drawDomainRank end ........')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawCrawlUsed(request):
    '''
    [主控面板] 采集入库统计（一周）
    '''
    # print( 'drawCrawlUsed start.........')
    r = RedisDriver()
    days, crawled, unUsed = r.get_crawlUsed()
    output = JsonResponse({"days": days, "crawled": crawled, "unUsed": unUsed})

    # print( 'drawCrawlUsed end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageTrend(request):
    '''
    [主控面板] 频道探测速度
    '''
    # print ('drawHubPageTrend start.........')
    db = MongoDriver()
    seconds = db.get_hubPage_scanPeriod()
    h = int(seconds / (60 * 60))
    m = int((seconds - (60 * 60) * h) / 60)
    s = int(seconds - (60 * 60) * h - 60 * m)

    times, cnt_list = db.get_hubPage_remainQueue()

    output = JsonResponse({"times": times, "remainQueue": cnt_list, "period": "{0}小时{1}分{2}秒".format(h, m, s)})

    # print( 'drawHubPageTrend end ........')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDetailTrend(request):
    '''
    [主控面板] 采集统计（24小时）
    '''
    # print ('drawDetailTrend start.........')
    db = MongoDriver()
    today, yesterday, beforeYesterday = db.get_detail_3dayDiff()
    output = JsonResponse({"beforeYesterday": beforeYesterday, "yesterday": yesterday, "today": today})
    # print( 'drawDetailTrend end ........')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawCrawlTimePart(request):
    '''
    [主控面板] 采集时间差（today）
    '''
    # print ('drawCrawlTimePart start.........')
    r = RedisDriver()
    ret = r.get_crawlTimePart()

    data = {}
    data['0-1'] = ret[0]
    data['1-2'] = ret[1]
    data['2-5'] = ret[2]
    data['5-15'] = ret[3]
    data['15-30'] = ret[4]
    data['30-60'] = ret[5]
    data['60-120'] = ret[6]
    data['120-240'] = ret[7]
    data['>240'] = ret[8]

    output = JsonResponse(data)

    # print ('drawCrawlTimePart end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawNewDomain(request):
    '''
    [主控面板] 新站发现(日增量)
    '''
    # print( 'drawNewDomain start ........')
    # print('drawNewDomain', request.POST)
    opt = request.POST.get('opt', 'week')

    db = MongoDriver()
    timeList, domainDaysCnt, domainTotalCnt, interval = db.get_domain_cnt(opt)

    output = JsonResponse({'timeList': timeList, 'domainDaysCnt': domainDaysCnt, 'domainTotalCnt': domainTotalCnt,
                           'interval': interval})
    # print( 'drawNewDomain end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')
