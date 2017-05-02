# coding=utf-8
import datetime, time
import os
import json
from io import StringIO
import bson.binary
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
from .setting import PAGE_SIZE, STATUS_INIT, STATUS_TEST, STATUS_RUN
from django.conf import settings

MDB = MongoDriver()
RDB = RedisDriver()


#################### 主控界面API ####################
def mainTopCntAPI(request):
    '''
    [主控面板] 顶端数字栏
    '''
    # print( 'dashBoardTopCntAPI start...')
    # 域名总数
    domain_cnt = MDB.get_domain_cnt()
    # 频道总数
    channels_cnt = MDB.get_channels_cnt()

    output = JsonResponse({"domain_cnt": '{:,}'.format(domain_cnt),
                           "channel_cnt": '{:,}'.format(channels_cnt)
                           })

    # print('[info] dashBoardTopCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def mainInfoFlagAPI(request):
    '''
    [主控面板] InfoFlag分类统计
    '''
    # print( 'mainInfoFlagAPI start...')
    cnt_list, flag_list = MDB.get_info_flag_draw()
    output = JsonResponse({"cnt_list": cnt_list, "flag_list": flag_list})
    # print('[info] mainInfoFlagAPI end.', cnt_list, flag_list)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def mainTaskAPI(request):
    '''
    [主控面板] 运行状态下的队列统计
    '''
    # print( 'mainTaskAPI start...')
    cnt_list, task_list = RDB.get_task_draw()
    output = JsonResponse({"cnt_list": cnt_list, "task_list": task_list})
    # print('[info] mainTaskAPI end.', cnt_list, task_list)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def mainStatusAPI(request):
    '''
    [主控面板] 各个状态的分类统计
    '''
    # print( 'mainStatusAPI start...')
    cnt_list, status_list = MDB.get_status_draw()
    output = JsonResponse({"cnt_list": cnt_list, "status_list": status_list})
    # print('[info] mainStatusAPI end.', cnt_list, status_list)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def domainTreeAPI(request):
    MDB.all_domain_tree()
    output = JsonResponse({})
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 频道管理 ####################
class ChannelListViewAPI(APIView):
    def _get_data(self, args):
        searchUrl = args.get('searchUrl', '')
        page = args.get('page', 1)
        cnt = MDB.get_channel_search_cnt(searchUrl)
        result = MDB.get_channel_list(searchUrl, (int(page) - 1) * PAGE_SIZE, PAGE_SIZE)
        ret = {
            'cnt': cnt,
            'result': result
        }
        return ret

    def _set_data(self, args):
        url = args.get('url')
        if not url:
            return None, 'url为空。'

        domain = args.get('domain', '')
        siteName = args.get('siteName', '')
        channel = args.get('channel', '')
        info_flag = args.get('info_flag', '')
        crawl_rules = json.loads(args.get('crawl_rules'))
        interval = args.get('interval', '')
        status = args.get('status', '')
        config_id = int(args.get('config_id')) if args.get('config_id') else -1
        detail_encoding = args.get('detail_encoding')
        channel_encoding = args.get('channel_encoding')
        router = args.get('router')

        config = MDB.get_config_info(config_id)
        if config:
            code = config['code']
        else:
            code = ''

        info = {
            'url': url,
            'channel': channel,
            'domain': domain,
            'siteName': siteName,
            'crawl_rules': crawl_rules,
            'config_id': config_id,
            'code': code,
            'detail_encoding': detail_encoding,
            'channel_encoding': channel_encoding,
            'info_flag': info_flag,
            'dedup_uri': router,
            'data_db': router
        }

        RDB.remove_test_result(config_id)  # 清除测试结果
        if status == '测试中':  # 写入redis测试队列,旧测试信息由爬虫框架pop掉。
            rds_info = MDB.translate_to_redis(info)
            RDB.set_test(rds_info)

        if status == '运行中':  # 写入redis运行队列.
            RDB.remove_task(url)
            rds_info = MDB.translate_to_redis(info)
            RDB.set_task(rds_info, interval)

        mdb_info = {
            'url': url,
            'channel': channel,
            'domain': domain,
            'siteName': siteName,
            'crawl_rules': crawl_rules,
            'config_id': config_id,
            'detail_encoding': detail_encoding,
            'channel_encoding': channel_encoding,
            'info_flag': info_flag,
            'interval': interval,
            'status': status,
            'router': router,
            'update_ts': time.mktime(datetime.datetime.now().timetuple())
        }

        ret = MDB.set_channel_info(mdb_info)
        if 'upserted' in ret:
            ret.pop('upserted')  # 含有objectId 无法json编码

        msg = '添加了一条信息。' if ret['updatedExisting'] == False else '修改了一条信息。'
        return ret, msg

    def _remove_data(self, args):
        channel_url = args.get('channel_url')
        config_id = int(args.get('config_id')) if args.get('config_id') else -1
        status = args.get('status')
        if status == '测试中':
            RDB.remove_test_result(config_id)

        if status == '运行中':
            RDB.remove_task(channel_url)

        ret = MDB.remove_channel_info(channel_url)
        msg = '删除了一条信息。' if ret['n'] == 1 else '删除失败，或者不是一条。'
        return ret, msg

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def post(self, request, *args, **kwargs):
        # print('post:', request.POST)
        ret, msg = self._set_data(request.POST)
        # print('post:', ret)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def put(self, request, *args, **kwargs):
        # print('put:', request.POST)
        ret, msg = self._set_data(request.POST)
        # print('put:', ret)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def delete(self, request, *args, **kwargs):
        # print('delete:', request.POST)
        ret, msg = self._remove_data(request.POST)
        # print('delete:', ret, ret['n'])
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 频道管理API ####################
def channelInfoListAPI(request):
    # print('[info] channelInfoListAPI start.', request.GET)
    args = request.GET
    searchUrl = args.get('searchUrl', '')
    page = args.get('page', 1)
    result = MDB.get_channel_list(searchUrl, (int(page) - 1) * PAGE_SIZE, PAGE_SIZE)
    ret = {
        'searchUrl': searchUrl,
        'result': result,
        'page': page,
    }
    output = JsonResponse(ret)
    # print('[info] channelInfoListAPI end.', len(result))
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def channelPaginatorAPI(request):
    # print('[info] channelPaginatorAPI start.', request.GET)
    searchUrl = request.GET.get('searchUrl')
    page_num = int(request.GET.get('page', 1))

    search_cnt = MDB.get_channel_search_cnt(searchUrl)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page_num)
    ret = {'search_cnt': search_cnt,
           'current_page': index.number,
           'total_pages': paginator.num_pages,
           'has_prev': index.has_previous(),
           'has_next': index.has_next(),
           }
    output = JsonResponse(ret)
    # print('[info] channelPaginatorAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def channelInfoAPI(request):
    # print('[info] channelInfoAPI start.', request.GET)
    args = request.GET
    searchUrl = args.get('searchUrl', '')
    result = MDB.get_channel_info(searchUrl)
    ret = {
        'ret': result,
    }
    output = JsonResponse(ret)
    # print('[info] channelInfoListAPI end.', len(result))
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 测试结果 ####################
class TestResultListViewAPI(APIView):
    def _get_data(self, args):
        # config_id 为整数,有效: 正， -1 : None
        searchConfigId = int(args.get('searchConfigId')) if args.get('searchConfigId') else -1
        searchChannel = args.get('searchChannel', '')
        searchTitle = args.get('searchTitle', '')
        result = RDB.get_test_result_detail_url(searchChannel, searchTitle)
        ret = {
            'cnt': len(result),
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 配置管理 ####################
class ConfigListViewAPI(APIView):
    def _get_data(self, args):
        # config_id 为整数,有效: 正， -1 : None
        searchConfigId = int(args.get('searchConfigId')) if args.get('searchConfigId') else -1
        searchDomain = args.get('searchDomain', '')
        delete_flag = False if args.get('active_flag', 'active') == 'active' else True
        page = int(args.get('page', '1'))
        cnt = MDB.get_config_search_cnt(delete_flag, searchConfigId, searchDomain)
        result = MDB.get_config_list(delete_flag, searchConfigId, searchDomain, (int(page) - 1) * PAGE_SIZE, PAGE_SIZE)
        ret = {
            'cnt': cnt,
            'result': result
        }
        return ret

    def _set_data(self, args, code_file):
        config_id = int(args.get('config_id')) if args.get('config_id') else -1
        channel_name = args.get('channel_name')
        domain = args.get('domain')
        website_name = args.get('website_name')
        config_filename = args.get('config_filename')
        codeView = args.get('codeView')
        if codeView:
            code = codeView
            up_msg = '代码上传成功。'
        else:
            myFile = code_file.get('file', None)
            if not myFile:
                code = bytes('无', encoding='utf8')
                up_msg = '代码未保存。'
            else:
                config_filename = myFile.name
                code = bytes()
                for chunk in myFile.chunks():  # 分块写入文件
                    code = code + chunk
                up_msg = '代码上传成功。'

            code = code.decode('utf8')

        info = {
            'config_id': config_id,
            'channel_name': channel_name,
            'domain': domain,
            'website_name': website_name,
            'code': code,
            'config_filename': config_filename,
        }
        ret, new_id = MDB.set_config_info(info)
        if 'upserted' in ret:
            ret.pop('upserted')  # 含有objectId 无法json编码

        cnt = sync_configInfo_to_channel(new_id)
        # print('post:', ret)
        msg = up_msg + '添加了一条信息。' if ret['updatedExisting'] == False else '修改了一条信息。'
        msg = msg + "重置了" + str(cnt) + "个频道的任务。"
        return ret, msg, new_id

    def _remove_data(self, args):
        config_id = int(args.get('config_id')) if args.get('config_id') else -1
        ret = MDB.remove_config_info(config_id)
        msg = '删除了一条信息。' if ret['n'] == 1 else '删除失败，或者不是一条。'
        return ret, msg

    def _recovery_data(self, args):
        config_id = int(args.get('config_id')) if args.get('config_id') else -1
        ret = MDB.recovery_config_info(config_id)
        msg = '恢复了一条信息。' if ret['n'] == 1 else '恢复失败，或者不是一条。'
        return ret, msg

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def post(self, request, *args, **kwargs):
        # print('post:', request.POST, request.FILES)
        ret, msg, new_id = self._set_data(request.POST, request.FILES)
        output = JsonResponse({'ret': ret, 'msg': msg, 'new_id': new_id})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def put(self, request, *args, **kwargs):
        # print('put:', request.POST)
        ret, msg, new_id = self._set_data(request.POST, request.FILES)
        # print('put:', msg)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def patch(self, request, *args, **kwargs):
        # print('put:', request.POST)
        ret, msg = self._recovery_data(request.POST)
        # print('put:', msg)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def delete(self, request, *args, **kwargs):
        # print('delete:', request.POST)
        ret, msg = self._remove_data(request.POST)
        # print('delete:', ret)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 配置管理API ####################
def configPaginatorAPI(request):
    # print('[info] configPaginatorAPI start.', request.GET)
    delete_flag = False if request.GET.get('active_flag', 'active') == 'active' else True
    config_id = int(request.GET.get('searchConfigId')) if request.GET.get('searchConfigId') else -1
    domain = request.GET.get('searchDomain', '')
    page = int(request.GET.get('page', '1'))

    search_cnt = MDB.get_config_search_cnt(delete_flag, config_id, domain)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page)

    ret = {'search_cnt': search_cnt,
           'current_page': index.number,
           'total_pages': paginator.num_pages,
           'has_prev': index.has_previous(),
           'has_next': index.has_next(),
           }
    output = JsonResponse(ret)
    # print('[info] configPaginatorAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def _add_test(channel_url):
    channel_info_mng = MDB.get_channel_info(channel_url)
    if not channel_info_mng:
        ret = {
            'ret': False,
            'msg': '未找到频道URL。'
        }
    else:
        config_id = channel_info_mng['config_id']
        if not config_id:
            ret = {
                'ret': False,
                'msg': '未找到配置ID。'
            }
        else:
            config = MDB.get_config_info(config_id)
            if not config:
                ret = {
                    'ret': False,
                    'msg': '未找到配置信息。'
                }
            else:
                channel_info_mng['status'] = '测试中'
                MDB.set_channel_info(channel_info_mng)

                info = {
                    'url': channel_url,
                    'config_id': config_id,
                    "info_flag": channel_info_mng['info_flag'],
                    "channel_encoding": channel_info_mng['channel_encoding'],
                    "detail_encoding": channel_info_mng['detail_encoding'],
                    'code': config['code'],
                    'siteName': channel_info_mng['siteName'],
                    'channel': channel_info_mng['channel'],
                    'data_db': channel_info_mng['router'],
                    'dedup_uri': channel_info_mng['router'],
                    'crawl_rules': channel_info_mng['crawl_rules']
                }

                rds_info = MDB.translate_to_redis(info)
                RDB.set_test(rds_info)
                ret = {
                    'ret': True,
                    'msg': '测试任务添加完成。'
                }

    return ret


