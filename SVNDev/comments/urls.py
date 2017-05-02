# coding=utf-8
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views, restAPI
from .views import CommentInfoListView, CommentInfoList2View, MainView
from .restAPI import commentsQueueAPI, commentsCacheQueueAPI, commentInfoListAPI, commentsPaginatorAPI, \
    dashBoardTopCntAPI, mainDomainNewsCntAPI
from django.views.decorators.cache import cache_page

cache_time_out = 60 * 3

urlpatterns = patterns('',
                       url(r'^main/$', cache_page(cache_time_out)(MainView.as_view()), name='main'),
                       url(r'^dashBoardTopCntAPI/$', dashBoardTopCntAPI, name='dashBoardTopCntAPI'),
                       url(r'^mainDomainNewsCntAPI/$', mainDomainNewsCntAPI, name='mainDomainNewsCntAPI'),

                       url(r'^commentsQueueAPI/$', commentsQueueAPI, name='commentsQueueAPI'),
                       url(r'^commentsCacheQueueAPI/$', commentsCacheQueueAPI, name='commentsCacheQueueAPI'),

                       url(r'^commentInfoListAPI/$', commentInfoListAPI, name='commentInfoListAPI'),
                       url(r'^commentInfoList/$', CommentInfoListView.as_view(), name='commentInfoList'),
                       url(r'^commentInfoList2/$', CommentInfoList2View.as_view(), name='commentInfoList2'),
                       url(r'^commentsPaginatorAPI/$', commentsPaginatorAPI,
                           name='commentsPaginatorAPI'),
                       )
