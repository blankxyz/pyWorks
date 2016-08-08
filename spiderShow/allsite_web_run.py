#!/usr/bin/python
# coding=utf-8
import re
import os
import urlparse
import redis
import json
import datetime
import dedup
import MySQLdb
import ConfigParser
import subprocess
from bs4 import BeautifulSoup, Comment
import requests
import allsite_clean_url
import traceback
from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, request, session, url_for, flash, redirect
from flask import send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import validators
from wtforms import FieldList, IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api

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
    SHELL_LIST_CMD = config.get('windows', 'shell_list_cmd')
    SHELL_DETAIL_CMD = config.get('windows', 'shell_detail_cmd')
    SHELL_CONTENT_CMD = config.get('windows', 'shell_content_cmd')
    ALLSITE_INI = config.get('windows', 'allsite_ini')
else:
    RUN_FILE = config.get('linux', 'run_file')
    SHELL_LIST_CMD = config.get('linux', 'shell_list_cmd')
    SHELL_DETAIL_CMD = config.get('linux', 'shell_detail_cmd')
    SHELL_CONTENT_CMD = config.get('linux', 'shell_content_cmd')
    ALLSITE_INI = config.get('linux', 'allsite_ini')
# deploy
DEPLOY_HOST = config.get('deploy', 'deploy_host')
DEPLOY_PORT = config.get('deploy', 'deploy_port')
####################################################################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'success'
app.config['EXPORT_FOLDER'] = EXPORT_FOLDER
bootstrap = Bootstrap(app)
api = Api(app)  # restful

global process_id


##################################################################################################
class SearchCondForm(Form):  # user search
    start_url = StringField(label=u'主页', default='')
    start_url_sel = SelectField(label=u'历史记录', choices=[('', '')], default=('', ''))
    site_domain = StringField(label=u'限定域名', default='')
    search = SubmitField(label=u'查询')
    list_download = SubmitField(label=u'列表页结果')
    detail_download = SubmitField(label=u'详情页结果')
    recover = SubmitField(label=u'导入')


class SearchResultForm(Form):  # user search
    # select = BooleanField(label=u'选择', default=False)
    start_url = StringField(label=u'主页', default='')
    site_domain = StringField(label=u'限定域名', default='')
    black_domain_str = StringField(label=u'域名黑名单', default='')
    detail_or_list = BooleanField(label=u'列表/详情', default=False)
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    weight = SelectField(label=u'权重', choices=[('0', u'确定'), ('1', u'可能'), ('2', u'。。。')])
    score = IntegerField(label=u'匹配数', default=0)
    search_result_list = []


class RegexForm(Form):  # setting
    # select = BooleanField(label=u'选择', default=False)
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    weight = SelectField(label=u'权重', choices=[('0', u'确定'), ('1', u'可能'), ('2', u'。。。')])
    score = IntegerField(label=u'匹配数', default=0)


class ListRegexInputForm(Form):  # setting
    start_url = StringField(label=u'主页')  # 'http://cpt.xtu.edu.cn/'
    site_domain = StringField(label=u'限定域名')  # cpt.xtu.edu.cn'  # 湘潭大学
    white_list = StringField(label=u'白名单')
    black_domain_str = StringField(label=u'域名黑名单')

    result = StringField(label=u'转换结果')
    convert = SubmitField(label=u'<< 转换')
    url = StringField(label=u'URL例子')

    list_regex_list = FieldList(FormField(RegexForm), label=u'列表页-正则表达式')
    detail_regex_list = FieldList(FormField(RegexForm), label=u'详情页-正则表达式')

    mode = BooleanField(label=u'精确匹配', default=True)

    save_run_list = SubmitField(label=u'保存-执行(列表页)')
    save_run_detail = SubmitField(label=u'保存-执行(详情页)')


class ShowServerLogInputForm(Form):  # show_server_log
    unkown_sel = BooleanField(label=u'仅未匹配', default=False)
    refresh = SubmitField(label=u'刷新')


class ContentItemForm(Form):  # 内容提取
    # 标题，内容，作者，创建时间，
    title_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    title_exp = StringField(label=u'表达式')

    content_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    content_exp = StringField(label=u'表达式')

    author_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    author_exp = StringField(label=u'表达式')

    ctime_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    ctime_exp = StringField(label=u'表达式')

    save_run = SubmitField(label=u'保存并执行')


