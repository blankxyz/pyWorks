# coding=utf-8
import datetime, time
from pprint import pprint
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.cache import cache_page
from rest_framework import filters, pagination, serializers
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response as restResponse
from rest_framework import status

from .dbDriver import MongoDriver
from .dbDriver import RedisDriver
from .setting import PAGE_SIZE, UNKOWN

from .serializers import XPathSerializer
from .models import XPathEntity

MDB = MongoDriver()
RDB = RedisDriver()


# restful 分页 实例
class TestListViewAPI(ListAPIView):
    class MySerializer(serializers.BaseSerializer):
        def to_representation(self, item):
            return item

    class MyPagination(pagination.PageNumberPagination):
        page_size = PAGE_SIZE
        page_size_query_param = 'page_size'
        max_page_size = 1000

    class MyFilter(filters.BaseFilterBackend):
        def filter_queryset(self, request, queryset, view):
            args = request.GET
            search = args.get('search', '')
            times = args.get('times', 'all')
            page_num = int(args.get('page', 1))

            result = MDB.get_domain_info_list(search,
                                              times,
                                              skip=(page_num - 1) * view.pagination_class.page_size,
                                              page_size=view.pagination_class.max_page_size)
            # return queryset
            return result

    serializer_class = MySerializer
    queryset = []
    filter_backends = [MyFilter]
    pagination_class = MyPagination


