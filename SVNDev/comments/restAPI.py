# coding=utf-8
import datetime, time
from pprint import pprint
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from rest_framework import filters, pagination, serializers
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response as restResponse
from rest_framework import status

from .dbDriver import MongoDriver
from .dbDriver import RedisDriver
from .setting import PAGE_SIZE, UNKOWN

MDB = MongoDriver()
RDB = RedisDriver()


def dashBoardTopCntAPI(request):
    print('[info] dashBoardTopCntAPI start.')
    news_cnt = MDB.get_news_search_cnt('')
    comments_cnt = MDB.get_comments_search_cnt('')
    news_comments_cnt = MDB.get_news_comments_cnt()
    # ret = {
    #     'news_cnt': news_cnt,
    #     'comments_cnt': comments_cnt,
    #     'news_comments_cnt': news_comments_cnt,
    # }
    ret = {
        'news_cnt': '{:,}'.format(news_cnt),
        'comments_cnt': '{:,}'.format(comments_cnt),
        'news_comments_cnt': '{:,}'.format(news_comments_cnt),
    }
    print('[info] dashBoardTopCntAPI end.', ret)
    output = JsonResponse(ret)
    print('[info] dashBoardTopCntAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def commentInfoListAPI(request):
    # print('[info] commentInfoListAPI start.', request.GET)
    args = request.GET
    search = args.get('search', '')
    page = args.get('page', 1)
    result = MDB.get_commentInfo_list(search, (int(page) - 1) * PAGE_SIZE, PAGE_SIZE)
    ret = {
        'search': search,
        'result': result,
        'page': page,
    }
    output = JsonResponse(ret)
    # print('[info] commentInfoListAPI end.', len(result))
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


@csrf_exempt
def commentsQueueAPI(request):
    '''
    [评论采集] 评论采集任务队列
    '''
    # print('[info] commentsQueueAPI start.')
    ret = RDB.get_commentsQueueSize()
    output = JsonResponse({'queueSize': ret})
    # print('[info] commentsQueueAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def commentsCacheQueueAPI(request):
    '''
    [评论采集] 评论采集任务队列
    '''
    # print('[info] commentsCacheQueueAPI start.')
    ret = RDB.get_commentsCacheQueueSize()
    output = JsonResponse({'queueSize': ret})
    # print('[info] commentsCacheQueueAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def commentsPaginatorAPI(request):
    '''
    [传播分析画面] 在选择条件下，查询结果的总数.
    '''
    # print('[info] commentsPaginatorAPI start.', request.GET)
    search = request.GET.get('search')
    page_num = int(request.GET.get('page_num', 1))

    search_cnt = MDB.get_comments_search_cnt(search)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page_num)
    ret = {'search_cnt': search_cnt,
           'current_page': index.number,
           'total_pages': paginator.num_pages,
           'has_prev': index.has_previous(),
           'has_next': index.has_next(),
           }
    output = JsonResponse(ret)
    # print('[info] commentsPaginatorAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def mainDomainNewsCntAPI(request):
    '''
    [主控画面] 新闻每天采集量统计
    '''
    # print('mainDomainNewsCntAPI start...')
    days, qq, toutiao, ifeng, wangyi, sina = RDB.get_newsCnt()
    ret = {'days': days,
           'qq': qq,
           'sina': sina,
           'ifeng': ifeng,
           '163': wangyi,
           'toutiao': toutiao,
           }
    # pprint(ret)
    output = JsonResponse(ret)
    # print('mainDomainNewsCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')
