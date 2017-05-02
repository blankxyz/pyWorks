from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /polls/123123123
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.do_logout, name='logout'),
    url(r'^changepassword$', views.change_password, name='change_password'),
]
