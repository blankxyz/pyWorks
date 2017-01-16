#!/usr/bin/python
# coding=utf-8
import os
import MySQLdb
from pprint import pprint
from flask import Flask
from flask_bootstrap import Bootstrap
# from flask_wtf import Form
from flask_wtf import Form
from wtforms import validators
from wtforms import FieldList, IntegerField, StringField, RadioField, DecimalField, DateTimeField, \
    FormField, SelectField, TextField, PasswordField, TextAreaField, BooleanField, SubmitField
from flask import Flask, render_template, request, session, url_for, flash, redirect, g
from werkzeug.utils import secure_filename

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess string'

EXPORT_FOLDER = 'static/export/'


class DBDrive(object):
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'root'
        self.port = 3306
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                    charset='utf8')
        self.conn.select_db('facePlus')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def articleList(self):
        result = []
        sql_str = "SELECT id,title,content,image,create_at FROM article"
        try:
            cnt = self.cur.execute(sql_str)
            rs = self.cur.fetchall()
            for r in rs:
                result.append({'id': r[0], 'title': r[1], 'content': r[2], 'image': r[3], 'create_at': r[4]})
            self.conn.commit()
            print '[info]search_article()', cnt, sql_str
        except Exception, e:
            print '[error]search_article()', e, sql_str

        # pprint(result)
        return result

    def article_detail(self, id):
        article = []
        sql_str1 = "SELECT id,title,content,image,create_at FROM article WHERE id=" + id + ""
        try:
            cnt = self.cur.execute(sql_str1)
            rs = self.cur.fetchall()
            for r in rs:
                article.append({'id': r[0], 'title': r[1], 'content': r[2], 'image': r[3], 'create_at': r[4]})
            self.conn.commit()
            print '[info] article: ', cnt, sql_str1
        except Exception, e:
            print '[error] article: ', e, sql_str1

        # pprint(article)

        detail = []
        sql_str2 = "SELECT id,user_name,comment,create_at,article_id FROM comment WHERE article_id=" + id + ""
        try:
            cnt = self.cur.execute(sql_str2)
            rs = self.cur.fetchall()
            for r in rs:
                detail.append({'id': r[0], 'user_name': r[1], 'comment': r[2], 'create_at': r[3], 'article_id': r[4]})
            self.conn.commit()
            print '[info] detail: ', cnt, sql_str2
        except Exception, e:
            print '[error] detail: ', e, sql_str2

        # pprint(detail)

        return article[0], detail

    def add_article(self, id, userName, title, content, image):
        sql_str = "INSERT INTO article(id,title,content,image,create_at) VALUES(%d,%s,%s,%s,%s)"
        parameter = (id, title, content, image, '2017-01-16 21:10:13',)

        try:
            cnt = self.cur.execute(sql_str, parameter)
            print '[info] add_article()', cnt, sql_str
            self.conn.commit()
        except Exception, e:
            # traceback.format_exc()
            print '[error]add_article()', e
            self.conn.rollback()

    def get_article_maxId(self):
        ret = -1
        sql_str = "select (Max(id)+1) from article"

        try:
            cnt = self.cur.execute(sql_str)
            rs = self.cur.fetchone()
            self.conn.commit()
            print '[info] get_article_maxId: ', rs[0], sql_str
            return int(rs[0])
        except Exception, e:
            print '[error] get_article_maxId: ', e, sql_str
            return -1


class ArticleForm(Form):
    id = IntegerField(label=u'id', default=0)
    title = StringField(label=u'title')
    content = StringField(label=u'content')
    image = StringField()
    create_at = DateTimeField(label=u'create_at')
    submit = SubmitField(label=u'Submit')


class ArticleListForm(Form):
    articleList = FieldList(FormField(ArticleForm), min_entries=5)


class PostArticleForm(Form):
    id = IntegerField(label=u'id')
    userName = StringField(label=u'userName')
    title = StringField(label=u'title')
    content = TextAreaField(label=u'content')
    image = StringField()
    submit = SubmitField(label=u'Submit')


class CommentForm(Form):
    id = IntegerField(label=u'id', default=0)
    name = StringField(label=u'name', default=u'name')
    comment = StringField(label=u'comment', default=u'comment')
    create_at = DateTimeField(label=u'create_at')
    article_id = IntegerField(label=u'article_id')
    submit = SubmitField(label=u'Submit')


@app.route('/')
def articleList():
    form = PostArticleForm()
    db = DBDrive()
    ret = db.articleList()
    return render_template('article.html', articleList=ret, form=form)


@app.route('/postArticle', methods=['GET', 'POST'])
def postArticle():
    if request.method == 'GET':
        print '[info] postArticle() get start.'
        form = PostArticleForm()
        print '[info] postArticle() get end.'
        return render_template('postArticle.html', form=form)

    if request.method == 'POST':
        print '[info] postArticle() post start.'
        db = DBDrive()
        id = db.get_article_maxId()
        userName = request.args.get('userName')
        title = request.args.get('title')
        content = request.args.get('content')
        image = request.args.get('image')

        f = request.files['file']
        # 获取一个安全的文件名，仅支持ascii字符。
        f_name = secure_filename(f.filename)
        f.save(os.path.join(EXPORT_FOLDER + id + '/', f_name))

        print '[info] postArticle()', id, userName, title, content, image
        ret = db.add_article(int(id) + 1, userName, title, content, image)

        print '[info] postArticle() post end.', ret
        return redirect(url_for('/'), 302)


@app.route('/article/<id>')
def articleDetail(id):
    db = DBDrive()
    article, detail = db.article_detail(id)

    return render_template('articleDetail.html', article=article, detail=detail)


if __name__ == '__main__':
    app.run()