class DomainListViewAPI(ListAPIView):
    def _get_data(self, args):
        search = args.get('search', '')
        times = args.get('times', 'all')
        page_num = args.get('page', 1)

        cnt = MDB.get_domain_info_list_cnt(search, times)
        result = MDB.get_domain_info_list(search, times, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        ret = {
            'cnt': cnt,
            'result': result,
        }
        return ret

    def _set_data(self, args):
        url = args.get('url')
        siteName = args.get('siteName')
        ret = MDB.set_domain_info(domain=url, siteName=siteName)
        return ret

    def get(self, request, *args, **kwargs):
        ret = self._get_data(request.GET)
        output = JsonResponse(ret)
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def put(self, request, *args, **kwargs):
        '''
        [域名管理画面 - dialog] 域名修改
        '''
        ret = self._set_data(request.POST)
        output = JsonResponse({"ret": ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


class HubPageListViewAPI(APIView):
    def _get_data(self, args):
        search = args.get('search', '')
        page_num = args.get('page', 1)
        cnt = MDB.get_hubPage_info_list_cnt(search)
        result = MDB.get_hubPage_info_list(search, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE, False)
        ret = {
            'cnt': cnt,
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        ret = self._get_data(request.GET)
        output = JsonResponse(ret)
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def post(self, request, *args, **kwargs):
        print('post:' + request.POST)
        ret = {'msg': 'ok'}
        output = JsonResponse(ret)
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


class QuickHubPageListViewAPI(APIView):
    def _get_data(self, args):
        search = args.get('search', '')
        page_num = args.get('page', 1)
        quick_flg = args.get('quick_flg', False)
        cnt = MDB.get_hubPage_info_list_cnt(search, quick_flg)
        result = MDB.get_hubPage_info_list(search, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE, True)
        ret = {
            'cnt': cnt,
            'result': result
        }
        return ret

    def _set_data(self, args):
        url = args.get('url')
        if not url: return -1

        name = args.get('name', '')
        period = args.get('period', 15)
        ret = MDB.set_hubPage_info(url, name, period)
        return ret

    def _remove_data(self, args):
        url = args.get('url')
        ret = MDB.remove_hubPage_info(url)
        return ret

    def get(self, request, *args, **kwargs):
        print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({"ret": ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def post(self, request, *args, **kwargs):
        print('post:', request.POST)
        ret = self._set_data(request.POST)
        if 'upserted' in ret: ret.pop('upserted')  # 含有objectId 无法json编码
        print('post:', ret)
        output = JsonResponse({"ret": "添加了一条信息。" if  ret['nModified'] == 0 else "修改了一条信息。"})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def put(self, request, *args, **kwargs):
        print('put:', request.POST)
        ret = self._set_data(request.POST)
        print('put:', ret)
        output = JsonResponse({"ret": ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def delete(self, request, *args, **kwargs):
        # print('delete:', request.POST)
        ret = self._remove_data(request.POST)
        # print('delete:', ret, ret['n'])
        output = JsonResponse({"ret": "删除了一条信息。" if  ret['n'] == 1 else "删除失败，或者不是一条。"  })
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


class DetailListViewAPI(APIView):
    def _get_data(self, args):
        search = args.get('search', '')
        select_cond = args.get('selectCond', '')
        hubPage = args.get('hubPage', '')
        page_num = args.get('page', 1)

        cnt = MDB.get_detail_search_cnt(search, hubPage, select_cond)
        result = MDB.get_detail_info_list(search, hubPage, select_cond, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        # paginator = Paginator(range(all_cnt), PAGE_SIZE)
        # index = paginator.page(page_num)
        ret = {
            'cnt': cnt,
            'result': result,
        }
        return ret

    def get(self, request, *args, **kwargs):
        ret = self._get_data(request.GET)
        output = JsonResponse(ret)
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


class CrawlTimesListViewAPI(APIView):
    def _get_data(self, args):
        search = args.get('search', '')
        result = RDB.get_crawlTimeList()
        ret = {
            'search': search,
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        ret = self._get_data(request.GET)
        output = JsonResponse(ret)
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


def dashBoardTopCntAPI(request):
    '''
    [主控面板] 顶端数字栏
    '''
    # print( 'dashBoardTopCntAPI start...')
    # 域名总数
    _, _, domain_total_cnt_list, _ = MDB.get_domain_cnt('week')
    # 频道总数
    hubPage_total_cnt = MDB.get_hubPage_sum()
    # 今日新增域名
    new_doamin_cnt = MDB.get_newDomain_cnt()
    # 详情页总数
    detail_today_all_cnt, detail_today_user_cnt = MDB.get_detail_today_cnt()
    detail_today_direct_cnt = MDB.get_detail_direct_cnt('today')

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

    # print ('dashBoardTopCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageRankAPI(request):
    '''
    [主控面板] 频道采集量排名
    '''
    # print( 'drawHubPageRankAPI start...')
    hubPageUrl, hubPageCrawledNum = MDB.get_hubPage_rank()
    output = JsonResponse({"hubPageUrl": hubPageUrl,
                           "hubPageCrawledNum": hubPageCrawledNum})
    # print( 'drawHubPageRankAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDomainRankAPI(request):
    '''
    [主控面板] 域名总数
    '''
    # print( 'drawDomainRankAPI start...')
    arr1 = [10000, 12000, 16000, 10000, 8000, 4000, 4000, 3000, 1000, 500]
    arr2 = [30000, 22000, 16000, 20000, 10000, 9000, 8000, 6000, 10000, 1000]
    output = JsonResponse({"domainRankUsed": arr1, "domainRankUnUsed": arr2})
    # print( 'drawDomainRankAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawCrawlUsedAPI(request):
    '''
    [主控面板] 采集入库统计（一周）
    '''
    # print( 'drawCrawlUsedAPI start...')
    days, crawled, unUsed = RDB.get_crawlUsed()
    output = JsonResponse({"days": days,
                           "crawled": crawled,
                           "unUsed": unUsed})
    # print( 'drawCrawlUsedAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawHubPageTrendAPI(request):
    '''
    [主控面板] 频道探测速度
    '''
    # print ('drawHubPageTrendAPI start...')
    seconds = MDB.get_hubPage_scanPeriod()
    h = int(seconds / (60 * 60))
    m = int((seconds - (60 * 60) * h) / 60)
    s = int(seconds - (60 * 60) * h - 60 * m)

    times, cnt_list = MDB.get_hubPage_remainQueue()
    output = JsonResponse({"times": times,
                           "remainQueue": cnt_list,
                           "period": "{0}小时{1}分{2}秒".format(h, m, s)})
    # print( 'drawHubPageTrendAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDetailTrendAPI(request):
    '''
    [主控面板] 采集统计（24小时）
    '''
    # print ('drawDetailTrendAPI start...')
    today, yesterday, beforeYesterday = MDB.get_detail_3dayDiff()
    output = JsonResponse({"beforeYesterday": beforeYesterday,
                           "yesterday": yesterday,
                           "today": today})
    # print( 'drawDetailTrendAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def _setDetailLikeness(day):
    cond = {'date': day}
    today_info = MDB.detail_likeness.find_one(cond)
    if today_info:
        MDB.detail_likeness.remove({'_id': today_info['_id']})

    all_cnt = MDB.get_detail_search_cnt('', '', '', day)
    info = dict()
    info['date'] = day
    info['all_cnt'] = all_cnt
    info['likeness'] = dict()

    for part in ['all', 'title', 'content', 'source', 'ctime']:
        part_ok_cnt = MDB.get_detail_part_ok_cnt('', '', '', all_cnt, part, day)
        part_likeness_rate = float(part_ok_cnt) / all_cnt if all_cnt else 0.000
        part_likeness_rate = float('%.1f' % (part_likeness_rate * 100))
        info['likeness'][part] = part_likeness_rate

    MDB.detail_likeness.insert(info)

    return info


def _getDetailLikeness(day):
    today = datetime.datetime.today().strftime('%Y%m%d')
    cond = {'date': day}
    info = MDB.detail_likeness.find_one(cond)
    if info:
        if day != today:
            return info
        else:  # 今天1小时以内生成的
            d = time.mktime((datetime.datetime.utcnow() - datetime.timedelta(hours=1)).timetuple())
            if d < time.mktime((info['_id'].generation_time).timetuple()):
                return info

    return _setDetailLikeness(day)


def mainDetailLikenessAPI(request):
    '''
    [详情页一览画面] 各项目准确性统计
    '''
    # print('mainDetailLikenessAPI start...', request.POST)
    args = request.POST
    start = args.get('start', '20170101')
    end = args.get('end', datetime.datetime.today().strftime('%Y%m%d'))

    all_likeness = []
    title_likeness = []
    content_likeness = []
    source_likeness = []
    ctime_likeness = []
    all_cnt = []
    days = []

    for i in range(30, -1, -1):
        day = datetime.datetime.now() - datetime.timedelta(days=i)
        days.append(day.strftime('%m%d'))

        info = _getDetailLikeness(day.strftime('%Y%m%d'))
        all_cnt.append(info['all_cnt'])
        all_likeness.append(info['likeness']['all'])
        title_likeness.append(info['likeness']['title'])
        content_likeness.append(info['likeness']['content'])
        source_likeness.append(info['likeness']['source'])
        ctime_likeness.append(info['likeness']['ctime'])

    output = JsonResponse({'days': days,
                           'all_cnt': all_cnt,
                           'all_likeness': all_likeness,
                           'title_likeness': title_likeness,
                           'content_likeness': content_likeness,
                           'source_likeness': source_likeness,
                           'ctime_likeness': ctime_likeness,
                           })

    # print('mainDetailLikenessAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawCrawlTimePartAPI(request):
    '''
    [主控面板] 采集时间差（today）
    '''
    # print ('drawCrawlTimePartAPI start...')
    ret = RDB.get_crawlTimePart()
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
    # print ('drawCrawlTimePartAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawNewDomainAPI(request):
    '''
    [主控面板] 新站发现(日增量)
    '''
    # print( 'drawNewDomainAPI start...',request.POST)
    opt = request.POST.get('opt', 'week')
    timeList, domainDaysCnt, domainTotalCnt, interval = MDB.get_domain_cnt(opt)
    output = JsonResponse({'timeList': timeList,
                           'domainDaysCnt': domainDaysCnt,
                           'domainTotalCnt': domainTotalCnt,
                           'interval': interval})
    # print( 'drawNewDomainAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def drawDomainSearchCategoryAPI(request):
    # print( 'drawDomainSearchCategoryAPI start...')
    manual_added_cnt, cross_domain_link_cnt, engine_sum, engine_baidu_cnt, engine_sogou_cnt, engine_so_cnt = \
        MDB.get_doamin_search_category_cnt()

    output = JsonResponse({'manual_added': manual_added_cnt,
                           'cross_domain_link': cross_domain_link_cnt,
                           'engine_sum': engine_sum,
                           'engine_baidu': engine_baidu_cnt,
                           'engine_sogou': engine_sogou_cnt,
                           'engine_so': engine_so_cnt
                           })
    # print('drawDomainSearchCategoryAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def getDetailDialogInfoAPI(request):
    '''
    [详情页一览画面 - dialog] 获取全站采集内容
    '''
    # print('[info] getDetailDialogInfoAPI start...', request.POST)
    url = request.POST.get('url')
    info = MDB.get_detail_dialog_info(url)
    output = JsonResponse(info)
    # pprint(info)
    # print('[info] getDetailDialogInfoAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def getDomainSearchCntAPI(request):
    '''
    [域名管理一览画面] 在选择条件下，查询结果的总数.
    '''
    # print('getDomainSearchCntAPI start.', request.POST)
    search = request.POST.get('search')
    times = request.POST.get('times')
    page_num = int(request.POST.get('page_num', 1))

    search_cnt = MDB.get_domain_info_list_cnt(search, times)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page_num)

    output = JsonResponse({'search_cnt': search_cnt,
                           'current_page': index.number,
                           'total_pages': paginator.num_pages,
                           'has_prev': index.has_previous(),
                           'has_next': index.has_next(),
                           })
    # print('getDomainSearchCntAPI end.',search_cnt)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def getHubPageSearchCntAPI(request):
    '''
    [频道页一览画面] 在选择条件下，查询结果的总数.
    '''
    # print('getHubPageSearchCntAPI start.', request.POST)
    search = request.POST.get('search')
    page_num = int(request.POST.get('page_num', 1))
    quick_flg = request.POST.get('quick_flg', False)

    search_cnt = MDB.get_hubPage_info_list_cnt(search, quick_flg)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page_num)

    output = JsonResponse({'search_cnt': search_cnt,
                           'current_page': index.number,
                           'total_pages': paginator.num_pages,
                           'has_prev': index.has_previous(),
                           'has_next': index.has_next(),
                           })
    # print('getHubPageSearchCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def getDetailSearchCntAPI(request):
    '''
    [详情页一览画面] 在选择条件下，查询结果的总数.
    '''
    # print('getDetailSearchCntAPI start.', request.POST)
    search = request.POST.get('search')
    selected_cond = request.POST.get('select_cond')
    hubPage = request.POST.get('hubPage')
    page_num = int(request.POST.get('page_num', 1))

    search_cnt = MDB.get_detail_search_cnt(search, hubPage, selected_cond)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page_num)

    output = JsonResponse({'search_cnt': search_cnt,
                           'current_page': index.number,
                           'total_pages': paginator.num_pages,
                           'has_prev': index.has_previous(),
                           'has_next': index.has_next(),
                           })
    # print('getDetailSearchCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def getDetailPartCntAPI(request):
    '''
    [详情页一览画面] 各项目正误统计
    '''
    # print('getDetailPartCntAPI start...', request.POST)
    search = request.POST.get('search')
    selected_cond = request.POST.get('select_cond')
    hubPage = request.POST.get('hubPage')
    part = request.POST.get('part')
    selected_cnt = int(request.POST.get('searchCnt', '0'))

    search_cnt = MDB.get_detail_search_cnt(search, hubPage, selected_cond)
    part_ok_cnt = MDB.get_detail_part_ok_cnt(search, hubPage, selected_cond, selected_cnt, part)
    output = JsonResponse({'part_ok_cnt': part_ok_cnt,
                           'part_ng_cnt': selected_cnt - part_ok_cnt})
    # print('getDetailPartCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def setDetailCorrectInfoAPI(request):
    '''
    [详情页一览画面] 各项目人工判断结果
    '''
    # print('[info] setDetailCorrectInfoAPI start...')
    # pprint(request.POST)
    url = request.POST.get('url')
    direct_title = True if request.POST.get('direct_title') == "true" else False
    direct_content = True if request.POST.get('direct_content') == "true"else False
    direct_source = True if request.POST.get('direct_source') == "true"else False
    direct_ctime = True if request.POST.get('direct_ctime') == "true"else False

    config_id = request.POST.get('config_id')
    correct_title = False if request.POST.get('correct_title') == "ng"else True
    correct_content = False if request.POST.get('correct_content') == "ng"else True
    correct_source = False if request.POST.get('correct_source') == "ng"else True
    correct_ctime = False if request.POST.get('correct_ctime') == "ng"else True

    info = {
        'url': url,
        'direct_compare': {
            'config_id': config_id,
            'title': direct_title,
            'content': direct_content,
            'source': direct_source,
            'ctime': direct_ctime
        },
        'correct': {
            'title': correct_title,
            'content': correct_content,
            'source': correct_source,
            'ctime': correct_ctime
        }
    }
    # pprint(info)
    ret = MDB.save_detail_correctInfo(info)
    output = JsonResponse({'ret': ret})
    # print('[info] setDetailCorrectInfoAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def mainDetailTop100API(request):
    draw = request.GET.get('draw')
    start = int(request.GET.get('start', '0'))
    length = int(request.GET.get('length', '6'))
    search = request.GET.get('search[value]')

    # pprint(request.GET)
    ret = MDB.get_detail_list_top100(search, start, length)
    output = JsonResponse({
        'data': ret,
        'draw': draw,
        'recordsTotal': 100,
        'recordsFiltered': 100
    })
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


# @csrf_protect
@csrf_exempt
def getMatchDetailUrlAPI(request):
    '''
    [跳转到频道页] 插件.
    '''
    print('[info] getMatchDetailUrlAPI start.', request.POST)
    requestUrls = []
    topPage = request.POST.get('topPage')
    hrefs = request.POST.getlist('hrefList')

    for href in hrefs:
        if href.find('http://') < 0:
            url = topPage + href
        else:
            url = href

        requestUrls.append(url)

    responseUrls = MDB.getMatchDetailUrls(requestUrls)
    responseUrls = ['/list-stocks-1.shtml', '/list-free-1.shtml']
    output = JsonResponse({'response': responseUrls})
    print('[info] getMatchDetailUrlAPI end.', responseUrls)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


# ORM模型
class XPathViewAPI(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        args = request.GET
        print('[info] XPathViewAPI get start.', args)
        username = args.get('username', 'admin')
        url = args.get('url', '')
        entity = XPathEntity.objects.filter(username=username, url=url)
        if len(entity) == 1:
            print('[info] XPathViewAPI get end.')
            # serializers = XPathSerializer(entity, many=False)
            msg = 'ok'
            # return restResponse(serializers.data, status=status.HTTP_200_OK)
            return restResponse(msg, status=status.HTTP_200_OK)
        else:
            print('[info] XPathViewAPI get end.', len(entity))
            return restResponse('not found.', status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request, format=None):
        args = request.POST
        print('[info] XPathViewAPI post start.')
        # pprint(args)

        username = args.get('username', 'admin')
        url = args.get('url', '')
        title_xpath = args.get('title_xpath', '')
        content_xpath = args.get('content_xpath', '')
        ctime_xpath = args.get('ctime_xpath', '')
        source_xpath = args.get('source_xpath', '')
        page_xpath = args.get('page_xpath', '')

        entity = XPathEntity.objects.filter(username=username, url=url)

        if len(entity) == 0:
            msg = 'created'
            newEntity = XPathEntity(
                username=username,
                url=url,
                title_xpath=title_xpath,
                content_xpath=content_xpath,
                ctime_xpath=ctime_xpath,
                source_xpath=source_xpath,
                page_xpath=page_xpath
            )
            newEntity.save()
            return restResponse(msg, status=status.HTTP_201_CREATED)
        elif len(entity) > 1:
            msg = 'found error' + str(len(entity))
            return restResponse(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:  # len(entity) == 1
            # serializers = XPathSerializer(instance=entity, data=request.data, many=False)

            entity.title_xpath = args.get('title_xpath')
            entity.content_xpath = args.get('content_xpath')
            entity.ctime_xpath = args.get('ctime_xpath')
            entity.source_xpath = args.get('source_xpath')
            entity.page_xpath = args.get('page_xpath')

            update_fields = []
            for field in ['title_xpath', 'content_xpath', 'ctime_xpath', 'source_xpath', 'page_xpath']:
                xpath = args.get(field)
                if xpath:
                    update_fields.append(field)

            if update_fields is not None:
                print('[info] XPathViewAPI post end. update_fields: ', update_fields)
                entity.save(update_fields=update_fields)
                # output = JsonResponse({'ret': status.HTTP_201_CREATED})
                # return HttpResponse(output, content_type='application/json; charset=UTF-8')
                msg = 'updated'
                return restResponse(msg, status=status.HTTP_302_FOUND)
            else:
                # msg = serializers.errors
                msg = 'update_fields is None'
                print('[info] XPathViewAPI post end. update_fields is None')
                return restResponse(msg, status=status.HTTP_400_BAD_REQUEST)
