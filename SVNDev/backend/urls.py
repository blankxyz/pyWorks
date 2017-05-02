"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from backend_admin import views as backend_admin_view

handler403 = backend_admin_view.perm_deny
handler404 = backend_admin_view.page_no

urlpatterns = [
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, }),
    url(r'', include('backend_admin.urls', namespace='backend_admin'), ),
    url(r'^config/', include('config.urls', namespace='config'), ),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^allsite/', include('allsite.urls', namespace='allsite'), ),
    url(r'^comments/', include('comments.urls', namespace='comments'), ),
    url(r'^channels/', include('channelConfigMgr.urls', namespace='channels'), ),
]
