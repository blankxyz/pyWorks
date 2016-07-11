#!/usr/bin/env python
# coding=utf-8
import re
import urlparse
import redis
import json
import datetime
import dedup
import subprocess
from flask import Flask, render_template, request, url_for, flash, redirect
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import FieldList, IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'success'
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

class RegexForm(Form):
    select = BooleanField(label=u'选择', default=False)
    regex = StringField(label=u'表达式') #, default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    score = IntegerField(label=u'匹配数', default=0)


class MyForm(Form):
    start_urls = StringField(label=u'主页', default='http://cpt.xtu.edu.cn/')
    site_domain = StringField(label='domain', default='cpt.xtu.edu.cn')
    redis_setting = StringField(label='redis', default='redis://127.0.0.1/14')
    dedup = StringField(label='dedup', default='redis://192.168.110.110/0')

    list_keyword = StringField(label=u'列表页特征词', default='list;index;')
    detail_keyword = StringField(label=u'详情页特征词', default='post;content;')

    result = StringField(label=u'转换结果')
    convert = SubmitField(label=u'<<转换')
    url = StringField(label=u'URL例子')

    regex_list = FieldList(FormField(RegexForm), label=u'详情页正则表达式列表', min_entries=5)

    reset = BooleanField(label=u'将原有正则表达式的score清零', default=False)

    submit = SubmitField(label=u'保存')


class DBDrive(object):
    def __init__(self, start_urls, site_domain, redis_setting):
        self.site_domain = site_domain  # 'cpt.xtu.edu.cn'  # 湘潭大学
        self.start_urls = start_urls  # 'http://cpt.xtu.edu.cn/'
        self.conn = redis.StrictRedis.from_url(redis_setting)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.list_urls_keyword_zset_key = 'list_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_keyword_zset_key = 'detail_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        # print 'DBDrive init()', self.site_domain, self.start_urls, self.conn

    def save_regex(self, regexs):
        print 'save_regex()', regexs, self.site_domain, self.start_urls, self.conn
        for regex in regexs:
            if regex:
                self.conn.zadd(self.detail_urls_rule1_zset_key, self.done_flg, regex)

    def get_detail_urls(self):
        return self.conn.zrangebyscore(self.detail_urls_zset_key, self.done_flg, self.done_flg)

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
            cnt = 80

        return float(cnt) / len(urls)

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


def convert_path_to_rule(url):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    # print path
    pos = path.rfind('.')
    suffix = path[pos:]
    path = path[:pos]
    # print suffix,path
    split_path = path.split('/')
    # print split_path
    new_path_list = []
    for p in split_path:
        regex = re.sub(r'[a-zA-Z]', '[a-zA-Z]', p)
        regex = re.sub(r'\d', '\d', regex)
        new_path_list.append(convert_regex_format(regex))
    # print new_path
    new_path = '/'.join(new_path_list) + suffix
    return urlparse.urlunparse((scheme, netloc, new_path, '', '', ''))


def convert_regex_format(rule):
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


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('menu.html')


@app.route('/show', methods=['GET', 'POST'])
def show():
    start_urls = 'http://cpt.xtu.edu.cn/'
    site_domain = 'cpt.xtu.edu.cn'
    redis_setting = 'redis://127.0.0.1/14'

    # 只启动一次 run_spider.bat
    json_file = "process-temp.json"
    # if os.path.exists(json_file) is False:
    #     subprocess.call(["run_spider.bat"], shell=True)

    # 从redis提取实时信息，转换成json文件
    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)
    db.covert_to_json(json_file)

    collage = CollageProcessInfo(json_file)
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    matched_rate = db.get_matched_rate() * 100.0
    un_match_rate = 100.0 - matched_rate

    # 将json映射到html
    return render_template('show.html',
                           times=times,
                           rule0_cnt=rule0_cnt,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt,
                           matched_rate=matched_rate,
                           un_match_rate=un_match_rate)


