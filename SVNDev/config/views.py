# coding=utf-8
import os
import re
import logging
import json

from django.http import JsonResponse, HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import Group
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

import arrow
import pysvn

from backend_admin.models import *
from backend_admin import models

from config.forms import *
from config.models import *
from config.db_driver import *
from config.db_driver import global_args as db_args

logget = logging.getLogger('backend_admin.views')

config_messages = {
    'config_exist': '您添加配置文件已存在，请不要再次添加！',
    'svn_repository_error': 'svn版本控制有误，请联系管理员',
}
global_args = {
    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
}

config_store_file = './Public/configs/'
config_store_path = os.path.join(settings.BASE_DIR, 'Public', 'configs')
tmp_store_path = os.path.join(settings.BASE_DIR, 'Public', 'tmp')


# 检测配置存储文件夹及pysvn临时存储文件夹是否存在
def dir_exist(dir_path):
    '''
    检测配置存储文件夹及pysvn临时存储文件夹是否存在
    :param dir_path:
    :return:
    '''
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# pysvn登录svn使用
def get_login(realm, username, may_save):
    '''
    pysvn登录svn使用
    :param realm:
    :param username:
    :param may_save:
    :return:
    '''
    return True, 'backend', 'abc123', True


# pysvn初始化和登录svn
client = pysvn.Client()
client.callback_get_login = get_login


# Create your views here.


# 所有配置展示
@login_required
@permission_required('config.view_config')
@cache_page(5)
def select_configs(request):
    '''
    所有配置展示
    :param request:
    :return:
    '''
    model_verbose_name = '配置'
    app_label = 'config'
    model_name = 'Config'
    model_list_fields = ['ID', '网站名称', '网站域名', '配置名称', '上传人', '上传时间', '操作']
    user = User.objects.get(pk=request.user.pk)
    # manager_groups = user.userconfigmanagerlevel_set.all()
    if request.user.is_superuser == 1 or Group.objects.get(name='配置主管') in user.groups.all():
        config_all = Config.objects.all()
    else:
        config_user_list = []
        config_user_list.extend(User.objects.filter(is_active=0))
        each_groups = user.userconfigeach_set.all()
        if len(each_groups) > 0:
            for j in each_groups:
                config_user_list.extend(
                    User.objects.filter(userconfigeach__group_config_each_id=j.group_config_each_id))
            config_user_list = list(set(config_user_list))
            config_all = Config.objects.filter(user__in=config_user_list)
        else:
            config_user_list.append(user)
            config_all = Config.objects.filter(user__in=config_user_list)
    limit = 20
    paginator = Paginator(config_all.order_by('-id'), limit)
    page = request.GET.get('page')
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)

    return render(request, 'config/config_list.html', locals())


# 配置管理组列表
@login_required
@permission_required('backend_admin.view_groupconfigeach', raise_exception=True)
def config_groups_list(request):
    '''
    配置管理组列表
    :param request:
    :return:
    '''
    groups = GroupConfigEach.objects.all()
    return render(request, 'config/config_group.html', locals())
    # return redirect('/admin/backend_admin/groupconfigeach/')


# 修改配置管理组
@login_required
@permission_required('backend_admin.change_groupconfigeach')
def config_group_change(request, group_id):
    '''
    修改配置管理组
    :param request:
    :param group_id: 配置管理组ID
    :return:
    '''
    change = 1
    group = GroupConfigEach.objects.get(pk=group_id)
    users = User.objects.filter(userconfigeach__group_config_each_id=group_id)
    data = {'groups_name': group.name, 'users': users}
    form = ConfigEachForm(initial=data)
    if request.method == 'POST':
        form = ConfigEachForm(request.POST, initial=data)
        if form.is_valid():
            if form.has_changed():
                for i in form.changed_data:
                    if i == 'users':
                        users = form.cleaned_data['users']
                        UserConfigEach.objects.filter(group_config_each=group).delete()
                        if len(users) > 1:
                            for user in users:
                                user_config_each = UserConfigEach(group_config_each=group, user=user)
                                user_config_each.save()
                    else:
                        setattr(group, 'name', form.cleaned_data[i])

                # user_permissions_list = request.POST.getlist('checkbox_permission')
                # for permission in user_permissions_list:
                #     user_permission = Permission.objects.get(name=permission)
                #     user.user_permissions.add(user_permission)
                group.save()
                data = {'groups_name': group.name, 'users': users}
                messages.success(request, '修改成功')
                return redirect(reverse('config:each_change', args=(group_id,)))
        else:
            messages.error(request, '数据输入有误')
    return render(request, 'config/each_form.html', locals())


# 增加配置管理组
@login_required
@permission_required('backend_admin.add_groupconfigeach')
def config_group_add(request):
    '''
    增加配置管理组
    :param request:
    :return:
    '''
    form = ConfigEachForm()
    if request.method == 'POST':
        form = ConfigEachForm(request.POST)
        if form.is_valid():
            groups_name = form.cleaned_data['groups_name']
            users = form.cleaned_data['users']
            create_user = request.user
            group_config_each_create = GroupConfigEach(name=groups_name, user=create_user)
            group_config_each_create.save()
            group_id = group_config_each_create.pk
            if len(users) > 1:
                for user in users:
                    user_config_each = UserConfigEach(group_config_each=group_config_each_create, user=user)
                    user_config_each.save()
            messages.success(request, '添加成功')
            return redirect(reverse('config:each_add'))
        else:
            messages.error(request, '数据输入有误')
    return render(request, 'config/each_form.html', locals())


# 删除配置管理组
@login_required
@permission_required('backend_admin.delete_groupconfigeach')
def config_group_delete(request):
    '''
    删除配置管理组
    :param request:
    :return:
    '''
    if request.method == 'POST':
        groups_list = request.POST.getlist('td_checkbox')
        if len(groups_list) == 0:
            messages.success(request, '请选择要删除的选项')
        else:
            for i in groups_list:
                GroupConfigEach.objects.filter(pk=i).delete()
            messages.success(request, '删除成功')
    else:
        messages.error(request, '数据输入有误')
    return redirect(reverse('config:group'))


