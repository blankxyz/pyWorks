#!/usr/bin/python
# coding=utf-8
import re
import os
import time
import urlparse, urllib
import redis
import json
import datetime
import dedup
import MySQLdb
import ConfigParser
import subprocess
from bs4 import BeautifulSoup, Comment
import requests
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
from myreadability import myreadability

####################################################################
# windows or linux or mac
MY_OS = os.getenv('SPIDER_OS')
if MY_OS is None:
    print '[error]please set a SPIDER_OS.'
    exit(-1)
else:
    print '[info]--- The OS is: %s ----' % MY_OS
####################################################################
if MY_OS == 'linux':
    INIT_CONFIG = './web_run.deploy.ini'
else:  # mac or windows
    INIT_CONFIG = './web_run.dev.ini'
####################################################################
config = ConfigParser.ConfigParser()
if len(config.read(INIT_CONFIG)) == 0:
    print '[error]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[info]read the config file.', INIT_CONFIG
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
# shell
SHELL_ADVICE_CMD = config.get(MY_OS, 'shell_advice_cmd')
SHELL_LIST_CMD = config.get(MY_OS, 'shell_list_cmd')
SHELL_DETAIL_CMD = config.get(MY_OS, 'shell_detail_cmd')
SHELL_CONTENT_CMD = config.get(MY_OS, 'shell_content_cmd')
ALLSITE_INI = config.get(MY_OS, 'allsite_ini')
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


######## setting_advice.html ##############################################################################
class AdviceRegexForm(Form):  # advice_setting
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}//[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    score = IntegerField(label=u'匹配数', default=0)
    select = SelectField(label=u'采用', choices=[('0', u'-'), ('1', u'列表'), ('2', u'详情')])


class AdviceKeyWordForm(Form):  # advice_setting
    keyword = StringField(label=u'关键字')
    score = IntegerField(label=u'匹配数', default=0)
    select = SelectField(label=u'采用', choices=[('0', u'-'), ('1', u'列表'), ('2', u'详情')])


class AdviceRegexListInputForm(Form):  # setting
    start_url = StringField(label=u'主页')
    site_domain = StringField(label=u'限定域名')
    white_list = StringField(label=u'白名单')
    black_domain_str = StringField(label=u'域名黑名单', description='请按照 域名1;域名2;域名3; 形式增加。')

    regex_list = FieldList(FormField(AdviceRegexForm), label=u'正则表达式')
    keyword_list = FieldList(FormField(AdviceKeyWordForm), label=u'关键字')

    advice = SubmitField(label=u'提取')
    use = SubmitField(label=u'采用')


######## advice_setting_window.html #######################################################################
class AdviceUrlForm(Form):
    url = StringField(label=u'url')


class AdviceUrlListForm(Form):
    url_list = FieldList(FormField(AdviceUrlForm), label=u'URL列表')


######## setting_list_detail.html #####################################################################################
class RegexSettingForm(Form):  # setting
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    weight = SelectField(label=u'权重', choices=[('0', u'高'), ('1', u'中'), ('2', u'低')])
    score = IntegerField(label=u'匹配数', default=0)


class ListDetailRegexSettingForm(Form):  # setting
    start_url = StringField(label=u'主页')  # 'http://cpt.xtu.edu.cn/'
    site_domain = StringField(label=u'限定域名')  # cpt.xtu.edu.cn'  # 湘潭大学
    white_list = StringField(label=u'白名单')
    black_domain_str = StringField(label=u'域名黑名单')
    scope_sel = SelectField(label=u'分类', coerce=str,
                            choices=[('00', u'不使用预置规则'), ('01', u'新闻'), ('02', u'论坛'), ('03', u'博客'), ('04', u'微博'),
                                     ('05', u'平媒'), ('06', u'微信'), ('07', u'视频'), ('99', u'搜索引擎')],
                            default=('00', u'不使用预置规则'))

    result = StringField(label=u'转换结果')
    convert = SubmitField(label=u'<< 转换')
    url = StringField(label=u'URL例子')

    list_regex_list = FieldList(FormField(RegexSettingForm), label=u'列表页-正则表达式')
    detail_regex_list = FieldList(FormField(RegexSettingForm), label=u'详情页-正则表达式')

    mode = BooleanField(label=u'精确匹配', default=True)
    hold = BooleanField(label=u'保留上次结果', default=True)

    save_run_list = SubmitField(label=u'保存-执行(列表页)')
    save_run_detail = SubmitField(label=u'保存-执行(详情页)')


######## show_result.html #############################################################################
class ResultForm(Form):  # 内容提取
    list_regex_sel = SelectField(label=u'列表页规则', choices=[], default='0')
    detail_regex_sel = SelectField(label=u'详情页规则', choices=[], default='0')
    list_match = SubmitField(label=u'列表正则')
    detail_match = SubmitField(label=u'详情正则')
    unkown_url_list = []  # 左侧
    keywords_str = ''  # 右侧
    keywords_matched_cnt = ''  # 右侧
    category_list = []  # 左侧
    category_compress_list = []  # 右侧


######## content_advice.html #############################################################################
class ContentAdvice(Form):
    mode = BooleanField(label=u'自动提取', default=True)

    detail_regex_sel = SelectField(label=u'详情页规则', choices=[], default='0')
    detail_regex_list = []
    match = SubmitField(label=u'详情页正则匹配')
    content_advice = SubmitField(label=u'自动提取')

    detail_url_list = []

    # 标题，内容，作者，创建时间，
    title = TextAreaField(label=u'标题')
    content = TextAreaField(label=u'内容')
    author = StringField(label=u'作者')
    ctime = StringField(label=u'做成时间')

    title_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    title_exp = StringField(label=u'表达式')

    content_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    content_exp = StringField(label=u'表达式')

    author_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    author_exp = StringField(label=u'表达式')

    ctime_sel = SelectField(label=u'提取方法', choices=[('0', u'xpath'), ('1', u'正则')], default='0')
    ctime_exp = StringField(label=u'表达式')

    save_run = SubmitField(label=u'保存并执行')


######## content_advice.html #############################################################################
class ContentItemForm(Form):  # 内容提取
    mode = BooleanField(label=u'自动提取', default=True)
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


########## history.html  ####################################################################################
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
    weight = SelectField(label=u'权重', choices=[('0', u'高'), ('1', u'中'), ('2', u'低')])
    score = IntegerField(label=u'匹配数', default=0)

    search_result_list = []


######## admin_server_log.html #############################################################################
class ShowServerLogInputForm(Form):  # show_server_log
    unkown_sel = BooleanField(label=u'仅显示筛选信息', default=True)
    refresh = SubmitField(label=u'刷新')


######## admin_preset.html #############################################################################
class PresetForm(Form):
    partn_type_sel = SelectField(label=u'规则类别', choices=[('list', u'列表'), ('detail', u'详情'), ('rubbish', u'无效')])
    partn = StringField(label=u'规则')
    weight_sel = SelectField(label=u'权重', choices=[('0', u'高'), ('1', u'中'), ('2', u'低')])


class PresetListForm(Form):
    # 01新闻、02论坛、03博客、04微博 05平媒 06微信 07 视频、99搜索引擎
    scope_sel = SelectField(label=u'分类',
                            choices=[('00', u'不使用预置规则'), ('01', u'新闻'), ('02', u'论坛'), ('03', u'博客'), ('04', u'微博'),
                                     ('05', u'平媒'), ('06', u'微信'), ('07', u'视频'), ('99', u'搜索引擎')],
                            default=('00', u'不使用预置规则'))
    partn_list = FieldList(FormField(PresetForm), label=u'URL列表')
    save = SubmitField(label=u'保存')