@app.route('/setting', methods=['GET', 'POST'])
def setting():
    # setting.ini -----------------------------------
    start_urls = 'http://cpt.xtu.edu.cn/'
    site_domain = 'cpt.xtu.edu.cn'
    redis_setting = 'redis://127.0.0.1/14'

    myForm = MyForm()

    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)
    # FiledList设置无效
    rules1 = db.conn.zrange(db.detail_urls_rule1_zset_key,start=0, end=999, withscores=True)
    i = 0
    for rule, score in dict(rules1).iteritems():
        myForm.regex_list.data[i]['regex'] = rule
        myForm.regex_list.data[i]['score'] = score
    # FiledList设置无效

    #清除原有所有规则
    db.conn.zremrangebyscore(db.detail_urls_rule1_zset_key,min=0,max=99999999)

    #保存详情页关键字
    detail_keywords_str = []
    detail_keywords = db.conn.zrange(db.detail_urls_keyword_zset_key, start=0, end=999, withscores=False)
    for keyword in detail_keywords:
        detail_keywords_str.append(keyword)
    myForm.detail_keyword.data = ';'.join(detail_keywords_str)

    list_keywords_str = []
    list_keywords = db.conn.zrange(db.list_urls_keyword_zset_key, start=0, end=999, withscores=False)
    for keyword in list_keywords:
        list_keywords_str.append(keyword)
    myForm.list_keyword.data = ';'.join(list_keywords_str)

    flash(u'初始化配置完成')

    return render_template('setting.html', myForm=myForm)


@app.route('/convert',methods=["GET", "POST"])
def convert_to_regex():
    ret = {}
    convert_url = request.args.get('convert_url')
    ret['regex'] = convert_path_to_rule(convert_url)
    jsonStr = json.dumps(ret)
    print 'ajax()', convert_url,'->',jsonStr
    return jsonStr


@app.route('/submit_save_regex', methods=['POST'])
def submit_save_regex():
    print 'submit_save_regex() start'
    start_urls = None  # 'http://cpt.xtu.edu.cn/'
    site_domain = None  # 'cpt.xtu.edu.cn'
    redis_setting = None  # 'redis://127.0.0.1/14'
    regex_list = []

    myForm = MyForm(request.form)
    # if myForm.validate_on_submit():
    print 'request.method', request.method, 'myForm.validate()', myForm.validate()
    # if request.method == 'POST' and myForm.validate():
    start_urls = myForm.start_urls.data
    site_domain = myForm.site_domain.data
    redis_setting = myForm.redis_setting.data

    regex_list = myForm.regex_list.data

    regex_save_list = []
    for r in regex_list:
        select = r['select']
        regex = r['regex']
        score = r['score']
        if select and regex != '':
            regex_save_list.append(regex)

    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)

    regex_save_list = list(set(regex_save_list))
    db.save_regex(regex_save_list)

    # 清除原有，保存页面存储的详情页关键字
    db.conn.zremrangebyscore(db.detail_urls_keyword_zset_key, min=0, max=99999999)
    detail_key =  myForm.detail_keyword.data
    for keyword in detail_key.split(';'):
        if keyword !='' and db.conn.zrank(db.detail_urls_keyword_zset_key,keyword) is None:
            db.conn.zadd(db.detail_urls_keyword_zset_key,0,keyword)

    # 清除原有，保存页面存储的列表页关键字
    db.conn.zremrangebyscore(db.list_urls_keyword_zset_key, min=0, max=99999999)
    list_key = myForm.list_keyword.data
    for keyword in list_key.split(';'):
        if keyword !='' and db.conn.zrank(db.list_urls_keyword_zset_key,keyword) is None:
            db.conn.zadd(db.list_urls_keyword_zset_key,0,keyword)

    # 将原有正则表达式的score清零
    if myForm.reset:
        regex_reset = db.conn.zrange(db.detail_urls_rule1_zset_key,start=0,end=9999999)
        for regex in regex_reset:
            db.conn.zadd(db.detail_urls_rule1_zset_key, 0, regex)

    flash(u"保存并执行...")
    print 'submit_save_regex() OK!'
    # 只启动一次 run_spider.bat
    # if os.path.exists(json_file) is False:
    #     subprocess.call(["run_spider.bat"], shell=True)
    # else:
    #     print 'no submit................'
    return render_template('setting.html', myForm=myForm)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', err=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', err=e), 500


if __name__ == '__main__':
    app.run(debug=True)
