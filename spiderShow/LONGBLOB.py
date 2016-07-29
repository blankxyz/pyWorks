#!/usr/bin/python
# coding=utf-8
import MySQLdb
import ConfigParser
import zipfile
import os
import traceback
import binascii

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
    print '[info]read the config file OK.', INIT_CONFIG

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
    RUN_ALLSITE_INI = config.get('windows', 'run_allsite_ini')

else:
    RUN_FILE = config.get('linux', 'run_file')
    SHELL_CMD = config.get('linux', 'shell_cmd')
    RUN_ALLSITE_INI = config.get('linux', 'run_allsite_ini')
# deploy
DEPLOY_HOST = config.get('deploy', 'deploy_host')
DEPLOY_PORT = config.get('deploy', 'deploy_port')


####################################################################

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

    def save_all_setting(self, user_id, start_url, site_domain, setting_json, black_domain_str, detail_regex_save_list,
                         list_regex_save_list):
        # print 'save_all_setting() start...', start_url, site_domain

        ret_cnt = 0
        try:
            sqlStr1 = (
                "DELETE FROM url_rule WHERE user_id = '" + user_id + "' AND start_url= '" + start_url + "' AND site_domain= '" + site_domain + "'")
            self.cur.execute(sqlStr1)
            self.conn.commit()

            # detail_or_list = '0'  # 0:detail,1:list
            # scope = '0'           # 0:netloc,1:path,2:query
            # white_or_black = '0'  # 0:white,1:black
            # weight = '0'          # 0:高，1：中，2：低

            for item in detail_regex_save_list:
                regex = item['regex']
                weight = item['weight']
                detail_or_list = '0'
                scope = '1'
                white_or_black = '0'
                sqlStr2 = "INSERT INTO url_rule(user_id,start_url,site_domain,black_domain_str,detail_or_list, scope,white_or_black,weight,regex) " \
                          "VALUES ( '" + user_id + "','" + start_url + "','" + site_domain + "','" + black_domain_str + "','" + detail_or_list + "','" + \
                          scope + "','" + white_or_black + "','" + weight + "','" + regex + "')"
                print '[info]save_all_setting()-detail', sqlStr2
                ret_cnt = self.cur.execute(sqlStr2)
                self.conn.commit()

            for item in list_regex_save_list:
                regex = item['regex']
                weight = item['weight']
                detail_or_list = '1'
                scope = '1'
                white_or_black = '0'
                sqlStr2 = "INSERT INTO url_rule(user_id,start_url,site_domain,black_domain_str,detail_or_list, scope,white_or_black,weight,regex) " \
                          "VALUES ('" + user_id + "','" + start_url + "','" + site_domain + "','" + black_domain_str + "','" + detail_or_list + "','" + \
                          scope + "','" + white_or_black + "','" + weight + "','" + regex + "')"
                print '[info]save_all_setting()-list', sqlStr2
                ret_cnt = self.cur.execute(sqlStr2)
                self.conn.commit()

        except Exception, e:
            ret_cnt = 0
            print '[error]save_all_setting()', e
            self.conn.rollback()

        return ret_cnt

    def search_regex_by_user(self, user_id, start_url, site_domain):
        search_result_list = []
        sqlStr = "SELECT start_url,site_domain,black_domain_str,detail_or_list,scope,white_or_black,weight,regex FROM url_rule " \
                 "WHERE user_id='" + user_id + "' AND start_url like '%" + start_url + "%' AND site_domain like '%" + site_domain + "%'"
        try:
            cnt = self.cur.execute(sqlStr)
            rs = self.cur.fetchall()
            for r in rs:
                # code 表意翻译
                if r[3] == '0':
                    detail_or_list = u'详情规则'
                else:
                    detail_or_list = u'列表规则'

                if r[2] == '' or r[2] is None:
                    black_domain_str = u'无'
                else:
                    black_domain_str = r[2]

                if r[6] == '0':
                    weight = u'确定'
                elif r[6] == '1':
                    weight = u'可能'
                else:
                    weight = u'。。。'

                search_result_list.append({'start_url': r[0], 'site_domain': r[1], 'black_domain_str': black_domain_str,
                                           'detail_or_list': detail_or_list, 'scope': r[4],
                                           'white_or_black': r[5], 'weight': weight,
                                           'regex': r[7]})
            self.conn.commit()
            print '[info]search_regex_by_user()', cnt, sqlStr
        except Exception, e:
            print '[error]search_regex_by_user()', e

        return search_result_list

    def search_start_url_by_user(self, user_id):
        search_result_list = []
        sqlStr = "SELECT DISTINCT(start_url) FROM url_rule WHERE user_id='" + user_id + "' ORDER BY start_url ASC"
        try:
            cnt = self.cur.execute(sqlStr)
            rs = self.cur.fetchall()
            for r in rs:
                search_result_list.append(r[0])
            self.conn.commit()
            print '[info]search_start_url_by_user()', cnt, sqlStr
        except Exception, e:
            print '[error]search_start_url_by_user()', e

        return search_result_list

    def check_password(self, user_id, password):
        sqlStr = "SELECT password FROM user WHERE user_id='" + user_id + "'"
        try:
            cnt = self.cur.execute(sqlStr)
            if cnt == 1:
                r = self.cur.fetchone()
                self.conn.commit()
                if password.strip() == r[0]:
                    print '[info]check_password() ok', user_id
                    return True
            else:
                print '[error]check_password() has more then one user_id ', cnt
                return False
        except Exception, e:
            print '[error]check_password()', e
            return False

    def get_current_main_setting(self, user_id):
        # 提取主页、域名
        start_url = ''
        site_domain = ''
        black_domain_str = ''
        sqlStr = "SELECT start_url, site_domain, black_domain_str, setting_json FROM current_domain_setting WHERE user_id='" + user_id + "'"
        try:
            cnt = self.cur.execute(sqlStr)
            if cnt == 1:
                (start_url, site_domain, black_domain_str, setting_json) = self.cur.fetchone()
                self.conn.commit()
                # print 'get_current_main_setting()', cnt, sqlStr
        except Exception, e:
            print 'get_current_main_setting()', e

        return start_url, site_domain, black_domain_str

    def set_current_main_setting(self, user_id='', start_url='', site_domain='', black_domain_str='', setting_json=''):
        # print 'set_current_main_setting() start'
        # 提取主页、域名
        sqlStr1 = "DELETE FROM current_domain_setting WHERE user_id='" + user_id + "'"
        sqlStr2 = "INSERT INTO current_domain_setting(user_id,start_url,site_domain,black_domain_str,setting_json) " \
                  "VALUES ('" + user_id + "','" + start_url + "','" + site_domain + "','" + black_domain_str + "','" + setting_json + "')"
        try:
            print '[info]set_current_main_setting()', sqlStr1
            self.cur.execute(sqlStr1)
            print '[info]set_current_main_setting()', sqlStr2
            cnt = self.cur.execute(sqlStr2)
            self.conn.commit()
        except Exception, e:
            print '[error]set_current_main_setting()', e, sqlStr1
            print '[error]set_current_main_setting()', e, sqlStr2

    def clean_current_main_setting(self, user_id):
        # 提取主页、域名
        sqlStr = "DELETE FROM current_domain_setting WHERE user_id = '" + user_id + "'"
        try:
            self.cur.execute(sqlStr)
            self.conn.commit()
        except Exception, e:
            print '[error]clean_current_main_setting()', e

    def get_regexs(self, type, user_id):
        # 0:detail,1:list
        if type == 'detail':
            detail_or_list = '0'
        else:
            detail_or_list = '1'
        regexs = []
        # 提取主页、域名
        start_url, site_domain, black_domain = self.get_current_main_setting(user_id)
        sqlStr = "SELECT scope,white_or_black,weight,regex,etc FROM url_rule WHERE user_id='" + user_id + "' AND start_url='" + start_url + "' AND site_domain = '" + site_domain + "' AND detail_or_list='" + detail_or_list + "'"
        try:
            cnt = self.cur.execute(sqlStr)
            rs = self.cur.fetchall()
            for r in rs:
                (scope, white_or_black, weight, regex, etc) = r
                regexs.append((scope, white_or_black, weight, regex, etc))
            self.conn.commit()
            # print 'get_regexs()', cnt, sqlStr
        except Exception, e:
            print '[error]get_regexs()', e
        return regexs

    def save_result_file(self, start_url, site_domain):
        # user_id = session['user_id']
        user_id = 'admin'
        tmp_path = ''
        # f = zipfile.ZipFile(EXPORT_FOLDER + 'result-list.zip', 'w', zipfile.ZIP_DEFLATED)
        # f.write(EXPORT_FOLDER + "result-list.log")
        # # f.write(EXPORT_FOLDER+"test.jpeg")
        # f.close()

        f = open(EXPORT_FOLDER + 'result-list.log')
        b = f.read()
        f.close()
        # os.remove(EXPORT_FOLDER + 'result-list.zip')

        # 将.zip写入表
        sql_str1 = "DELETE FROM result_file_list WHERE user_id='%s' AND start_url='%s' AND site_domain='%s'" % \
                   (user_id, start_url, site_domain)
        sql_str2 = "INSERT INTO result_file_list(user_id,start_url,site_domain,result_file,tmp_path) VALUES(%s,%s,%s,_binary%s,%s)"

        try:
            print '[info]save_result_file()', sql_str1
            self.cur.execute(sql_str1)
            print '[info]save_result_file()', sql_str2
            cnt = self.cur.execute(sql_str2, (user_id, start_url, site_domain, b, tmp_path,))
            self.conn.commit()
        except Exception, e:
            traceback.format_exc()
            print '[error]save_result_file()', e

    def get_result_file(self, start_url, site_domain):
        # user_id = session['user_id']
        user_id = 'admin'
        # 从mysql表中读取.zip，还原下载文件。
        sql_str = "SELECT result_file FROM result_file_list WHERE user_id='%s' AND start_url='%s' AND site_domain='%s'" % \
                  (user_id, start_url, site_domain)
        try:
            cnt = self.cur.execute(sql_str)
            d = self.cur.fetchone()[0]
        except Exception, e:
            print '[error]get_result_file()', e

        f = open(EXPORT_FOLDER + "result-list_copy.log", "wb")
        f.write(d)
        f.close()

        # f = zipfile.ZipFile(EXPORT_FOLDER + "result-list_aaa.zip", 'w', zipfile.ZIP_DEFLATED)
        # zipfile.ZipFile('result-list_aaa.jpeg')
        # f.extractall()
        # f.close()

        return EXPORT_FOLDER + "result-list_copy.log"


if __name__ == '__main__':
    start_url = 'http://bbs.tianya.cn'
    site_domain = 'bbs.tianya.cn'
    temp_path = 'd:\\workspace\\pyWorks\\spiderShow\\'
    mysql_db = MySqlDrive()
    mysql_db.save_result_file(start_url, site_domain)
    mysql_db.get_result_file(start_url, site_domain)
