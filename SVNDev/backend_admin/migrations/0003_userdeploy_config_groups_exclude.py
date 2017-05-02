# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0002_userdeploy'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeploy',
            name='config_groups_exclude',
            field=models.CharField(null=True, max_length=2000, verbose_name='配置分组排除'),
        ),
    ]
