# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0004_auto_20170407_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeploy',
            name='forums_domain_exclude',
            field=models.CharField(null=True, max_length=2000, verbose_name='所有配置排除'),
        ),
    ]