##################################################################################################
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
            sql_str1 = ("DELETE FROM url_rule WHERE user_id =%s AND start_url=%s AND site_domain=%s")
            parameter1 = (user_id, start_url, site_domain)
            print '[info]save_all_setting()', sql_str1 % parameter1
            self.cur.execute(sql_str1, parameter1)

            # detail_or_list = '0'  # 0:detail,1:list
            # scope = '0'           # 0:netloc,1:path,2:query
            # white_or_black = '0'  # 0:white,1:black
            # weight = '0'          # 0:高，1：中，2：低

            for item in detail_regex_save_list:
                regex = item['regex']
                weight = item['weight']
                detail_or_list = '0'
                scope = '1'
                if regex.find('/^') >= 0:
                    white_or_black = '1'  # 黑名单
                else:
                    white_or_black = '0'

                parameter2 = (user_id, start_url, site_domain, black_domain_str,
                              detail_or_list, scope, white_or_black, weight, regex)
                sql_str2 = "INSERT INTO url_rule(user_id,start_url,site_domain,black_domain_str,detail_or_list, " \
                           "scope,white_or_black,weight,regex) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                print '[info]save_all_setting()-detail', sql_str2 % parameter2
                ret_cnt = self.cur.execute(sql_str2, parameter2)
                self.conn.commit()

            for item in list_regex_save_list:
                regex = item['regex']
                weight = item['weight']
                detail_or_list = '1'
                scope = '1'
                if regex.find('/^') >= 0:
                    white_or_black = '1'  # 黑名单
                else:
                    white_or_black = '0'

                sql_str3 = "INSERT INTO url_rule(user_id,start_url,site_domain,black_domain_str,detail_or_list, " \
                           "scope,white_or_black,weight,regex) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                parameter3 = (user_id, start_url, site_domain, black_domain_str,
                              detail_or_list, scope, white_or_black, weight, regex)
                print '[info]save_all_setting()-list', sql_str3 % parameter3
                ret_cnt = self.cur.execute(sql_str3, parameter3)
                self.conn.commit()

        except Exception, e:
            ret_cnt = 0
            print '[error]save_all_setting()', e
            self.conn.rollback()

        return ret_cnt

    def save_content_setting(self, user_id, start_url, site_domain, title_exp, author_exp, content_exp, ctime_exp):
        # print 'save_content_setting() start...', start_url, site_domain
        ret_cnt = 0
        try:
            sql_str = ("DELETE FROM content_rule WHERE user_id =%s AND start_url=%s AND site_domain=%s")
            parameter = (user_id, start_url, site_domain)
            self.cur.execute(sql_str, parameter)

            list_regex = ''
            regex_or_xpath = '0'
            # title
            sql_title = "INSERT INTO content_rule(user_id,start_url,site_domain,list_regex,regex_or_xpath,item,content_rule) " \
                        "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            parameter_title = (user_id, start_url, site_domain, list_regex, regex_or_xpath, 'title', title_exp)
            print '[info]save_content_setting()', sql_title % parameter_title
            ret_cnt = self.cur.execute(sql_title, parameter_title)
            # author
            sql_author = "INSERT INTO content_rule(user_id,start_url,site_domain,list_regex,regex_or_xpath,item,content_rule) " \
                         "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            parameter_author = (user_id, start_url, site_domain, list_regex, regex_or_xpath, 'author', author_exp)
            print '[info]save_content_setting()', sql_author % parameter_author
            ret_cnt = self.cur.execute(sql_author, parameter_author)
            # content
            sql_content = "INSERT INTO content_rule(user_id,start_url,site_domain,list_regex,regex_or_xpath,item,content_rule) " \
                          "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            parameter_content = (user_id, start_url, site_domain, list_regex, regex_or_xpath, 'content', content_exp)
            print '[info]save_content_setting()', sql_content % parameter_content
            ret_cnt = self.cur.execute(sql_content, parameter_content)
            # ctime
            sql_ctime = "INSERT INTO content_rule(user_id,start_url,site_domain,list_regex,regex_or_xpath,item,content_rule) " \
                        "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            parameter_ctime = (user_id, start_url, site_domain, list_regex, regex_or_xpath, 'ctime', ctime_exp)
            print '[info]save_content_setting()', sql_ctime % parameter_ctime
            ret_cnt = self.cur.execute(sql_ctime, parameter_ctime)

            self.conn.commit()

        except Exception, e:
            ret_cnt = 0
            print '[error]save_content_setting()', e
            self.conn.rollback()

        return ret_cnt

    def search_regex_by_user(self, user_id, start_url, site_domain):
        search_result_list = []

        sql_str = "SELECT start_url,site_domain,black_domain_str,detail_or_list,scope,white_or_black,weight,regex" \
                  " FROM url_rule  WHERE user_id='" + user_id + "' AND start_url LIKE '%" + start_url + "%' AND site_domain LIKE '%" + site_domain + "%'"
        # parameter = (user_id, start_url, site_domain)

        try:
            cnt = self.cur.execute(sql_str)
            rs = self.cur.fetchall()
            for r in rs:
                # code 表意翻译
                if r[3] == '0':
                    detail_or_list = u'详情'
                else:
                    detail_or_list = u'列表'

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
            print '[info]search_regex_by_user()', cnt, sql_str
        except Exception, e:
            print '[error]search_regex_by_user()', e, sql_str

        return search_result_list

    def search_start_url_by_user(self, user_id):
        search_result_list = []
        sql_str = "SELECT DISTINCT(start_url) FROM url_rule WHERE user_id=%s ORDER BY start_url ASC"
        parameter = (user_id,)
        try:
            cnt = self.cur.execute(sql_str, parameter)
            rs = self.cur.fetchall()
            for r in rs:
                search_result_list.append(r[0])
            self.conn.commit()
            print '[info]search_start_url_by_user()', cnt, sql_str % parameter
        except Exception, e:
            print '[error]search_start_url_by_user()', e

        return search_result_list

    def check_password(self, user_id, password):
        sql_str = "SELECT password FROM user WHERE user_id=%s"
        parameter = (user_id,)
        try:
            cnt = self.cur.execute(sql_str, parameter)
            if cnt == 1:
                r = self.cur.fetchone()
                self.conn.commit()
                if password.strip() == r[0]:
                    print '[info]check_password() ok', parameter
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

        sql_str = "SELECT start_url, site_domain, black_domain_str, setting_json FROM current_domain_setting WHERE user_id=%s"
        parameter = (user_id,)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            if cnt == 1:
                (start_url, site_domain, black_domain_str, setting_json) = self.cur.fetchone()
                self.conn.commit()
                # print 'get_current_main_setting()', cnt, sql_str%parameter
        except Exception, e:
            print 'get_current_main_setting()', e

        return start_url, site_domain, black_domain_str

    def set_current_main_setting(self, user_id='', start_url='', site_domain='', black_domain_str='', setting_json=''):
        # print 'set_current_main_setting() start'
        # 提取主页、域名
        sql_str1 = "DELETE FROM current_domain_setting WHERE user_id=%s"
        parameter1 = (user_id,)

        sql_str2 = "INSERT INTO current_domain_setting(user_id,start_url,site_domain,black_domain_str,setting_json) " \
                   "VALUES (%s,%s,%s,%s,%s)"
        parameter2 = (user_id, start_url, site_domain, black_domain_str, setting_json)

        try:
            print '[info]set_current_main_setting()', sql_str1 % parameter1
            self.cur.execute(sql_str1, parameter1)

            print '[info]set_current_main_setting()', sql_str2 % parameter2
            cnt = self.cur.execute(sql_str2, parameter2)

            self.conn.commit()
        except Exception, e:
            print '[error]set_current_main_setting()', e, sql_str1 % parameter1
            print '[error]set_current_main_setting()', e, sql_str2 % parameter2

    def clean_current_main_setting(self, user_id):
        # 提取主页、域名
        sql_str = "DELETE FROM current_domain_setting WHERE user_id =%s"
        parameter = (user_id,)
        try:
            self.cur.execute(sql_str, parameter)
            self.conn.commit()
        except Exception, e:
            print '[error]clean_current_main_setting()', e, sql_str % parameter

    def get_current_regexs(self, type, user_id):
        # 0:detail,1:list
        if type == 'detail':
            detail_or_list = '0'
        else:
            detail_or_list = '1'
        regexs = []
        # 提取主页、域名
        start_url, site_domain, black_domain = self.get_current_main_setting(user_id)
        sql_str = "SELECT scope,white_or_black,weight,regex,etc FROM url_rule WHERE user_id=%s AND start_url=%s AND site_domain =%s AND detail_or_list=%s"
        parameter = (user_id, start_url, site_domain, detail_or_list)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            rs = self.cur.fetchall()
            for r in rs:
                (scope, white_or_black, weight, regex, etc) = r
                regexs.append((scope, white_or_black, weight, regex, etc))
            self.conn.commit()
            # print 'get_current_regexs()', cnt, sql_str % parameter
        except Exception, e:
            print '[error]get_current_regexs()', e, sql_str % parameter
        return regexs

    def save_result_file(self, start_url, site_domain):
        # user_id = session['user_id']
        user_id = 'admin'
        # f = zipfile.ZipFile(EXPORT_FOLDER + 'result-list.zip', 'w', zipfile.ZIP_DEFLATED)
        # f.write(EXPORT_FOLDER + "result-list.log")
        # # f.write(EXPORT_FOLDER+"test.jpeg")
        # f.close()

        f = open(EXPORT_FOLDER + 'result-list.log', 'r')
        list_b = f.read()
        f.close()

        f = open(EXPORT_FOLDER + 'result-detail.log')
        detail_b = f.read()
        f.close()

        # os.remove(EXPORT_FOLDER + 'result-list.zip')

        # 将.zip写入表
        sql_str1 = "DELETE FROM result_file WHERE user_id=%s AND start_url=%s AND site_domain=%s"
        parameter1 = (user_id, start_url, site_domain)

        sql_str2 = "INSERT INTO result_file(user_id,start_url,site_domain,list_result_file,detail_result_file) VALUES(%s,%s,%s,_binary%s,_binary%s)"
        parameter2 = (user_id, start_url, site_domain, list_b, detail_b,)

        try:
            print '[info]save_result_file()', sql_str1
            self.cur.execute(sql_str1, parameter1)

            print '[info]save_result_file()', sql_str2
            cnt = self.cur.execute(sql_str2, parameter2)

            self.conn.commit()
        except Exception, e:
            # traceback.format_exc()
            print '[error]save_result_file()', e

    def get_result_file(self, start_url):
        '''
        Args:
            start_url: is not empty string.
        Returns:
            list_copy_file: copy the log file from DB to EXPORT_FOLDER. with out path.
            detail_copy_file: ...
            cnt: 0:not found, >0: must be 1.
        '''
        if start_url is None or start_url == '':
            print '[error]get_result_file() start_url is None.'
            return None, None, 0

        # user_id = session['user_id']
        user_id = 'admin'
        cnt = 0

        try:
            # 从mysql表中读取log，还原下载文件。
            sql_str = "SELECT site_domain, list_result_file, detail_result_file FROM result_file WHERE user_id=%s AND start_url=TRIM(%s)"
            parameter = (user_id, start_url,)

            print '[info]get_result_file()', sql_str, parameter
            cnt = self.cur.execute(sql_str, parameter)
            if cnt == 0:
                print '[info]get_result_file() DB not found.', start_url
                return None, None, 0
            else:
                (site_domain, list_txt, detail_txt) = self.cur.fetchone()

                list_copy_file = 'result-list_(' + site_domain + ').log'
                f = open(EXPORT_FOLDER + list_copy_file, "wb")
                f.write(list_txt)
                f.close()

                detail_copy_file = 'result-detail_(' + site_domain + ').log'
                f = open(EXPORT_FOLDER + detail_copy_file, "wb")
                f.write(detail_txt)
                f.close()

                print '[info]get_result_file() DB >>', list_copy_file, detail_copy_file
                return list_copy_file, detail_copy_file, cnt

        except Exception, e:
            traceback.format_exc()
            print '[error]get_result_file()', e, start_url, cnt
            return None, None, 0

            # f = zipfile.ZipFile(EXPORT_FOLDER + "result-list_aaa.zip", 'w', zipfile.ZIP_DEFLATED)
            # zipfile.ZipFile('result-list_aaa.jpeg')
            # f.extractall()
            # f.close()


