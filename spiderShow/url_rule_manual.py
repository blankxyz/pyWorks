#!/usr/bin/env python
# coding=utf-8
import re
import os
import urlparse
import redis
import json
import datetime
import dedup
import MySQLdb
import subprocess
from flask import Flask, render_template, request, url_for, flash, redirect
from flask import send_from_directory
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import validators
from wtforms import FieldList, IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'success'
bootstrap = Bootstrap(app)

redis_setting = 'redis://127.0.0.1/14'
dedup_setting = 'redis://192.168.110.110/0'
process_show_json = "process_show_temp.json"
SETTING_FOLDER = 'static/setting/'
# RUN_PY_FILE = "run_spider.bat"
if os.name == 'nt':
    RUN_PY_FILE = 'D:\workspace\pyWorks\spider\syq_url_rule_manual.py'
else:
    RUN_PY_FILE = '/Users/song/workspace/pyWorks/spider/syq_url_rule_manual.py'


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
    regex = StringField(label=u'表达式')  # , default='/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\d{4}\/?\d{4}/\d{1,}.html')
    score = IntegerField(label=u'匹配数', default=0)


class MyForm(Form):
    start_urls = StringField(label=u'主页')  # cpt.xtu.edu.cn'  # 湘潭大学
    site_domain = StringField(label=u'限定域名')  # 'http://cpt.xtu.edu.cn/'

    list_keyword = StringField(label=u'列表页特征词', default='list;index')
    detail_keyword = StringField(label=u'详情页特征词', default='post;content;detail')

    result = StringField(label=u'转换结果')
    convert = SubmitField(label=u'<< 转换')
    url = StringField(label=u'URL例子')

    regex_list = FieldList(FormField(RegexForm), label=u'详情页正则表达式列表', min_entries=50)

    reset = BooleanField(label=u'将原有正则表达式的score清零', default=False)

    submit = SubmitField(label=u'保存并执行')

    import_setting = SubmitField(label=u'导入')


class MySqlDrive(object):
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'root'
        self.port = 3306
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                    charset="utf8")
        self.conn.select_db('spider')
        self.cur = self.conn.cursor()

    def save_to_mysql(self, start_urls, site_domain, setting_json):
        print 'save_to_mysql() start...', start_urls, site_domain, setting_json

        setting, get_cnt = self.get_setting()
        if get_cnt > 0:
            sqlStr = (
                "UPDATE setting SET setting_json = '" + setting_json + "' WHERE start_urls= '" + start_urls + "' AND site_domain= '" + site_domain + "'")
        else:
            sqlStr = (
                "INSERT INTO setting(start_urls,site_domain,setting_json) VALUES ('" + start_urls + "','" + site_domain + "','" + setting_json + "')")

        ret_cnt = 0
        try:
            ret_cnt = self.cur.execute(sqlStr)
            self.conn.commit()
            print 'save_to_mysql()', ret_cnt, sqlStr
        except Exception, e:
            print 'save_to_mysql()', e
            self.conn.rollback()
        # finally:
        #     self.cur.close()
        #     self.conn.close()
        return ret_cnt

    def get_setting(self):
        # 提取主页、域名
        db = DBDrive(start_urls='',
                     site_domain='',
                     redis_setting=redis_setting)
        start_urls = db.conn.hget(db.setting_hset_key, 'start_urls')
        site_domain = db.conn.hget(db.setting_hset_key, 'site_domain')

        setting_json = ''
        sqlStr = (
            "SELECT setting_json FROM setting WHERE start_urls='" + start_urls + "' AND site_domain ='" + site_domain + "'")
        cnt = 0

        try:
            cnt = self.cur.execute(sqlStr)
            r = self.cur.fetchone()
            setting_json = r[0]
            self.conn.commit()
            print 'get_setting()', cnt, sqlStr
        except Exception, e:
            print 'get_setting()', e
        # finally:
        #     self.cur.close()
        #     self.conn.close()

        return setting_json, cnt