def testAPI(request):
    # print('[info] testAPI start.', request.POST)
    args = request.POST
    channel_url = args.get('channel_url')
    ret = _add_test(channel_url)
    output = JsonResponse(ret)
    # print('[info] testAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def testResultAPI(request):
    # print('[info] testResultAPI start.', request.GET)
    config_id = int(request.GET.get('config_id')) if request.GET.get('config_id') else -1
    detail_url = request.GET.get('detail_url')
    ret = RDB.get_test_result_by_url(config_id, detail_url)
    output = JsonResponse({
        'ret': ret,
        'msg': '找到测试结果。' if ret else '未找到测试结果。'
    })
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def _add_task(channel_url):
    channel_info_mng = MDB.get_channel_info(channel_url)
    if not channel_info_mng:
        ret = {
            'ret': False,
            'msg': '未找到频道URL。'
        }
    else:
        config_id = channel_info_mng['config_id']
        if not config_id:
            ret = {
                'ret': False,
                'msg': '未找到配置ID。'
            }
        else:
            config = MDB.get_config_info(config_id)
            if not config:
                ret = {
                    'ret': False,
                    'msg': '未找到配置信息。'
                }
            else:
                channel_info_mng['status'] = '运行中'
                MDB.set_channel_info(channel_info_mng)

                info = {
                    'url': channel_url,
                    'config_id': config_id,
                    "info_flag": channel_info_mng['info_flag'],
                    "channel_encoding": channel_info_mng['channel_encoding'],
                    "detail_encoding": channel_info_mng['detail_encoding'],
                    'code': config['code'],
                    'siteName': channel_info_mng['siteName'],
                    'channel': channel_info_mng['channel'],
                    'interval': channel_info_mng['interval'],
                    'data_db': channel_info_mng['router'],
                    'dedup_uri': channel_info_mng['router'],
                    'crawl_rules': channel_info_mng['crawl_rules']
                }

                rds_info = MDB.translate_to_redis(info)
                RDB.set_task(rds_info, channel_info_mng['interval'])
                ret = {
                    'ret': True,
                    'msg': '运行任务添加完成。'
                }
    return ret


