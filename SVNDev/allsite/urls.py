# coding=utf-8
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views, restAPI
from .views import MainView, DomainListView, HubPageListView, QuickHubPageListView, DetailListView, \
    DetailLikenessListView, \
    DetailCorrectListView, CrawlTimesListView
from .restAPI import DomainListViewAPI, HubPageListViewAPI, QuickHubPageListViewAPI, DetailListViewAPI, \
    CrawlTimesListViewAPI, \
    TestListViewAPI, XPathViewAPI
from django.views.decorators.cache import cache_page

cache_time_out = 60 * 3

urlpatterns = patterns('',
                       # web View
                       url(r'^main/$', cache_page(cache_time_out)(MainView.as_view()), name='main'),
                       url(r'^domainList/$', DomainListView.as_view(), name='domainList'),
                       url(r'^hubPageList/$', HubPageListView.as_view(), name='hubPageList'),
                       url(r'^quickHubPageList/$', QuickHubPageListView.as_view(), name='quickHubPageList'),
                       url(r'^detailList/$', DetailListView.as_view(), name='detailList'),
                       url(r'^detailLikenessList/$', DetailLikenessListView.as_view(), name='detailLikenessList'),
                       url(r'^detailCorrectList/$', DetailCorrectListView.as_view(), name='detailCorrectList'),
                       url(r'^crawlTimes/$', CrawlTimesListView.as_view(), name='crawlTimes'),
                       # restful view API
                       url(r'^testListViewAPI/$', TestListViewAPI.as_view(), name='testListViewAPI'),
                       url(r'^domainListViewAPI/$', DomainListViewAPI.as_view(), name='domainListViewAPI'),
                       url(r'^hubPageListViewAPI/$', HubPageListViewAPI.as_view(), name='hubPageListViewAPI'),
                       url(r'^quickHubPageListViewAPI/$', QuickHubPageListViewAPI.as_view(),
                           name='quickHubPageListViewAPI'),
                       url(r'^detailListViewAPI/$', DetailListViewAPI.as_view(), name='detailListViewAPI'),
                       url(r'^crawlTimesListViewAPI/$', CrawlTimesListViewAPI.as_view(), name='crawlTimesListViewAPI'),
                       url(r'^xpathViewAPI/$', XPathViewAPI.as_view(), name='xpathViewAPI'),
                       # restful function API
                       url(r'^dashBoardTopCntAPI/$', cache_page(cache_time_out)(restAPI.dashBoardTopCntAPI),
                           name='dashBoardTopCntAPI'),
                       url(r'^drawHubPageRankAPI/$', cache_page(cache_time_out)(restAPI.drawHubPageRankAPI),
                           name='drawHubPageRankAPI'),
                       url(r'^drawDomainRankAPI/$', cache_page(cache_time_out)(restAPI.drawDomainRankAPI),
                           name='drawDomainRankAPI'),
                       url(r'^drawDomainSearchCategoryAPI/$',
                           cache_page(cache_time_out)(restAPI.drawDomainSearchCategoryAPI),
                           name='drawDomainSearchCategoryAPI'),
                       url(r'^drawHubPageTrendAPI/$', cache_page(cache_time_out)(restAPI.drawHubPageTrendAPI),
                           name='drawHubPageTrendAPI'),
                       url(r'^drawDetailTrendAPI/$', cache_page(cache_time_out)(restAPI.drawDetailTrendAPI),
                           name='drawDetailTrendAPI'),
                       url(r'^mainDetailLikenessAPI/$', cache_page(cache_time_out)(restAPI.mainDetailLikenessAPI),
                           name='mainDetailLikenessAPI'),
                       url(r'^mainDetailTop100API/$', restAPI.mainDetailTop100API, name='mainDetailTop100API'),
                       url(r'^drawCrawlTimePartAPI/$', cache_page(cache_time_out)(restAPI.drawCrawlTimePartAPI),
                           name='drawCrawlTimePartAPI'),
                       url(r'^drawNewDomainAPI/$', cache_page(cache_time_out)(restAPI.drawNewDomainAPI),
                           name='drawNewDomainAPI'),
                       url(r'^drawCrawlUsedAPI/$', cache_page(cache_time_out)(restAPI.drawCrawlUsedAPI),
                           name='drawCrawlUsedAPI'),

                       url(r'^getDomainSearchCntAPI/$', restAPI.getDomainSearchCntAPI, name='getDomainSearchCntAPI'),
                       url(r'^getHubPageSearchCntAPI/$', restAPI.getHubPageSearchCntAPI, name='getHubPageSearchCntAPI'),
                       url(r'^getDetailDialogInfoAPI/$', restAPI.getDetailDialogInfoAPI, name='getDetailDialogInfoAPI'),
                       url(r'^getDetailSearchCntAPI/$', restAPI.getDetailSearchCntAPI, name='getDetailSearchCntAPI'),
                       url(r'^getDetailPartCntAPI/$', restAPI.getDetailPartCntAPI, name='getDetailPartCntAPI'),
                       url(r'^setDetailCorrectInfoAPI/$', restAPI.setDetailCorrectInfoAPI,
                           name='setDetailCorrectInfoAPI'),
                       url(r'^getMatchDetailUrlAPI/$', restAPI.getMatchDetailUrlAPI, name='getMatchDetailUrlAPI'),
                       )
