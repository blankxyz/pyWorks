# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='B1ClassifyHash',
            fields=[
                ('sl_num', models.IntegerField(serialize=False, primary_key=True)),
                ('sl_code', models.CharField(max_length=50)),
                ('msl_num', models.IntegerField()),
                ('msl_code', models.CharField(max_length=255)),
                ('ctime', models.IntegerField()),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'b_1classify_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BArea',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('level', models.IntegerField()),
                ('upid', models.IntegerField()),
                ('fword', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'b_area',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BBigdatalog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('job_id', models.IntegerField()),
                ('result_count', models.IntegerField()),
                ('time_cost', models.FloatField()),
                ('term', models.TextField()),
                ('from_version', models.CharField(max_length=20)),
                ('time_stamp', models.CharField(max_length=30)),
                ('topic_id', models.CharField(max_length=50, blank=True, null=True)),
                ('waitting_time', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_bigdatalog',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BClassifyHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_classify_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BClassifyRecord11',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('getversion', models.IntegerField()),
                ('returnversion', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_classify_record_11',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BClassifyVersionlog',
            fields=[
                ('version_num', models.IntegerField(serialize=False, primary_key=True)),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_classify_versionlog',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BCollectRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField()),
                ('c_num', models.IntegerField()),
                ('r_num', models.IntegerField()),
            ],
            options={
                'db_table': 'b_collect_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConfchannel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cid', models.IntegerField()),
                ('channelname', models.CharField(max_length=255)),
                ('channelurl', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_confchannel',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConfData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cid', models.IntegerField()),
                ('content', models.TextField()),
                ('param', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_conf_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConfDomain',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('domain', models.CharField(max_length=255)),
                ('domain_name', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_conf_domain',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConfDomainChannel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('did', models.IntegerField()),
                ('channel', models.TextField()),
            ],
            options={
                'db_table': 'b_conf_domain_channel',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConferror',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('worker_id', models.IntegerField()),
                ('config_id', models.CharField(max_length=11)),
                ('error_description', models.TextField(blank=True, null=True)),
                ('config_name', models.CharField(max_length=50)),
                ('end_time', models.IntegerField()),
                ('status', models.IntegerField()),
                ('deal_e', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_conferror',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BConfigtype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_configtype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BDomain',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('site', models.CharField(max_length=100, blank=True, null=True)),
                ('name', models.CharField(max_length=100, blank=True, null=True)),
                ('type', models.CharField(max_length=100, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_domain',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BDomainType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=255, blank=True, null=True)),
                ('type_name', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_domain_type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BEmail',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('email', models.CharField(max_length=50)),
                ('isemail', models.IntegerField()),
                ('isflag', models.IntegerField()),
                ('ext', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_email',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BError',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('worker_id', models.IntegerField()),
                ('config_id', models.CharField(max_length=11)),
                ('error_info', models.IntegerField()),
                ('error_description', models.CharField(max_length=50)),
                ('config_name', models.CharField(max_length=50)),
                ('end_time', models.IntegerField()),
                ('status', models.IntegerField()),
                ('deal_e', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_error',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BFile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('filename', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('site', models.CharField(max_length=50)),
                ('path', models.CharField(max_length=100)),
                ('domains', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('type', models.CharField(max_length=10, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_file',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BFilterRules',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('rulesname', models.CharField(max_length=255)),
                ('rule', models.TextField()),
            ],
            options={
                'db_table': 'b_filter_rules',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BFormatHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_format_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BFormatRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('getversion', models.IntegerField()),
                ('returnversion', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_format_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BGeturlcs',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('webname', models.CharField(max_length=255, blank=True, null=True)),
                ('url', models.CharField(max_length=255, blank=True, null=True)),
                ('channelname', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_geturlcs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BGroup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('groupname', models.CharField(max_length=30, blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_group',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BIdserver',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('host', models.CharField(max_length=50)),
                ('dbnum', models.SmallIntegerField()),
                ('list', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_idserver',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BJobRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('spider_id', models.CharField(max_length=20, blank=True, null=True)),
                ('worker_id', models.CharField(max_length=10, blank=True, null=True)),
                ('config_id', models.IntegerField(blank=True, null=True)),
                ('result', models.CharField(max_length=32)),
                ('start_time', models.IntegerField()),
                ('end_time', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_job_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BJobResult',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('config_id', models.IntegerField()),
                ('end_time', models.IntegerField(blank=True, null=True)),
                ('new_count', models.IntegerField(blank=True, null=True)),
                ('error_info', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_job_result',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('province', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=64)),
                ('district', models.CharField(max_length=64)),
                ('word', models.CharField(max_length=64)),
                ('level', models.IntegerField()),
                ('status', models.IntegerField(blank=True, null=True)),
                ('word_diff', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_location',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationecharts',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cid', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_locationecharts',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_location_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationinfo',
            fields=[
                ('uuid', models.AutoField(serialize=False, primary_key=True)),
                ('province', models.CharField(max_length=80, blank=True, null=True)),
                ('city', models.CharField(max_length=80, blank=True, null=True)),
                ('county', models.CharField(max_length=80, blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('parent_uuid', models.CharField(max_length=40, blank=True, null=True)),
                ('arg0', models.CharField(max_length=50, blank=True, null=True)),
                ('proshot', models.CharField(max_length=255, blank=True, null=True)),
                ('lname_en', models.CharField(max_length=255, blank=True, null=True)),
                ('lname_ft', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_locationinfo',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationinfoCopy',
            fields=[
                ('uuid', models.AutoField(serialize=False, primary_key=True)),
                ('province', models.CharField(max_length=80, blank=True, null=True)),
                ('city', models.CharField(max_length=80, blank=True, null=True)),
                ('county', models.CharField(max_length=80, blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('parent_uuid', models.CharField(max_length=40, blank=True, null=True)),
                ('arg0', models.CharField(max_length=50, blank=True, null=True)),
                ('proshot', models.CharField(max_length=255, blank=True, null=True)),
                ('lname_en', models.CharField(max_length=255, blank=True, null=True)),
                ('lname_ft', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_locationinfo_copy',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('user', models.CharField(max_length=255)),
                ('uid', models.IntegerField()),
                ('time', models.IntegerField()),
                ('action', models.CharField(max_length=255)),
                ('obj', models.CharField(max_length=255)),
                ('remarks', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_location_log',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('getversion', models.IntegerField()),
                ('returnversion', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_location_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationTemp',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('e_name', models.CharField(max_length=255, blank=True, null=True)),
                ('level', models.IntegerField()),
                ('pid', models.IntegerField()),
                ('postal', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_location_temp',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationWord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('word', models.CharField(max_length=255, blank=True, null=True)),
                ('word_diff', models.CharField(max_length=255, blank=True, null=True)),
                ('level', models.IntegerField()),
                ('aid', models.IntegerField()),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'b_location_word',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationwordCopy',
            fields=[
                ('w_uuid', models.AutoField(serialize=False, primary_key=True)),
                ('l_uuid', models.CharField(max_length=40, blank=True, null=True)),
                ('word', models.CharField(max_length=64, blank=True, null=True)),
                ('word_diff', models.TextField(blank=True, null=True)),
                ('whitelist', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_locationword_copy',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BLocationwordThird',
            fields=[
                ('w_uuid', models.AutoField(serialize=False, primary_key=True)),
                ('l_uuid', models.CharField(max_length=40, blank=True, null=True)),
                ('word', models.CharField(max_length=64, blank=True, null=True)),
                ('word_diff', models.TextField(blank=True, null=True)),
                ('whitelist', models.TextField(blank=True, null=True)),
                ('pending', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_locationword',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BMblogWord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('ctime', models.IntegerField(blank=True, null=True)),
                ('euser', models.CharField(max_length=255, blank=True, null=True)),
                ('etime', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_mblog_word',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BMediarank',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('rankname', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_mediarank',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BMediatwotype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50, blank=True, null=True)),
                ('mtid', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_mediatwotype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BMediatype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_mediatype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BMod',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('mname', models.CharField(max_length=50)),
                ('mname_e', models.CharField(max_length=50)),
                ('fname', models.CharField(max_length=50)),
                ('fname_e', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_mod',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BNegativeHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_negative_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BNegativeRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
                ('getversion', models.IntegerField()),
                ('returnversion', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_negative_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BNoData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField()),
                ('url', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_no_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BNode',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sid', models.IntegerField()),
                ('mid', models.IntegerField()),
            ],
            options={
                'db_table': 'b_node',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BOperate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('cname', models.CharField(max_length=50)),
                ('uid', models.IntegerField()),
                ('status', models.IntegerField()),
                ('remarks', models.TextField(blank=True, null=True)),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_operate',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BOperation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('mid', models.IntegerField()),
                ('op_name', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'b_operation',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BOperationRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('op_time', models.IntegerField()),
                ('operator', models.CharField(max_length=50)),
                ('op_module', models.CharField(max_length=32)),
                ('op_content', models.CharField(max_length=32)),
                ('result', models.CharField(max_length=11)),
            ],
            options={
                'db_table': 'b_operation_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BOpRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('user', models.CharField(max_length=255)),
                ('module', models.CharField(max_length=255)),
                ('action', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=255, blank=True, null=True)),
                ('time', models.IntegerField(blank=True, null=True)),
                ('ip', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_op_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BPermissionDistribution',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('mid', models.IntegerField()),
                ('oid', models.IntegerField()),
            ],
            options={
                'db_table': 'b_permission_distribution',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BPNRecord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_p_n_record',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BPnType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('tid', models.IntegerField()),
                ('tname', models.CharField(max_length=255, blank=True, null=True)),
                ('filename', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_pn_type',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BPNWord',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('ctime', models.IntegerField(blank=True, null=True)),
                ('etime', models.IntegerField(blank=True, null=True)),
                ('euser', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_p_n_word',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BRecpostuser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50, blank=True, null=True)),
                ('url', models.CharField(max_length=200, blank=True, null=True)),
                ('sid', models.IntegerField(blank=True, null=True)),
                ('uid', models.IntegerField()),
            ],
            options={
                'db_table': 'b_recpostuser',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSaler',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('saler', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'b_saler',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSC',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sid', models.IntegerField()),
                ('cid', models.IntegerField()),
            ],
            options={
                'db_table': 'b_s_c',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSertype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_sertype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BServer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('host', models.CharField(max_length=50)),
                ('dbnum', models.SmallIntegerField()),
                ('list', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_server',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSpider',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('status', models.IntegerField()),
                ('spider_id', models.CharField(max_length=20)),
                ('gid', models.IntegerField(blank=True, null=True)),
                ('host_id', models.CharField(max_length=50, blank=True, null=True)),
                ('time', models.IntegerField(blank=True, null=True)),
                ('checkstatus', models.IntegerField(blank=True, null=True)),
                ('checktime', models.IntegerField(blank=True, null=True)),
                ('starttime', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_spider',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSpiderconfig',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sid', models.IntegerField()),
                ('cid', models.IntegerField()),
                ('time', models.IntegerField()),
            ],
            options={
                'db_table': 'b_spiderconfig',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BStatus',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('status_name', models.CharField(max_length=50)),
                ('status_cname', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_status',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSummaryHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_summary_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BSummaryIndHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField(blank=True, null=True)),
                ('version_code', models.CharField(max_length=255, blank=True, null=True)),
                ('ctime', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_summary_ind_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BTencentBlogword',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('saler', models.IntegerField()),
                ('customer', models.CharField(db_column='Customer', max_length=255)),
                ('words', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'b_tencent_blogword',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BTopicHash',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('version_num', models.IntegerField()),
                ('version_code', models.CharField(max_length=255)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_topic_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BTopicweb',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('host', models.CharField(max_length=50)),
                ('keyname', models.CharField(max_length=50)),
                ('countkey', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_topicweb',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BTrade',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_trade',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUcr',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('cid', models.IntegerField()),
                ('c_right', models.IntegerField()),
            ],
            options={
                'db_table': 'b_ucr',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUselesschannel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('channel', models.CharField(max_length=255)),
                ('status', models.IntegerField()),
                ('type', models.IntegerField()),
            ],
            options={
                'db_table': 'b_uselesschannel',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUselesschanneltype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_uselesschanneltype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUselessurl',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('type', models.IntegerField()),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'b_uselessurl',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUselessurltype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'b_uselessurltype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUselessword',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('word_type', models.IntegerField()),
                ('ctime', models.IntegerField(blank=True, null=True)),
                ('etime', models.IntegerField(blank=True, null=True)),
                ('euser', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'b_uselessword',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=32)),
                ('status', models.IntegerField()),
                ('create_time', models.IntegerField(blank=True, null=True)),
                ('last_login', models.IntegerField(blank=True, null=True)),
                ('nickname', models.CharField(max_length=50, blank=True, null=True)),
                ('exist', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'b_user',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUserData',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('login_record', models.IntegerField()),
            ],
            options={
                'db_table': 'b_user_data',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUserWordHash',
            fields=[
                ('version_num', models.IntegerField(serialize=False, primary_key=True)),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_user_word_hash',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BUserWordVersionlog',
            fields=[
                ('version_num', models.IntegerField(serialize=False, primary_key=True)),
                ('version_code', models.CharField(max_length=40)),
                ('ctime', models.IntegerField()),
            ],
            options={
                'db_table': 'b_user_word_versionlog',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BWebtype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_webtype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BWeibowords',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'b_weibowords',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BWordstatus',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('wordtype', models.CharField(max_length=255)),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'b_wordstatus',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BWordtype',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('typename', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'b_wordtype',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('webname', models.CharField(max_length=50, verbose_name='网站名称')),
                ('url', models.CharField(max_length=50, verbose_name='网站域名')),
                ('area', models.CharField(max_length=32, blank=True)),
                ('serveip', models.CharField(db_column='serveIP', max_length=16, blank=True)),
                ('servearea', models.CharField(max_length=32, blank=True)),
                ('icp', models.CharField(db_column='ICP', max_length=11, blank=True)),
                ('channelname', models.CharField(max_length=100, blank=True)),
                ('channelurl', models.TextField(blank=True)),
                ('savename', models.CharField(max_length=50)),
                ('savepath', models.CharField(max_length=100)),
                ('savetime', models.IntegerField()),
                ('filesize', models.IntegerField()),
                ('author', models.CharField(max_length=50)),
                ('last_crawl_time', models.IntegerField(default=0)),
                ('intervaltime', models.IntegerField(default=0)),
                ('gid', models.IntegerField(blank=True, null=True)),
                ('configid', models.IntegerField(blank=True, null=True)),
                ('level', models.IntegerField(blank=True, null=True)),
                ('tags', models.CharField(max_length=50, blank=True, null=True)),
                ('tid', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('mrid', models.IntegerField(default=0)),
                ('mtid', models.IntegerField(default=0)),
                ('mttid', models.IntegerField(default=0)),
                ('description', models.TextField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column='uid', null=True)),
                ('webtype', models.ForeignKey(db_column='webtype', to='config.BWebtype')),
            ],
            options={
                'db_table': 'b_conf',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='GbCity',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('level', models.IntegerField()),
                ('parentid', models.IntegerField()),
            ],
            options={
                'db_table': 'gb_city',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Locallog',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=255, serialize=False, primary_key=True)),
                ('sheng', models.CharField(max_length=255, blank=True, null=True)),
                ('shengid', models.CharField(db_column='shengID', max_length=255, blank=True, null=True)),
                ('shi', models.CharField(max_length=255, blank=True, null=True)),
                ('shiid', models.CharField(db_column='shiID', max_length=255, blank=True, null=True)),
                ('xian', models.CharField(max_length=255, blank=True, null=True)),
                ('xianid', models.CharField(db_column='xianID', max_length=255, blank=True, null=True)),
                ('ip', models.CharField(db_column='IP', max_length=255, blank=True, null=True)),
                ('addtime', models.CharField(max_length=255, blank=True, null=True)),
                ('modifytime', models.CharField(max_length=255, blank=True, null=True)),
                ('word', models.CharField(max_length=255, blank=True, null=True)),
                ('diffword', models.CharField(max_length=255, blank=True, null=True)),
                ('author', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'LocalLog',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Ltest',
            fields=[
                ('id', models.CharField(db_column='ID', max_length=255, serialize=False, primary_key=True)),
                ('localuuid', models.CharField(db_column='LOCALUUID', max_length=255, blank=True, null=True)),
                ('sheng', models.CharField(max_length=255, blank=True, null=True)),
                ('shi', models.CharField(max_length=255, blank=True, null=True)),
                ('xian', models.CharField(max_length=255, blank=True, null=True)),
                ('parent', models.CharField(max_length=255, blank=True, null=True)),
                ('lev', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'db_table': 'ltest',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SyncMonitor',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
                ('value', models.BigIntegerField()),
                ('utime', models.DateTimeField()),
            ],
            options={
                'db_table': 'sync_monitor',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TC3P0Test',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('a', models.CharField(max_length=1, blank=True, null=True)),
            ],
            options={
                'db_table': 't_c3p0_test',
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='blocation',
            unique_together=set([('id', 'level')]),
        ),
    ]