##################################################################################################
class RedisDrive(object):
    def __init__(self, start_url, site_domain):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果
        self.detail_urls_set_key = 'detail_urls_set_%s' % self.site_domain  # 输出详情页URL
        self.manual_w_list_rule_zset_key = 'manual_w_list_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_list_rule_zset_key = 'manual_b_list_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.manual_w_detail_rule_zset_key = 'manual_w_detail_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_detail_rule_zset_key = 'manual_b_detail_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        self.detail_flg = 9

    def get_detail_urls(self):
        return self.conn.smembers(self.detail_urls_set_key)

    def get_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.done_flg, start=0,
                                       num=SHOW_MAX)

    def get_done_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.done_flg, max=self.done_flg, start=0,
                                       num=SHOW_MAX)

    def get_matched_rate(self):
        cnt = 0
        urls = self.get_detail_urls()
        if len(urls) == 0:
            return 0.0

        de = dedup.Dedup('192.168.110.110', 'dedup')
        for url in urls:
            # if (de.is_dedup(url)):
            #     print 'matched:', url
            #     cnt += 1
            cnt = 1

        return float(cnt) / len(urls)

    def get_done_list_rate(self):
        cnt = 0
        urls = self.get_list_urls()
        if len(urls) == 0:
            return 0.0

        done = self.get_done_list_urls()
        return float(len(done)) / len(urls)

    def get_keywords_match(self):
        score_list = []
        keywords = []
        list_rules = self.conn.zrevrangebyscore(self.manual_w_list_rule_zset_key,
                                                max=999999, min=0, start=0, num=5, withscores=True)
        for rule, score in dict(list_rules).iteritems():
            score_list.append(str(score))
            keywords.append(rule)

        detail_rules = self.conn.zrevrangebyscore(self.manual_w_detail_rule_zset_key,
                                                  max=999999, min=0, start=0, num=5, withscores=True)
        for rule, score in dict(detail_rules).iteritems():
            score_list.append(str(score))
            keywords.append(rule)

        matched_cnt = ','.join(score_list)
        return keywords, matched_cnt

    def covert_redis_cnt_to_json(self):
        # rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        # rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        rule0_cnt = 0
        rule1_cnt = 0
        detail_cnt = self.conn.scard(self.detail_urls_set_key)
        list_cnt = self.conn.zcard(self.list_urls_zset_key)
        list_done_urls = self.conn.zrangebyscore(
            self.list_urls_zset_key, self.done_flg, self.done_flg)
        list_done_cnt = len(list_done_urls)

        detail_done_urls = self.conn.zrangebyscore(self.list_urls_zset_key, self.detail_flg, self.detail_flg)
        detail_done_cnt = len(detail_done_urls)

        t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cnt_info = {'times': t_stamp, 'rule0_cnt': rule0_cnt, 'rule1_cnt': rule1_cnt,
                    'detail_cnt': detail_cnt, 'list_cnt': list_cnt, 'list_done_cnt': list_done_cnt,
                    'detail_done_cnt': detail_done_cnt}
        self.conn.hset(
            self.process_cnt_hset_key, t_stamp, json.dumps(cnt_info, sort_keys=True))
        # print cnt_info
        jsonStr = json.dumps(cnt_info)
        fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON + '(' + self.site_domain + ').json', 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()


