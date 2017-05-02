# coding=utf-8
from pprint import pprint
import datetime
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from .dbDriver import RedisDriver
from .dbDriver import MongoDriver

MDB = MongoDriver()
RDB = RedisDriver()


# [主控画面]
class MainView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/main.html'

# [频道管理画面]
class DomainTreeView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/domainTree.html'

# [频道管理画面]
class ChannelInfoListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/channelMgr.html'


# [测试结果画面]
class TestResultListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/testResultList.html'


# [配置管理画面]
class ConfigInfoListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/configMgr.html'


# [运行结果画面]
class RunResultListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/runResult.html'


# [时间差画面]
class TimeDeltaListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/timedelta.html'

    def _get_data(self, args):
        searchChannel = args.get('searchChannel')
        result = MDB.get_timedelta_list(searchChannel)
        ret = {
            'search': searchChannel,
            'result': result
        }
        return ret

    def get(self, request, *args, **kwargs):
        context = self._get_data(request.GET)
        return render(request, self.template_name, context)


# [路由管理画面]
class RouterListView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/router.html'

# [Debug画面]
class DebugView(TemplateView):
    queryset = []
    template_name = 'channelConfigMgr/debug.html'
