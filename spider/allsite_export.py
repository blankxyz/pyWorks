#!/usr/bin/python
# coding=utf-8
import redis
import ConfigParser

####################################################################
INIT_CONFIG = './run_allsite.ini'
####################################################################
config = ConfigParser.ConfigParser()
if len(config.read(INIT_CONFIG)) == 0:
    print '[ERROR]cannot read the config file.', INIT_CONFIG
    exit(-1)
else:
    print '[INFO] read the config file.', INIT_CONFIG

# redis
REDIS_SERVER = config.get('redis', 'redis_server')
DEDUP_SETTING = config.get('redis', 'dedup_server')

# spider
START_URLS = config.get('spider', 'start_urls')
SITE_DOMAIN = config.get('spider', 'site_domain')
BLACK_DOMAIN_LIST = config.get('spider', 'black_domain_list')
DETAIL_RULE_LIST = config.get('spider', 'detail_rule_list')
LIST_RULE_LIST = config.get('spider', 'list_rule_list')

#############################################################################

class RedisDrive(object):
    def __init__(self, start_url, site_domain):
        self.site_domain = site_domain
        self.start_url = start_url
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.list_urls_zset_key = 'list_urls_zset_%s' % self.site_domain  # 计算结果
        self.todo_flg = -1
        self.done_flg = 0

    def export_list(self):
        fp = open('result-list.log', 'w')
        for line in  self.conn.zrange(self.list_urls_zset_key, self.done_flg, self.todo_flg, withscores=False):
            fp.write(line + '\n')
        fp.close()


if __name__ == '__main__':
    redis_db = RedisDrive(START_URLS,SITE_DOMAIN)
    redis_db.export_list()