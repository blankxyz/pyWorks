# -*- coding: UTF-8 -*-
import MySQLdb
import json


class ShowDB:
    def __init__(self,flg):
        self.__offline = None
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.host = 'localhost'
        self.user = 'root'
        self.password = 'root'
        self.port = 3306
        self.offline == flg
        self.path = "jsonData/"

    def process(self, interval):
        if self.offline == False :
            show_data = []
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port, charset="utf8")
            cur = conn.cursor()
            conn.select_db('allsite')
            count = cur.execute("SELECT * FROM process")
            rs = cur.fetchall()
            for r in rs:
                #print r
                process = {}
                process['time'] = r[0]
                process['rule0'] = r[1]
                process['rule1'] = r[2]
                process['detail'] = r[3]
                process['list'] = r[4]
                process['list_done'] = r[5]
                show_data.append(process)
            conn.commit()
            cur.close()
            conn.close()
            # dump json to file
            jsonStr = json.dumps(show_data)  # object to json encode
            fp = open(self.path + "db-process.json", 'w')
            fp.write(jsonStr)
            fp.close()
        else:
            fp = open(self.path + "db-process.json", 'r')
            jsonStr = fp.read()
            fp.close()
            #print  jsonStr
        return jsonStr


if __name__ == '__main__':
    myShow = ShowDB(True)
    myShow.path = "jsonData/"
    print myShow.process(10)
    #r.statusChangeById(['35'])
    #print r.getComment('34', '2015-10-10 15:48:57')