class DBDrive(object):
    def __init__(self, start_urls, site_domain, redis_setting):
        self.site_domain = site_domain
        self.start_urls = start_urls
        self.conn = redis.StrictRedis.from_url(redis_setting)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.list_urls_keyword_zset_key = 'list_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_keyword_zset_key = 'detail_urls_keyword_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.setting_hset_key = 'setting_hset'
        self.process_cnt_hset_key = 'process_cnt_hset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        # print 'DBDrive init()', self.site_domain, self.start_urls, self.conn

    def save_regex(self, regexs):
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
            cnt = 1

        return float(cnt) / len(urls)

    def get_keywords_match(self):
        # keywords = "'" + "','".join(['list', 'index', 'detail', 'post', 'content']) + "'"
        keywords = "'" + "','".join(['list', 'index', 'detail', 'post', 'content']) + "'"
        matched_cnt = ','.join(['99', '2', '10', '30', '1'])
        print keywords,matched_cnt
        return keywords, matched_cnt

    def covert_redis_cnt_to_json(self, process_show_json):
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
        fp = open(SETTING_FOLDER + '/' + process_show_json, 'a')
        fp.write(jsonStr)
        fp.write('\n')
        fp.close()


class CollageProcessInfo(object):
    def __init__(self, process_show_json):
        self.process_show_json = process_show_json

    def convert_file_to_list(self):
        rule0_cnt = []
        rule1_cnt = []
        detail_cnt = []
        list_cnt = []
        list_done_cnt = []
        times = []

        fp = open(SETTING_FOLDER + '/' + self.process_show_json, 'r')
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
        new_path_list.append(convert_regex_format(regex))
    # print new_path
    new_path = '/'.join(new_path_list) + suffix
    return urlparse.urlunparse(('', '', new_path, '', '', ''))


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


def modify_pyfile(py_file, start_urls, site_domain):
    try:
        lines = open(py_file, 'r').readlines()
        # print type(lines)
        i = 0
        for line in lines:
            s = line.strip()
            i += 1
            if s != '' and s[0] == '#':
                continue
            else:
                if i < 100 and re.search(r'self\.start_urls\s*?=', s):
                    lines[i - 1] = line[:line.find('=') + 1] + ' ' + start_urls + '\n'
                    print 'modify_pyfile()', lines[i - 1]

                if i < 100 and re.search(r'self\.site_domain\s*?=', s):
                    lines[i - 1] = line[:line.find('=') + 1] + ' ' + site_domain + '\n'
                    print 'modify_pyfile()', lines[i - 1]

        open(py_file, 'w').writelines(lines)

    except Exception, e:
        print 'modify_pyfile()', e


@app.route('/', methods=['GET', 'POST'])
def menu():
    # 清空主页、域名
    db = DBDrive(start_urls='',
                 site_domain='',
                 redis_setting=redis_setting)
    db.conn.hset(db.setting_hset_key, 'start_urls', '')
    db.conn.hset(db.setting_hset_key, 'site_domain', '')
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
    ret['regex'] = convert_path_to_rule(convert_url)
    jsonStr = json.dumps(ret)
    print 'convert_to_regex()', convert_url, '->', jsonStr
    return jsonStr


@app.route('/show_process', methods=['GET', 'POST'])
def show_process():
    myForm = MyForm()

    # 提取主页、域名
    db = DBDrive(start_urls='',
                 site_domain='',
                 redis_setting=redis_setting)
    start_urls = db.conn.hget(db.setting_hset_key, 'start_urls')
    site_domain = db.conn.hget(db.setting_hset_key, 'site_domain')
    if start_urls is None or start_urls.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show.html', myForm=myForm)

    # 从redis提取实时信息，转换成json文件
    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)
    db.covert_redis_cnt_to_json(process_show_json)

    collage = CollageProcessInfo(process_show_json)
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    matched_rate = db.get_matched_rate() * 100.0
    un_match_rate = 100.0 - matched_rate

    keywords, matched_cnt = db.get_keywords_match()

    # 将json映射到html
    flash(u'每隔10秒刷新 ' + start_urls + u' 的实时采集信息。')
    return render_template('show.html',
                           times=times,
                           rule1_cnt=rule1_cnt,
                           detail_cnt=detail_cnt,
                           list_cnt=list_cnt,
                           list_done_cnt=list_done_cnt,
                           matched_rate=matched_rate,
                           un_match_rate=un_match_rate,
                           keywords=keywords,
                           matched_cnt=matched_cnt)