########################################################################################################
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

    def save_advice(self, user_id, start_url, site_domain, advice_start_url_list, advice_regex_list,
                    advice_keyword_list):
        # print 'save_advice() start...', start_url, site_domain
        ret_cnt = 0
        try:
            sql_str1 = ("SELECT id FROM result_file WHERE user_id =%s AND start_url=%s AND site_domain=%s")
            parameter1 = (user_id, start_url, site_domain)
            print '[info]save_all_setting()', sql_str1 % parameter1
            ret_cnt = self.cur.execute(sql_str1, parameter1)

            if ret_cnt > 0:
                sql_str2 = "UPDATE result_file SET advice_start_url_list=%s WHERE user_id=% AND start_url=%s AND site_domain=%s"
                parameter2 = (advice_start_url_list, user_id, start_url, site_domain)
            else:
                sql_str2 = "INSERT INTO result_file(user_id,start_url,site_domain,advice_start_url_list) VALUES (%s,%s,%s,%s)"
                parameter2 = (user_id, start_url, site_domain, advice_start_url_list)

            print '[info]save_advice() sql:', sql_str2 % parameter2
            ret_cnt = self.cur.execute(sql_str2, parameter2)
            self.conn.commit()

        except Exception, e:
            ret_cnt = 0
            print '[error]save_advice()', e
            self.conn.rollback()

        return ret_cnt

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
                weight = '0'
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
                weight = '0'
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

    def get_detail_regex(self, user_id, start_url, site_domain):
        regex_list = []
        sql_str = "SELECT regex FROM url_rule  WHERE user_id=%s AND start_url=%s AND site_domain=%s " \
                  "AND detail_or_list='0' AND white_or_black='0'"
        parameter = (user_id, start_url, site_domain)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            rs = self.cur.fetchall()
            for r in rs:
                regex_list.append(r[0])
            self.conn.commit()
            print '[info]get_detail_regex()', cnt, sql_str % parameter
        except Exception, e:
            print '[error]get_detail_regex()', e, sql_str % parameter

        return regex_list

    def get_list_regex(self, user_id, start_url, site_domain):
        regex_list = []
        sql_str = "SELECT regex FROM url_rule  WHERE user_id=%s AND start_url=%s AND site_domain=%s " \
                  "AND detail_or_list='1' AND white_or_black='0'"
        parameter = (user_id, start_url, site_domain)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            rs = self.cur.fetchall()
            for r in rs:
                regex_list.append(r[0])
            self.conn.commit()
            print '[info]get_list_regex()', cnt, sql_str % parameter
        except Exception, e:
            print '[error]get_list_regex()', e, sql_str % parameter

        return regex_list

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

    def get_current_regexs(self, regex_type, user_id, start_url, site_domain, black_domain):
        # 0:detail,1:list
        if regex_type == 'detail':
            detail_or_list = '0'
        else:
            detail_or_list = '1'
        regexs = []
        sql_str = "SELECT scope,white_or_black,weight,regex,etc FROM url_rule WHERE user_id=%s AND start_url=%s AND site_domain =%s AND detail_or_list=%s"
        parameter = (user_id, start_url, site_domain, detail_or_list)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            rs = self.cur.fetchall()
            for r in rs:
                (scope, white_or_black, weight, regex, etc) = r
                regexs.append((scope, white_or_black, weight, regex, etc))
            self.conn.commit()
            print '[info]get_current_regexs()', cnt, sql_str % parameter
        except Exception, e:
            print '[error]get_current_regexs()', e, sql_str % parameter
        return regexs

    def add_regex(self, user_id, start_url, site_domain, black_domain_str, is_detail_regex, regex):
        print '[info]add_regex() start.', user_id, start_url, site_domain, black_domain_str, is_detail_regex, regex
        weight = '0'
        if is_detail_regex:
            detail_or_list = '0'  # 详情
        else:
            detail_or_list = '1'
        scope = '1'
        if regex.find('/^') >= 0:
            white_or_black = '1'  # 黑名单
        else:
            white_or_black = '0'  # 白名单

        try:
            sql_str1 = ("SELECT id FROM url_rule WHERE user_id=%s AND start_url=%s AND site_domain=%s AND "
                        "detail_or_list=%s AND white_or_black=%s AND regex=%s")
            parameter1 = (user_id, start_url, site_domain, detail_or_list, white_or_black, regex)
            print '[info]add_regex()', sql_str1 % parameter1
            ret_cnt = self.cur.execute(sql_str1, parameter1)
            if ret_cnt == 0:
                sql_str2 = "INSERT INTO url_rule(user_id,start_url,site_domain,black_domain_str,detail_or_list, " \
                           "scope,white_or_black,weight,regex) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                parameter2 = (user_id, start_url, site_domain, black_domain_str,
                              detail_or_list, scope, white_or_black, weight, regex)
                print '[info]add_regex()', sql_str2 % parameter2
                ret_cnt = self.cur.execute(sql_str2, parameter2)
                self.conn.commit()
                '[info]add_regex() end.'
                return True
            else:
                print '[info]add_regex() regex exist.'
                return False
        except Exception, e:
            print '[error]add_regex()', e
            self.conn.rollback()
            return None

    def delete_regex(self, user_id, start_url, site_domain, regex_type, regex):
        weight = '0'
        if regex_type == 'detail':
            detail_or_list = '0'  # 详情
        else:
            detail_or_list = '1'
        scope = '1'
        if regex.find('/^') >= 0:
            white_or_black = '1'  # 黑名单
        else:
            white_or_black = '0'  # 白名单
        try:
            sql_str1 = ("SELECT id FROM url_rule WHERE user_id=%s AND start_url=%s AND site_domain=%s AND "
                        "detail_or_list=%s AND white_or_black=%s AND regex=%s")
            parameter1 = (user_id, start_url, site_domain, detail_or_list, white_or_black, regex)
            print '[info]delete_regex()', sql_str1 % parameter1
            ret_cnt = self.cur.execute(sql_str1, parameter1)
            if ret_cnt != 0:
                r = self.cur.fetchone()
                regex_id = r[0]
                sql_str2 = "DELETE FROM url_rule WHERE id=%s"
                parameter2 = (regex_id,)
                print '[info]delete_regex()', sql_str2 % parameter2
                ret_cnt = self.cur.execute(sql_str2, parameter2)
                self.conn.commit()
                print '[info]delete_regex() delete', ret_cnt, regex
                return True
            else:
                print '[error]delete_regex() regex not exist.'
                return False
        except Exception, e:
            print '[error]delete_regex()', e
            self.conn.rollback()
            return None

    def save_result_file_to_mysql(self, start_url, site_domain):
        msg = ''
        user_id = session['user_id']

        f = EXPORT_FOLDER + 'result-list(' + site_domain + ').log'
        if os.path.isfile(f):
            fp = open(f, 'r')
            list_b = fp.read()
            fp.close()
        else:
            msg = u'文件没找到：' + f
            print '[error]save_result_file_to_mysql() file not found.', f
            return False, msg

        f = EXPORT_FOLDER + 'result-detail(' + site_domain + ').log'
        if os.path.isfile(f):
            fp = open(f, 'r')
            detail_b = fp.read()
            fp.close()
        else:
            msg = u'文件没找到：' + f
            print '[error]save_result_file_to_mysql() file not found.', f
            return False, msg

        # 写入MySql
        sql_str1 = "DELETE FROM result_file WHERE user_id=%s AND start_url=%s AND site_domain=%s"
        parameter1 = (user_id, start_url, site_domain)

        sql_str2 = "INSERT INTO result_file(user_id,start_url,site_domain,list_result_file,detail_result_file) VALUES(%s,%s,%s,_binary%s,_binary%s)"
        parameter2 = (user_id, start_url, site_domain, list_b, detail_b,)

        try:
            print '[info]save_result_file_to_mysql()', sql_str1
            self.cur.execute(sql_str1, parameter1)

            print '[info]save_result_file_to_mysql()', sql_str2
            cnt = self.cur.execute(sql_str2, parameter2)

            self.conn.commit()
        except Exception, e:
            # traceback.format_exc()
            print '[error]save_result_file_to_mysql()', e

        return True, msg

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

    def get_preset_partn(self, scope='01', partn_type=''):
        # scope: 01新闻、02论坛、03博客、04微博 05平媒 06微信 07 视频、99搜索引擎
        # partn_type: list,detail,rubbish
        partn_list = []
        sql_str = "SELECT partn_type, partn, weight FROM preset_patrn  WHERE scope='" + scope + "' AND partn_type LIKE '%" + partn_type + "%'"

        try:
            cnt = self.cur.execute(sql_str)
            rs = self.cur.fetchall()
            for r in rs:
                partn_list.append((r[0], r[1], r[2]))
            self.conn.commit()
            print '[info]get_detail_regex()', cnt, sql_str
        except Exception, e:
            print '[error]get_detail_regex()', e, sql_str

        return partn_list

    def get_preset_partn_to_str(self, scope='01'):
        rubbish_list = []
        detail_list = []
        list_list = []

        sql_str = "SELECT partn_type, partn FROM preset_patrn WHERE scope=%s"
        parameter = (scope,)
        try:
            cnt = self.cur.execute(sql_str)
            rs = self.cur.fetchall()
            for r in rs:
                if r[0] == 'list':
                    list_list.append(r[1])
                elif r[0] == 'detail':
                    detail_list.append(r[1])
                else:
                    rubbish_list.append(r[1])
            self.conn.commit()
            print '[info]get_detail_regex()', cnt, sql_str
        except Exception, e:
            print '[error]get_detail_regex()', e, sql_str

        patrn_list = '/' + '|'.join(list_list) + '/'
        patrn_detail = '/' + '|'.join(detail_list) + '/'
        patrn_rubbish = '/' + '|'.join(rubbish_list) + '/'
        return patrn_list, patrn_detail, patrn_rubbish
        # patrn_rubbish = '/uid|username|space|search|blog|group/'
        # patrn_detail = '/post|thread|detail/'
        # patrn_list = '/list|index|forum|fid/'