##################################################################################################
class CollageProcessInfo(object):
    def __init__(self, site_domain):
        self.site_domain = site_domain
        self.json_file = PROCESS_SHOW_JSON

    def convert_file_to_list(self):
        rule0_cnt = []
        rule1_cnt = []
        detail_cnt = []
        list_cnt = []
        list_done_cnt = []
        detail_done_cnt = []
        times = []

        fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON + '(' + self.site_domain + ').json', 'r')
        for line in fp.readlines():
            dic = eval(line)
            times.append(dic.get('times'))
            rule0_cnt.append(dic.get('rule0_cnt'))
            rule1_cnt.append(dic.get('rule1_cnt'))
            detail_cnt.append(dic.get('detail_cnt'))
            list_cnt.append(dic.get('list_cnt'))
            list_done_cnt.append(dic.get('list_done_cnt'))
            detail_done_cnt.append(dic.get('detail_done_cnt'))
        fp.close()
        return times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt, detail_done_cnt


##################################################################################################
class Advise(object):
    def __init__(self, start_url, site_domain, black_domain_list):
        self.site_domain = site_domain
        self.start_url = start_url
        self.black_domain_list = black_domain_list
        self.cleaner = allsite_clean_url.Cleaner(site_domain=self.site_domain, black_domain_list=self.black_domain_list)

    def header_maker(self, text=''):
        if not text:
            text = {'Proxy-Connection': 'keep-alive',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Upgrade-Insecure-Requests': 1,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
                    }
        return text

    def get_clean_soup(self, url):
        headers = self.header_maker()
        try:
            data = requests.get(url, headers=headers, timeout=5)
        except Exception, e:
            print "[error]get_clean_soup()", e
            return None
        soup = BeautifulSoup(data.content, 'lxml')
        # print 'before',soup.prettify()
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]
        [input.extract() for input in soup('input')]
        [input.extract() for input in soup('form')]
        [foot.extract() for foot in soup(attrs={'class': 'footer'})]
        [foot.extract() for foot in soup(attrs={'class': 'bottom'})]
        # print 'after',soup.prettify()
        return soup

    def get_page_valid_urls(self, soup, org_url):
        # print '[info]get_page_valid_urls() start'
        all_links = []
        remove_links = []
        try:
            for tag in soup.find_all("a"):
                if tag.has_attr('href'):
                    all_links.append(tag['href'])

            for tag in soup.find_all("a", href=re.compile(r"(javascript.*?|#.*?)", re.I)):
                if tag.has_attr('href'):
                    remove_links.append(tag['href'])

        except Exception, e:
            print '[error]get_page_valid_urls()', e

        removed = list(set(all_links) - set(remove_links))

        urls = self.urls_join(org_url, removed)
        urls = self.filter_links(urls)
        # print '[info]get_page_valid_urls() end'
        return urls

    def urls_join(self, org_url, links):
        # print '[info]urls_join() start',org_url,links
        urls = []
        for link in links:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(link.strip())
            if scheme:
                url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
            else:
                link = urlparse.urlunparse(('', '', path, params, query, ''))
                # url = urlparse.urljoin(org_url, urllib.quote(link))
                # print '[info]urljoin()', org_url, link
                url = urlparse.urljoin(org_url, link)

            urls.append(url)

        # print '[info]urls_join() end', urls
        return urls

    def filter_links(self, urls):
        # print '[INFO]filter_links() start', len(urls), urls
        try:
            # 下载页
            urls = filter(lambda x: self.cleaner.is_suffixes_ok(x), urls)
            # print 'filter_links() is_download', len(urls)
            # 错误url识别
            urls = filter(lambda x: not self.cleaner.is_error_url(x), urls)
            # print 'filter_links() is_error_url', len(urls)
            # 清洗无效参数#?
            urls = self.cleaner.url_clean(urls)
            # 跨域检查
            urls = filter(lambda x: self.cleaner.check_cross_domain(x), urls)
            # print 'filter_links() check_cross_domain', len(urls)
            # 黑名单过滤
            urls = filter(lambda x: not self.cleaner.in_black_list(x), urls)  # bbs. mail.
            # print 'filter_links() in_black_list', len(urls)
            # 链接时间过滤
            # urls = filter(lambda x: not self.cleaner.is_old_url(x), urls)
            # 非第一页链接过滤
            urls = filter(lambda x: not self.cleaner.is_next_page(x), urls)
            # print 'filter_links() is_next_page', len(urls)
            # for url in urls:
            #     if  self.conn.zrank(self.detail_urls_zset_key, url) is not None:
            #         print 'remove:', url
            #         urls.remove(url)
            # 去重
            urls = list(set(urls))
            # print 'filter_links() set', len(urls)
            # 404
            # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
            # print '[INFO]filter_links() end', len(urls), urls
        except Exception, e:
            print '[ERROR]filter_links()', e
        return urls


