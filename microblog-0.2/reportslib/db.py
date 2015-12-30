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
            sqlstr = ("select "
            "usr.login_name,count(distinct a.bug_id) as reopen,count(distinct b.bug_id) as resolve,count(distinct c.bug_id) as verify,count(distinct d.bug_id) as close "
            "from "
            "  (select * from profiles where `show`='1') as usr "
            "left join "
            "  (select * from bugs_activity where fieldid='9' and removed='RESOLVED' and added='REOPENED' and TO_DAYS(bug_when)=TO_DAYS('"+ day +"')) as a "
            "on usr.userid=a.who "
            "left join "
            "  (select * from bugs_activity where fieldid='9' and removed='NEW' and added='RESOLVED' and TO_DAYS(bug_when)=TO_DAYS('"+ day +"')) as b "
            "on usr.userid=b.who "
            "left join "
            "  (select * from bugs_activity where fieldid='9' and removed='RESOLVED' and added='VERIFIED' and TO_DAYS(bug_when)=TO_DAYS('"+ day +"')) as c "
            "on usr.userid=c.who "
            "left join "
            "  (select * from bugs_activity where fieldid='9' and removed='VERIFIED' and added='CLOSED' and TO_DAYS(bug_when)=TO_DAYS('"+ day +"')) as d "
            "on usr.userid=d.who "
            "group by usr.userid")
            #print self.sqlstr
            count = cur.execute(sqlstr)
            #print 'total member is: %s' % count
            rs = cur.fetchall()
            for r in rs:
                #print r
                people = {}
                people['name'] = r[0]
                status = {}
                status['reopen'] = r[1]
                status['resolve'] = r[2]
                status['verify'] =  r[3]
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
        jsonStr = json.dumps(reports) # object to json encode
        fp = open("db-daysTotalByMember.json",'w+')
        fp.write(jsonStr)
        fp.close()
        return jsonStr

    def statusChangeById(self,bugIds):
        bugs = []
        for bugId in bugIds:
            bug={}
            change = []
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port)
            cur = conn.cursor()
            conn.select_db('bugs')
            sqlStr = ("select "
            " LEFT(usr.login_name,LENGTH(usr.login_name)-8),bugs.bug_when,cast(removed as char) as old,cast(added as char) as new "
            "from "
            " (select * from bugs_activity where fieldid='9' and bug_id='"+ bugId + "')  as bugs "
            "left join "
            " profiles as usr "
            "on "
            " usr.userid=bugs.who "
            "order by bugs.bug_when")
            #print sqlStr
            count = cur.execute(sqlStr)
            # print 'total member is: %s' % count
            rs = cur.fetchall()
            for r in rs:
                #print r
                rec = {}
                rec['member'] = r[0]
                rec['time'] = r[1].strftime('%Y-%m-%d')
                rec['changeTo'] = r[2] + u'→' + r[3]
                change.append(rec)
            conn.commit()
            cur.close()
            conn.close()
            bug['id']=bugId
            bug['change']=change
            bugs.append(bug)
        # dump json to file
        jsonStr = json.dumps(bugs) # object to json encode
        fp = open("db-statusChangeById.json",'w+')
        fp.write(jsonStr)
        fp.close()
        return jsonStr

    def getComment(self,bugId,when):
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port)
        cur = conn.cursor()
        conn.select_db('bugs')
        sqlStr = ("select thetext from longdescs where bug_id='"+ bugId +"' and bug_when ='"+ when +"'")
        print sqlStr
        count = cur.execute(sqlStr)
        r = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        # dump json to file
        jsonStr = json.dumps(r[0]) # object to json encode
        fp = open("db-getComment.json",'w+')
        fp.write(jsonStr)
        fp.close()
        #return jsonStr
        return json.dumps()

if __name__ == '__main__':
    r = dbRead()
    #print r.daysTotalByMember('2015-11-12')
    #print r.statusChangeById(['34','35'])
    print r.getComment('34','2015-10-10 15:48:57')