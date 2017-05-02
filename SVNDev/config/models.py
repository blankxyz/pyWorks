# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from backend_admin.models import User


class DomainsAll(models.Model):
    domain = models.CharField(max_length=255)


class Locallog(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=255)  # Field name made lowercase.
    sheng = models.CharField(max_length=255, blank=True, null=True)
    shengid = models.CharField(db_column='shengID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    shi = models.CharField(max_length=255, blank=True, null=True)
    shiid = models.CharField(db_column='shiID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    xian = models.CharField(max_length=255, blank=True, null=True)
    xianid = models.CharField(db_column='xianID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ip = models.CharField(db_column='IP', max_length=255, blank=True, null=True)  # Field name made lowercase.
    addtime = models.CharField(max_length=255, blank=True, null=True)
    modifytime = models.CharField(max_length=255, blank=True, null=True)
    word = models.CharField(max_length=255, blank=True, null=True)
    diffword = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'LocalLog'


class B1ClassifyHash(models.Model):
    sl_num = models.IntegerField(primary_key=True)
    sl_code = models.CharField(max_length=50)
    msl_num = models.IntegerField()
    msl_code = models.CharField(max_length=255)
    ctime = models.IntegerField()
    type = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'b_1classify_hash'


class BArea(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    upid = models.IntegerField()
    fword = models.CharField(max_length=30)

    class Meta:
        managed = True
        db_table = 'b_area'


class BBigdatalog(models.Model):
    job_id = models.IntegerField()
    result_count = models.IntegerField()
    time_cost = models.FloatField()
    term = models.TextField()
    from_version = models.CharField(max_length=20)
    time_stamp = models.CharField(max_length=30)
    topic_id = models.CharField(max_length=50, blank=True, null=True)
    waitting_time = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_bigdatalog'


class BClassifyHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_classify_hash'


class BClassifyRecord11(models.Model):
    getversion = models.IntegerField()
    returnversion = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_classify_record_11'


class BClassifyVersionlog(models.Model):
    version_num = models.IntegerField(primary_key=True)
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_classify_versionlog'


class BCollectRecord(models.Model):
    time = models.IntegerField()
    c_num = models.IntegerField()
    r_num = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_collect_record'


class BWebtype(models.Model):
    typename = models.CharField(max_length=50)

    def __str__(self):
        return self.typename

    class Meta:
        managed = True
        db_table = 'b_webtype'


class Config(models.Model):
    webname = models.CharField(max_length=50, verbose_name='网站名称')
    url = models.CharField(max_length=50, verbose_name='网站域名')
    area = models.CharField(max_length=32, blank=True)
    serveip = models.CharField(db_column='serveIP', max_length=16, blank=True)  # Field name made lowercase.
    servearea = models.CharField(max_length=32, blank=True)
    icp = models.CharField(db_column='ICP', max_length=11, blank=True)  # Field name made lowercase.
    webtype = models.ForeignKey(BWebtype, db_column='webtype')
    channelname = models.CharField(max_length=100, blank=True)
    channelurl = models.TextField(blank=True, )
    savename = models.CharField(max_length=50, )
    savepath = models.CharField(max_length=100, )
    savetime = models.IntegerField()
    filesize = models.IntegerField()
    author = models.CharField(max_length=50)
    last_crawl_time = models.IntegerField(default=0)
    intervaltime = models.IntegerField(default=0)
    gid = models.IntegerField(blank=True, null=True)
    configid = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    tags = models.CharField(max_length=50, blank=True, null=True)
    tid = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, db_column='uid', null=True)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    mrid = models.IntegerField(default=0)
    mtid = models.IntegerField(default=0)
    mttid = models.IntegerField(default=0)
    description = models.TextField(default=0)

    class Meta:
        managed = True
        db_table = 'b_conf'


class BConfData(models.Model):
    cid = models.IntegerField()
    content = models.TextField()
    param = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_conf_data'


class BConfDomain(models.Model):
    domain = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_conf_domain'


class BConfDomainChannel(models.Model):
    did = models.IntegerField()
    channel = models.TextField()

    class Meta:
        managed = True
        db_table = 'b_conf_domain_channel'


class BConfchannel(models.Model):
    cid = models.IntegerField()
    channelname = models.CharField(max_length=255)
    channelurl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_confchannel'


class BConferror(models.Model):
    worker_id = models.IntegerField()
    config_id = models.CharField(max_length=11)
    error_description = models.TextField(blank=True, null=True)
    config_name = models.CharField(max_length=50)
    end_time = models.IntegerField()
    status = models.IntegerField()
    deal_e = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_conferror'


class BConfigtype(models.Model):
    typename = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_configtype'


class BDomain(models.Model):
    id = models.BigIntegerField(primary_key=True)
    site = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_domain'


class BDomainType(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)
    type_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_domain_type'


class BEmail(models.Model):
    email = models.CharField(max_length=50)
    isemail = models.IntegerField()
    isflag = models.IntegerField()
    ext = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_email'


class BError(models.Model):
    worker_id = models.IntegerField()
    config_id = models.CharField(max_length=11)
    error_info = models.IntegerField()
    error_description = models.CharField(max_length=50)
    config_name = models.CharField(max_length=50)
    end_time = models.IntegerField()
    status = models.IntegerField()
    deal_e = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_error'


class BFile(models.Model):
    filename = models.CharField(max_length=100)
    content = models.TextField()
    site = models.CharField(max_length=50)
    path = models.CharField(max_length=100)
    domains = models.CharField(max_length=100)
    status = models.IntegerField()
    type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_file'


class BFilterRules(models.Model):
    rulesname = models.CharField(max_length=255)
    rule = models.TextField()

    class Meta:
        managed = True
        db_table = 'b_filter_rules'


class BFormatHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_format_hash'


class BFormatRecord(models.Model):
    getversion = models.IntegerField()
    returnversion = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_format_record'


class BGeturlcs(models.Model):
    webname = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    channelname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_geturlcs'


class BGroup(models.Model):
    groupname = models.CharField(max_length=30, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_group'


class BIdserver(models.Model):
    name = models.CharField(max_length=50)
    host = models.CharField(max_length=50)
    dbnum = models.SmallIntegerField()
    list = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_idserver'


class BJobRecord(models.Model):
    spider_id = models.CharField(max_length=20, blank=True, null=True)
    worker_id = models.CharField(max_length=10, blank=True, null=True)
    config_id = models.IntegerField(blank=True, null=True)
    result = models.CharField(max_length=32)
    start_time = models.IntegerField()
    end_time = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_job_record'


class BJobResult(models.Model):
    config_id = models.IntegerField()
    end_time = models.IntegerField(blank=True, null=True)
    new_count = models.IntegerField(blank=True, null=True)
    error_info = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_job_result'


class BLocation(models.Model):
    province = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    word = models.CharField(max_length=64)
    level = models.IntegerField()
    status = models.IntegerField(blank=True, null=True)
    word_diff = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_location'
        unique_together = (('id', 'level'),)


class BLocationHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_location_hash'


class BLocationLog(models.Model):
    user = models.CharField(max_length=255)
    uid = models.IntegerField()
    time = models.IntegerField()
    action = models.CharField(max_length=255)
    obj = models.CharField(max_length=255)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_location_log'


class BLocationRecord(models.Model):
    getversion = models.IntegerField()
    returnversion = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_location_record'


class BLocationTemp(models.Model):
    name = models.CharField(max_length=255)
    e_name = models.CharField(max_length=255, blank=True, null=True)
    level = models.IntegerField()
    pid = models.IntegerField()
    postal = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_location_temp'


class BLocationWord(models.Model):
    word = models.CharField(max_length=255, blank=True, null=True)
    word_diff = models.CharField(max_length=255, blank=True, null=True)
    level = models.IntegerField()
    aid = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_location_word'


class BLocationecharts(models.Model):
    cid = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_locationecharts'


class BLocationinfo(models.Model):
    uuid = models.AutoField(primary_key=True)
    province = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    county = models.CharField(max_length=80, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    parent_uuid = models.CharField(max_length=40, blank=True, null=True)
    arg0 = models.CharField(max_length=50, blank=True, null=True)
    proshot = models.CharField(max_length=255, blank=True, null=True)
    lname_en = models.CharField(max_length=255, blank=True, null=True)
    lname_ft = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_locationinfo'


class BLocationinfoCopy(models.Model):
    uuid = models.AutoField(primary_key=True)
    province = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=80, blank=True, null=True)
    county = models.CharField(max_length=80, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    parent_uuid = models.CharField(max_length=40, blank=True, null=True)
    arg0 = models.CharField(max_length=50, blank=True, null=True)
    proshot = models.CharField(max_length=255, blank=True, null=True)
    lname_en = models.CharField(max_length=255, blank=True, null=True)
    lname_ft = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_locationinfo_copy'


class BLocationwordThird(models.Model):  # 此处原名为BLocationwordThird
    w_uuid = models.AutoField(primary_key=True)
    l_uuid = models.CharField(max_length=40, blank=True, null=True)
    word = models.CharField(max_length=64, blank=True, null=True)
    word_diff = models.TextField(blank=True, null=True)
    whitelist = models.TextField(blank=True, null=True)
    pending = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_locationword'


class BLocationwordCopy(models.Model):
    w_uuid = models.AutoField(primary_key=True)
    l_uuid = models.CharField(max_length=40, blank=True, null=True)
    word = models.CharField(max_length=64, blank=True, null=True)
    word_diff = models.TextField(blank=True, null=True)
    whitelist = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_locationword_copy'


class BMblogWord(models.Model):
    word = models.CharField(max_length=255)
    ctime = models.IntegerField(blank=True, null=True)
    euser = models.CharField(max_length=255, blank=True, null=True)
    etime = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_mblog_word'


class BMediarank(models.Model):
    rankname = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_mediarank'


class BMediatwotype(models.Model):
    typename = models.CharField(max_length=50, blank=True, null=True)
    mtid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_mediatwotype'


class BMediatype(models.Model):
    typename = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_mediatype'


class BMod(models.Model):
    mname = models.CharField(max_length=50)
    mname_e = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    fname_e = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_mod'


class BNegativeHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_negative_hash'


class BNegativeRecord(models.Model):
    type = models.CharField(max_length=255)
    getversion = models.IntegerField()
    returnversion = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_negative_record'


class BNoData(models.Model):
    time = models.IntegerField()
    url = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_no_data'


class BNode(models.Model):
    sid = models.IntegerField()
    mid = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_node'


class BOpRecord(models.Model):
    user = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    content = models.CharField(max_length=255, blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_op_record'


class BOperate(models.Model):
    cname = models.CharField(max_length=50)
    uid = models.IntegerField()
    status = models.IntegerField()
    remarks = models.TextField(blank=True, null=True)
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_operate'


class BOperation(models.Model):
    mid = models.IntegerField()
    op_name = models.CharField(max_length=32)

    class Meta:
        managed = True
        db_table = 'b_operation'


class BOperationRecord(models.Model):
    op_time = models.IntegerField()
    operator = models.CharField(max_length=50)
    op_module = models.CharField(max_length=32)
    op_content = models.CharField(max_length=32)
    result = models.CharField(max_length=11)

    class Meta:
        managed = True
        db_table = 'b_operation_record'


class BPNRecord(models.Model):
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_p_n_record'


class BPNWord(models.Model):
    word = models.CharField(max_length=255)
    type = models.IntegerField(blank=True, null=True)
    ctime = models.IntegerField(blank=True, null=True)
    etime = models.IntegerField(blank=True, null=True)
    euser = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_p_n_word'


class BPermissionDistribution(models.Model):
    uid = models.IntegerField()
    mid = models.IntegerField()
    oid = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_permission_distribution'


class BPnType(models.Model):
    tid = models.IntegerField()
    tname = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_pn_type'


class BRecpostuser(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    sid = models.IntegerField(blank=True, null=True)
    uid = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_recpostuser'


class BSC(models.Model):
    sid = models.IntegerField()
    cid = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_s_c'


class BSaler(models.Model):
    saler = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'b_saler'


class BSertype(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_sertype'


class BServer(models.Model):
    name = models.CharField(max_length=50)
    host = models.CharField(max_length=50)
    dbnum = models.SmallIntegerField()
    list = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_server'


class BSpider(models.Model):
    status = models.IntegerField()
    spider_id = models.CharField(max_length=20)
    gid = models.IntegerField(blank=True, null=True)
    host_id = models.CharField(max_length=50, blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    checkstatus = models.IntegerField(blank=True, null=True)
    checktime = models.IntegerField(blank=True, null=True)
    starttime = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_spider'


class BSpiderconfig(models.Model):
    sid = models.IntegerField()
    cid = models.IntegerField()
    time = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_spiderconfig'


class BStatus(models.Model):
    status_name = models.CharField(max_length=50)
    status_cname = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_status'


class BSummaryHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_summary_hash'


class BSummaryIndHash(models.Model):
    version_num = models.IntegerField(blank=True, null=True)
    version_code = models.CharField(max_length=255, blank=True, null=True)
    ctime = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_summary_ind_hash'


class BTencentBlogword(models.Model):
    saler = models.IntegerField()
    customer = models.CharField(db_column='Customer', max_length=255)  # Field name made lowercase.
    words = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'b_tencent_blogword'


class BTopicHash(models.Model):
    version_num = models.IntegerField()
    version_code = models.CharField(max_length=255)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_topic_hash'


class BTopicweb(models.Model):
    host = models.CharField(max_length=50)
    keyname = models.CharField(max_length=50)
    countkey = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_topicweb'


class BTrade(models.Model):
    typename = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_trade'


class BUcr(models.Model):
    uid = models.IntegerField()
    cid = models.IntegerField()
    c_right = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_ucr'


class BUselesschannel(models.Model):
    channel = models.CharField(max_length=255)
    status = models.IntegerField()
    type = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_uselesschannel'


class BUselesschanneltype(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_uselesschanneltype'


class BUselessurl(models.Model):
    url = models.CharField(max_length=255)
    type = models.IntegerField()
    status = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_uselessurl'


class BUselessurltype(models.Model):
    type = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'b_uselessurltype'


class BUselessword(models.Model):
    word = models.CharField(max_length=255)
    word_type = models.IntegerField()
    ctime = models.IntegerField(blank=True, null=True)
    etime = models.IntegerField(blank=True, null=True)
    euser = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_uselessword'


class BUser(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=32)
    status = models.IntegerField()
    create_time = models.IntegerField(blank=True, null=True)
    last_login = models.IntegerField(blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    exist = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'b_user'


class BUserData(models.Model):
    uid = models.IntegerField()
    login_record = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_user_data'


class BUserWordHash(models.Model):
    version_num = models.IntegerField(primary_key=True)
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_user_word_hash'


class BUserWordVersionlog(models.Model):
    version_num = models.IntegerField(primary_key=True)
    version_code = models.CharField(max_length=40)
    ctime = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_user_word_versionlog'


class BWeibowords(models.Model):
    uid = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'b_weibowords'


class BWordstatus(models.Model):
    wordtype = models.CharField(max_length=255)
    status = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'b_wordstatus'


class BWordtype(models.Model):
    typename = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'b_wordtype'


class GbCity(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField()
    parentid = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'gb_city'


class Ltest(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=255)  # Field name made lowercase.
    localuuid = models.CharField(db_column='LOCALUUID', max_length=255, blank=True,
                                 null=True)  # Field name made lowercase.
    sheng = models.CharField(max_length=255, blank=True, null=True)
    shi = models.CharField(max_length=255, blank=True, null=True)
    xian = models.CharField(max_length=255, blank=True, null=True)
    parent = models.CharField(max_length=255, blank=True, null=True)
    lev = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ltest'


class SyncMonitor(models.Model):
    name = models.CharField(unique=True, max_length=10)
    value = models.BigIntegerField()
    utime = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'sync_monitor'


class TC3P0Test(models.Model):
    a = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 't_c3p0_test'