def taskRunAPI(request):
    # print('[info] configTaskRunAPI start.', request.POST)
    args = request.POST
    channel_url = args.get('channel_url')
    ret = _add_task(channel_url)
    output = JsonResponse(ret)
    # print('[info] configTaskRunAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def resetAPI(request):
    # print('[info] resetAPI start.', request.POST)
    args = request.POST
    channel_url = args.get('channel_url')
    config_id = int(args.get('config_id')) if args.get('config_id') else -1

    RDB.remove_test_url_result(channel_url)  # 删除测试结果（列表URL）
    RDB.remove_test_result(config_id)  # 删除测试结果
    RDB.remove_task(channel_url)  # 删除运行任务
    up = MDB.set_channel_info_status(channel_url, '待测试')

    ret = {
        'ret': up,
        'msg': '清除测试结果、运行任务。' if up['n'] == 1 else '状态更新失败。'
    }
    output = JsonResponse(ret)
    # print('[info] resetAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def sync_configInfo_to_channel(config_id):
    if not MDB.get_config_use_channels(config_id):
        return 0

    RDB.remove_test_result(config_id)  # 删除测试结果
    l = MDB.get_channelInfo_by_configId(config_id)
    for info in l:
        RDB.remove_test_url_result(info['url'])  # 删除测试结果（列表URL）
        RDB.remove_task(info['url'])  # 删除运行任务
        if info['status'] == STATUS_TEST:
            _add_test(info['url'])

        if info['status'] == STATUS_RUN:
            _add_task(info['url'])

    return len(l)


