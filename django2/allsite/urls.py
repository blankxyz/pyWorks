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
                       url(r'^detailPageList/$', views.detailPageList, name='detailPageList'),
                       url(r'^newDomainList/$', views.newDomainList, name='newDomainList'),
                       url(r'^sitelistJson/$', views.sitelistJson, name='sitelistJson'),
                       )
