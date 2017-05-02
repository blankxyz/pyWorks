# coding=utf-8
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from .views import (
    MainView,
    DebugView,
    DomainTreeView,
    ChannelInfoListView,
    TestResultListView,
    ConfigInfoListView,
    RunResultListView,
    TimeDeltaListView,
    RouterListView
)

from .restAPI import (
    mainTopCntAPI, mainInfoFlagAPI, mainTaskAPI, mainStatusAPI,
    domainTreeAPI,
    ChannelListViewAPI, channelPaginatorAPI, channelInfoAPI,
    TestResultListViewAPI,
    ConfigListViewAPI, configPaginatorAPI,
    testAPI, testResultAPI, taskRunAPI, resetAPI, configCodeAPI, configUseCntAPI,
    RunResultListViewAPI, runResultPaginatorAPI, errorInfoAPI,
    TimeDeltaListViewAPI,
    RouterListViewAPI,
)

cache_time_out = 60 * 3

urlpatterns = patterns('',
                       url(r'^main/$', cache_page(cache_time_out)(MainView.as_view()), name='main'),
                       url(r'^debug/$', DebugView.as_view(), name='debug'),
                       url(r'^domainTree/$', DomainTreeView.as_view(), name='domainTree'),
                       url(r'^channelInfoList/$', ChannelInfoListView.as_view(), name='channelInfoList'),
                       url(r'^testResultList/$', TestResultListView.as_view(), name='testResultList'),
                       url(r'^configInfoList/$', ConfigInfoListView.as_view(), name='configInfoList'),
                       url(r'^runResultList/$', RunResultListView.as_view(), name='runResultList'),
                       url(r'^timedeltaList/$', TimeDeltaListView.as_view(), name='timedeltaList'),
                       url(r'^routerList/$', RouterListView.as_view(), name='routerList'),

                       url(r'^mainTopCntAPI/$', mainTopCntAPI, name='mainTopCntAPI'),
                       url(r'^mainInfoFlagAPI/$', mainInfoFlagAPI, name='mainInfoFlagAPI'),
                       url(r'^mainTaskAPI/$', mainTaskAPI, name='mainTaskAPI'),
                       url(r'^mainStatusAPI/$', mainStatusAPI, name='mainStatusAPI'),

                       url(r'^domainTreeAPI/$', domainTreeAPI, name='domainTreeAPI'),

                       url(r'^channelListAPI/$', ChannelListViewAPI.as_view(), name='channelListAPI'),
                       url(r'^channelPaginatorAPI/$', channelPaginatorAPI, name='channelPaginatorAPI'),
                       url(r'^channelInfoAPI/$', channelInfoAPI, name='channelInfoAPI'),

                       url(r'^testResultListAPI/$', TestResultListViewAPI.as_view(), name='testResultListAPI'),

                       url(r'^configListAPI/$', ConfigListViewAPI.as_view(), name='configlListAPI'),
                       url(r'^configPaginatorAPI/$', configPaginatorAPI, name='configPaginatorAPI'),

                       url(r'^runResultListAPI/$', RunResultListViewAPI.as_view(), name='runResultListAPI'),
                       url(r'^runResultPaginatorAPI/$', runResultPaginatorAPI, name='runResultPaginatorAPI'),
                       url(r'^errorInfoAPI/$', errorInfoAPI, name='errorInfoAPI'),

                       url(r'^timedeltaAPI/$', TimeDeltaListViewAPI.as_view(), name='timedeltaAPI'),

                       url(r'^routerListAPI/$', RouterListViewAPI.as_view(), name='routerListAPI'),

                       url(r'^testAPI/$', testAPI, name='testAPI'),
                       url(r'^testResultAPI/$', testResultAPI, name='testResultAPI'),
                       url(r'^taskRunAPI/$', taskRunAPI, name='taskRunAPI'),
                       url(r'^resetAPI/$', resetAPI, name='resetAPI'),
                       url(r'^configCodeAPI/$', configCodeAPI, name='configCodeAPI'),
                       url(r'^configUseCntAPI/$', configUseCntAPI, name='configUseCntAPI'),
                       )
