# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDeploy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('delta_domain_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差新闻域名排除')),
                ('delta_domain_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差新闻域名排除')),
                ('delta_user_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差用户排除')),
                ('delta_user_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差用户排除')),
                ('delta_config_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差新闻配置排除')),
                ('delta_config_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差新闻配置排除')),
                ('config_groups_exclude', models.CharField(max_length=2000, null=True, verbose_name='配置分组排除')),
                ('config_groups_exclude_group', models.CharField(max_length=200, null=True, verbose_name='配置分组排除')),
                ('delta_alldomains_exclude', models.CharField(max_length=2000, null=True, verbose_name='所有域名排除')),
                ('delta_alldomains_exclude_group', models.CharField(max_length=200, null=True, verbose_name='所有域名排除')),
                ('delta_allconfigs_exclude', models.CharField(max_length=2000, null=True, verbose_name='所有配置排除')),
                ('delta_allconfigs_exclude_group', models.CharField(max_length=200, null=True, verbose_name='所有配置排除')),
                ('forums_domain_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差论坛域名排除')),
                ('forums_domain_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差论坛域名排除')),
                ('forums_user_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差论坛域名不去重排除')),
                ('forums_user_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差论坛域名不去重排除')),
                ('forums_config_exclude', models.CharField(max_length=2000, null=True, verbose_name='时间差论坛配置排除')),
                ('forums_config_exclude_group', models.CharField(max_length=200, null=True, verbose_name='时间差论坛配置排除')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
    ]
