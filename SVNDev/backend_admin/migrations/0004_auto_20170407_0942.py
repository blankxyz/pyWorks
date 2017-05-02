# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0003_userdeploy_config_groups_exclude'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeploy',
            name='delta_allconfigs_exclude',
            field=models.CharField(verbose_name='所有配置排除', max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='userdeploy',
            name='delta_alldomains_exclude',
            field=models.CharField(verbose_name='所有域名排除', max_length=2000, null=True),
        ),
    ]