##################################################################################################
class Util(object):
    def __init__(self):
        pass

    def convert_path_to_rule(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print path
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''
        # print suffix,path
        split_path = path.split('/')
        # print split_path
        new_path_list = []
        for p in split_path:
            regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', regex)
            new_path_list.append(self.convert_regex_format(regex))
        # print new_path
        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

    def convert_regex_format(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
        '''
        ret = ''
        digit = '\d'
        word = '[a-zA-Z]'
        cnt = 0
        pos = 0
        temp = ''
        while pos <= len(rule):
            if rule[pos:pos + len(digit)] == digit:
                if temp.find(digit) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (digit, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d}' % (word, cnt)
                pos = pos + len(word)
            elif pos == len(rule):
                ret = ret + temp
                break
            else:
                ret = ret + temp + rule[pos]
                temp = ''
                cnt = 0
                pos = pos + 1
        return ret

    def modify_config(self, start_urls, site_domain, black_domain_str, detail_rule_str, list_rule_str, mode):
        try:
            config = ConfigParser.ConfigParser()
            config.read(ALLSITE_INI)
            config.set('spider', 'start_urls', start_urls)
            config.set('spider', 'site_domain', site_domain)
            config.set('spider', 'black_domain_list', black_domain_str)
            config.set('spider', 'list_rule_list', list_rule_str)
            config.set('spider', 'detail_rule_list', detail_rule_str)
            config.set('spider', 'mode', mode)
            fp = open(ALLSITE_INI, "w")
            config.write(fp)
            # write_ready = False
            # copy_list = []
            # fp = open('../spider/config.py', "r")
            # for row in fp.readlines():
            #     if row.find('spider-modify-start')>=0: write_ready = True
            #     if row.find('spider-modify-end')>=0: write_ready = False
            #     if write_ready:
            #         if row.find('START_URLS')>=0:
            #             row = "START_URLS = '" + start_urls + "'\n"
            #         if row.find('SITE_DOMAIN')>=0:
            #             row = "SITE_DOMAIN = '"+ site_domain + "'\n"
            #         if row.find('BLACK_DOMAIN_LIST')>=0:
            #             row = "BLACK_DOMAIN_LIST = '"+ black_domain_str + "'\n"
            #         if row.find('DETAIL_RULE_LIST')>=0:
            #             row = "DETAIL_RULE_LIST = '"+ detail_rule_str + "'\n"
            #         if row.find('LIST_RULE_LIST')>=0:
            #             row = "LIST_RULE_LIST = '"+ list_rule_str + "'\n"
            #     copy_list.append(row)
            #
            # fp.close()
            #
            # fp = open('../spider/config.py', "w")
            # for row in copy_list: fp.write(row)
            # fp.close()

            print '[info] modify_config() ok.'
            return True
        except Exception, e:
            print "[error] modify_config(): %s" % e
            return False


##################################################################################################
@app.route("/aaaaaaaaa", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        mysql_db = MySqlDrive()
        if mysql_db.check_password(user_id, password):
            session['user_id'] = user_id  # password OK！
            mysql_db.set_current_main_setting(user_id=user_id)
            # return redirect(url_for('menu'))
            return render_template('menu.html', user_id=session.get('user_id'))
        else:
            flash(u"输入密码不正确。")

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def menu():
    user_id = 'admin'
    mysql_db = MySqlDrive()
    mysql_db.clean_current_main_setting(user_id)
    return render_template('menu.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', err=e), 500


@app.route('/convert', methods=["GET", "POST"])
def convert_to_regex():
    ret = {}
    convert_url = request.args.get('convert_url')
    util = Util()
    ret['regex'] = util.convert_path_to_rule(convert_url)
    jsonStr = json.dumps(ret, sort_keys=True)
    print 'convert_to_regex()', convert_url, '->', jsonStr
    return jsonStr


@app.route('/user_search', methods=['GET', 'POST'])
def user_search():
    # user_id = session.get('user_id')
    user_id = 'admin'
    print '[info]user_search()', user_id
    mysql_db = MySqlDrive()

    inputForm = SearchCondForm(request.form)
    start_url = inputForm.start_url.data
    site_domain = inputForm.site_domain.data
    # 设定域名选项
    select_items = [(i, i) for i in mysql_db.search_start_url_by_user(user_id)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.start_url_sel.choices = select_items
    start_url_sel = inputForm.start_url_sel.data

    outputForm = SearchResultForm()
    outputForm.search_result_list = mysql_db.search_regex_by_user(user_id, start_url, site_domain)

    # 点击 查询 按钮
    if inputForm.search.data:
        if len(outputForm.search_result_list) == 0:
            flash(u'请输入合适的查询条件（ 主页，限定域名   支持like查询 ）。')
        else:
            flash(u'请确认的查询结果。')

        if start_url_sel != '':
            start_url = start_url_sel
        outputForm.search_result_list = mysql_db.search_regex_by_user(user_id, start_url, site_domain)

    # 点击 导出列表页历史结果 按钮
    if inputForm.list_download.data:
        if start_url_sel == '':
            flash(u'请从历史记录中选择主页。')
        else:
            list_copy_file, detail_copy_file, cnt = mysql_db.get_result_file(start_url_sel)
            if list_copy_file is not None and cnt != 0:
                flash(u'列表页历史记录下载成功。')
                return send_from_directory(app.config['EXPORT_FOLDER'], list_copy_file, as_attachment=True)

            if cnt == 0:
                flash(u'没有列表页历史记录。')
                print '[error]user_search() get_result_file() not found.', start_url_sel

    # 点击 导出详情页历史结果 按钮
    if inputForm.detail_download.data:
        if start_url_sel == '':
            flash(u'请从历史记录中选择主页。')
        else:
            list_copy_file, detail_copy_file, cnt = mysql_db.get_result_file(start_url_sel)
            if detail_copy_file is not None and cnt != 0:
                flash(u'详情页历史记录下载成功。')
                return send_from_directory(app.config['EXPORT_FOLDER'], detail_copy_file, as_attachment=True)

            if cnt == 0:
                flash(u'没有详情页历史记录。')
                print '[error]user_search() get_result_file() not found.', start_url_sel

    # 点击 导入 按钮
    if inputForm.recover.data:
        if len(outputForm.search_result_list) > 0:
            d = set()
            for i in outputForm.search_result_list:
                start_url = i['start_url']
                site_domain = i['site_domain']
                d.add(start_url + site_domain)

            if len(d) == 1:
                mysql_db.set_current_main_setting(user_id, start_url, site_domain, '', '')
            else:
                flash(u'请选择唯一的首页和域名进行导入。')
        else:
            flash(u'请检索取得结果后再导入。')

    return render_template('user.html', user_id=user_id, inputForm=inputForm, outputForm=outputForm)


@app.route('/show_process', methods=['GET', 'POST'])
def show_process():
    # user_id = session.get('user_id')
    user_id = 'admin'
    inputForm = ListRegexInputForm()
    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain = mysql_db.get_current_main_setting(user_id)
    print '[info]show_process()', user_id, start_url, site_domain, black_domain
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show_process.html', inputForm=inputForm)

    # 从redis提取实时信息，转换成json文件
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    redis_db.covert_redis_cnt_to_json()

    collage = CollageProcessInfo(site_domain)
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt, detail_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    # print list_done_cnt[-1],list_cnt[-1]
    if len(list_cnt) == 0 or list_cnt[-1] == 0:
        list_done_rate = 0
    else:
        list_done_rate = float(list_done_cnt[-1]) / list_cnt[-1] * 100.0

    if len(list_cnt) == 0 or list_cnt[-1] == 0:
        detail_done_rate = 0
    else:
        detail_done_rate = float(detail_done_cnt[-1]) / list_cnt[-1] * 100.0

    keywords, matched_cnt = redis_db.get_keywords_match()

    regexs_str = ("'" + "','".join(keywords) + "'")
    # from flask import Markup
    # 将json映射到html
    flash(u'每隔10秒刷新 ' + start_url + u' 的实时采集信息。')
    return render_template('show_process.html',
                           times=times,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt,
                           detail_done_cnt=detail_done_cnt,
                           list_done_rate=list_done_rate,
                           list_todo_rate=(100.0 - list_done_rate),
                           detail_done_rate=detail_done_rate,
                           detail_todo_rate=(100.0 - detail_done_rate),
                           keywords=keywords,
                           regexs_str=regexs_str,
                           matched_cnt=matched_cnt)


@app.route('/save_finally_result', methods=['GET', 'POST'])
def save_finally_result():
    # user_id = session.get('user_id')
    user_id = 'admin'
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain = mysql_db.get_current_main_setting(user_id)
    # 将实时结果作为最终结果保存到DB
    mysql_db.save_result_file(start_url, site_domain)
    flash(u'列表页结果保存DB成功。')
    print '[info]save finally result to DB OK.'
    return redirect(url_for('show_process'), 302)


@app.route('/show_server_log', methods=['GET', 'POST'])
def show_server_log():
    # user_id = session.get('user_id')
    user_id = 'admin'
    inputForm = ShowServerLogInputForm(request.form)
    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain_str = mysql_db.get_current_main_setting(user_id)
    print 'show_server_log()', start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show_server_log.html', inputForm=inputForm, server_log_list=[])

    # windows
    if os.name == 'nt':
        import random
        f = open('web_server.log', 'r').readlines()
        l = []
        for i in range(80):
            num = random.random()
            n = int(num * len(f))
            l.append(f[n])
        server_log_list = l

    else:
        if inputForm.unkown_sel.data:
            cmd = 'tail -10000 ./web_server.log | grep unkown |tail -80'
        else:
            cmd = 'tail -80 ./web_server.log'

        p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
        server_log_list = p.stdout.readlines()

    if len(server_log_list) == 0:
        flash(u'请使用 ./web_start.sh 生成 web_server.log 。')
        return render_template('show_server_log.html', inputForm=inputForm, server_log_list=[])

    # 保存 实时 列表页结果
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    fp = open(EXPORT_FOLDER + '/result-list.log', 'w')
    for line in redis_db.conn.zrange(redis_db.list_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
    fp.close()

    # 保存 实时 详情页结果
    fp = open(EXPORT_FOLDER + '/result-detail.log', 'w')
    for line in redis_db.conn.smembers(redis_db.detail_urls_set_key):
        fp.write(line + '\n')
    fp.close()

    return render_template('show_server_log.html', inputForm=inputForm,
                           server_log_list=[x.encode('utf8') for x in server_log_list])


@app.route('/setting_list_init', methods=['GET', 'POST'])
def setting_list_init():
    '''
    从MySql初始化Web页面和Redis
    '''
    INIT_MAX = 10
    # user_id = session.get('user_id')
    user_id = 'admin'
    inputForm = ListRegexInputForm()

    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain_str = mysql_db.get_current_main_setting(user_id)
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        for j in range(INIT_MAX):
            inputForm.detail_regex_list.append_entry()

        for j in range(INIT_MAX):
            inputForm.list_regex_list.append_entry()

        return render_template('setting.html', inputForm=inputForm)
    else:
        inputForm.start_url.data = start_url
        inputForm.site_domain.data = site_domain
        inputForm.black_domain_str.data = black_domain_str

    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    #### 从MySql 设置/还原 redis 和 页面(详情页)
    i = 0
    for (scope, white_or_black, weight, regex, etc) in mysql_db.get_current_regexs('detail', user_id):
        # 还原redis
        if regex.find('/^') < 0:  # 白名单
            if redis_db.conn.zrank(redis_db.manual_w_detail_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_w_detail_rule_zset_key, 0, regex)
                score = 0
            else:
                score = redis_db.conn.zscore(redis_db.manual_w_detail_rule_zset_key, regex)
        else:  # 黑名单
            if redis_db.conn.zrank(redis_db.manual_b_detail_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_b_detail_rule_zset_key, 0, regex)
                score = 0
            else:
                score = redis_db.conn.zscore(redis_db.manual_b_detail_rule_zset_key, regex)
        # 还原页面
        # regex_data = MultiDict([('regex', regex), ('weight', weight), ('score', int(score))])
        # regexForm = RegexForm(regex_data)
        # inputForm.detail_regex_list.entries[i] = regexForm

        regexForm = RegexForm()
        regexForm.regex = regex
        regexForm.weight = weight
        regexForm.score = int(score)
        inputForm.detail_regex_list.append_entry(regexForm)
        i += 1

    for j in range(INIT_MAX - i):
        inputForm.detail_regex_list.append_entry()

    ####  从MySql 设置/还原 redis 和 页面(列表页)
    i = 0
    for (scope, white_or_black, weight, regex, etc) in mysql_db.get_current_regexs('list', user_id):
        # 还原redis
        if regex.find('/^') < 0:  # 白名单
            if redis_db.conn.zrank(redis_db.manual_w_list_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_w_list_rule_zset_key, 0, regex)
                score = 0
            else:
                score = redis_db.conn.zscore(redis_db.manual_w_list_rule_zset_key, regex)
        else:  # 黑名单
            if redis_db.conn.zrank(redis_db.manual_b_list_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_b_list_rule_zset_key, 0, regex)
                score = 0
            else:
                score = redis_db.conn.zscore(redis_db.manual_b_list_rule_zset_key, regex)
        # 还原页面
        # regex_data = MultiDict([('regex', regex), ('weight', weight), ('score', int(score))])
        # regexForm = RegexForm(regex_data)
        # inputForm.list_regex_list.entries[i] = regexForm

        regexForm = RegexForm()
        regexForm.regex = regex
        regexForm.weight = weight
        regexForm.score = int(score)
        inputForm.list_regex_list.append_entry(regexForm)
        i += 1

    for j in range(INIT_MAX - i):
        inputForm.list_regex_list.append_entry()

    flash(u'初始化配置完成')
    return render_template('setting.html', inputForm=inputForm)


@app.route('/list_save_and_run', methods=['POST'])
def setting_list_save_and_run():
    # user_id = session['user_id']
    user_id = 'admin'
    global process_id
    inputForm = ListRegexInputForm(request.form)
    # if inputForm.validate_on_submit():
    # if request.method == 'POST' and inputForm.validate():
    start_url = inputForm.start_url.data
    site_domain = inputForm.site_domain.data
    site_domain = site_domain.split('/')[0]
    black_domain_str = inputForm.black_domain_str.data
    if inputForm.mode.data == False:
        mode = 'all'  # 全部
    else:
        mode = 'exact'  # 精确匹配

    if start_url.strip() == '' or site_domain.strip() == '':
        flash(u'必须设置主页、域名信息！')
        return render_template('setting.html', inputForm=inputForm)

    #### 保存详情页配置
    detail_regex_save_list = []
    for r in inputForm.detail_regex_list.data:
        # select = r['select']
        regex = r['regex']
        weight = r['weight']
        score = r['score']
        if regex != '':
            detail_regex_save_list.append({'regex': regex, 'weight': weight})

    #### 保存列表页配置
    list_regex_save_list = []
    for r in inputForm.list_regex_list.data:
        # select = r['select']
        regex = r['regex']
        weight = r['weight']
        score = r['score']
        if regex != '':
            list_regex_save_list.append({'regex': regex, 'weight': weight})

    #### check 详情页/列表页 正则表达式的整合性
    if len(list_regex_save_list) + len(detail_regex_save_list) == 0:
        flash(u"请填写并勾选要执行的 列表/详情页正则表达式。")
        return render_template('setting.html', inputForm=inputForm)

    if len(list_regex_save_list) != len(set([i['regex'] + i['weight'] for i in list_regex_save_list])):
        flash(u"列表页正则表达式有重复。")
        return render_template('setting.html', inputForm=inputForm)

    if len(detail_regex_save_list) != len(set([i['regex'] + i['weight'] for i in detail_regex_save_list])):
        flash(u"详情页正则表达式有重复。")
        return render_template('setting.html', inputForm=inputForm)

    if len(set([i['regex'] for i in list_regex_save_list]).intersection(
            set([i['regex'] for i in detail_regex_save_list]))) > 0:
        flash(u"列表和详情页中的正则表达式不能重复。")
        return render_template('setting.html', inputForm=inputForm)

    #### 清空所有Redis,保存手工配置,用于匹配次数积分。
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    for regex in redis_db.conn.zrange(redis_db.manual_w_list_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_w_list_rule_zset_key, regex)
    for item in list_regex_save_list:
        if item['regex'].find('/^') < 0:
            redis_db.conn.zadd(redis_db.manual_w_list_rule_zset_key, 0, item['regex'])

    for regex in redis_db.conn.zrange(redis_db.manual_b_list_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_b_list_rule_zset_key, regex)
    for item in list_regex_save_list:
        if item['regex'].find('/^') >= 0:
            redis_db.conn.zadd(redis_db.manual_b_list_rule_zset_key, 0, item['regex'])

    for regex in redis_db.conn.zrange(redis_db.manual_w_detail_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_w_detail_rule_zset_key, regex)
    for item in detail_regex_save_list:
        if item['regex'].find('/^') < 0:
            redis_db.conn.zadd(redis_db.manual_w_detail_rule_zset_key, 0, item['regex'])

    for regex in redis_db.conn.zrange(redis_db.manual_b_detail_rule_zset_key, start=0, end=-1):
        redis_db.conn.zrem(redis_db.manual_b_detail_rule_zset_key, regex)
    for item in detail_regex_save_list:
        if item['regex'].find('/^') >= 0:
            redis_db.conn.zadd(redis_db.manual_b_detail_rule_zset_key, 0, item['regex'])

    #### 保存所有手工配置信息到MySql
    setting_json = ''
    mysql_db = MySqlDrive()
    mysql_db.set_current_main_setting(user_id=user_id, start_url=start_url, site_domain=site_domain,
                                      black_domain_str=black_domain_str, setting_json=setting_json)

    cnt = mysql_db.save_all_setting(user_id=user_id, start_url=start_url, site_domain=site_domain,
                                    setting_json=setting_json, black_domain_str=black_domain_str,
                                    detail_regex_save_list=detail_regex_save_list,
                                    list_regex_save_list=list_regex_save_list)
    if cnt == 1:
        flash(u"MySQL保存完毕.")
        print u'[info]setting_list_save_and_run() MySQL save success.'
    else:
        flash(u"MySQL保存失败.")
        print u'[error]setting_list_save_and_run() MySQL save failure.'
        return render_template('setting.html', inputForm=inputForm)

    #### 修改配置文件的执行入口信息
    detail_rule_str = ''
    for item in detail_regex_save_list:
        detail_rule_str += item['regex'] + '@'

    list_rule_str = ''
    for item in list_regex_save_list:
        list_rule_str += item['regex'] + '@'

    util = Util()
    ret = util.modify_config(start_urls=start_url, site_domain=site_domain, black_domain_str=black_domain_str,
                             list_rule_str=list_rule_str, detail_rule_str=detail_rule_str, mode=mode)
    if ret == False:
        flash(u"修改" + INIT_CONFIG + u"文件失败.")
        print u'[error]setting_main_save_and_run() modify ' + INIT_CONFIG + u' failure.'
        return render_template('setting.html', inputForm=inputForm)

    # 执行抓取程序
    if inputForm.save_run_list.data:
        if os.name == 'nt':
            # DOS "start" command
            print '[info] run windows', SHELL_LIST_CMD
            os.startfile(SHELL_LIST_CMD)
        else:
            print '[info] run linux', SHELL_LIST_CMD
            p = subprocess.Popen(SHELL_LIST_CMD, shell=True)
            process_id = p.pid
            print '[info] process_id:', process_id

    if inputForm.save_run_detail.data:
        if os.name == 'nt':
            # DOS "start" command
            print '[info] run windows', SHELL_DETAIL_CMD
            os.startfile(SHELL_DETAIL_CMD)
        else:
            print '[info] run linux', SHELL_DETAIL_CMD
            p = subprocess.Popen(SHELL_DETAIL_CMD, shell=True)
            process_id = p.pid
            print '[info] process_id:', process_id

    return render_template('setting.html', inputForm=inputForm)


@app.route('/setting_content_init', methods=['GET', 'POST'])
def setting_content_init():
    # user_id = session['user_id']
    user_id = 'admin'
    inputForm = ContentItemForm(request.form)
    return render_template('setting_content.html', inputForm=inputForm)


@app.route('/content_save_and_run', methods=['GET', 'POST'])
def content_save_and_run():
    # user_id = session['user_id']
    user_id = 'admin'
    inputForm = ContentItemForm(request.form)

    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain = mysql_db.get_current_main_setting(user_id)
    print '[info]content_save_and_run()', user_id, start_url, site_domain, black_domain
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('setting_content.html', inputForm=inputForm)

    cnt = mysql_db.save_content_setting(user_id=user_id, start_url=start_url, site_domain=site_domain,
                                        title_exp=inputForm.title_exp.data, author_exp=inputForm.author_exp.data,
                                        content_exp=inputForm.content_exp.data, ctime_exp=inputForm.ctime_exp.data)
    if cnt == 1:
        flash(u"MySQL保存完毕.")
        print u'[info]content_save_and_run() MySQL save success.'
    else:
        flash(u"MySQL保存失败.")
        print u'[error]content_save_and_run() MySQL save failure.'
        return render_template('setting_content.html', inputForm=inputForm)

    if os.name == 'nt':
        # DOS "start" command
        print '[info] run windows', SHELL_CONTENT_CMD
        os.startfile(SHELL_CONTENT_CMD)
    else:
        print '[info] run linux', SHELL_CONTENT_CMD
        p = subprocess.Popen(SHELL_CONTENT_CMD, shell=True)
        process_id = p.pid
        print '[info] process_id:', process_id

    return render_template('setting_content.html', inputForm=inputForm)


@app.route('/export/<path:filename>')
def download_file(filename):
    print 'download_file()', filename
    return send_from_directory(app.config['EXPORT_FOLDER'], filename, as_attachment=True)


@app.route('/export_upload', methods=['GET', 'POST'])
def export_upload():
    if request.method == 'GET':
        return render_template('export.html')

    elif request.method == 'POST':
        f = request.files['file']
        # 获取一个安全的文件名，仅支持ascii字符。
        f_name = secure_filename(f.filename)
        f.save(os.path.join(EXPORT_FOLDER, f_name))
        flash(u"上传成功.")
        return render_template('export.html')


@app.route('/kill', methods=['GET', 'POST'])
def kill():
    if os.name == 'nt':
        flash(u"请手工关闭windows控制台.")
        # os.system("taskkill /PID %s /F" % process_id)
    else:
        flash(u"已经结束进程.")
        subprocess.Popen(['/bin/sh', '-c', './kill.sh'])
    return redirect(url_for('show_process'), 302)


@app.route('/resetZero', methods=['GET', 'POST'])
def reset_zero():
    # user_id = session['user_id']
    user_id = 'admin'
    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain = mysql_db.get_current_main_setting(user_id)

    fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON + '(' + site_domain + ').json', 'w')
    fp.write('')
    fp.close()
    return redirect(url_for('show_process'), 302)


@app.route('/setting_detail_init', methods=['GET', 'POST'])
def setting_detail_init():
    inputForm = None
    return render_template('setting_content.html', inputForm=inputForm)


@app.route('/export_init')
def export_import():
    flash(u"请选择导入/导出操作。")
    return redirect(url_for('export_upload'), 302)


##########################################################################################
#  restful api
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        print TODOS
        return TODOS[todo_id], 201


##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')

##########################################################################################

if __name__ == '__main__':
    if INIT_CONFIG.find('deploy') > 0:
        app.run(host=DEPLOY_HOST, port=DEPLOY_PORT, debug=False)
    else:
        app.run(debug=True)

        # -------------------unit test-----------------------------------
        # mysql = MySqlDrive()
        # print mysql.save_to_mysql('http://bbs.tianya.com','bbs.tianya.con','aaaaaaaaaaaaaaa')
        # print mysql.get_current_main_setting()
        # modify_config('http://bbs.tianya.cn','bbs.tianya.cn','blog.tianya.cn','\/$@/[a-zA-Z]{1,}/[a-zA-Z]{1,}/d{4}/?d{4}/d{1,}.html@/L/d{1,}.shtml@','list@index@')