# 增加配置
@login_required
@permission_required('config.add_config', raise_exception=True)
@cache_page(0)
def add_config(request):
    '''
    增加配置
    :param request:
    :return:
    '''
    dir_exist(config_store_file)
    form = ConfigForm()
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            config = Config(webname=form.cleaned_data['webname'], url=form.cleaned_data['url'],
                            webtype=form.cleaned_data['webtype'])

            store_path = config_store_path

            config_file = request.FILES.get('config_file')
            text = request.POST.get('code').replace('\r', '')

            file_name = os.path.join(store_path, config_file.name)
            if os.path.exists(file_name):
                messages.warning(request, config_messages['config_exist'])
                return render(request, 'config/add.html', locals())
                # return redirect(reverse('config:add_config'))

            with open(file_name, 'w', encoding='utf-8') as fc:
                fc.write(text)
                fc.close()
            try:
                entry_log = client.log(store_path)
            except Exception:
                try:
                    client.checkout('svn://192.168.16.223:3690/backend', store_path)
                except Exception:
                    messages.error(request, config_messages['svn_repository_error'])
                    return render(request, 'config/add.html', locals())
            svn_message = 'author：%s , add %s' % (request.user.nickname, config_file.name)
            client.add(file_name)
            client.checkin([file_name], svn_message)
            entry_log = client.log(file_name)
            # 获取单个文件某个版本的内容
            # file_path = os.path.join(store_path, '1.txt')
            # entry_cat = client.cat(file_path, revision=pysvn.Revision(pysvn.opt_revision_kind.number, 1))
            config.savename = str(config_file.name)
            config.savepath = os.path.join(config_store_file, config_file.name)
            config.savetime = entry_log[-1].date
            config.filesize = os.path.getsize(file_name)
            config.author = request.user.nickname
            config.user = User.objects.get(id=request.user.id)
            config.save()
            return redirect(reverse('config:change_config', args=(config.id,)))

            # svn_log = list()
            # for info in entry_log:
            #     info_dict = {'revision': info.revision.number,
            #                  'author': info.author,
            #                  'message': info.message,
            #                  'date': arrow.Arrow.fromtimestamp(info.date).format(
            #                      arrow.Arrow.fromtimestamp(info.date).format('YYYY-MM-DD HH:mm:ss:SS'))
            #                  }
            #     svn_log.append(info_dict)

    return render(request, 'config/add.html', locals())


# 修改配置
@login_required
@permission_required('config.change_config')
def change_config(request, config_id):
    '''
    修改配置
    :param request:
    :param config_id:
    :return:
    '''
    change = 1
    config = Config.objects.get(id=config_id)
    name = config.savename
    file_name = os.path.join(config_store_path, name)
    config_id = config.id
    savetime = arrow.Arrow.fromtimestamp(config.savetime).format('YYYY-MM-DD HH:mm:ss:SS')

    if not os.path.exists(file_name):
        # 如果文件在本地不存在，从版本库更新
        try:
            client.update(config_store_path)
        except Exception:
            no_file_message = '本地和版本库都不存在此文件'
            messages.ERROR(no_file_message)
            return redirect(reverse('config:select'))
    else:
        # 如果文件在本地存在，版本库不存在，上传到版本库
        if not os.path.exists(os.path.join(config_store_path, '.configs')):
            client.checkout('svn://192.168.16.223:3690/backend', config_store_path)

        try:
            entry_log = client.log(file_name)
        except Exception:
            svn_message = 'author：%s , add %s' % (config.author, name)
            client.add(file_name)
            client.checkin([file_name], svn_message)

    # with open(file_name, 'rb') as fc:
    #     code = fc.read()
    #     fc.close()

    if request.method == 'POST':
        change_message = request.POST.get('change_config_message')
        text = request.POST.get('code').replace('\r', '')
        with open(file_name, 'w', encoding='utf-8') as fc:
            fc.write(text)
            fc.close()

        svn_message = 'author：%s , change： %s' % (request.user.nickname, change_message)
        client.checkin([file_name], svn_message)

    entry_log = client.log(file_name)
    svn_log = list()
    for info in entry_log:
        info_dict = {'revision': info.revision.number,
                     'author': info.author,
                     'message': info.message,
                     'date': arrow.Arrow.fromtimestamp(info.date).format(
                         arrow.Arrow.fromtimestamp(info.date).format('YYYY-MM-DD HH:mm:ss:SS'))
                     }
        svn_log.append(info_dict)
    code = client.cat(file_name, revision=pysvn.Revision(pysvn.opt_revision_kind.number, svn_log[0]['revision']))
    # diff_text = client.diff(tmp_path=tmp_store_path, url_or_path=file_name,
    #                         revision1=pysvn.Revision(pysvn.opt_revision_kind.number, svn_log[1]['revision']),
    #                         revision2=pysvn.Revision(pysvn.opt_revision_kind.number, svn_log[0]['revision']),
    #                         )
    return render(request, 'config/change_config.html', locals())


# 代码修改历史
@login_required
@permission_required('config.change_config')
def change_history(request, config_id):
    '''
    代码修改历史
    :param request:
    :param config_id:
    :return:
    '''
    config = Config.objects.get(id=config_id)
    name = config.savename
    file_name = os.path.join(config_store_path, name)

    entry_log = client.log(file_name)
    svn_log = list()
    for info in entry_log:
        info_dict = {'revision': info.revision.number,
                     'author': info.author,
                     'message': info.message,
                     'date': arrow.Arrow.fromtimestamp(info.date).format('YYYY-MM-DD HH:mm:ss:SS')
                     }
        svn_log.append(info_dict)
    return render(request, 'config/change_history.html', locals())


