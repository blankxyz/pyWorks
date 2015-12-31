import json
from flask import render_template
from flask import jsonify
from flask import request
from app import app
from reportslib.db import dbRead

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

@app.route('/add')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/')
@app.route('/getComment')
def getComment():
    bugId = request.args.get('bugId')
    when = request.args.get('when')
    db = dbRead()
    result = db.getComment(bugId, when)
    print bugId
    print when
    print result
    #return jsonify(result)
    return render_template('ajaxTest.html',bugId=bugId,when=when)