@app.route('/show_list', methods=['GET', 'POST'])
def get_show_list():
    myForm = MyForm()

    # 提取主页、域名
    db = DBDrive(start_urls='',
                 site_domain='',
                 redis_setting=redis_setting)
    start_urls = db.conn.hget(db.setting_hset_key, 'start_urls')
    site_domain = db.conn.hget(db.setting_hset_key, 'site_domain')
    if start_urls is None or start_urls.strip() == '' or site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、限定的域名信息。')
        return render_template('show.html', myForm=myForm)

    # 从redis提取实时信息，转换成json文件
    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)
    db.covert_redis_cnt_to_json(process_show_json)

    collage = CollageProcessInfo(process_show_json)
    times, rule0_cnt, rule1_cnt, detail_cnt, list_cnt, list_done_cnt = collage.convert_file_to_list()
    times = range(len(times))  # 转换成序列[1,2,3...], high-chart不识别时间

    flash(u'每隔10秒刷新 ' + start_urls + u' 的实时采集信息。')
    return render_template('show-list.html',myForm=myForm)


@app.route('/setting', methods=['GET', 'POST'])
def setting_init():
    myForm = MyForm(request.form)

    db = DBDrive(start_urls='',
                 site_domain='',
                 redis_setting=redis_setting)

    start_urls = db.conn.hget(db.setting_hset_key, 'start_urls')
    site_domain = db.conn.hget(db.setting_hset_key, 'site_domain')
    if start_urls is None or start_urls.strip() == '' or \
                    site_domain is None or site_domain.strip() == '':
        flash(u'请设置主页、域名信息。')
        return render_template('setting.html', myForm=myForm)
    else:
        myForm.start_urls.data = start_urls
        myForm.site_domain.data = site_domain

    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)

    # 保存详情页关键字
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

    # 还原原有的正则表达式
    rules1 = db.conn.zrange(db.detail_urls_rule1_zset_key, start=0, end=999, withscores=True)
    i = 0
    for rule, score in dict(rules1).iteritems():
        regex_data = MultiDict([('select', True), ('regex', rule), ('score', int(score))])
        regexForm = RegexForm(regex_data)
        # myForm.regex_list.append_entry(regexForm)
        myForm.regex_list.entries[i] = regexForm
        i += 1

    # 清除原有所有规则
    # db.conn.zremrangebyscore(db.detail_urls_rule1_zset_key, min=0, max=99999999)

    flash(u'初始化配置完成')
    return render_template('setting.html', myForm=myForm)


