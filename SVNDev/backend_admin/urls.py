from django.conf.urls import url, patterns
from . import views
from django.views.generic import RedirectView

# from django.views.generic.simple import redirect_to

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^changepassword$', views.change_password, name='change_password'),
    url(r'^createuser/$', views.create_user, name='create_user', ),
    url(r'^admin/backend_admin/user/(\d+)/password$', views.change_user_password, name='change_user_password', ),
    url(r'^admin/backend_admin/user/(\d+)/$', views.change_user, name='change_user', ),
    url(r'^admin/backend_admin/user/add/$', RedirectView.as_view(url='/createuser'),),
    # url(r'^admin/backend_admin/user/\d/$', RedirectView.as_view(url='/changeuser'),),

    url(r'^duplicate_username$', views.username_duplicate_verify, name='duplicate_username'),
    url(r'^duplicate_email$', views.email_duplicate_verify, name='duplicate_email'),
]
