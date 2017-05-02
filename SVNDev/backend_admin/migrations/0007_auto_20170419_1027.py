# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0006_userdeploy_forums_user_exclude'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeploy',
            name='forums_config_exclude',
            field=models.CharField(max_length=2000, verbose_name='时间差论坛配置排除', null=True),
        ),
        migrations.AlterField(
            model_name='userdeploy',
            name='delta_config_exclude',
            field=models.CharField(max_length=2000, verbose_name='时间差新闻配置排除'),
        ),
        migrations.AlterField(
            model_name='userdeploy',
            name='delta_domain_exclude',
            field=models.CharField(max_length=2000, verbose_name='时间差新闻域名排除'),
        ),
        migrations.AlterField(
            model_name='userdeploy',
            name='forums_domain_exclude',
            field=models.CharField(max_length=2000, verbose_name='时间差论坛域名排除', null=True),
        ),
        migrations.AlterField(
            model_name='userdeploy',
            name='forums_user_exclude',
            field=models.CharField(max_length=2000, verbose_name='时间差论坛域名不去重排除', null=True),
        ),
    ]
