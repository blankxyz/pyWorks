# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_admin', '0005_userdeploy_forums_domain_exclude'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdeploy',
            name='forums_user_exclude',
            field=models.CharField(verbose_name='所有配置排除', null=True, max_length=2000),
        ),
    ]