##################################################################################################
class RedisDrive(object):
    def __init__(self, start_url='', site_domain=''):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果(列表)
        self.detail_urls_set_key = 'detail_urls_set_%s' % self.site_domain  # 计算结果(详情)
        self.unkown_urls_set_key = 'unkown_urls_set_%s' % self.site_domain  # 计算结果(未知)
        self.manual_w_list_rule_zset_key = 'manual_w_list_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_list_rule_zset_key = 'manual_b_list_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.manual_w_detail_rule_zset_key = 'manual_w_detail_rule_zset_%s' % self.site_domain  # 手工配置规则(白)
        self.manual_b_detail_rule_zset_key = 'manual_b_detail_rule_zset_%s' % self.site_domain  # 手工配置规则（黑）
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.list_rules = []  # 手工配置规则-内存形式
        self.detail_rules = []  # 手工配置规则-内存形式
        self.todo_flg = -1
        self.done_flg = 0
        self.detail_flg = 1
        self.content_flg = 9
        self.end_flg = 99  # 状态管理flg最大值

    def get_detail_urls(self):
        return self.conn.smembers(self.detail_urls_set_key)

    def get_unkown_urls(self):
        return self.conn.smembers(self.unkown_urls_set_key)

    def get_detail_urls_by_regex(self, regex):
        urls = []
        cnt = 0
        if regex == '':
            for url in self.conn.smembers(self.detail_urls_set_key):
                urls.append(url)
                cnt += 1
                if cnt > 100: break
        else:
            for url in self.conn.smembers(self.detail_urls_set_key):
                if re.search(regex, url):
                    urls.append(url)
                    cnt += 1
                if cnt > 100: break

        return urls

    def get_list_urls_by_regex(self, regex):
        urls = []
        cnt = 0
        if regex == '':  # all
            print '[info]get_list_urls_by_regex() all'
            for url in self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.end_flg,
                                               withscores=False):
                urls.append(url)
                cnt += 1
                if cnt > 100: break
        else:  # match
            print '[info]get_list_urls_by_regex() regex'
            for url in self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.end_flg,
                                               withscores=False):
                if re.search(regex, url):
                    urls.append(url)
                    cnt += 1
                if cnt > 100: break

        return urls

    def get_list_urls(self):
        return self.conn.zrangebyscore(self.list_urls_zset_key, min=self.todo_flg, max=self.end_flg, withscores=False)

    def get_list_urls_limit(self):
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
        urls = self.get_list_urls_limit()
        if len(urls) == 0:
            return 0.0

        done = self.get_done_list_urls()
        return float(len(done)) / len(urls)

    def get_keywords_match(self):
        score_list = []
        keywords = []
        list_rules = self.conn.zrevrangebyscore(self.manual_w_list_rule_zset_key,
                                                max=99999999, min=0, start=0, num=5, withscores=True)
        for rule, score in dict(list_rules).iteritems():
            score_list.append(str(score))
            keywords.append(rule)

        detail_rules = self.conn.zrevrangebyscore(self.manual_w_detail_rule_zset_key,
                                                  max=99999999, min=0, start=0, num=5, withscores=True)
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

    def reset_rule(self, mode, list_rules, detail_rules):
        # 按照新规则，重置上次计算结果（unkown,list,detail）
        self.list_rules = [item['regex'] for item in list_rules]
        self.detail_rules = [item['regex'] for item in detail_rules]

        all_urls = []
        for url in self.conn.zrangebyscore(self.list_urls_zset_key, self.detail_flg, self.detail_flg, withscores=False):
            all_urls.append(url)

        self.conn.delete(self.list_urls_zset_key)

        for url in self.conn.smembers(self.detail_urls_set_key):
            all_urls.append(url)

        self.conn.delete(self.detail_urls_set_key)

        for url in self.conn.smembers(self.unkown_urls_set_key):
            all_urls.append(url)

        self.conn.delete(self.unkown_urls_set_key)

        for url in all_urls:
            ret = self.path_is_list(mode, url)
            if ret == True:
                self.conn.zadd(self.list_urls_zset_key, self.todo_flg, url)
            elif ret == False:
                self.conn.sadd(self.detail_urls_set_key, url)
            else:
                self.conn.sadd(self.unkown_urls_set_key, url)

    def path_is_list(self, mode, url):
        # None：未知, True：列表页，False：详情页
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        new_url = urlparse.urlunparse(('', '', path, params, query, ''))

        # 页面手工配置规则
        ret = self.is_manual_detail_rule(new_url)
        if ret is not None:  # 未知
            return not ret

        ret = self.is_manual_list_rule(new_url)
        if ret is not None:  # 未知
            return ret

        print '[unkown]', new_url

        if mode == 'all':
            return True

        if mode == 'exact':
            return None

        return True

    def is_manual_detail_rule(self, url):
        for rule in self.detail_rules:
            if rule.find('/^') < 0:  # 白
                if re.search(rule, url):
                    print '[detail-white]', rule, '<-', url
                    return True  # 符合详情页规则（白）

            else:  # 黑
                if re.search(rule[2:-1], url):  # 去掉 /^xxxxxx/ 中的 '/^','/'
                    print '[detail-black]', rule, '<-', url
                    return False  # 符合详情页规则（黑）

    def is_manual_list_rule(self, url):
        for rule in self.list_rules:
            if rule.find('/^') < 0:  # 白
                if re.search(rule, url):
                    print '[list-white]', rule, '<-', url
                    return True  # 符合详情页规则（白）

            else:  # 黑
                if re.search(rule[2:-1], url):  # 去掉 /^xxxxxx/ 中的 '/^','/'
                    print '[list-black]', rule, '<-', url
                    return False  # 符合详情页规则（黑）


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
class Util(object):
    def __init__(self):
        pass

    #####  setting convert start  #############################################
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

    #####  setting convert end  ##########################################################

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

            print '[info]modify_config() success.'
            return True
        except Exception, e:
            print "[error]modify_config(): %s" % e
            return False

    #####  推荐算法  start  ################################################################
    def convert_path_to_rule_advice(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print path
        pos = path.rfind('.')
        if pos > 0:
            suffix = path[pos:]
            path = path[:pos]
        else:
            suffix = ''
        split_path = path.split('/')
        new_path_list = []
        for p in split_path:
            # regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
            regex = re.sub(r'\d', '\d', p)
            new_path_list.append(self.convert_regex_format_advice(regex))

        new_path = '/'.join(new_path_list) + suffix
        return urlparse.urlunparse(('', '', new_path, '', '', ''))

    def convert_regex_format_advice(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6,6}/[a-zA-Z]\d{8,8}_\d{6,6}.htm
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
                temp = '%s{%d,%d}' % (digit, cnt, cnt)
                pos = pos + len(digit)
            elif rule[pos:pos + len(word)] == word:
                if temp.find(word) < 0:
                    ret = ret + temp
                    temp = ''
                    cnt = 0
                cnt = cnt + 1
                temp = '%s{%d,%d}' % (word, cnt, cnt)
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

    def merge_digit(self, rules):
        # print '[INFO]merge_digit() start.', len(rules), rules
        for i in range(len(rules)):
            for j in range(i + 1, len(rules), 1):
                if self.is_same_rule(rules[i], rules[j]):
                    rule_new = self.merge_digit_scope(rules[i], rules[j])
                    # 原有全部替换为新规则
                    for k in range(len(rules)):
                        if rules[k] == rules[i]:
                            rules[k] = rule_new

                    for k in range(len(rules)):
                        if rules[k] == rules[j]:
                            rules[k] = rule_new

        rules = list(set(rules))
        rules.sort()
        # print '[INFO]merge_digit() end.', len(rules), rules
        return rules

    def is_same_rule(self, rule1, rule2):
        ret = False
        if len(rule1) == len(rule2):
            for i in range(len(rule1)):
                if rule1[i] != rule2[i]:
                    if rule1[i].isdigit() and rule2[i].isdigit():
                        ret = True
                    else:
                        return False
        return ret

    def merge_digit_scope(self, rule1, rule2):
        ''' {1,2} + {2,3} -> {1,3}'''
        rule_new = ''
        for i in range(len(rule1)):
            if cmp(rule1[i], rule2[i]) < 0:
                if rule1[i - 1] == '{':
                    new = rule1[i]
                else:
                    new = rule2[i]
            elif cmp(rule1[i], rule2[i]) > 0:
                if rule1[i - 1] == '{':  # {M,N}
                    new = rule2[i]
                else:
                    new = rule1[i]
            else:
                new = rule1[i]

            rule_new += new

        return rule_new

    def without_digit_regex(self, regex):
        # '/post-culture-\\d{6,6}-\\d{1,1}.shtml' -> '/post-culture--.shtml'
        return re.sub(r'\\d\{\d\,\d\}', "", regex)

    def get_words(self, regex):
        # '/post-culture--.shtml' -> ['post','culture','shtml']
        words = []
        word = ''
        for i in range(len(regex)):
            if regex[i].isalpha():
                word += regex[i]
            else:
                if word != '':
                    words.append(word)
                word = ''

        return words

    def get_regexs_words_with_score(self, regexs, urls):
        # print '[INFO]get_regexs_words_score() start.'
        ''' regexs:
            ['/post-\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-\\d{3,3}-\\d{7,7}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{4,4}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{5,5}-\\d{1,1}.shtml',
             '/post-\\d{4,4}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{6,6}-\\d{1,1}.shtml',
             '/post-no\\d{2,2}-\\d{7,7}-\\d{1,1}.shtml',
             '/list-\\d{1,1}d-\\d{1,1}.shtml',
             '/list-\\d{2,4}-\\d{1,1}.shtml',
             '/list-apply-\\d{1,1}.shtml']

             return  {'apply': 1, 'post': 11, 'list': 3, 'd': 1, 'no': 2}
        '''
        all_words = []
        for regex in regexs:
            without_digit = self.without_digit_regex(regex)
            words = self.get_words(without_digit)
            all_words.extend(words)

        all_words = list(set(all_words))
        # all_words.sort()
        # print all_words

        all_words_dic = {}
        for w in all_words:
            w_cnt = 0
            for r in urls:
                path = urlparse.urlparse(r).path
                without_digit = self.without_digit_regex(path)
                words = self.get_words(without_digit)
                if w in words:
                    w_cnt += 1  # 匹配次数

            all_words_dic[w] = w_cnt

        sum = 0
        for i in all_words_dic.iteritems():
            (k, v) = i
            sum += v

        # print '[INFO]get_regexs_words_score() end.', len(all_words_dic), 'sum=', sum, all_words_dic
        return all_words_dic

    def get_hot_words(self, all_words_dic):
        # print '[INFO]get_hot_words() start.', all_words_dic
        ret_dict = {}

        sum = 0
        for (k, v) in all_words_dic.iteritems():
            sum += v

        dict = sorted(all_words_dic.iteritems(), key=lambda d: d[1], reverse=True)
        s = 0
        for i in dict:
            (k, v) = i
            if s >= sum * 0.8:
                break
            else:
                ret_dict.update({k: v})
                s += v

        # print '[INFO]get_hot_words() end.', s, '/', sum, ret_dict
        return ret_dict

    def get_hot_regexs_with_score(self, merge_digit_list, urls):
        # print '[INFO]get_hot_regexs_with_score() start.', len(urls), urls
        ret_dict = {}
        for regex in merge_digit_list:
            r_cnt = 0
            for url in urls:
                path = urlparse.urlparse(url).path
                if re.search(regex, path):
                    r_cnt += 1
            # 计数完毕保存
            ret_dict.update({regex: r_cnt})

        for url in urls:
            found = False
            for r in merge_digit_list:
                path = urlparse.urlparse(url).path
                if re.search(r, path):
                    found = True

            if found == False:
                print '[error]get_hot_regexs_with_score() not match:', url

        sum = 0
        for i in ret_dict.iteritems():
            (k, v) = i
            sum += v

        # print '[INFO]get_hot_regexs_with_score() end.', len(ret_dict), 'sum=', sum, ret_dict
        return ret_dict

    def get_hot_regexs(self, regexs_dic):
        # print '[INFO]get_hot_regexs() start.', len(regexs_dic), regexs_dic
        ret_dict = {}

        sum = 0
        for (k, v) in regexs_dic.iteritems():
            sum += v

        dict = sorted(regexs_dic.iteritems(), key=lambda d: d[1], reverse=True)
        s = 0
        for i in dict:
            (k, v) = i
            if s >= sum * 0.8:
                break
            else:
                ret_dict.update({k: v})
                s += v

        # print '[INFO]get_hot_regexs() end.', s, '/', sum, ret_dict
        return ret_dict

    def merge_word(self, advice_regex_dic, ignore_words):
        # print '[INFO]merge_word() start.', advice_regex_dic, ignore_words
        ret_merged_list = []
        merged_word = {}
        for k, v in advice_regex_dic.items():
            matched = False
            # 和所有的忽略词匹配
            for word in ignore_words:
                if k.find(word) >= 0:
                    matched = True
                    replace = '[a-zA-Z]{%d,%d}' % (len(word), len(word))
                    regex = re.sub(word, replace, k)
                    merged_word.update({regex: v})

            # 没有忽略词匹配
            if matched is False:
                merged_word.update({k: v})

        l = [k for k, v in merged_word.items()]
        ret_merged_list = self.merge_digit(l)

        # print '[INFO]merge_word() end.', ret_merged_list
        return ret_merged_list

    def advice_regex_keyword(self, links):
        # print '[info]advice_regex_keyword() start.'
        regexs = []
        for link in links:
            if link != '' and link[-1] != '/':
                regex = self.convert_path_to_rule_advice(link)
                if regex != '': regexs.append(regex)

        # 转换规则后
        regexs = list(set(regexs))
        regexs.sort()

        merge_digit_list = self.merge_digit(regexs)
        merge_digit_list.append('\/$')
        merge_digit_list.sort()

        regex_dic = self.get_hot_regexs_with_score(merge_digit_list, links)
        advice_regex_dic = self.get_hot_regexs(regex_dic)

        word_dic = self.get_regexs_words_with_score(merge_digit_list, links)
        advice_words_dic = self.get_hot_words(word_dic)

        # print '[info]advice_regex_keyword() end.', len(advice_regex_dic), advice_regex_dic
        # print '[info]advice_regex_keyword() end.', len(advice_words_dic), advice_words_dic
        return advice_regex_dic, advice_words_dic

    # 未匹配URL归类算法
    def compress_url(self, url):
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
        # if url.find('%') >= 0:
        url_new = urlparse.urlunparse((scheme, netloc, self.compress_path_digit(path), params,
                                       self.compress_qurey(query), fragment))
        return url_new

    def compress_path_digit(self, path):
        # http://www.ynsf.ccoo.cn/forum/board-61399-1-1.html
        # -> http://www.ynsf.ccoo.cn/forum/board-999-999-999.html
        path_without_digit = re.sub(r'\d+', '999', path)
        return path_without_digit

    def compress_qurey(self, query):
        # dateline=86400&fid=2&filter=dateline&mod=forumdisplay&orderby=lastpost
        # print query
        q = re.sub(r'=.*?&', '=&', query)
        qurey_without_digit = q[:q.rfind('=') + 1]
        return qurey_without_digit

    def compress_path_alpha(self, url):
        # http://www.ynsf.ccoo.cn/forum/board-999-999-999.html
        # -> http://www.ynsf.ccoo.cn/aaa/aaa-999-999-999.html
        # url ='http://www.ynsf.ccoo.cn/forum/board-999-999-999.html'
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        # print type(scheme), type(netloc), type(path), type(params), type(query), type(fragment)
        if path.rfind('.') >= 0:
            path_without_alpha = re.sub(r'[a-zA-Z]+', 'AAA', path[:path.rfind('.')]) + path[path.rfind('.'):]
        else:
            path_without_alpha = re.sub(r'[a-zA-Z]+', 'AAA', path)
        # path_without_alpha = path
        # print (scheme, netloc, path_without_alpha, params, query, fragment)
        return urlparse.urlunparse((scheme, netloc, path_without_alpha, params, query, fragment))

    def convert_urls_to_category(self, urls):
        category_dict = {}
        for url in urls:
            category = self.compress_url(url)
            if category_dict.has_key(category):
                url_list = category_dict.pop(category)
                url_list.append(url)
                category_dict.update({category: url_list})
            else:
                url_list = [url]
                category_dict.update({category: url_list})
        return category_dict

    def compress_category_alpha(self, category_dict):
        category_compress_dict = {}
        category_list = []
        for (category, url_list) in category_dict.items():
            category_compress = self.compress_path_alpha(category)
            category_list.append((category_compress, len(url_list)))

        category_set = set([k for (k, v) in category_list])
        for category in category_set:
            l = 0
            for (k, v) in category_list:
                if category == k:
                    l += v
            category_compress_dict.update({category: l})

        return category_compress_dict


#####  推荐算法  end  ################################################################

def get_domain_init(inputForm=None):
    start_url = ''
    site_domain = ''
    black_domain_str = ''

    # 页面输入优先
    if inputForm is not None:
        start_url = inputForm.start_url.data
        site_domain = inputForm.site_domain.data
        black_domain_str = inputForm.black_domain_str.data

    # 没有的话,使用session
    if start_url == '':
        start_url = session['start_url']
    if site_domain == '':
        site_domain = session['site_domain']
    if black_domain_str == '':
        black_domain_str = session['black_domain_str']
    return start_url, site_domain, black_domain_str


def set_domain_init(inputForm, start_url, site_domain, black_domain_str):
    if start_url != '':
        if start_url[-1] == '/': start_url = start_url[:-1]
        session['start_url'] = start_url
        inputForm.start_url.data = start_url
    if site_domain != '':
        if site_domain[-1] == '/': site_domain = site_domain[:-1]
        session['site_domain'] = site_domain
        inputForm.site_domain.data = site_domain
    if black_domain_str != '':
        session['black_domain_str'] = black_domain_str
        inputForm.black_domain_str.data = black_domain_str


######### router and action  ###############################################################################
@app.route("/login", methods=['POST', 'GET'])
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
    # 初始化session
    session['user_id'] = 'admin'  # login页面设置
    session['start_url'] = ''
    session['site_domain'] = ''
    session['black_domain_str'] = ''
    session['advice_regex_list'] = json.dumps('')
    session['advice_keyword_list'] = json.dumps('')

    user_id = session['user_id']

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


######### setting_advice.html ###########################################################################
@app.route('/setting_advice_init', methods=["GET", "POST"])
def setting_advice_init():
    # print '[info]setting_advice_init() start.'
    user_id = session['user_id']
    inputForm = AdviceRegexListInputForm(request.form)

    start_url, site_domain, black_domain_str = get_domain_init(inputForm)
    advice_regex_list = json.loads(session['advice_regex_list'])
    advice_keyword_list = json.loads(session['advice_keyword_list'])

    # 恢复 主页、域名
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。', category='warning')
        for j in range(SHOW_MAX):
            inputForm.regex_list.append_entry()

        for j in range(SHOW_MAX):
            inputForm.keyword_list.append_entry()

        return render_template('setting_advice.html', inputForm=inputForm)

    ####  页面(regex)
    for (regex, score, select) in advice_regex_list:
        regexForm = AdviceRegexForm()
        regexForm.regex = regex
        regexForm.score = score
        regexForm.select = select
        inputForm.regex_list.append_entry(regexForm)

    for j in range(SHOW_MAX - len(advice_regex_list)):
        inputForm.regex_list.append_entry()

    ####  页面(keyword)
    for (keyword, score, select) in advice_keyword_list:
        regexForm = AdviceKeyWordForm()
        regexForm.keyword = keyword
        regexForm.score = score
        regexForm.select = select
        inputForm.keyword_list.append_entry(regexForm)

    for j in range(SHOW_MAX - len(advice_keyword_list)):
        inputForm.keyword_list.append_entry()

    # 初始化预置规则
    mysql_db = MySqlDrive()
    patrn_list, patrn_detail, patrn_rubbish = mysql_db.get_preset_partn_to_str('01')

    flash(u'初始化配置完成')
    # print '[info]setting_advice_init() end.'
    return render_template('setting_advice.html', inputForm=inputForm,
                           patrn_rubbish=patrn_rubbish, patrn_detail=patrn_detail, patrn_list=patrn_list)


@app.route('/setting_advice_try', methods=["GET", "POST"])
def setting_advice_try():
    print '[info]setting_advice_try() start.'
    user_id = session['user_id']
    inputForm = AdviceRegexListInputForm(request.form)
    start_url, site_domain, black_domain_str = get_domain_init(inputForm)
    # 提取主页、域名
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        for j in range(SHOW_MAX):
            inputForm.regex_list.append_entry()

        for j in range(SHOW_MAX):
            inputForm.keyword_list.append_entry()

        return render_template('setting_advice.html', inputForm=inputForm,
                               patrn_rubbish='', patrn_detail='', patrn_list='')
    else:
        set_domain_init(inputForm, start_url, site_domain, black_domain_str)

    # 保存初始化信息
    mysql_db = MySqlDrive()
    mysql_db.set_current_main_setting(user_id=user_id, start_url=start_url, site_domain=site_domain,
                                      black_domain_str=black_domain_str, setting_json='')
    # 初始化预置规则
    patrn_list, patrn_detail, patrn_rubbish = mysql_db.get_preset_partn_to_str(scope='01')
    # print patrn_list, patrn_detail, patrn_rubbish

    # 修改配置文件的执行入口信息
    util = Util()
    ret = util.modify_config(start_urls=start_url, site_domain=site_domain,
                             black_domain_str=black_domain_str,
                             list_rule_str='', detail_rule_str='', mode='all')  # mode 必须设置
    if ret == False:
        flash(u"修改" + INIT_CONFIG + u"文件失败.")
        print '[error]setting_advice_try() modify ' + INIT_CONFIG + u' failure.'
        return render_template('setting_advice.html', inputForm=inputForm,
                               patrn_rubbish='', patrn_detail='', patrn_list='')
    else:
        print '[info]setting_advice_try() modify ' + INIT_CONFIG + u' success.'

    # windows
    if os.name == 'nt':
        # DOS "start" command
        print '[info] %s run on windows.' % SHELL_ADVICE_CMD
        os.startfile(SHELL_ADVICE_CMD)
    # linux
    else:
        print '[info] %s run on linux.' % SHELL_ADVICE_CMD
        p = subprocess.Popen(SHELL_ADVICE_CMD, shell=True)
        process_id = p.pid
        print '[info] process_id:', process_id

    # 读取首页链接列表文件
    flash(u"正在下载并解析，请稍等。。。")
    time.sleep(5.0)  # 等待 链接下载/写入文件 完成
    f = EXPORT_FOLDER + '/advice(' + site_domain + ').json'
    if os.path.isfile(f):
        fp = open(f, "r")
        url_list = fp.readlines()
        fp.close()
    else:
        flash(u"文件不存在：" + f)
        print '[error]setting_advice_try() json file not found.', f
        return render_template('setting_advice.html', inputForm=inputForm,
                               patrn_rubbish='', patrn_detail='', patrn_list='')

    advice_regex_dic, advice_keyword_dic = util.advice_regex_keyword(url_list)

    ####  页面设置计算结果(regex)
    advice_regex_list = []
    for (regex, score) in advice_regex_dic.items():
        regexForm = AdviceRegexForm()
        regexForm.regex = regex
        regexForm.score = int(score)
        regexForm.select = '0'
        inputForm.regex_list.append_entry(regexForm)
        advice_regex_list.append({'regex': regex, 'score': score, 'select': '0'})

    for j in range(SHOW_MAX - len(advice_regex_dic)):
        inputForm.regex_list.append_entry()
        advice_regex_list.append({'regex': '', 'score': '0', 'select': '0'})

    ####  页面设置计算结果(keyword)
    advice_keyword_list = []
    for (keyword, score) in advice_keyword_dic.items():
        regexForm = AdviceKeyWordForm()
        regexForm.keyword = keyword
        regexForm.score = int(score)
        regexForm.select = '0'
        inputForm.keyword_list.append_entry(regexForm)
        advice_keyword_list.append({'keyword': keyword, 'score': score, 'select': '0'})

    for j in range(SHOW_MAX - len(advice_keyword_dic)):
        inputForm.keyword_list.append_entry()
        advice_keyword_list.append({'keyword': '', 'score': '0', 'select': '0'})

    # 通过session保存,以免页面再次初始化时重新计算。
    session['advice_regex_list'] = json.dumps(advice_regex_list)
    session['advice_keyword_list'] = json.dumps(advice_keyword_list)

    flash(u'初始化配置完成')
    print '[info]setting_advice_try() end.'
    return render_template('setting_advice.html', inputForm=inputForm,
                           patrn_rubbish=patrn_rubbish, patrn_detail=patrn_detail, patrn_list=patrn_list)


@app.route('/setting_advice_use', methods=["GET", "POST"])
def setting_advice_use():
    print '[info]setting_advice_save() start.'
    patrn_rubbish = '\/uid|username|space|search|blog|group\/'
    patrn_detail = '\/post\/'
    patrn_list = '\/list\/'

    user_id = session['user_id']
    inputForm = AdviceRegexListInputForm(request.form)
    start_url, site_domain, black_domain_str = get_domain_init(inputForm)

    # 提取主页、域名
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        for j in range(SHOW_MAX):
            inputForm.regex_list.append_entry()

        for j in range(SHOW_MAX):
            inputForm.keyword_list.append_entry()

        return render_template('setting_advice.html', inputForm=inputForm)
    else:
        set_domain_init(inputForm, start_url, site_domain, black_domain_str)

    detail_regex_save_list = []
    list_regex_save_list = []

    for item in inputForm.regex_list.data:
        if item['select'] == '1':  # 列表
            list_regex_save_list.append({'regex': item['regex'], 'weight': '0'})
        elif item['select'] == '2':  # 详情
            detail_regex_save_list.append({'regex': item['regex'], 'weight': '0'})
        else:
            continue

    for item in inputForm.keyword_list.data:
        if item['select'] == '1':  # 列表
            list_regex_save_list.append({'regex': item['keyword'], 'weight': '0'})
        elif item['select'] == '2':  # 详情
            detail_regex_save_list.append({'regex': item['keyword'], 'weight': '0'})
        else:
            continue

    if len(detail_regex_save_list) == 0 and len(list_regex_save_list) == 0:
        flash(u'请选择采用规则或关键字的类别。')
        return render_template('setting_advice.html', inputForm=inputForm)

    mysql_db = MySqlDrive()
    cnt = mysql_db.save_all_setting(user_id, start_url, site_domain, '', black_domain_str,
                                    detail_regex_save_list, list_regex_save_list)
    if cnt == 1:
        flash(u"采用项目保存完成.")
        print u'[info]setting_list_save_and_run() MySQL save success.'
    else:
        flash(u"采用项目保存失败.")
        print u'[error]setting_list_save_and_run() MySQL save failure.'

    return render_template('setting_advice.html', inputForm=inputForm,
                           patrn_rubbish=patrn_rubbish, patrn_detail=patrn_detail, patrn_list=patrn_list)


@app.route('/setting_advice_window', methods=['GET', 'POST'])
def setting_advice_window():
    user_id = session['user_id']
    inputForm = AdviceUrlListForm()

    # 提取主页、域名
    start_url, site_domain, black_domain_str = get_domain_init()
    # 提取主页、域名
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        return render_template('setting_advice_window.html', inputForm=inputForm)

    regex = request.args.get('regex')
    print '[info]setting_advice_window() regex or keyword is: ', regex

    fp = open(EXPORT_FOLDER + '/advice(' + site_domain + ').json', "r")
    url_list = fp.readlines()
    fp.close()

    matched_url_list = []
    for url in url_list:
        if re.search(regex, url):
            matched_url_list.append(url)

    # print '[info]setting_advice_window()',regex, '->', matched_url_list
    ####  页面(url)
    for url in matched_url_list:
        regexForm = AdviceUrlForm()
        regexForm.url = url
        inputForm.url_list.append_entry(regexForm)

    for j in range(SHOW_MAX - len(matched_url_list)):
        inputForm.url_list.append_entry()

    return render_template('setting_advice_window.html', inputForm=inputForm)


######### 配置详情页/列表页  #############################################################################
@app.route('/list_detail_init', methods=['GET', 'POST'])
def list_detail_init():
    '''
    从MySql初始化Web页面和Redis
    '''
    INIT_MAX = 10
    user_id = session['user_id']
    req_scope_sel = request.args.get('scope')

    inputForm = ListDetailRegexSettingForm(request.form)
    inputForm.scope_sel.data = req_scope_sel

    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain_str = get_domain_init()
    print start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        for j in range(INIT_MAX):
            inputForm.detail_regex_list.append_entry()

        for j in range(INIT_MAX):
            inputForm.list_regex_list.append_entry()

        return render_template('setting_list_detail.html', inputForm=inputForm)
    else:
        inputForm.start_url.data = start_url
        inputForm.site_domain.data = site_domain
        inputForm.black_domain_str.data = black_domain_str

    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    if req_scope_sel is None or req_scope_sel == '00':  # 未设定 预置规则
        #### 从MySql 设置/还原 redis 和 页面(详情页)
        detail_regexs = mysql_db.get_current_regexs('detail', user_id, start_url, site_domain, black_domain_str)
        cnt = 0
        for (scope, white_or_black, weight, regex, etc) in detail_regexs:
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
            # regexForm = RegexSettingForm(regex_data)
            # inputForm.detail_regex_list.entries[i] = regexForm

            regexForm = RegexSettingForm()
            regexForm.regex = regex
            regexForm.weight = weight
            regexForm.score = int(score)
            inputForm.detail_regex_list.append_entry(regexForm)
            cnt += 1

        for j in range(INIT_MAX - cnt):
            inputForm.detail_regex_list.append_entry()

        ####  从MySql 设置/还原 redis 和 页面(列表页)
        list_regexs = mysql_db.get_current_regexs('list', user_id, start_url, site_domain, black_domain_str)
        cnt = 0
        for (scope, white_or_black, weight, regex, etc) in list_regexs:
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
            # regexForm = RegexSettingForm(regex_data)
            # inputForm.list_regex_list.entries[i] = regexForm

            regexForm = RegexSettingForm()
            regexForm.regex = regex
            regexForm.weight = weight
            regexForm.score = int(score)
            inputForm.list_regex_list.append_entry(regexForm)
            cnt += 1

        for j in range(INIT_MAX - cnt):
            inputForm.list_regex_list.append_entry()

    else:  # 设定 预置规则
        #### 将预置设定 表示到 页面
        partn_list = mysql_db.get_preset_partn(req_scope_sel)
        for (partn_type, partn, weight) in partn_list:
            regexForm = RegexSettingForm()
            regexForm.regex = partn
            regexForm.weight = weight
            regexForm.score = 0
            inputForm.list_regex_list.append_entry(regexForm)

        for j in range(SHOW_MAX - len(partn_list)):
            inputForm.list_regex_list.append_entry()

    flash(u'初始化配置完成')
    return render_template('setting_list_detail.html', inputForm=inputForm)


@app.route('/list_detail_save_and_run', methods=['POST'])
def list_detail_save_and_run():
    user_id = session['user_id']
    # user_id = 'admin'
    global process_id
    inputForm = ListDetailRegexSettingForm(request.form)
    # if inputForm.validate_on_submit():
    # if request.method == 'POST' and inputForm.validate():
    start_url, site_domain, black_domain_str = get_domain_init(inputForm)
    set_domain_init(inputForm, start_url, site_domain, black_domain_str)  # 同步回sesstion
    if inputForm.mode.data == False:
        mode = 'all'  # 全部
    else:
        mode = 'exact'  # 精确匹配

    if start_url.strip() == '' or site_domain.strip() == '':
        flash(u'必须设置主页、域名信息！')
        return render_template('setting_list_detail.html', inputForm=inputForm)

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
        return render_template('setting_list_detail.html', inputForm=inputForm)

    if len(list_regex_save_list) != len(set([i['regex'] + i['weight'] for i in list_regex_save_list])):
        flash(u"列表页正则表达式有重复。")
        return render_template('setting_list_detail.html', inputForm=inputForm)

    if len(detail_regex_save_list) != len(set([i['regex'] + i['weight'] for i in detail_regex_save_list])):
        flash(u"详情页正则表达式有重复。")
        return render_template('setting_list_detail.html', inputForm=inputForm)

    if len(set([i['regex'] for i in list_regex_save_list]).intersection(
            set([i['regex'] for i in detail_regex_save_list]))) > 0:
        flash(u"列表和详情页中的正则表达式不能重复。")
        return render_template('setting_list_detail.html', inputForm=inputForm)

    #### 清空所有Redis,保存手工配置,用于匹配次数积分。
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    redis_db.conn.delete(redis_db.manual_w_list_rule_zset_key)
    for item in list_regex_save_list:
        if item['regex'].find('/^') < 0:
            redis_db.conn.zadd(redis_db.manual_w_list_rule_zset_key, 0, item['regex'])

    redis_db.conn.delete(redis_db.manual_b_list_rule_zset_key)
    for item in list_regex_save_list:
        if item['regex'].find('/^') >= 0:
            redis_db.conn.zadd(redis_db.manual_b_list_rule_zset_key, 0, item['regex'])

    redis_db.conn.delete(redis_db.manual_w_detail_rule_zset_key)
    for item in detail_regex_save_list:
        if item['regex'].find('/^') < 0:
            redis_db.conn.zadd(redis_db.manual_w_detail_rule_zset_key, 0, item['regex'])

    redis_db.conn.delete(redis_db.manual_b_detail_rule_zset_key)
    for item in detail_regex_save_list:
        if item['regex'].find('/^') >= 0:
            redis_db.conn.zadd(redis_db.manual_b_detail_rule_zset_key, 0, item['regex'])

    if inputForm.hold.data == False:  # 清除上次结果
        redis_db.conn.delete(redis_db.list_urls_zset_key)
        redis_db.conn.delete(redis_db.detail_urls_set_key)
    else:  # 保留上次结果
        redis_db.reset_rule(mode=mode, detail_rules=detail_regex_save_list, list_rules=list_regex_save_list)

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
        print u'[info]list_detail_save_and_run() MySQL save success.'
    else:
        flash(u"MySQL保存失败.")
        print u'[error]list_detail_save_and_run() MySQL save failure.'
        return render_template('setting_list_detail.html', inputForm=inputForm)

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
        print u'[error]list_detail_save_and_run() modify ' + INIT_CONFIG + u' failure.'
        return render_template('setting_list_detail.html', inputForm=inputForm)

    # 执行抓取程序
    if inputForm.save_run_list.data:
        if os.name == 'nt':
            # DOS "start" command
            print '[info]--- %s run on windows' % SHELL_LIST_CMD
            os.startfile(SHELL_LIST_CMD)
        else:
            print '[info]--- %s run on %s' % (SHELL_LIST_CMD, MY_OS)
            p = subprocess.Popen(SHELL_LIST_CMD, shell=True)
            process_id = p.pid
            print '[info]--- process_id:', process_id

    if inputForm.save_run_detail.data:
        if os.name == 'nt':
            # DOS "start" command
            print '[info]--- %s run on windows' % SHELL_DETAIL_CMD
            os.startfile(SHELL_DETAIL_CMD)
        else:
            print '[info]--- %s run on %s.', SHELL_DETAIL_CMD
            p = subprocess.Popen(SHELL_DETAIL_CMD, shell=True)
            process_id = p.pid
            print '[info]--- process_id:', process_id

    return render_template('setting_list_detail.html', inputForm=inputForm)


######### show_result.html   #############################################################################
@app.route('/show_result_init', methods=['GET', 'POST'])
def show_result_init():
    user_id = session['user_id']
    inputForm = ResultForm()
    # 提取主页、域名
    start_url, site_domain, black_domain_str = get_domain_init()
    print '[info]show_result()', start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。', category='warning')
        return render_template('show_result.html', inputForm=inputForm)

    mysql_db = MySqlDrive()
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    # 列表页正则
    select_items = [(i, i) for i in mysql_db.get_list_regex(user_id, start_url, site_domain)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.list_regex_sel.choices = select_items
    regex_sel = inputForm.list_regex_sel.data
    inputForm.list_result = redis_db.get_list_urls_by_regex(regex_sel)

    # 详情页正则
    select_items = [(i, i) for i in mysql_db.get_detail_regex(user_id, start_url, site_domain)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.detail_regex_sel.choices = select_items
    regex_sel = inputForm.detail_regex_sel.data
    inputForm.detail_result = redis_db.get_detail_urls_by_regex(regex_sel)

    return render_template('show_result.html', inputForm=inputForm)


@app.route('/show_result', methods=['GET', 'POST'])
def show_result():
    user_id = session['user_id']
    inputForm = ResultForm(request.form)
    # 提取主页、域名
    start_url, site_domain, black_domain_str = get_domain_init()
    print '[info]show_result()', start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。', category='warning')
        return render_template('show_result.html', inputForm=inputForm)

    mysql_db = MySqlDrive()
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)

    # 列表页正则
    if inputForm.list_match.data:
        regex_sel = inputForm.list_regex_sel.data
        inputForm.list_result = redis_db.get_list_urls_by_regex(regex_sel)

        select_items = [(i, i) for i in mysql_db.get_detail_regex(user_id, start_url, site_domain)]
        select_items.append(('', ''))
        select_items.sort()
        inputForm.detail_regex_sel.choices = select_items
        regex_sel = inputForm.detail_regex_sel.data
        inputForm.detail_result = redis_db.get_detail_urls_by_regex(regex_sel)

    # 详情页正则
    if inputForm.detail_match.data:
        regex_sel = inputForm.detail_regex_sel.data
        inputForm.detail_result = redis_db.get_detail_urls_by_regex(regex_sel)

        select_items = [(i, i) for i in mysql_db.get_list_regex(user_id, start_url, site_domain)]
        select_items.append(('', ''))
        select_items.sort()
        inputForm.list_regex_sel.choices = select_items
        regex_sel = inputForm.list_regex_sel.data
        inputForm.list_result = redis_db.get_list_urls_by_regex(regex_sel)

    return render_template('show_result.html', inputForm=inputForm)


######### show_unkown.html  #############################################################################
@app.route('/show_unkown_urls', methods=['GET', 'POST'])
def show_unkown_urls():
    inputForm = ResultForm()

    # 提取主页、域名
    user_id = session['user_id']
    start_url, site_domain, black_domain_str = get_domain_init()
    print '[info]show_unkown_urls()', start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。', category='warning')
        return render_template('show_unkown_urls.html', inputForm=inputForm)

    mysql_db = MySqlDrive()
    # 列表页正则
    select_items = [(i, i) for i in mysql_db.get_list_regex(user_id, start_url, site_domain)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.list_regex_sel.choices = select_items

    # 详情页正则
    select_items = [(i, i) for i in mysql_db.get_detail_regex(user_id, start_url, site_domain)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.detail_regex_sel.choices = select_items

    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    inputForm.unkown_url_list = redis_db.get_unkown_urls()
    if len(inputForm.unkown_url_list) == 0:
        flash(u'目前URL已全部匹配。')
        return render_template('show_unkown_urls.html', inputForm=inputForm)

    util = Util()
    advice_regex_dic, advice_keyword_dic = util.advice_regex_keyword(inputForm.unkown_url_list)
    # 关键字统计
    keywords = []
    score_list = []
    sorted_list = sorted(advice_keyword_dic.iteritems(), key=lambda d: d[1], reverse=True)
    for (k, v) in sorted_list:
        keywords.append(k)
        score_list.append(str(v))

    inputForm.keywords_str = ("'" + "','".join(keywords) + "'")
    inputForm.keywords_matched_cnt = ','.join(score_list)

    # 数字归一化后分类统计
    category_withlist_dict = util.convert_urls_to_category(inputForm.unkown_url_list)
    for (k, v) in category_withlist_dict.items():
        inputForm.category_list.append({'category': k, 'page_count': len(v)})

    category_compress_dict = util.compress_category_alpha(category_withlist_dict)
    for (k, v) in category_compress_dict.items():
        inputForm.category_compress_list.append({'category': k, 'page_count': v})

    inputForm.category_list.sort(key=lambda x: x['page_count'], reverse=True)
    inputForm.category_compress_list.sort(key=lambda x: x['page_count'], reverse=True)
    print inputForm.category_list
    print inputForm.category_compress_list
    return render_template('show_unkown_urls.html', inputForm=inputForm)


######### show_process.html  #############################################################################
@app.route('/show_process', methods=['GET', 'POST'])
def show_process():
    user_id = session['user_id']
    inputForm = ListDetailRegexSettingForm()
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
    flash(u'每隔30秒刷新 ' + start_url + u' 的实时采集信息。')
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
    user_id = session['user_id']
    # user_id = 'admin'
    start_url, site_domain, black_domain = get_domain_init()

    # 保存 实时 列表页结果
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    fp = open(EXPORT_FOLDER + '/result-list(' + site_domain + ').log', 'w')
    for line in redis_db.conn.zrange(redis_db.list_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
    fp.close()
    # 保存 实时 详情页结果
    fp = open(EXPORT_FOLDER + '/result-detail(' + site_domain + ').log', 'w')
    for line in redis_db.conn.smembers(redis_db.detail_urls_set_key):
        fp.write(line + '\n')
    fp.close()

    # 将实时结果作为最终结果保存到DB
    mysql_db = MySqlDrive()
    mysql_db.save_result_file_to_mysql(start_url, site_domain)
    flash(u'列表页结果保存DB成功。')
    print '[info]save finally result to DB OK.'
    return redirect(url_for('show_process'), 302)


@app.route('/kill_spider', methods=['GET', 'POST'])
def kill_spider():
    if os.name == 'nt':
        flash(u"请手工关闭windows控制台.")
        # os.system("taskkill /PID %s /F" % process_id)
    else:
        subprocess.Popen(['/bin/sh', '-c', './kill_spider_list.sh'])
        flash(u"已经结束进程.")
    return redirect(url_for('show_process'), 302)


@app.route('/reset_all', methods=['GET', 'POST'])
def reset_all():
    user_id = session['user_id']
    start_url, site_domain, black_domain_str = get_domain_init()
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return redirect(url_for('show_process'), 302)

    # 绘图文件清零
    fp = open(EXPORT_FOLDER + '/' + PROCESS_SHOW_JSON + '(' + site_domain + ').json', 'w')
    fp.write('')
    fp.close()

    # web_server.log清零
    if os.name == 'nt':  # windows
        fp = open('web_server.log', 'w')
        fp.write('')
        fp.close()
    else:  # linux
        fp = open('./web_server.log', 'w')
        fp.write('')
        fp.close()

    # 清除redis 计算过程中的数据
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    redis_db.conn.delete(redis_db.process_cnt_hset_key)
    redis_db.conn.delete(redis_db.list_urls_zset_key)
    redis_db.conn.delete(redis_db.detail_urls_set_key)
    redis_db.conn.delete(redis_db.manual_w_list_rule_zset_key)
    redis_db.conn.delete(redis_db.manual_b_list_rule_zset_key)
    redis_db.conn.delete(redis_db.manual_w_detail_rule_zset_key)
    redis_db.conn.delete(redis_db.manual_b_detail_rule_zset_key)
    redis_db.conn.delete(redis_db.unkown_urls_set_key)

    return redirect(url_for('show_process'), 302)


######### content_advice.html  #############################################################################
@app.route('/content_advice', methods=['GET', 'POST'])
def content_advice():
    inputForm = ContentAdvice(request.form)
    user_id = session['user_id']
    start_url, site_domain, black_domain_str = get_domain_init()
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('content_advice.html', inputForm=inputForm)

    mysql_db = MySqlDrive()
    select_items = [(i, i) for i in mysql_db.get_detail_regex(user_id, start_url, site_domain)]
    select_items.append(('', ''))
    select_items.sort()
    inputForm.detail_regex_sel.choices = select_items
    regex_sel = inputForm.detail_regex_sel.data
    # inputForm.detail_regex_list = inputForm.detail_regex_sel.data
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    inputForm.detail_url_list = redis_db.get_detail_urls_by_regex(regex_sel)
    print '[info]content_advice()', inputForm.detail_url_list

    flash(u'获取链接内容需要一点时间，请稍等。。。')
    return render_template('content_advice.html', inputForm=inputForm)


@app.route('/get_content_advice', methods=["GET", "POST"])
def get_content_advice():
    url = request.args.get('url')
    title, ctime, content, auther = myreadability.get_content_advice(url)
    ret = {'title': title, 'content': content}
    jsonStr = json.dumps(ret, sort_keys=True)
    return jsonStr


@app.route('/content_save_and_run', methods=['GET', 'POST'])
def content_save_and_run():
    user_id = session['user_id']
    inputForm = ContentItemForm(request.form)

    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain_str = mysql_db.get_current_main_setting(user_id)
    print '[info]content_save_and_run()', user_id, start_url, site_domain, black_domain_str
    if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('admin_preset.html', inputForm=inputForm)

    cnt = mysql_db.save_content_setting(user_id=user_id, start_url=start_url, site_domain=site_domain,
                                        title_exp=inputForm.title_exp.data, author_exp=inputForm.author_exp.data,
                                        content_exp=inputForm.content_exp.data, ctime_exp=inputForm.ctime_exp.data)
    if cnt == 1:
        flash(u"MySQL保存完毕.")
        print u'[info]content_save_and_run() MySQL save success.'
    else:
        flash(u"MySQL保存失败.")
        print u'[error]content_save_and_run() MySQL save failure.'
        return render_template('admin_preset.html', inputForm=inputForm)

    if os.name == 'nt':
        # DOS "start" command
        print '[info] run windows', SHELL_CONTENT_CMD
        os.startfile(SHELL_CONTENT_CMD)
    else:
        print '[info] run linux', SHELL_CONTENT_CMD
        p = subprocess.Popen(SHELL_CONTENT_CMD, shell=True)
        process_id = p.pid
        print '[info] process_id:', process_id

    return render_template('admin_preset.html', inputForm=inputForm)


######### history.html  #############################################################################
@app.route('/history_search', methods=['GET', 'POST'])
def history_search():
    user_id = session['user_id']
    # user_id = 'admin'
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

    return render_template('history.html', user_id=user_id, inputForm=inputForm, outputForm=outputForm)


######### admin_preset.html  #############################################################################
@app.route('/preset_init', methods=['GET', 'POST'])
def preset_init():
    user_id = session['user_id']
    inputForm = PresetListForm(request.form)

    mysql_db = MySqlDrive()
    partn_list = mysql_db.get_preset_partn(scope='01')

    ####  页面(regex)
    for (partn_type, partn, weight) in partn_list:
        presetForm = PresetForm()
        presetForm.partn_type_sel = partn_type
        presetForm.partn = partn
        presetForm.weight_sel = weight
        inputForm.partn_list.append_entry(presetForm)

    for j in range(SHOW_MAX * 5 - len(partn_list)):
        inputForm.partn_list.append_entry()

    return render_template('admin_preset.html', inputForm=inputForm, user_id=user_id)


@app.route('/preset_change', methods=['GET', 'POST'])
def preset_change():
    user_id = session['user_id']
    scope_sel = request.args.get('scope')
    inputForm = PresetListForm(request.form)
    inputForm.scope_sel.data = scope_sel

    mysql_db = MySqlDrive()
    partn_list = mysql_db.get_preset_partn(scope_sel)

    ####  页面(regex)
    for (partn_type, partn, weight) in partn_list:
        presetForm = PresetForm()
        presetForm.partn_type_sel = partn_type
        presetForm.partn = partn
        presetForm.weight_sel = weight
        inputForm.partn_list.append_entry(presetForm)

    for j in range(SHOW_MAX * 5 - len(partn_list)):
        inputForm.partn_list.append_entry()

    return render_template('admin_preset.html', inputForm=inputForm, user_id=user_id)


######### admin_server_log.html #############################################################################
@app.route('/admin_server_log', methods=['GET', 'POST'])
def admin_server_log():
    user_id = session['user_id']
    # user_id = 'admin'
    inputForm = ShowServerLogInputForm(request.form)
    # 提取主页、域名
    mysql_db = MySqlDrive()
    start_url, site_domain, black_domain_str = get_domain_init()

    if MY_OS == 'windows':  # windows
        f = open('web_server.log', 'r').readlines()
        if len(f) >= 80:
            l = f[-80:]
        else:
            l = f
        server_log_list = l
    else:  # linux mac
        if inputForm.unkown_sel.data:
            cmd = 'tail -80 ./web_server.log'
            # cmd = "tail -10000 web_server.log | grep -E 'unkown|list|detail' |tail -80"
        else:
            cmd = 'tail -80 ./web_server.log'

        p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
        server_log_list = p.stdout.readlines()

    if len(server_log_list) == 0:
        flash(u'web_server.log未生成。')
        return render_template('admin_server_log.html', inputForm=inputForm, server_log_list=[])

    # 保存 实时 列表页结果
    redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
    fp = open(EXPORT_FOLDER + '/result-list(' + site_domain + ').log', 'w')
    for line in redis_db.conn.zrange(redis_db.list_urls_zset_key, 0, -1, withscores=False):
        fp.write(line + '\n')
    fp.close()

    # 保存 实时 详情页结果
    fp = open(EXPORT_FOLDER + '/result-detail(' + site_domain + ').log', 'w')
    for line in redis_db.conn.smembers(redis_db.detail_urls_set_key):
        fp.write(line + '\n')
    fp.close()

    return render_template('admin_server_log.html', inputForm=inputForm,
                           server_log_list=[x.encode('utf8') for x in server_log_list])


######### admin_tools.html  #############################################################################
@app.route('/admin_tools')
def admin_tools():
    # print request.path
    flash(u"请选择操作。")
    return redirect(url_for('tool_upload'), 302)


@app.route('/export/<path:filename>')
def download_file(filename):
    print '[info]download_file()', filename
    return send_from_directory(app.config['EXPORT_FOLDER'], filename, as_attachment=True)


@app.route('/tool_upload', methods=['GET', 'POST'])
def tool_upload():
    if request.method == 'GET':
        return render_template('admin_tools.html')

    elif request.method == 'POST':
        f = request.files['file']
        # 获取一个安全的文件名，仅支持ascii字符。
        f_name = secure_filename(f.filename)
        f.save(os.path.join(EXPORT_FOLDER, f_name))
        flash(u"上传成功.")
        print '[info]help_upload() ok.', f_name
        return render_template('admin_tools.html')


@app.route('/tool_reset_redis', methods=['GET', 'POST'])
def tool_reset_redis():
    redis_db = RedisDrive()
    keys = redis_db.conn.keys()
    for key in keys:
        redis_db.conn.delete(key)

    return redirect(url_for('tool_upload'), 302)


@app.route('/tool_getenv', methods=['GET', 'POST'])
def tool_getenv():
    json_str = {'INIT_CONFIG': INIT_CONFIG,

                'REDIS_SERVER': REDIS_SERVER,
                'DEDUP_SETTING': DEDUP_SETTING,

                'MYSQLDB_HOST': MYSQLDB_HOST,
                'MYSQLDB_USER': MYSQLDB_USER,
                'MYSQLDB_PORT': MYSQLDB_PORT,
                'MYSQLDB_PASSWORD': MYSQLDB_PASSWORD,
                'MYSQLDB_SELECT_DB': MYSQLDB_SELECT_DB,
                'MYSQLDB_CHARSET': MYSQLDB_CHARSET,

                'PROCESS_SHOW_JSON': PROCESS_SHOW_JSON,
                'SHOW_MAX': SHOW_MAX,
                'EXPORT_FOLDER': EXPORT_FOLDER,
                'CONFIG_JSON': CONFIG_JSON,

                'MY_OS': MY_OS,
                'SHELL_ADVICE_CMD': SHELL_ADVICE_CMD,
                'SHELL_LIST_CMD': SHELL_LIST_CMD,
                'SHELL_CONTENT_CMD': SHELL_CONTENT_CMD,
                'ALLSITE_INI': ALLSITE_INI,

                'DEPLOY_HOST': DEPLOY_HOST,
                'DEPLOY_PORT': DEPLOY_PORT
                }
    return render_template('admin_tools.html', json_str=json.dumps(json_str, indent=2))


@app.route('/tool_session_setting', methods=['POST'])
def tool_session_setting():
    session['start_url'] = request.form['start_url']
    session['site_domain'] = request.form['site_domain']
    return redirect(url_for('tool_upload'), 302)


##########################################################################################
#  restful api
parser = reqparse.RequestParser()
parser.add_argument('regex')


def is_regex_exist(regex):
    user_id = session['user_id']
    start_url, site_domain, black_domain_str = get_domain_init()

    regexs = []
    mysql_db = MySqlDrive()
    current_regexs = mysql_db.get_current_regexs('detail', user_id, start_url, site_domain, black_domain_str)
    for (scope, white_or_black, weight, regex, etc) in current_regexs:
        regexs.append(regex)
    print '[info]is_regex_exist()', unicode(regex), regexs
    for r in regexs:
        if unicode(regex) == r:
            print '[info]is_regex_exist() True'
            return True
        else:
            print '[info]is_regex_exist() False'
            return False


# DetailRegexMaintenance
class DetailRegexMaintenance(Resource):
    def get(self, regex_type):
        msg = ''
        args = parser.parse_args()
        regex = args['regex']
        if is_regex_exist(regex_type):
            msg = u"{} 不存在。".format(regex)
        return {'msg': msg}

    def delete(self, regex_type):
        print '[info]DetailRegexMaintenance() delete start.', regex_type
        user_id = session['user_id']
        start_url, site_domain, black_domain_str = get_domain_init()
        if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
            return {'msg': u'请设定主页，域名信息。'}, 201

        args = parser.parse_args()
        regex = args['regex']

        if is_regex_exist(regex) is not True:
            msg = u"{} 不存在，无法删除。".format(regex)
            return {'msg': msg}, 404

        mysql_db = MySqlDrive()
        ret = mysql_db.delete_regex(user_id, start_url, site_domain, 'detail', regex)

        redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
        if regex.find('/^') < 0:  # 白名单
            redis_db.conn.zrem(redis_db.manual_w_detail_rule_zset_key, regex)
        else:  # 黑名单
            redis_db.conn.zrem(redis_db.manual_b_detail_rule_zset_key, regex)

        print '[info]DetailRegexMaintenance() delete end.'
        return {'regex': u'删除完成。'}, 204

    def put(self, regex_type):
        print '[info]DetailRegexMaintenance() put start.', regex_type
        user_id = session['user_id']
        start_url, site_domain, black_domain_str = get_domain_init()
        if start_url is None or start_url.strip() == '' or site_domain is None or site_domain.strip() == '':
            return {'msg': u'请设定主页，域名信息。'}, 201

        args = parser.parse_args()
        regex = args['regex']

        if is_regex_exist(regex) is True:
            msg = u"{} 已存在，无法添加。".format(regex)
            return {'msg': msg}, 404

        mysql_db = MySqlDrive()
        ret = mysql_db.add_regex(user_id, start_url, site_domain, black_domain_str, is_detail_regex=True, regex=regex)

        redis_db = RedisDrive(start_url=start_url, site_domain=site_domain)
        if regex.find('/^') < 0:  # 白名单
            if redis_db.conn.zrank(redis_db.manual_w_detail_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_w_detail_rule_zset_key, 0, regex)
        else:  # 黑名单
            if redis_db.conn.zrank(redis_db.manual_b_detail_rule_zset_key, regex) is None:
                redis_db.conn.zadd(redis_db.manual_b_detail_rule_zset_key, 0, regex)
        print '[info]DetailRegexMaintenance() put end.'
        return {'msg': u'添加完成。'}, 201


##
## Actually setup the Api resource routing here
##
api.add_resource(DetailRegexMaintenance, '/regexs/<regex_type>')

REGEXS = {
    'regex1': {'regex': '\/$'},
    'regex2': {'regex': '/list-'},
    'regex3': {'regex': '/index'},
    'regex4': {'regex': 'unkown'},
}


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return REGEXS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(REGEXS.keys()).lstrip('regex')) + 1
        todo_id = 'regex%i' % todo_id
        REGEXS[todo_id] = {'regex': args['regex']}
        return REGEXS[todo_id], 201


##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')

##########################################################################################
if __name__ == '__main__':
    if INIT_CONFIG.find('deploy') > 0:
        app.run(host=DEPLOY_HOST, port=DEPLOY_PORT, debug=False)
    else:
        app.run(debug=True)
