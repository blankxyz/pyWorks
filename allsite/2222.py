from threading import Timer
import time
import redis
import MySQLdb
import json

class SetDB():
    def __init__(self):
        self.site_domain = 'k618.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/5')
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.collage_zset_key = 'coolage_zset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0

    def collageCount(self):
        rule0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        rule1_cnt = self.conn.zcard(self.detail_urls_rule1_zset_key)
        detail_cnt = self.conn.zcard(self.detail_urls_zset_key)
        list_urls = self.conn.zcard(self.list_urls_zset_key)
        list_done_urls = self.conn.zrangebyscore(self.list_urls_zset_key, self.done_flg, self.done_flg)
        list_done_cnt = len(list_done_urls)
        self.conn.zadd()


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
            count = cur.execute("select * from process")
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
    show = ShowDB()
    timer_interval = 1

    t = Timer(timer_interval, show.collageCount())
    t.start()

    while True:
        time.sleep(60)
        print 'sleeping'
