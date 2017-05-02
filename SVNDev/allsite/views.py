# coding=utf-8

# Create your views here.
from pprint import pprint
import datetime
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from .dbDriver import RedisDriver
from .dbDriver import MongoDriver
from .dbDriver import CONFIG_ID

from .setting import PAGE_SIZE

MDB = MongoDriver()
RDB = RedisDriver()


# [主控面板画面]
class MainView(TemplateView):
    queryset = []
    template_name = 'allsite/main.html'


# [域名管理画面]
class DomainListView(TemplateView):
    queryset = []
    template_name = 'allsite/domainList.html'

    def _get_data(self, args):
        search = args.get('search', '')
        times = args.get('times', 'all')
        page_num = args.get('page', 1)

        result = MDB.get_domain_info_list(search, times, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        ret = {
            'search': search,
            'times': times,
            'result': result,
            'page': page_num,
        }
        return ret

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self._get_data(request.POST)
        return render(request, self.template_name, context)


# [列表URL（频道）管理画面]
class HubPageListView(TemplateView):
    queryset = []
    template_name = 'allsite/hubPageList.html'

    def _get_data(self, args):
        search = args.get('search', '')
        page_num = args.get('page', 1)
        result = MDB.get_hubPage_info_list(search, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE, False)

        ret = {
            'search': search,
            'result': result,
            'page': page_num,
        }
        return ret

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self._get_data(request.POST)
        return render(request, self.template_name, context)


# [列表URL（频道）管理画面]
class QuickHubPageListView(TemplateView):
    queryset = []
    template_name = 'allsite/quickHubPageList.html'

    def _get_data(self, args):
        search = args.get('search', '')
        page_num = args.get('page', 1)
        result = MDB.get_hubPage_info_list(search, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE, True)

        ret = {
            'search': search,
            'result': result,
            'page': page_num,
        }
        return ret

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)


# [详情URL一览画面]
class DetailListView(TemplateView):
    queryset = []
    template_name = 'allsite/detailList.html'

    def _get_data(self, args):
        search = args.get('search', '')
        select_cond = args.get('selectCond', '')
        hubPage = args.get('hubPage', '')
        page_num = args.get('page', 1)

        result = MDB.get_detail_info_list(search, hubPage, select_cond, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        # 前端post提交未记录参数(search,select_cond,page_num)，由后端再传回。
        ret = {
            'search': search,
            'selectCond': select_cond,
            'hubPage': hubPage,
            'page': page_num,
            'result': result,
            'allsite_config_id': CONFIG_ID,
            # 'user_id': request.user.id
        }
        return ret

    def get(self, request, *args, **kwargs):
        # print('[info] DetailListView get', request.GET)
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # print('[info] DetailListView post', request.POST)
        context = self._get_data(request.POST)
        return render(request, self.template_name, context)


# [详情各项目相似度画面]
class DetailLikenessListView(TemplateView):
    queryset = []
    template_name = 'allsite/detailLikenessList.html'

    def _get_data(self, args):
        start = args.get('start', '')
        end = args.get('end', '')
        page_num = args.get('page', 1)

        result = MDB.get_detail_likeness_list(start, end, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        paginator = Paginator(result, PAGE_SIZE)
        loaded = paginator.page(page_num)
        ret = {
            'start': start,
            'end': end,
            'page': page_num,
            'result': loaded,
        }
        return ret

    def get(self, request, *args, **kwargs):
        # print('[info] DetailLikenessListView get', request.GET)
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # print('[info] DetailLikenessListView post', request.POST)
        context = self._get_data(request.POST)
        return render(request, self.template_name, context)


# [详情手工判断一览画面]
class DetailCorrectListView(TemplateView):
    queryset = []
    template_name = 'allsite/detailCorrectList.html'

    def _get_data(self, args):
        url = args.get('url', '')
        start = args.get('start', '')
        end = args.get('end', '')
        page_num = args.get('page', 1)
        user = 'admin'

        result = MDB.get_detail_correct_list(url, user, start, end)
        paginator = Paginator(result, PAGE_SIZE)
        loaded = paginator.page(page_num)
        ret = {
            'url': url,
            'start': start,
            'end': end,
            'page': page_num,
            'result': loaded,
            'search_cnt': len(result),
        }
        # pprint(result)
        return ret

    def get(self, request, *args, **kwargs):
        print('[info] DetailCorrectListView get start.')
        pprint(request.GET)
        context = self._get_data(request.GET)
        print('[info] DetailCorrectListView get end.')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print('[info] DetailCorrectListView post start.')
        pprint(request.POST)
        context = self._get_data(request.POST)
        print('[info] DetailCorrectListView post end.')
        return render(request, self.template_name, context)


# [采集时间差画面]
class CrawlTimesListView(TemplateView):
    queryset = []
    template_name = 'allsite/crawlTimes.html'

    def _get_data(self, args):
        search = args.get('search', '')
        result = RDB.get_crawlTimeList()
        ret = {
            'search': search,
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)
