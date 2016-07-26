#!/usr/bin/python
# coding=utf-8
import os
import redis
import MySQLdb
import ConfigParser
from werkzeug.datastructures import MultiDict

####################################################################
INIT_CONFIG = './web_run.dev.ini'
# INIT_CONFIG = './web_run.deploy.ini'
####################################################################
config = ConfigParser.ConfigParser()
# _cur_path = os.path.dirname(__file__)
# print _cur_path
if len(config.read(INIT_CONFIG)) == 0:
    print '[error]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[info] read the config file.', INIT_CONFIG

# redis
REDIS_SERVER = config.get('redis', 'redis_server')
DEDUP_SETTING = config.get('redis', 'dedup_server')
# mysql
MYSQLDB_HOST = config.get('mysql', 'mysql_host')
MYSQLDB_USER = config.get('mysql', 'mysql_user')
MYSQLDB_PORT = config.getint('mysql', 'mysql_port')
MYSQLDB_PASSWORD = config.get('mysql', 'mysql_password')
MYSQLDB_SELECT_DB = config.get('mysql', 'mysql_select_db')
MYSQLDB_CHARSET = config.get('mysql', 'mysql_charset')
# show json
PROCESS_SHOW_JSON = config.get('show', 'process_show_json')
SHOW_MAX = config.getint('show', 'show_max')
# export path
EXPORT_FOLDER = config.get('export', 'export_folder')
CONFIG_JSON = config.get('export', 'config_json')
# windows or linux or mac
if os.name == 'nt':
    RUN_FILE = config.get('windows', 'run_file')
    SHELL_CMD = config.get('windows', 'shell_cmd')
else:
    RUN_FILE = config.get('linux', 'run_file')
    SHELL_CMD = config.get('linux', 'shell_cmd')
# deploy
DEPLOY_HOST = config.get('deploy', 'deploy_host')
DEPLOY_PORT = config.get('deploy', 'deploy_port')
####################################################################

class RedisDrive(object):
    def __init__(self, start_url, site_domain):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain  # 计算结果
        self.manual_list_urls_rule_zset_key = 'manual_list_urls_rule_zset_%s' % self.site_domain  # 手工配置规则
        self.manual_detail_urls_rule_zset_key = 'manual_detail_urls_rule_zset_%s' % self.site_domain  # 手工配置规则
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0


    def get_detail_urls(self):
        return self.conn.zrangebyscore(self.detail_urls_zset_key, min=self.done_flg, max=self.done_flg, start=0,
                                       num=SHOW_MAX)


    def get_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.done_flg, start=0,
                                       num=SHOW_MAX)


    def get_done_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.done_flg, max=self.done_flg, start=0,
                                       num=SHOW_MAX)


class MySqlDrive(object):
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding(MYSQLDB_CHARSET)
        self.host = MYSQLDB_HOST
        self.user = MYSQLDB_USER
        self.password = MYSQLDB_PASSWORD
        self.port = 3306
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                    charset=MYSQLDB_CHARSET)
        self.conn.select_db(MYSQLDB_SELECT_DB)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def get_current_main_setting(self):
        # 提取主页、域名
        start_url = ''
        site_domain = ''
        black_domain = ''
        sqlStr = "SELECT start_url, site_domain, black_domain, setting_json FROM current_domain_setting"
        try:
            cnt = self.cur.execute(sqlStr)
            if cnt == 1:
                (start_url, site_domain, black_domain, setting_json) = self.cur.fetchone()
                self.conn.commit()
                # print 'get_current_main_setting()', cnt, sqlStr
        except Exception, e:
            print 'get_current_main_setting()', e

        return start_url, site_domain, black_domain


def get_result():
    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain = mysql_db.get_current_main_setting()
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        print(u'请设置主页、限定的域名信息。')

    # 从redis提取实时信息，转换成json文件
    redis_db = RedisDrive(start_url=start_url,
                          site_domain=site_domain)

    i = 0
    for list_url in redis_db.get_list_urls():
        list_url_data = MultiDict([('list_url', list_url), ('select', True)])
        i += 1

    i = 0
    for detail_url in redis_db.get_detail_urls():
        detail_url_data = MultiDict([('detail_url', detail_url), ('select', True)])
        i += 1

    # result-list.log
    i = 0
    fp = open(EXPORT_FOLDER + '/result-list.log', 'w')
    for line in redis_db.conn.zrange(redis_db.list_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
        i += 1
    fp.close()

    i = 0
    # result-detail.log
    fp = open(EXPORT_FOLDER + '/result-detail.log', 'w')
    for line in redis_db.conn.zrange(redis_db.detail_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
        i += 1
    fp.close()

if __name__ == '__main__':
    get_result()