# 代码版本比较
@login_required
@permission_required('config.change_config')
def change_config_diff(request):
    '''
    代码版本比较
    :param request:
    :return:
    '''
    if request.method == 'POST':
        name = request.POST.get('name')
        v1 = request.POST.get('v1')
        v2 = request.POST.get('v2')
        # config = Config.objects.get(id=config_id)
        # file_name = os.path.join(config_store_path, config.savename)
        file_name = os.path.join(config_store_path, name)
        dir_exist(tmp_store_path)
        if v2 == 'none':
            diff_text = client.cat(file_name, revision=pysvn.Revision(pysvn.opt_revision_kind.number, v1))
            diff_text = diff_text.decode('utf-8').split('\n')
        else:
            diff_text = client.diff(tmp_path=tmp_store_path, url_or_path=file_name,
                                    revision1=pysvn.Revision(pysvn.opt_revision_kind.number, v2),
                                    revision2=pysvn.Revision(pysvn.opt_revision_kind.number, v1),
                                    )
            diff_text = str(diff_text).split('\r\n')
        # diff_dict = {'content': diff_text}
        return JsonResponse(diff_text, safe=False)


# 计算已有的时间差数据的总数据
def search_delta_result(time_deltas):
    '''
    计算已有的时间差数据的总数据
    :param time_deltas: 从数据库获取的时间差字典数据
    :return:
        {
         'total': 22, 876, 129,
         'data': {'d1': {'percent': '8.7%', 'cnt': 1999450, 'width': ''},
                  'd2': {'percent': '2.1%', 'cnt': 489652, 'width': ''},
                  'd3': {'percent': '3.3%', 'cnt': 748103, 'width': ''},
                 }
    },
    '''
    sum_search = dict()
    total = 0
    data = dict()
    time_datas = list()
    for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
        time_level = 'd' + str(i)
        data[time_level] = dict()

    for single in time_deltas:
        total_single = int(''.join(single['total'].split(',')))
        if total_single > 0:
            total += total_single

        for i in range(1, 10):  # 时间差hash time_1_2017-03-24_d2
            time_level = 'd' + str(i)
            try:
                data[time_level]['cnt'] += single['data'][time_level]['cnt']
            except Exception:
                data[time_level]['cnt'] = single['data'][time_level]['cnt']
    if total != 0:
        for i in range(1, 10):
            time_level = 'd' + str(i)
            p = data[time_level]['cnt'] / total
            data[time_level]['percent'] = '{:.2f}'.format(p * 100) + '%'
            data[time_level]['width'] = ''
    sum_search['data'] = data
    sum_search['total'] = total

    result = dict()
    result['sum_search'] = sum_search
    return result


