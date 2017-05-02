# coding:utf-8
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models


# 用户管理模块models
class User(AbstractUser):
    nickname = models.CharField(verbose_name='姓名', max_length=50)
    email_required = models.EmailField(verbose_name='电子邮箱', )
    role = models.CharField(max_length=200, verbose_name='角色', blank=True, default='无角色')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        groups_name = self.groups.all()
        if self.is_superuser == 1:
            self.role = '超级管理员'
        elif len(groups_name) > 0:
            groups_list = list()
            for i in groups_name:
                groups_list.append(i.name)
            self.role = '，'.join(groups_list)
        else:
            self.role = '无任何权限'
        super(User, self).save(*args, **kwargs)


# class PermissionRead(models.Model):
#     read_permission = models.OneToOneField(Permission, verbose_name='子模块权限')


class PermissionGroups(models.Model):
    groups_name = models.CharField(verbose_name='名称', max_length=50)
    groups_permissions = models.ManyToManyField(Permission, verbose_name='权限', blank=True)

    def __str__(self):
        return self.groups_name


# 全站管理models
class AllSite(models.Model):
    model_name = models.CharField(verbose_name='模块名称', max_length=20)

    class Meta:
        verbose_name = '全站爬虫'
        verbose_name_plural = verbose_name
        ordering = ['-id']


# 配置管理分组
class GroupConfigEach(models.Model):
    name = models.CharField(verbose_name='组名', max_length=30)
    user = models.ForeignKey(User, verbose_name='创建者')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '配置分组'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class GroupConfigManager(models.Model):
    name = models.CharField(verbose_name='组名', max_length=30)
    user = models.ForeignKey(User, verbose_name='创建者')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '配置管理组'
        verbose_name_plural = verbose_name
        ordering = ['-id']


class UserConfigEach(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_config_each = models.ForeignKey(GroupConfigEach, on_delete=models.CASCADE)
    level = models.IntegerField(default=0, blank=True)


class UserConfigManagerLevel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group_config_manager = models.ForeignKey(GroupConfigManager, on_delete=models.CASCADE)
    level = models.IntegerField(default=0, blank=True)


class UserDeploy(models.Model):
    user = models.ForeignKey(User, verbose_name='用户')
    delta_domain_exclude = models.CharField(max_length=2000, verbose_name='时间差新闻域名排除', null=True)
    delta_domain_exclude_group = models.CharField(max_length=200, verbose_name='时间差新闻域名排除', null=True)
    delta_user_exclude = models.CharField(max_length=2000, verbose_name='时间差用户排除', null=True)
    delta_user_exclude_group = models.CharField(max_length=200, verbose_name='时间差用户排除', null=True)
    delta_config_exclude = models.CharField(max_length=2000, verbose_name='时间差新闻配置排除', null=True)
    delta_config_exclude_group = models.CharField(max_length=200, verbose_name='时间差新闻配置排除', null=True)
    config_groups_exclude = models.CharField(max_length=2000, verbose_name='配置分组排除', null=True)
    config_groups_exclude_group = models.CharField(max_length=200, verbose_name='配置分组排除', null=True)
    delta_alldomains_exclude = models.CharField(max_length=2000, verbose_name='所有域名排除', null=True)
    delta_alldomains_exclude_group = models.CharField(max_length=200, verbose_name='所有域名排除', null=True)
    delta_allconfigs_exclude = models.CharField(max_length=2000, verbose_name='所有配置排除', null=True)
    delta_allconfigs_exclude_group = models.CharField(max_length=200, verbose_name='所有配置排除', null=True)
    forums_domain_exclude = models.CharField(max_length=2000, verbose_name='时间差论坛域名排除', null=True)
    forums_domain_exclude_group = models.CharField(max_length=200, verbose_name='时间差论坛域名排除', null=True)
    forums_user_exclude = models.CharField(max_length=2000, verbose_name='时间差论坛域名不去重排除', null=True)
    forums_user_exclude_group = models.CharField(max_length=200, verbose_name='时间差论坛域名不去重排除', null=True)
    forums_config_exclude = models.CharField(max_length=2000, verbose_name='时间差论坛配置排除', null=True)
    forums_config_exclude_group = models.CharField(max_length=200, verbose_name='时间差论坛配置排除', null=True)