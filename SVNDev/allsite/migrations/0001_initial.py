# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='XPathEntity',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('username', models.CharField(max_length=50, db_index=True)),
                ('url', models.CharField(max_length=255, db_index=True)),
                ('title_xpath', models.CharField(max_length=255, null=True)),
                ('content_xpath', models.CharField(max_length=255, null=True)),
                ('ctime_xpath', models.CharField(max_length=255, null=True)),
                ('source_xpath', models.CharField(max_length=255, null=True)),
                ('page_xpath', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
