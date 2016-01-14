import json
from flask import Flask, jsonify, render_template, request
from app import app
from reportslib.db import dbRead

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/statusChange')
def index():
    bugs = ['34', '35', '36', '37', '38', '39', '40', '41', '42']
    title = 'status change by bugId'
    db = dbRead()
    ret = db.statusChangeById(bugs)
    return render_template('statusChange.html', title=title, bugs=bugs, changes=json.loads(ret))

@app.route('/dayReport')
def dayReport():
    days = {'2015-11-12'}
    title = 'Daily Reports by Developer'
    db = dbRead()
    reports = db.daysTotalByMember(days)
    return render_template("dayReport.html", title=title, reportDays=days, reports=json.loads(reports))

@app.route('/add',methods=["GET", "POST"])
def add_numbers():
    print "add_numbers()"
    bugId = request.args.get('a')
    when = request.args.get('b')
    db = dbRead()
    # '34','2015-10-10 15:48:57'
    result = db.getComment(bugId, when)
    print result
    return result

@app.route('/ajax')
def getComment():
    return render_template('ajaxTest.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',err=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',err=e), 500