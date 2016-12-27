"""weibo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from appWeibo.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, 'users')
router.register(r'lists', ListViewSet, 'lists')
router.register(r'daily', DailyRecordViewSet, 'daily')
router.register(r'log', LogViewSet, 'log')
router.register(r'redis', RedisViewSet, 'redis')
router.register(r'spider', SpiderViewSet, 'spider')


# router.register(r'status', StatusViewSet,'appWeibo')

urlpatterns = router.urls

# router.register(r'groups', views.GroupViewSet)

# router.register(r'user',views.UserViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
# urlpatterns = [
#     url(r'^', include(router.urls)),
#     # url(r'^', UserViewSet.as_view(), name='api-nosql'),
#     # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
# ]
