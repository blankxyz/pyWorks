from django.conf.urls import patterns, url
from allsite import views

urlpatterns = patterns('',
                       url(r'^$', views.login, name='login'),
                       url(r'^login/$', views.login, name='login'),
                       url(r'^regist/$', views.regist, name='regist'),
                       url(r'^logout/$', views.logout, name='logout'),
                       url(r'^index/$', views.index, name='index'),

                       url(r'^allsite/$', views.allsite, name='allsite'),
                       url(r'^domainlist/$', views.domainlist, name='domainlist'),
                       url(r'^hubPageList/$', views.hubPageList, name='hubPageList'),
                       url(r'^detailList/$', views.detailList, name='detailList'),
                       url(r'^dashBoardCnt/$', views.dashBoardCnt, name='dashBoardCnt'),
                       url(r'^sitelistJson/$', views.sitelistJson, name='sitelistJson'),

                       url(r'^drawHubPageRank/$', views.drawHubPageRank, name='drawHubPageRank'),
                       url(r'^drawDomainRank/$', views.drawDomainRank, name='drawDomainRank'),
                       url(r'^drawHubPageTrend/$', views.drawHubPageTrend, name='drawHubPageTrend'),
                       url(r'^drawDetailTrend/$', views.drawDetailTrend, name='drawDetailTrend'),
                       url(r'^drawCrawlTimePart/$', views.drawCrawlTimePart, name='drawCrawlTimePart'),
                       url(r'^drawNewDomain/$', views.drawNewDomain, name='drawNewDomain'),
                       url(r'^drawDetailList/$', views.drawDetailList, name='drawDetailList'),
                       url(r'^urlList/$', views.urlList, name='urlList'),
                       url(r'^domainModify/$', views.domainModify, name='domainModify'),
                       )
