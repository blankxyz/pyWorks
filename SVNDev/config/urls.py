from django.conf.urls import url, patterns
from django.views.generic import RedirectView
# from django.views.generic.simple import redirect_to

from . import views
from config import rest_api


urlpatterns = [
    url(r'^$', views.select_configs, name='select'),
    url(r'^groups/$', views.config_groups_list, name='group'),
    url(r'^groups/(\d+)/$', views.config_group_change, name='each_change'),
    url(r'^groups/add/$', views.config_group_add, name='each_add'),
    url(r'^groups/delete/$', views.config_group_delete, name='each_delete'),
    url(r'^groups/api/$', rest_api.ConfigGroupsListApi.as_view(), name='config_groups_list_api'),

    url(r'^add/$', views.add_config, name='add_config'),
    url(r'^(\d+)/change/$', views.change_config, name='change_config'),
    url(r'^(\d+)/change/history/$', views.change_history, name='change_history'),
    url(r'^diff/$', views.change_config_diff, name='change_diff'),

    # 时间差统计
    url(r'^delta/news/domain/domain$', views.news_user_timedelta_view, name='news_user_timedelta_view'),
    url(r'^delta/news/domain/domain/search/$', views.news_user_timedelta_view, name='news_user_timedelta_view_search'),
    url(r'^delta/news/domain/users/$', views.news_all_user_timedelta_view, name='news_all_user_timedelta_view'),
    url(r'^delta/news/domain/users/search/$', views.news_all_user_timedelta_view, name='news_all_user_timedelta_view_search'),
    url(r'^delta/news/config/config/$', views.config_timedelta_view, name='config_timedelta_view'),
    url(r'^delta/news/config/config/search/$', views.config_timedelta_view, name='config_timedelta_view_search'),
    url(r'^delta/news/config/groupsexclude/$', views.config_groupsexclude_delta, name='config_groupsexclude_delta'),
    url(r'^delta/news/config/groupsexclude/search/$', views.config_groupsexclude_delta, name='config_groupsexclude_delta_search'),

    url(r'^delta/forums/domain/domain$', views.forums_user_timedelta_view, name='forums_user_timedelta_view'),
    url(r'^delta/forums/domain/domain/search/$', views.forums_user_timedelta_view, name='forums_user_timedelta_view_search'),
    url(r'^delta/forums/domain/users/$', views.forums_all_user_timedelta_view, name='forums_all_user_timedelta_view'),
    url(r'^delta/forums/domain/users/search/$', views.forums_all_user_timedelta_view, name='forums_all_user_timedelta_view_search'),
    url(r'^delta/forums/config/config/$', views.forums_config_timedelta_view, name='forums_config_timedelta_view'),
    url(r'^delta/forums/config/config/search/$', views.forums_config_timedelta_view, name='forums_config_timedelta_view_search'),

    url(r'^delta/alldomains/$', views.all_domains_timedelta_view, name='all_domains_timedelta_view'),
    url(r'^delta/alldomains/search/$', views.all_domains_timedelta_view, name='all_domains_timedelta_view_search'),
    url(r'^delta/allconfigs/$', views.all_configs_timedelta_view, name='all_configs_timedelta_view'),
    url(r'^delta/allconfigs/search/$', views.all_configs_timedelta_view, name='all_configs_timedelta_view_search'),

    # 时间差排除
    url(r'^delta/exclude/(\w+)/(\w+)/(\w+)/$', views.exclude_manage, name='exclude_manage'),
    url(r'^delta/excludegroups/(\w+)/(\w+)/(\w+)/$', views.exclude_groups_manage, name='exclude_groups_manage'),

    # 时间差总数
    # url(r'^delta/sum/(\w+)/$', views.sum_deltas, name='sum_deltas'),
    url(r'^delta/basesum/(\w+)/(\w+)/(\w+)/(\S*)/$', views.base_sum_deltas, name='base_sum_deltas'),
    url(r'^delta/ranksum/(\w+)/(\w+)/(\w+)/(\S*)/(\d+)/$', views.rank_sum_deltas, name='rank_sum_deltas'),
    url(r'^delta/customsum/(\w+)/(\w+)/(\w+)/(\S*)/$', views.custom_sum_deltas, name='custom_sum_deltas'),
    url(r'^delta/searchsum/(\w+)/(\w+)/(\w+)/(\S*)/$', views.search_sum_deltas, name='search_sum_deltas'),

    # 时间差历史
    url(r'^delta/history/news/(\w+)/(\w+)/(\S*)/$', views.time_delta_history_view, name='time_delta_history_view'),

    url(r'^delta/history/sum/(\w+)/(\w+)/(\w+)/$', views.sum_delta_history_view, name='sum_delta_history_view'),
    url(r'^delta/history/searchsum/(\w+)/(\w+)/(\w+)/$', views.search_sum_delta_history_view, name='search_sum_delta_history_view'),

    # 其他零碎功能
    url(r'^spider/monitor/$', views.spider_groups_monitor, name='spider_groups_monitor'),
    url(r'^config/urlsearch/$', views.config_url_search, name='config_url_search'),

    url(r'^test/$', views.select_multiply, name='test'),

]
