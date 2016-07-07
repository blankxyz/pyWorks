#!/usr/bin/env python
# coding=utf-8
import re
import os
import redis
import json
import datetime
import subprocess
from flask import Flask, render_template
from flask.ext.wtf import Form
from flask.ext.bootstrap import Bootstrap
from wtforms.validators import Required
from flask.ext.wtf import Form
from wtforms import IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms import validators

app = Flask(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'guess'
bootstrap = Bootstrap(app)


# def is_me(form, field): #自定义check函数
#     if field.data != 'yes':
#         raise validators.ValidationError('Must input "yes"') #FormField对象
#
# class addressForm(Form):
#     city = IntegerField('city', [validators.required()])
#     area = IntegerField('area', [validators.required()])
#     building = StringField('building')
#
#
# class MyForm(Form):
#     me = StringField('Is your self info?',[is_me,validators.Length(min=1,max=3)])
#     name = StringField('What is your name?',
#                        [validators.InputRequired('name'),
#                        validators.Regexp('\w+', message="Must contain 0-9 aA-zZ")],
#                        description='must input your name.',default=u'songyq')
#     birthday  = DateTimeField('Your Birthday', format='%m/%d/%y')
#     sex  = RadioField('Sex', choices=[(1,'man'),(2,'women')])
#     age = DecimalField('How old are you?',
#                        [validators.DataRequired('must be number!'),
#                         validators.NumberRange(min=10, max=100, message='10~100')],
#                        description='must input your age.')
#     national = SelectField('national', choices=[('cn', 'china'), ('en', 'usa'), ('jp', 'japan')])
#     address1 = TextAreaField('Address1', [validators.optional(), validators.length(max=200)])
#     address2 = FormField(addressForm)
#     phone = IntegerField('What is your phone number?',
#                          [validators.InputRequired('phone')],
#                          description='must input your phone.')
#     password = PasswordField('New Password',
#                              [validators.Required()])
#     confirm = PasswordField('Repeat Password',
#                             [validators.Required(),
#                              validators.EqualTo('password', message='Passwords must match')])
#     accept_tos = BooleanField('singe boy', [validators.Required()])
#     email = TextField('Email Address', [validators.Length(min=6, message=(u'Little short for an email address?')),
#                                         validators.Email(message=(u'That\'s not a valid email address.'))])
#     submit = SubmitField('Submit')
class DBDrive(object):
    def __init__(self, start_urls, site_domain, redis_setting):
        self.site_domain = site_domain  # 'cpt.xtu.edu.cn'  # 湘潭大学
        self.start_urls = start_urls  # 'http://cpt.xtu.edu.cn/'
        self.conn = redis.StrictRedis.from_url(redis_setting)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        print 'init DBDrive',self.site_domain,self.start_urls,self.conn

    def save_regex(self, regexs):
        print 'save_regex DBDrive', regexs, self.site_domain, self.start_urls, self.conn
        for reg in regexs:
            if reg:
                print 'write', reg
                self.conn.zadd(self.detail_urls_rule1_zset_key, self.done_flg, reg)

    def covert_to_json(self, json_file):
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        detail_cnt = self.conn.zcard(self.detail_urls_zset_key)
        list_cnt = self.conn.zcard(self.list_urls_zset_key)
        list_done_urls = self.conn.zrangebyscore(
            self.list_urls_zset_key, self.done_flg, self.done_flg)
        list_done_cnt = len(list_done_urls)
        t_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cnt_info = {'times': t_stamp, 'rule0_cnt': rule0_cnt, 'rule1_cnt': rule1_cnt,
                    'detail_cnt': detail_cnt, 'list_cnt': list_cnt, 'list_done_cnt': list_done_cnt}
        self.conn.hset(
            self.process_cnt_hset_key, t_stamp, json.dumps(cnt_info))
        print cnt_info
        jsonStr = json.dumps(cnt_info)
        fp = open(json_file, 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()


class MyForm(Form):
    start_urls = StringField(u'主页', [validators.InputRequired('start_urls')],
                             description='home page.', default='http://cpt.xtu.edu.cn/')
    site_domain = StringField(u'domain', [validators.InputRequired('site_domain')],
                              description='domain.', default='cpt.xtu.edu.cn')
    regex1 = StringField(u'表达式1', [validators.InputRequired('regex1')],
                         description='regex.',
                         default='http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    regex2 = StringField(u'表达式2', [validators.InputRequired('regex2')],
                         description='regex.',
                         default='http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html')
    regex3 = StringField(u'表达式3', [validators.InputRequired('regex3')],
                         description='regex.',
                         default='http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html')
    submit = SubmitField(u'添加')


class CollageProcessInfo(object):
    def __init__(self, json_file):
        self.json_file = json_file

    def convert_file_to_list(self):
        rule0_cnt = []
        rule1_cnt = []
        detail_cnt = []
        list_cnt = []
        list_done_cnt = []
        times = []

        fp = open(self.json_file, 'r')
        for line in fp.readlines():
            dic = eval(line)
            times.append(dic.get('times'))
            rule0_cnt.append(dic.get('rule0_cnt'))
            rule1_cnt.append(dic.get('rule1_cnt'))
            detail_cnt.append(dic.get('detail_cnt'))
            list_cnt.append(dic.get('list_cnt'))
            list_done_cnt.append(dic.get('list_done_cnt'))
        fp.close()
        return times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt


@app.route('/', methods=['GET', 'POST'])
def index():
    start_urls = 'http://cpt.xtu.edu.cn/'
    site_domain = 'cpt.xtu.edu.cn'
    redis_setting = 'redis://127.0.0.1/14'
    regex1, regex2, regex3 = None, None, None

    myForm = MyForm(start_urls=start_urls, domain=site_domain)
    if myForm.validate_on_submit():
        start_urls = myForm.start_urls.data
        site_domain = myForm.site_domain.data
        regex1 = myForm.regex1.data
        regex2 = myForm.regex2.data
        regex3 = myForm.regex3.data
    else:
        print 'no submit................'
        regex1 = 'http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html'
        regex2 = 'http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html'
        regex3 = 'http://cpt.xtu.edu.cn/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\d{4}/?\d{4}/\d{1,}.html'
    # myForm.regex.data = ''
    # myForm.start_urls.data = ''
    # myForm.site_domain.data = ''
    print 'index',start_urls,site_domain, [regex1, regex2, regex3]
    # 将regex写入redis-rule1
    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)
    db.save_regex([regex1, regex2, regex3])

    # 只启动一次 run_spider.bat
    json_file = "process-temp.json"
    # if os.path.exists(json_file) is False:
    #     subprocess.call(["run_spider.bat"], shell=True)

    # 从redis提取实时信息，转换成json文件
    db.covert_to_json(json_file)

    collage = CollageProcessInfo(json_file)
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    # 将json映射到html
    return render_template('url_rule_manual.html',
                           myForm=myForm,
                           start_urls=start_urls,
                           site_domain=site_domain,
                           regex1=regex1,
                           regex2=regex2,
                           regex3=regex3,
                           times=times,
                           rule0_cnt=rule0_cnt,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt)


if __name__ == '__main__':
    app.run(debug=True)
