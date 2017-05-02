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

from .setting import PAGE_SIZE

MDB = MongoDriver()
RDB = RedisDriver()


# [传播分析画面]
class MainView(TemplateView):
    queryset = []
    template_name = 'comments/commentsMain.html'

class CommentInfoListView(TemplateView):
    queryset = []
    template_name = 'comments/commentInfoList.html'

    def _get_data(self, args):
        search = args.get('search', '')
        page_num = args.get('page', 1)

        result = MDB.get_commentInfo_list(search, (int(page_num) - 1) * PAGE_SIZE, PAGE_SIZE)
        # pprint(result)
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

class CommentInfoList2View(TemplateView):
    queryset = []
    template_name = 'comments/commentInfoList2.html'