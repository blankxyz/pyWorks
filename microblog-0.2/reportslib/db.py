# -*- coding: UTF-8 -*-
import MySQLdb
import json

# read DB to json
class dbRead:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '314159'
        self.port = 3306

    def daysTotalByMember(self, days):
        reports = []
        for day in days:
            report = {}
            team = []
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port)
            cur = conn.cursor()
            conn.select_db('bugs')
            sqlstr = ("SELECT "
                      "usr.login_name,count(DISTINCT a.bug_id) AS reopen,count(DISTINCT b.bug_id) AS resolve,count(DISTINCT c.bug_id) AS verify,count(DISTINCT d.bug_id) AS close "
                      "from "
                      "  (SELECT * FROM PROFILES WHERE `show`='1') AS usr "
                      "left JOIN "
                      "  (SELECT * FROM bugs_activity WHERE fieldid='9' AND removed='RESOLVED' AND added='REOPENED' AND TO_DAYS(bug_when)=TO_DAYS('" + day + "')) AS a "
                                                                                                                                                             "on usr.userid=a.who "
                                                                                                                                                             "left JOIN "
                                                                                                                                                             "  (SELECT * FROM bugs_activity WHERE fieldid='9' AND removed='NEW' AND added='RESOLVED' AND TO_DAYS(bug_when)=TO_DAYS('" + day + "')) AS b "
                                                                                                                                                                                                                                                                                               "on usr.userid=b.who "
                                                                                                                                                                                                                                                                                               "left JOIN "
                                                                                                                                                                                                                                                                                               "  (SELECT * FROM bugs_activity WHERE fieldid='9' AND removed='RESOLVED' AND added='VERIFIED' AND TO_DAYS(bug_when)=TO_DAYS('" + day + "')) AS c "
                                                                                                                                                                                                                                                                                                                                                                                                                                      "on usr.userid=c.who "
                                                                                                                                                                                                                                                                                                                                                                                                                                      "left JOIN "
                                                                                                                                                                                                                                                                                                                                                                                                                                      "  (SELECT * FROM bugs_activity WHERE fieldid='9' AND removed='VERIFIED' AND added='CLOSED' AND TO_DAYS(bug_when)=TO_DAYS('" + day + "')) AS d "
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           "ON usr.userid=d.who "
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           "GROUP BY usr.userid")
            # print self.sqlstr
            count = cur.execute(sqlstr)
            # print 'total member is: %s' % count
            rs = cur.fetchall()
            for r in rs:
                #print r
                people = {}
                people['name'] = r[0]
                status = {}
                status['reopen'] = r[1]
                status['resolve'] = r[2]
                status['verify'] = r[3]
                status['close'] = r[4]
                people['status'] = status
                team.append(people)
            conn.commit()
            cur.close()
            conn.close()
            report['day'] = day
            report['team'] = team
            reports.append(report)
        # dump json to file
        # {"day": "2015-12-03", "team": [{"status": {"close": 0, "reopen": 0, "resolve": 2, "verify": 0}, "name": "mac@ehr.com"},{},{}]},...
        jsonStr = json.dumps(reports)  # object to json encode
        fp = open("db-daysTotalByMember.json", 'w+')
        fp.write(jsonStr)
        fp.close()
        return jsonStr

    def statusChangeById(self, bugIds):
        bugs = []
        for bugId in bugIds:
            bug = {}
            change = []
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port)
            cur = conn.cursor()
            conn.select_db('bugs')
            sqlStr = ("SELECT "
                      " LEFT(usr.login_name,LENGTH(usr.login_name)-8),bugs.bug_when,cast(removed AS CHAR) AS old,cast(added AS CHAR) AS new "
                      "from "
                      " (SELECT * FROM bugs_activity WHERE fieldid='9' AND bug_id='" + bugId + "')  AS bugs "
                                                                                               "LEFT JOIN "
                                                                                               " PROFILES AS usr "
                                                                                               "ON "
                                                                                               " usr.userid=bugs.who "
                                                                                               "ORDER BY bugs.bug_when")
            # print sqlStr
            count = cur.execute(sqlStr)
            # print 'total member is: %s' % count
            rs = cur.fetchall()
            for r in rs:
                # print r
                rec = {}
                rec['member'] = r[0]
                rec['time'] = r[1].strftime('%Y-%m-%d')
                rec['changeTo'] = r[2] + u'→' + r[3]
                change.append(rec)
            conn.commit()
            cur.close()
            conn.close()
            bug['id'] = bugId
            bug['change'] = change
            bugs.append(bug)
        # dump json to file
        jsonStr = json.dumps(bugs)  # object to json encode
        fp = open("db-statusChangeById.json", 'w+')
        fp.write(jsonStr)
        fp.close()
        return jsonStr

    def getComment(self, bugId, when):
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port)
        cur = conn.cursor()
        conn.select_db('bugs')
        sqlStr = ("SELECT thetext FROM longdescs WHERE bug_id='" + bugId + "' AND bug_when ='" + when + "'")
        print sqlStr
        count = cur.execute(sqlStr)
        r = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        # dump json to file
        jsonStr = json.dumps(r[0])  # object to json encode
        fp = open("db-getComment.json", 'w+')
        fp.write(jsonStr)
        fp.close()
        # return jsonStr
        return json.dumps()


if __name__ == '__main__':
    r = dbRead()
    # print r.daysTotalByMember('2015-11-12')
    # print r.statusChangeById(['34','35'])
    print r.getComment('34', '2015-10-10 15:48:57')