@app.route('/save_and_run', methods=['POST'])
def save_and_run():
    myForm = MyForm(request.form)
    # if myForm.validate_on_submit():
    # if request.method == 'POST' and myForm.validate():
    start_urls = myForm.start_urls.data
    site_domain = myForm.site_domain.data
    if start_urls.strip() == '' or site_domain.strip() == '':
        flash(u'必须设置主页、域名信息！')
        return render_template('setting.html', myForm=myForm)

    db = DBDrive(start_urls=start_urls,
                 site_domain=site_domain,
                 redis_setting=redis_setting)

    # 保存主页、域名
    db.conn.hset(db.setting_hset_key, 'start_urls', start_urls)
    db.conn.hset(db.setting_hset_key, 'site_domain', site_domain)

    detail_keys = []
    detail_key = myForm.detail_keyword.data
    for keyword in detail_key.split(';'):
        if keyword != '':
            detail_keys.append(keyword)

    list_keys = []
    list_key = myForm.list_keyword.data
    for keyword in list_key.split(';'):
        if keyword != '':
            list_keys.append(keyword)

    if len(list(set(list_keys) & set(detail_keys))) > 0:
        flash(u"详情页/列表页 特征词有重复，请修改。")
        return render_template('setting.html', myForm=myForm)

    # 清除原有，保存页面填写的详情页关键字
    db.conn.zremrangebyscore(db.detail_urls_keyword_zset_key, min=0, max=99999999)
    for keyword in detail_keys:
        db.conn.zadd(db.detail_urls_keyword_zset_key, 0, keyword)

    # 清除原有，保存页面填写的列表页关键字
    db.conn.zremrangebyscore(db.list_urls_keyword_zset_key, min=0, max=99999999)
    for keyword in list_keys:
        db.conn.zadd(db.list_urls_keyword_zset_key, 0, keyword)

    # 将原有正则表达式的score清零
    if myForm.reset.data:
        regex_reset = db.conn.zrange(db.detail_urls_rule1_zset_key, start=0, end=9999999)
        for regex in regex_reset:
            db.conn.zadd(db.detail_urls_rule1_zset_key, 0, regex)

    # 只启动一次 run_spider.bat
    # if os.path.exists(process_show_json) is False:
    #     subprocess.call(["run_spider.bat"], shell=True)
    # else:
    #     print 'no submit................'
    # 保存rule1
    regex_list = myForm.regex_list.data
    regex_save_list = []
    regex_cnt = 0
    for r in regex_list:
        select = r['select']
        regex = r['regex']
        score = r['score']
        if select and regex != '':
            regex_cnt += 1
            regex_save_list.append(regex)

    if regex_cnt == 0:
        flash(u"请填写并勾选要执行的 详情页正则表达式。")
        return render_template('setting.html', myForm=myForm)

    regex_save_list = list(set(regex_save_list))
    db.save_regex(regex_save_list)

    modify_pyfile(py_file=RUN_PY_FILE, start_urls="\'" + start_urls + "\'", site_domain="\'" + site_domain + "\'")

    # DOS "start" command
    if os.name == 'nt':
        os.startfile(RUN_PY_FILE)
    else:
        os.popen("python " + RUN_PY_FILE)
        # print p.read()

    export_file = {'start_urls': start_urls,
                   'site_domain': site_domain,
                   'regex_save_list': regex_save_list,
                   'detail_keys': detail_keys,
                   'list_keys': list_keys
                   }
    json_str = json.dumps(export_file)

    mysql = MySqlDrive()
    cnt = mysql.save_to_mysql(start_urls, site_domain, json_str)

    if cnt == 1:
        flash(u"MySQL保存完毕，执行中...")
    else:
        flash(u"MySQL保存失败，执行中...")

    open(SETTING_FOLDER + 'setting.json', 'w').write(json_str)
    return render_template('setting.html', myForm=myForm)


@app.route('/setting/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['SETTING_FOLDER'], filename, as_attachment=True)


@app.route('/export_upload', methods=['GET', 'POST'])
def export_upload():
    if request.method == 'GET':
        return render_template('export_import.html')

    elif request.method == 'POST':
        f = request.files['file']
        # 获取一个安全的文件名，仅支持ascii字符。
        f_name = secure_filename(f.filename)
        f.save(os.path.join(SETTING_FOLDER, f_name))
        flash(u"上传成功.")
        return render_template('export_import.html')


@app.route('/export_setting', methods=['GET', 'POST'])
def export_setting():
    mysql_db = MySqlDrive()
    setting_json, cnt = mysql_db.get_setting()
    flash(u"MySQL导出结果。")
    return render_template('export_import.html', setting_json=setting_json)


@app.route('/export_import')
def export_import():
    flash(u"请选择导入/导出操作。")
    return redirect(url_for('export_upload'), 302)


if __name__ == '__main__':
    app.run(debug=True)

    # -------------------unit test-----------------------------------
    # mysql = MySqlDrive()
    # print mysql.save_to_mysql('http://bbs.tianya.com','bbs.tianya.con','aaaaaaaaaaaaaaa')
    # print mysql.get_setting()
