#!/usr/bin/python
# coding=utf-8
import os
import MySQLdb
import Image

from pprint import pprint
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import FieldList, IntegerField, StringField, DateTimeField, FormField, TextField, TextAreaField, \
    SubmitField
from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess string'

EXPORT_FOLDER = 'static/'


class Util(object):
    @staticmethod
    def convet_img(img_file):
        im = Image.open(img_file)
        (width, hight) = im.size
        if width > 1024:
            h = hight * 1024 / width
            new_img = im.resize((1024, h))
            new_img.save(img_file)
            # new_img.show()


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

    def articleList(self, start):
        result = []
        sql_str = "SELECT id,title,content,image,create_at FROM article limit " + str(start) + ",10"
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
        sql_str = "INSERT INTO article(id,title,content,image,create_at) VALUES(" + str(id) + ", '" + str(
            title) + "', '" + \
                  str(content) + "', '/static/" + str(image) + "', '2017-01-16 21:10:13')"
        try:
            cnt = self.cur.execute(sql_str)
            print '[info] add_article()', cnt, sql_str
            self.conn.commit()

        except Exception, e:
            traceback.format_exc()
            print '[error] add_article()', e, sql_str
            self.conn.rollback()

    def update_article(self, id, userName, title, content, image):
        sql_str = "UPDATE article SET title='" + title + "',content='" + content + "',image='" + image + " WHERE id=" + id
        print '[info] update_article()', sql_str
        try:
            cnt = self.cur.execute(sql_str)
            print '[info] update_article()', cnt
            self.conn.commit()

        except Exception, e:
            traceback.format_exc()
            print '[error] update_article()', e
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
    upload_image = StringField()
    submit = SubmitField(label=u'Submit')


class CommentForm(Form):
    id = IntegerField(label=u'id', default=0)
    name = StringField(label=u'name', default=u'name')
    comment = StringField(label=u'comment', default=u'comment')
    create_at = DateTimeField(label=u'create_at')
    article_id = IntegerField(label=u'article_id')
    submit = SubmitField(label=u'Submit')


@app.route('/')
@app.route('/<int:page>')
def articleList(page=0):
    form = PostArticleForm()
    db = DBDrive()
    if page:
        start = page * 10
    else:
        start = 0

    print 'start', start
    ret = db.articleList(start)
    return render_template('article.html', articleList=ret, form=form)


@app.route('/article/post')
def postArticle():
    if request.method == 'GET':
        return render_template('postArticle.html')

    if request.method == 'POST':
        db = DBDrive()
        maxId = db.get_article_maxId()
        id = maxId +1

        userName = request.form['userName']
        title = request.form['title']
        content = request.form['content']

        f = request.files['upload_file']
        f_name = secure_filename(f.filename)
        up_img_file = os.path.join(EXPORT_FOLDER, f_name)
        f.save(up_img_file)
        Util.convet_img(up_img_file)

        print '[info] postArticle() post:', id, userName, title, content, f_name

        ret = db.add_article(id, userName, title, content, f_name)

        # return redirect(url_for('/article/2'), 302)
        return 'add ok!'

@app.route('/article/post/<id>', methods=['GET','POST'])
def editArticle(id):
    if request.method == 'GET':
        return render_template('editArticle.html')

    if request.method == 'POST':
        print '[info] editArticle() POST start.'
        db = DBDrive()
        userName = request.form['userName']
        title = request.form['title']
        content = request.form['content']
        print '[info] editArticle() post:', id, userName, title, content

        f = request.files['upload_file']
        f_name = secure_filename(f.filename)
        up_img_file = os.path.join(EXPORT_FOLDER, f_name)
        f.save(up_img_file)
        Util.convet_img(up_img_file)

        # print '[info] editArticle() post:', f_name

        print '[info] editArticle()', id, userName, title, content, f_name

        ret = db.update_article(id, userName, title, content, f_name)

        # return redirect(url_for('/article/2'), 302)
        return 'update ok!'


@app.route('/article/<id>')
def articleDetail(id):
    db = DBDrive()
    article, detail = db.article_detail(id)

    return render_template('articleDetail.html', article=article, detail=detail)


if __name__ == '__main__':
    app.run()
