from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter

from . import views
from .views import DomainListView, DomainListViewAPI

router = DefaultRouter()
# router.register(r'domainListApi', views.DomainListViewSet)

urlpatterns = patterns('',
                       url(r'^main/$', views.main, name='main'),

                       url(r'^crawlTimes/$', views.crawlTimesMain, name='crawlTimes'),

                       # url(r'^domainList/$', views.domainList, name='domainList'),
                       url(r'^domainList/$', DomainListView.as_view(), name='domainList'),
                       url(r'^domainListAPI/$', DomainListViewAPI.as_view(), name='domainListAPI'),

                       url(r'^hubPageList/$', views.hubPageList, name='hubPageList'),
                       url(r'^detailList/$', views.detailList, name='detailList'),
                       url(r'^getDetailDialogInfo/$', views.getDetailDialogInfo, name='getDetailDialogInfo'),
                       url(r'^dashBoardTopCnt/$', views.dashBoardTopCnt, name='dashBoardTopCnt'),

                       url(r'^drawHubPageRank/$', views.drawHubPageRank, name='drawHubPageRank'),
                       url(r'^drawDomainRank/$', views.drawDomainRank, name='drawDomainRank'),
                       url(r'^drawHubPageTrend/$', views.drawHubPageTrend, name='drawHubPageTrend'),
                       url(r'^drawDetailTrend/$', views.drawDetailTrend, name='drawDetailTrend'),
                       url(r'^drawCrawlTimePart/$', views.drawCrawlTimePart, name='drawCrawlTimePart'),
                       url(r'^drawNewDomain/$', views.drawNewDomain, name='drawNewDomain'),
                       url(r'^drawCrawlUsed/$', views.drawCrawlUsed, name='drawCrawlUsed'),
                       url(r'^domainModify/$', views.domainModify, name='domainModify'),
                       )