# 采集时间差通用函数，用来处理一些相同的参数和动作
def config_time_delta(request, timedelta_func, kwargs):
    '''
    采集时间差通用函数，用来处理一些相同的参数和动作
    :param request:
    :param timedelta_func: 获取时间差数据的函数
    :param kwargs: 其他一些参数
    :return:
    '''
    kwargs['url_exclude'] = reverse('config:exclude_manage',
                                    args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'],))

    kwargs['url_sum'] = reverse('config:base_sum_deltas',
                                args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'], kwargs['date']))
    kwargs['url_sum_history'] = reverse('config:sum_delta_history_view',
                                        args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'],))
    kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].__dict__.get(kwargs['exclude_field'])
    kwargs['search_arg_name'] = '域名'
    kwargs['exclude_groups_configs_num'] = 0

    if kwargs['rank_tag'] == 1 and kwargs['time_delta_rank_selected'] > 0:
        kwargs['url_rank_sum'] = reverse('config:rank_sum_deltas',
                                         args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'], kwargs['date'],
                                               kwargs['time_delta_rank_selected']))
        kwargs['all_domains'] = all_nums_rank(kwargs['time_hash_basic'].format(kwargs['date'], kwargs['sum_hash_d']),
                                          kwargs['search_arg'])
    elif kwargs['delta_custom_tag'] == 1:
        result_delta_custom = custom_all_sums(kwargs['time_hash_basic'], kwargs['search_arg'], kwargs['date'],
                                              kwargs['time_delta_rank_begin'], kwargs['time_delta_rank_end'])
        kwargs['all_domains'] = result_delta_custom['domains']

        kwargs['nums_delta_custom'] = result_delta_custom['nums']
        kwargs['url_custom_sum'] = reverse(
            'config:custom_sum_deltas',
            args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'], kwargs['date']))
    else:
        kwargs['all_domains'] = all_nums(kwargs['time_delta_zset'], kwargs['date'])

    # 排除域名或配置的处理
    if kwargs['user_deploy_delta_exclude'] not in ['', None]:
        kwargs['delta_domain_exclude'] = re.split('\s+', kwargs['user_deploy_delta_exclude'])
    else:
        kwargs['delta_domain_exclude'] = []
    if kwargs['domain_exclude_add'] != '':
        for i in kwargs['domain_exclude_add']:
            if i not in kwargs['delta_domain_exclude']:
                kwargs['delta_domain_exclude'].append(i)
        kwargs['user_deploy_delta_exclude'] = ' '.join(kwargs['delta_domain_exclude'])
        kwargs['user_deploy_delta'].__dict__.update({kwargs['exclude_field']: kwargs['user_deploy_delta_exclude']})
        kwargs['user_deploy_delta'].save()
    exclude_list = kwargs['delta_domain_exclude']
    kwargs['exclude_list'] = exclude_list
    kwargs['exclude_list_num'] = len(exclude_list)

    if kwargs['domains'] is not None:
        kwargs['domains'] = list(set(kwargs['domains']))
        if request.method == 'POST' and kwargs['search_arg'] == 'domain':
            # 域名模糊搜索
            kwargs['domains'] = list(
                i['domain'] for i in DomainsAll.objects.filter(domain__contains=kwargs['domains'][0]).values('domain')
            )
        kwargs['all_domains_list'] = kwargs['domains']
    else:
        kwargs['all_domains_list'] = kwargs['all_domains']
    kwargs['all_num_org'] = kwargs['all_domains']

    if request.method == 'POST' and kwargs['search_tag'] == 1:
        kwargs['url_sum_history'] = reverse('config:search_sum_delta_history_view',
                                            args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'],))
        search_domains = list()
        if len(kwargs['all_domains_list']) > 0:
            # 从b_conf取出的配置与从redis中取出的配置进行比较
            for dm in kwargs['all_num_org']:
                if dm.decode('utf-8') in kwargs['all_domains_list']:
                    search_domains.append(dm)
                if dm.decode('utf-8') == kwargs['all_domains_list'][-1]:
                    break
        kwargs['all_domains_list'] = search_domains
        with open('delta_search_domains.txt', 'w', encoding='utf-8') as fd:
            for i in kwargs['all_domains_list']:
                fd.write(i.decode('utf-8') + ',')
            fd.close()
        kwargs['url_search_sum'] = reverse(
            'config:search_sum_deltas',
            args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'], kwargs['date']))

    kwargs['all_num'] = len(kwargs['all_domains_list'])
        # kwargs['all_num'] = len(time_deltas)
        # paginator = Paginator(time_deltas, limit)
        # page = request.GET.get('page')
        # try:
        #     result = paginator.page(page)
        # except PageNotAnInteger:
        #     result = paginator.page(1)
        # except EmptyPage:
        #     result = paginator.page(paginator.num_pages)
        # result1 = result

    if kwargs['search_arg'] == 'config':
        kwargs['select_options1'] = ['配置', '分组']
        kwargs['search_arg_name'] = '配置'

        kwargs['url_exclude_groups'] = reverse('config:exclude_groups_manage',
                                               args=(kwargs['url_arg'], kwargs['search_arg'], kwargs['args'],))

        kwargs['exclude_groups_field'] = kwargs['exclude_field'] + '_group'
        kwargs['user_delta_config_groups_exclude'] = kwargs['user_deploy_delta'].__dict__.get(
            kwargs['exclude_groups_field'])
        kwargs['exclude_groups_num'] = 0

        # 排除分组的处理
        if kwargs['user_delta_config_groups_exclude'] not in ['', None]:
            kwargs['delta_config_groups_exclude'] = re.split('\s+', kwargs['user_delta_config_groups_exclude'])
        else:
            kwargs['delta_config_groups_exclude'] = []
        if len(kwargs['groups_exclude_add']) > 0:
            # 提交的排除分组的处理
            for i in kwargs['groups_exclude_add']:
                if i not in kwargs['delta_config_groups_exclude']:
                    kwargs['delta_config_groups_exclude'].append(i)
            kwargs['user_delta_config_groups_exclude'] = ' '.join(kwargs['delta_config_groups_exclude'])
            kwargs['user_deploy_delta'].__dict__.update(
                {kwargs['exclude_groups_field']: kwargs['user_delta_config_groups_exclude']})
            kwargs['user_deploy_delta'].save()
        exclude_config_groups_list = kwargs['delta_config_groups_exclude']
        # kwargs['exclude_config_groups_list_num'] = len(exclude_config_groups_list)

        if kwargs['args'] == 'groupsexclude':
            # 去除巡查、海外两个分组的内容
            gid_list = ['89', '21']
            exclude_config_groups_list += gid_list

        if len(exclude_config_groups_list) > 0:
            kwargs['delta_config_groups_exclude_list'] = list()
            for i in exclude_config_groups_list:
                config_group_obj = BGroup.objects.get(id=int(i))
                kwargs['spider_config_groups'].remove(config_group_obj)
                kwargs['delta_config_groups_exclude_list'].append(config_group_obj)

            exclude_list_groups = config_ids_get(tuple(exclude_config_groups_list))
            exclude_groups_configs = list()
            for i in exclude_list_groups:
                k = i.encode('utf-8')
                if k in kwargs['all_domains_list']:
                    kwargs['all_domains_list'].remove(k)
                    exclude_groups_configs.append(k)
            kwargs['exclude_groups_configs_num'] = len(exclude_groups_configs)

            # exclude_list = exclude_list + exclude_list_groups
            # kwargs['delta_domain_exclude'] = exclude_list
        kwargs['delta_config_groups_exclude_num'] = len(exclude_config_groups_list)

    limit = 20
    for i in exclude_list:
        k = i.encode('utf-8')
        if k in kwargs['all_domains_list']:
            kwargs['all_domains_list'].remove(k)
    if kwargs['search_arg'] == 'config':
        # if kwargs['search_tag'] == 1 and kwargs['id_rank_tag'] == 0:
        #     request.session['id_rank_configs'] = json.dumps(list(i.decode('utf-8') for i in kwargs['all_domains_list']))
        if kwargs['id_rank_tag'] == -1:
            # kwargs['all_domains_list'] = json.loads(request.session['id_rank_configs'])
            kwargs['all_domains_list'] = list(sorted(kwargs['all_domains_list'], key=lambda x: int(x), reverse=True))
        elif kwargs['id_rank_tag'] == 1:
            # kwargs['all_domains_list'] = json.loads(request.session['id_rank_configs'])
            kwargs['all_domains_list'] = list(sorted(kwargs['all_domains_list'], key=lambda x: int(x), reverse=False))

    paginator = Paginator(kwargs['all_domains_list'], limit)
    page = request.GET.get('page')
    try:
        result1 = paginator.page(page)
    except PageNotAnInteger:
        result1 = paginator.page(1)
    except EmptyPage:
        result1 = paginator.page(paginator.num_pages)
    result = timedelta_func(kwargs['date'], kwargs['time_hash_basic'], result1.object_list)
    if kwargs['delta_custom_tag'] == 1:
        if page is None:
            page = 1
        delta_custom_result = dict()
        for k in result1.object_list:
            delta_custom_result[k] = kwargs['nums_delta_custom'][k]

        with open('delta_custom_domains.txt', 'w', encoding='utf-8') as fd:
            for i in kwargs['all_domains_list']:
                fd.write(i.decode('utf-8') + ',')
            fd.close()
    # 搜索框展示搜索的域名
    # if kwargs['domains'] is None:
    #     kwargs['domains'] = ''
    # else:
    #     kwargs['domains'] = ' '.join(kwargs['domains'])

    return render(request, 'config/time_delta.html', locals())


# 通用函数，获取时间差等参数
def delta_kwargs(request):
    '''
    获取时间差需要使用的通用参数
    :param request:
    :return:
    '''
    kwargs = dict()
    kwargs['select_options1_tag'] = 0
    kwargs['select_options1'] = ['域名']
    kwargs['search_tag'] = 0
    kwargs['search_tag_post'] = 0
    time_delta_rank_list = ['全部', '0-1', '1-2', '2-5', '5-15', '15-30', '30-60',
                            '60-120', '120-240', '超过240', '自定义']
    time_delta_rank_list1 = ['0', '1', '2', '5', '15', '30', '60', '120', '240', 'all']
    kwargs['time_delta_rank_list'] = time_delta_rank_list
    kwargs['time_delta_rank_list1'] = time_delta_rank_list1
    kwargs['time_delta_rank_selected'] = 0
    kwargs['time_delta_rank_len'] = len(time_delta_rank_list) - 1  # 确定时间差240所在位置，当为自定义时做其他处理
    kwargs['time_delta_rank_begin'] = 0
    kwargs['time_delta_rank_end'] = 0
    kwargs['rank_tag'] = 0
    kwargs['id_rank_tag'] = 0
    kwargs['delta_custom_tag'] = 0
    kwargs['spider_config_groups'] = [{'id': -1, 'groupname': '分组筛选'}]  # 所有包含数字的配置分组
    kwargs['url_add_args'] = ''  # ?page=2等参数
    for i in BGroup.objects.filter(status=1).order_by('groupname'):
        kwargs['spider_config_groups'].append(i)
    # kwargs['spider_config_groups'] = BGroup.objects.filter(status=1).order_by('groupname')
    kwargs['spider_config_groups_count'] = -1
    # 解决post的检索结果，进行分页之后，从第二页开始数据丢失的问题

    date = datetime.datetime.now().strftime('%Y-%m-%d')  # 尝试修复一直获取旧数据问题
    domains = None
    domain_exclude_add = ''
    groups_exclude_add = []

    if 'search' in request.get_full_path():
        kwargs['search_tag'] = 1
        if not request.method == 'POST':
            if 'search-persons-post' in request.session:
                request.POST = request.session['search-persons-post']
                request.method = 'POST'
        if request.method == 'POST':
            request.session['search-persons-post'] = request.POST
    if request.method == 'POST':
        # date = request.POST.get('datetime')
        kwargs['search_tag_post'] = tag = request.POST.get('tag')
        date = request.POST.get('date-begin')
        if tag == 'search':
            domains_original = request.POST.get('domains')
            domains = re.split('\s', domains_original.strip())
            spider_config_group = request.POST.get('spider-config-groups')
            if spider_config_group is not None:
                spider_config_group = int(spider_config_group)
            else:
                spider_config_group = -1
            if domains_original == '':
                if spider_config_group == -1:
                    kwargs['search_tag'] = 0
                    domains = None
                elif spider_config_group > -1:
                    # 通过配置搜索配置
                    kwargs['search_tag'] = 1
                    kwargs['select_options1_tag'] = 1
                    gid_list = (str(spider_config_group),)
                    domains = config_ids_get(gid_list)
                    kwargs['spider_config_groups_count'] = spider_config_group
        elif tag == 'exclude':
            checkbox_exclude_list = request.POST.getlist('exclude_check')
            domain_exclude_add = checkbox_exclude_list
        elif tag == 'exclude_group':
            kwargs['search_tag'] = 0
            groups_exclude_add = request.POST.getlist('spider-config-groups-exclude')
        elif tag == 'rank':
            kwargs['search_tag'] = 0
            kwargs['rank_tag'] = 1
            kwargs['sum_hash_d'] = request.POST.get('delta_ranks')
            kwargs['time_delta_rank_selected'] = int(kwargs['sum_hash_d'])
        elif tag == 'custom':
            kwargs['time_delta_rank_selected'] = kwargs['time_delta_rank_len']
            kwargs['search_tag'] = 0
            kwargs['delta_custom_tag'] = 1
            kwargs['time_delta_rank_begin'] = int(request.POST.get('time_delta_rank_begin'))
            kwargs['time_delta_rank_begin_time'] = time_delta_rank_list1[kwargs['time_delta_rank_begin'] - 1]
            kwargs['time_delta_rank_end'] = int(request.POST.get('time_delta_rank_end'))
            kwargs['time_delta_rank_end_time'] = time_delta_rank_list1[kwargs['time_delta_rank_end'] - 1]

    id_rank_tag = request.GET.get('idrank')
    rank_judge = request.GET.get('rankg')
    if id_rank_tag:
        kwargs['id_rank_tag'] = int(id_rank_tag)
        if rank_judge and int(rank_judge) == 1:
            if kwargs['id_rank_tag'] in [0, 1]:
                kwargs['id_rank_tag'] = -1
            else:
                kwargs['id_rank_tag'] = 1
    if kwargs['id_rank_tag'] != 0:
        url_idrank_add = '&idrank={0}'.format(kwargs['id_rank_tag'])
        kwargs['url_add_args'] += url_idrank_add
    try:
        user_deploy_delta = UserDeploy.objects.get(user_id=request.user.id)
    except Exception:
        user_deploy_delta = UserDeploy.objects.create(user_id=request.user.id)

    kwargs['domain_exclude_add'] = domain_exclude_add
    kwargs['groups_exclude_add'] = groups_exclude_add
    kwargs['date'] = date
    kwargs['domains'] = domains
    kwargs['user_deploy_delta'] = user_deploy_delta
    return kwargs


# 新闻-域名-对用户（入库）时间差
@login_required
def news_user_timedelta_view(request):
    '''
    新闻-域名-对用户（入库）时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '新闻-域名-入库时间差'
    kwargs['url_arg'] = 'news'
    kwargs['search_arg'] = 'domain'
    kwargs['args'] = 'domain'
    url = reverse('config:news_user_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:news_user_timedelta_view_search')
    kwargs['exclude_field'] = 'delta_domain_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_domain_exclude
    kwargs['time_hash_basic'] = db_args['news_time_hash_format']
    kwargs['time_delta_zset'] = db_args['news_user_zset']
    return config_time_delta(request, common_time_delta, kwargs)


# 新闻-域名-不去重用户时间差
@login_required
def news_all_user_timedelta_view(request):
    '''
    新闻-域名-不去重用户时间差
    :param request:
    :return:
    '''

    kwargs = delta_kwargs(request)

    kwargs['title'] = '新闻-域名-用户不去重'
    kwargs['url_arg'] = 'news'
    kwargs['search_arg'] = 'domain'
    kwargs['args'] = 'users'
    url = reverse('config:news_all_user_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:news_all_user_timedelta_view_search')
    kwargs['user'] = 1
    kwargs['exclude_field'] = 'delta_user_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_user_exclude
    kwargs['time_hash_basic'] = db_args['all_user_news_hash_format']
    kwargs['time_delta_zset'] = db_args['news_all_users_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def config_timedelta_view(request):
    '''
    配置，对上用户时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '新闻-配置-入库时间差'
    kwargs['url_arg'] = 'news'
    kwargs['search_arg'] = 'config'
    kwargs['args'] = 'config'
    url = reverse('config:config_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:config_timedelta_view_search')
    kwargs['config'] = 1
    kwargs['exclude_field'] = 'delta_config_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_config_exclude
    kwargs['time_hash_basic'] = db_args['news_time_hash_format']
    kwargs['time_delta_zset'] = db_args['news_config_zset']
    return config_time_delta(request, common_time_delta, kwargs)


# 新闻分组过滤时间差统计  首页巡查 89  海外21
@login_required
def config_groupsexclude_delta(request):
    '''
    配置，排除了海外、首页巡查两组配置的时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '新闻-配置-除巡查海外'
    kwargs['url_arg'] = 'news'
    kwargs['search_arg'] = 'config'
    kwargs['args'] = 'groupsexclude'
    url = reverse('config:config_groupsexclude_delta')
    kwargs['url'] = url
    kwargs['config'] = 1
    kwargs['url_search'] = reverse('config:config_groupsexclude_delta_search')
    kwargs['exclude_field'] = 'config_groups_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].config_groups_exclude
    kwargs['time_hash_basic'] = db_args['news_time_hash_format']
    kwargs['time_delta_zset'] = db_args['news_config_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def forums_user_timedelta_view(request):
    '''
    对用户时间差，域名
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '论坛-域名-入库时间差'
    kwargs['url_arg'] = 'forums'
    kwargs['search_arg'] = 'domain'
    kwargs['args'] = 'domain'
    url = reverse('config:forums_user_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:forums_user_timedelta_view_search')
    kwargs['exclude_field'] = 'forums_domain_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_domain_exclude
    kwargs['time_hash_basic'] = db_args['forums_time_hash_format']
    kwargs['time_delta_zset'] = db_args['forums_user_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def forums_all_user_timedelta_view(request):
    '''
    对用户时间差，域名
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '论坛-域名-用户不去重'
    kwargs['url_arg'] = 'forums'
    kwargs['search_arg'] = 'domain'
    kwargs['args'] = 'users'
    url = reverse('config:forums_all_user_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:forums_all_user_timedelta_view_search')
    kwargs['exclude_field'] = 'forums_user_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_domain_exclude
    kwargs['time_hash_basic'] = db_args['forums_all_user_hash_format']
    kwargs['time_delta_zset'] = db_args['forums_all_users_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def forums_config_timedelta_view(request):
    '''
    配置，对上用户时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '论坛-配置-入库时间差'
    kwargs['url_arg'] = 'forums'
    kwargs['search_arg'] = 'config'
    kwargs['args'] = 'config'
    url = reverse('config:forums_config_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:forums_config_timedelta_view_search')
    kwargs['config'] = 1
    kwargs['exclude_field'] = 'forums_config_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_config_exclude
    kwargs['time_hash_basic'] = db_args['forums_time_hash_format']
    kwargs['time_delta_zset'] = db_args['forums_config_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def all_domains_timedelta_view(request):
    '''
    所有域名时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '域名-所有时间差'
    kwargs['url_arg'] = 'all'
    kwargs['search_arg'] = 'domain'
    kwargs['args'] = 'alldomains'
    kwargs['all_domains_configs'] = 1
    url = reverse('config:all_domains_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:all_domains_timedelta_view_search')
    kwargs['exclude_field'] = 'delta_alldomains_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_alldomains_exclude
    kwargs['time_hash_basic'] = db_args['all_hash_format']
    kwargs['time_delta_zset'] = db_args['all_domains_zset']
    return config_time_delta(request, common_time_delta, kwargs)


@login_required
def all_configs_timedelta_view(request):
    '''
    所有配置时间差
    :param request:
    :return:
    '''
    kwargs = delta_kwargs(request)

    kwargs['title'] = '配置-所有时间差'
    kwargs['url_arg'] = 'all'
    kwargs['search_arg'] = 'config'
    kwargs['args'] = 'allconfigs'
    kwargs['all_domains_configs'] = 1
    url = reverse('config:all_configs_timedelta_view')
    kwargs['url'] = url
    kwargs['url_search'] = reverse('config:all_configs_timedelta_view_search')
    kwargs['exclude_field'] = 'delta_allconfigs_exclude'
    # kwargs['user_deploy_delta_exclude'] = kwargs['user_deploy_delta'].delta_allconfigs_exclude
    kwargs['time_hash_basic'] = db_args['all_hash_format']
    kwargs['time_delta_zset'] = db_args['all_configs_zset']
    return config_time_delta(request, common_time_delta, kwargs)


user_deploy_delta_dict = {
    'news_domain_domain': "delta_domain_exclude",
    'news_domain_users': "delta_user_exclude",
    'news_config_config': "delta_config_exclude",
    'news_config_groupsexclude': "config_groups_exclude",

    'forums_domain_domain': "forums_domain_exclude",
    'forums_domain_users': "forums_user_exclude",
    'forums_config_config': "forums_config_exclude",

    'all_domain_alldomains': "delta_alldomains_exclude",
    'all_config_allconfigs': "delta_allconfigs_exclude",
}

time_hash_dict = {
    'news': db_args['news_time_hash_format'],
    'all': db_args['all_hash_format'],
    'forums': db_args['forums_time_hash_format'],
    'news_users': db_args['all_user_news_hash_format'],
    'forums_users': db_args['forums_all_user_hash_format']
}


def kwargs_sum_deltas(request, url_arg, search_arg, args):
    '''
    获取采集总数的hash和排除选项
    :param request:
    :param url_arg:
    :param search_arg:
    :param args:
    :return:
    '''
    kwargs = dict()
    delta_dict_key = '{0}_{1}_{2}'.format(url_arg, search_arg, args)
    delta_exclude_key = user_deploy_delta_dict[delta_dict_key]
    delta_exclude_group_key = user_deploy_delta_dict[delta_dict_key] + '_group'
    user_deploy_delta = UserDeploy.objects.get(user=request.user)
    exclude_list_original = user_deploy_delta.__dict__.get(delta_exclude_key)
    delta_exclude_groups = user_deploy_delta.__dict__.get(delta_exclude_group_key)
    time_hash = time_hash_dict[url_arg]
    if args == 'users':
        user_key = '{0}_{1}'.format(url_arg, args)
        time_hash = time_hash_dict[user_key]

    if exclude_list_original in ['', None]:
        exclude_list = []
    else:
        exclude_list = re.split('\s+', exclude_list_original)

    if delta_exclude_groups in ['', None]:
        exclude_groups = []
    else:
        exclude_groups = re.split('\s+', delta_exclude_groups)

    if args == 'groupsexclude':
        # 分组过滤时间差统计  首页巡查 89  海外21
        gid_list = ('89', '21')
        exclude_list_groups = config_ids_get(gid_list)
        exclude_list = exclude_list + exclude_list_groups

    kwargs['time_hash'] = time_hash
    kwargs['exclude_list'] = exclude_list
    kwargs['delta_dict_key'] = delta_dict_key
    kwargs['delta_exclude_group_key'] = delta_exclude_group_key
    kwargs['exclude_groups'] = tuple(exclude_groups)
    return kwargs


def base_sum_deltas(request, url_arg, search_arg, args, date):
    '''
    总时间差通用函数，处理不同条件下的总时间差
    :param request:
    :param url_arg:
    :param search_arg:
    :param args:
    :param date:
    :return:
    '''
    key_need = search_arg
    kwargs = kwargs_sum_deltas(request, url_arg, search_arg, args)
    time_hash = kwargs['time_hash']
    exclude_list = kwargs['exclude_list']
    all_timedelta = all_deltas(time_hash, key_need, date, exclude_list=exclude_list)
    return JsonResponse(all_timedelta)


# def sum_deltas(request, args):
#     '''
#     总时间差函数，當天不同條件下日期
#     :param request:
#     :param args:
#     :return:
#     '''
#     date = datetime.datetime.now().strftime('%Y-%m-%d')  # 尝试修复获取旧数据的问题
#     # return base_sum_deltas(request, args, date)


def rank_sum_deltas(request, url_arg, search_arg, args, date, delta):
    '''
    不同时间差维度所有数据的时间差
    :param request:
    :param url_arg:
    :param search_arg:
    :param args:
    :param date:
    :param delta:
    :return:
    '''
    key_need = search_arg
    key_need = search_arg
    kwargs = kwargs_sum_deltas(request, url_arg, search_arg, args)
    time_hash = kwargs['time_hash']
    exclude_list = kwargs['exclude_list']
    all_timedelta = all_deltas_rank(date, delta, time_hash, exclude_list, key_need)
    return JsonResponse(all_timedelta)


def custom_sum_deltas(request, url_arg, search_arg, args, date):
    '''
    不同时间差维度所有数据的时间差
    :param request:
    :param args:
    :param date:
    :return:
    '''
    time_hash = time_hash_dict[url_arg]
    if args == 'users':
        user_key = '{0}_{1}'.format(url_arg, args)
        time_hash = time_hash_dict[user_key]

    with open('delta_custom_domains.txt', 'r', encoding='utf-8') as fr:
        domains_string = fr.read()
        fr.close()
    domains = list(i.encode('utf-8') for i in domains_string.split(','))

    time_deltas = common_time_delta(date, time_hash, domains)
    all_timedelta = search_delta_result(time_deltas)['sum_search']
    return JsonResponse(all_timedelta)


def search_sum_deltas(request, url_arg, search_arg, args, date):
    '''
    搜索具体配置和分组的时间差
    :param request:
    :param args:
    :param date:
    :return:
    '''
    time_hash = time_hash_dict[url_arg]
    if args == 'users':
        user_key = '{0}_{1}'.format(url_arg, args)
        time_hash = time_hash_dict[user_key]

    with open('delta_search_domains.txt', 'r', encoding='utf-8') as fr:
        domains_string = fr.read()
        fr.close()
    domains = list(i.encode('utf-8') for i in domains_string.split(','))

    time_deltas = common_time_delta(date, time_hash, domains)
    all_timedelta = search_delta_result(time_deltas)['sum_search']
    all_timedelta['date'] = date
    return JsonResponse(all_timedelta)


# 已排除域名、配置管理
def exclude_manage(request, url_arg, search_arg, args):
    kwargs = kwargs_sum_deltas(request, url_arg, search_arg, args)
    time_hash = kwargs['time_hash']
    exclude_list = kwargs['exclude_list']

    date = datetime.datetime.now().strftime('%Y-%m-%d')  # 尝试修复获取旧数据的问题

    result = ''
    recover_key = ''
    url_recover = request.get_full_path()
    kwargs['url_recover'] = url_recover

    delta_dict_key = '{0}_{1}_{2}'.format(url_arg, search_arg, args)
    user_deploy_delta = UserDeploy.objects.get(user=request.user)
    domains = exclude_list
    # result = common_time_delta(date, time_hash, domains_org=domains)

    if request.method == 'POST':
        url = request.POST.get('now-url')
        user_deploy_delta = UserDeploy.objects.get(user=request.user)
        recover_list = request.POST.getlist('recover_check')
        domains_recover = list(set(domains).difference(recover_list))
        domains_recover = ' '.join(domains_recover)
        user_deploy_delta.__dict__.update({user_deploy_delta_dict[delta_dict_key]: domains_recover})
        user_deploy_delta.save()
        # return redirect(reverse('config:%s' % (url,)))
        return redirect(url)
    return render(request, 'config/time_delta_exclude.html', locals())


# 已排除分组管理
def exclude_groups_manage(request, url_arg, search_arg, args):
    kwargs = kwargs_sum_deltas(request, url_arg, search_arg, args)
    time_hash = kwargs['time_hash']
    exclude_groups = kwargs['exclude_groups']

    date = datetime.datetime.now().strftime('%Y-%m-%d')  # 尝试修复获取旧数据的问题

    result = ''
    recover_key = ''
    url_recover = request.get_full_path()
    kwargs['url_recover'] = url_recover

    user_deploy_delta = UserDeploy.objects.get(user=request.user)
    # result = common_time_delta(date, time_hash, domains_org=domains)

    if request.method == 'POST':
        url = request.POST.get('now-url')
        user_deploy_delta = UserDeploy.objects.get(user=request.user)
        recover_list = request.POST.getlist('recover_check')
        groups_recover = list(set(exclude_groups).difference(recover_list))
        groups_recover = ' '.join(groups_recover)
        user_deploy_delta.__dict__.update({kwargs['delta_exclude_group_key']: groups_recover})
        user_deploy_delta.save()
        # return redirect(reverse('config:%s' % (url,)))
        return redirect(url)
    return render(request, 'config/time_delta_exclude.html', locals())


def time_delta_history_view(request, url_arg, args, domain):
    kwargs = dict()
    time_hash = time_hash_dict[url_arg]
    if args == 'users':
        user_key = '{0}_{1}'.format(url_arg, args)
        time_hash = time_hash_dict[user_key]

    date_end_str = datetime.datetime.now().strftime('%Y-%m-%d')
    date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
    date_begin = date_end.replace(days=-15)
    date_begin_str = date_begin.format('YYYY-MM-DD')
    kwargs['domain'] = domain
    kwargs['url'] = request.get_full_path()
    if request.method == 'POST':
        date_begin_str = request.POST.get('date-begin')
        date_begin = arrow.get(date_begin_str, 'YYYY-MM-DD')
        date_end_str = request.POST.get('date-end')
        date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
        domain = request.POST.get('domain-link')

    result = time_delta_history(date_begin, date_end, domain, time_hash)
    return render(request, 'config/time_delta_history.html', locals())


# def time_delta_history(request, delta_history_func, kwargs):
#     date_end_str = datetime.datetime.now().strftime('%Y-%m-%d')
#     date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
#     date_begin = date_end.replace(days=-15)
#     date_begin_str = date_begin.format('YYYY-MM-DD')
#     domain = kwargs['domain']
#     kwargs['url'] = request.get_full_path()
#     if request.method == 'POST':
#         date_begin_str = request.POST.get('date-begin')
#         date_begin = arrow.get(date_begin_str, 'YYYY-MM-DD')
#         date_end_str = request.POST.get('date-end')
#         date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
#         domain = request.POST.get('domain-link')
#
#     result = delta_history_func(date_begin, date_end, domain)
# return render(request, 'config/time_delta_history.html', locals())


def base_sum_delta_history_view(request, url_arg, search_arg, args, kwargs):
    '''
    所有数据时间差历史基本模板
    :param request:
    :param args:
    :return:
    '''
    date_end_str = datetime.datetime.now().strftime('%Y-%m-%d')
    date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
    date_begin = date_end.replace(days=-13)
    date_begin_str = date_begin.format('YYYY-MM-DD')
    kwargs['url_search'] = reverse('config:sum_delta_history_view', args=(url_arg, search_arg, args))
    kwargs['config'] = 1
    kwargs['url_exclude'] = reverse('config:exclude_manage', args=(url_arg, search_arg, args))
    if request.method == 'POST':
        date_begin_str = request.POST.get('date-begin')
        date_begin = arrow.get(date_begin_str, 'YYYY-MM-DD')
        date_end_str = request.POST.get('date-end')
        date_end = arrow.get(date_end_str, 'YYYY-MM-DD')
        domain = request.POST.get('domain-link')

    url_list = []
    for i in arrow.Arrow.span_range('day', date_begin, date_end):
        i_dict = dict()
        date = i[1].format('YYYY-MM-DD')
        url_sum = reverse(kwargs['single_sum_url'], args=(url_arg, search_arg, args, date))
        i_dict['url_sum'] = url_sum
        i_dict['id'] = 'id' + date

        url_list.append(i_dict)
    result = url_list[::-1]
    return render(request, 'config/time_delta_history_all.html', locals())


# 所有数据时间差历史
def sum_delta_history_view(request, url_arg, search_arg, args):
    kwargs = dict()
    kwargs['single_sum_url'] = 'config:base_sum_deltas'
    return base_sum_delta_history_view(request, url_arg, search_arg, args, kwargs)


# 搜索数据时间差历史
def search_sum_delta_history_view(request, url_arg, search_arg, args):
    kwargs = dict()
    kwargs['single_sum_url'] = 'config:search_sum_deltas'
    return base_sum_delta_history_view(request, url_arg, search_arg, args, kwargs)


# 配置分组检测
def spider_groups_monitor(request):
    spider_con = redis.StrictRedis(host='192.168.16.223', port=6379, db=8)
    result = spider_con.hgetall('gid_avgtime_hash')
    result_list = []
    for k, val in result.items():
        result_single = dict()
        result_single['key'] = k
        dict_val = eval(str(val, encoding='utf-8'))
        for k1, val1 in dict_val.items():
            result_single[k1] = val1
        result_list.append(result_single)
    return render(request, 'config/spider_grous_list.html', locals())


def select_multiply(request):
    # config = 1
    # from backend_admin.forms import GroupForm
    # group_form = GroupForm()
    # name = '权限'
    # # 2-permission, 4-contenttype
    # group_form.fields['permissions'].queryset = Permission.objects.exclude(content_type_id__in=['2', '4'])
    # if request.method == 'POST':
    #     selects = request.POST.getlist('permissions')
    return render(request, 'config/select_test.html', locals())


# 配置url查詢
def config_url_search(request):
    kwargs = dict()
    kwargs['title'] = '配置-url查询'
    kwargs['config'] = ''
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        domains_original = request.POST.get('domains')
        domains = re.split('\s', domains_original.strip())
        kwargs['config'] = domains[0]
        date = request.POST.get('date-begin')

        result = config_url(date, domains[0])

    return render(request, 'config/config_url.html', locals())