def configCodeAPI(request):
    # print('[info] configCodeAPI start.', request.GET)
    args = request.GET
    config_id = int(args.get('config_id')) if args.get('config_id') else -1

    code = MDB.get_config_code(config_id)
    ret = {
        'code': code,
        'msg': '取得代码。'
    }
    output = JsonResponse(ret)
    # print('[info] configCodeAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def configUseCntAPI(request):
    # print('[info] configUseCntAPI start.', request.GET)
    args = request.GET
    config_id = int(args.get('config_id')) if args.get('config_id') else -1
    channels = MDB.get_config_use_channels(config_id)
    ret = {
        'use_cnt': len(channels),
        'channels': channels
    }
    output = JsonResponse(ret)
    # print('[info] configUseCntAPI end.')
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### RunResult ####################
class RunResultListViewAPI(APIView):
    def _get_data(self, args):
        searchChannel = args.get('searchChannel')
        page = int(args.get('page', '1'))
        result = MDB.get_runResult_list(searchChannel, -1 * int(page) * PAGE_SIZE, PAGE_SIZE)
        ret = {
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


def runResultPaginatorAPI(request):
    # print('[info] runResultPaginatorAPI start.', request.GET)
    searchChannel = request.GET.get('searchChannel', '')
    page = int(request.GET.get('page', '1'))

    search_cnt = MDB.get_runResult_search_cnt(searchChannel)
    paginator = Paginator(range(search_cnt), PAGE_SIZE)
    index = paginator.page(page)

    ret = {'search_cnt': search_cnt,
           'current_page': index.number,
           'total_pages': paginator.num_pages,
           'has_prev': index.has_previous(),
           'has_next': index.has_next(),
           }
    output = JsonResponse(ret)
    # print('[info] runResultPaginatorAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


def errorInfoAPI(request):
    # print('[info] errorInfoAPI start.', request.GET)
    searchChannel = request.GET.get('searchChannel', '')
    run_log_idx = int(request.GET.get('run_log_idx', '1'))
    code_error_idx = int(request.GET.get('code_error_idx', '1'))
    info, code, cnt = MDB.get_runError_info(searchChannel, run_log_idx, code_error_idx)
    _, d = divmod(code_error_idx, cnt)
    msg = '共有' + str(cnt) + ' 条错误信息，这是第 ' + str(d + 1) + ' 条'
    ret = {'result': info,
           'code': code,
           'msg': msg
           }
    output = JsonResponse(ret)
    # print('[info] errorInfoAPI end.', ret)
    return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 时间差 ####################
class TimeDeltaListViewAPI(APIView):
    def _get_data(self, args):
        searchChannel = args.get('searchChannel')
        result = MDB.get_timedelta_list(searchChannel)
        ret = {
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')


#################### 路由管理 ####################
class RouterListViewAPI(APIView):
    def _get_data(self, args):
        result = MDB.get_router_list()
        cnt = len(result)
        ret = {
            'cnt': cnt,
            'result': result
        }
        return ret

    def _set_data(self, args):
        name = args.get('name', '')
        dedup = args.get('dedup', '')
        data_db = args.get('data_db', '')
        info = {
            'name': name,
            'dedup': dedup,
            'data_db': data_db
        }
        ret = MDB.set_router(info)
        msg = '添加了一条信息。'
        return ret, msg

    def _remove_data(self, args):
        name = args.get('name', '')
        ret = MDB.remove_router(name)
        msg = '删除了一条信息。'
        return ret, msg

    def get(self, request, *args, **kwargs):
        # print('get:', request.GET)
        ret = self._get_data(request.GET)
        output = JsonResponse({'ret': ret})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def post(self, request, *args, **kwargs):
        # print('post:', request.POST)
        ret, msg = self._set_data(request.POST)
        if 'upserted' in ret:
            ret.pop('upserted')  # 含有objectId 无法json编码
        # print('post:', ret)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def put(self, request, *args, **kwargs):  # print('put:', request.POST)
        ret, msg = self._set_data(request.POST)
        # print('put:', msg)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')

    def delete(self, request, *args, **kwargs):
        # print('delete:', request.POST)
        # print('delete:', request.query_params)
        if request.POST:
            ret, msg = self._remove_data(request.POST)
        else:
            ret, msg = self._remove_data(request.query_params)
        # print('delete:', ret)
        output = JsonResponse({'ret': ret, 'msg': msg})
        return HttpResponse(output, content_type='application/json; charset=UTF-8')
