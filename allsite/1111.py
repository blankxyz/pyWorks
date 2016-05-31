# coding=utf-8
import re
import urlparse
import redis
import myreadability


class MySpider():

    def __init__(self):
        # 网站名称
        self.siteName = "k618"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        # self.start_urls = 'http://www.k618.cn/'
        self.start_urls = 'http://news.k618.cn/dj/'
        self.encoding = 'gbk'
        self.site_domain = 'k618.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/7')
        self.ok_urls_zset_key = 'ok_urls_zset_%s' % self.site_domain
        self.todo_urls_zset_key = 'todo_urls_zset_%s' % self.site_domain
        self.error_urls_zset_key = 'error_urls_zset_%s' % self.site_domain
        self.detail_urls_zset_key = 'detail_urls_zset_%s' % self.site_domain
        self.detail_urls_rule0_zset_key = 'detail_rule0_urls_zset_%s' % self.site_domain
        self.detail_urls_rule1_zset_key = 'detail_rule1_urls_zset_%s' % self.site_domain
        self.todo_urls_limits = 10
        self.todo_flg = -1
        self.done_flg = 0
        self.max_level = 7  # 最大级别
        self.detail_level = 99

    def is_list_by_url_name(url):  # syq
        # print 'is_list_by_url_name start:', url
        ret = False
        path = urlparse.urlparse(url).path
        if len(path) != 0:
            if path == u'/':
                ret = True
            if path[-1] == u'/':
                ret = True
        else:
            ret = True
        # print 'is_list_by_url_name end'
        return ret

    def convert_detail_to_regex(url):
        path = urlparse.urlparse(url).path
        pos1 = path.rindex('/')
        pos2 = path.find('.')
        if pos2 == -1:
            pos2 = len(path)
        tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
        tag = re.sub(r'\d', '\d', tag)
        return path[:pos1 + 1] + tag + path[pos2:]

    def convert_path1_to_regex(path):
        if path.count('/') >= 2:
            pos2 = path.rindex('/')
            pos1 = path[:pos2 - 1].rindex('/')
            tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
            tag = re.sub(r'\d', '\d', tag)
            return path[:pos1 + 1] + tag + path[pos2:]
        else:
            return None

    def convert_path_to_regex(self, path):
        '''
        /news/201404/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm
        '''
        # print 'convert_path_to_regex() start:', path
        if path.count('/') >= 2:
            pos2 = path.rindex('/')
            pos1 = path[:pos2 - 1].rindex('/')
            tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
            tag = re.sub(r'\d', '\d', tag)
            # print 'convert_path_to_regex() end:', path[:pos1 + 1] + tag +
            # path[pos2:]
            return path[:pos1 + 1] + tag + path[pos2:]
        else:
            return None

    def convert_regex_cnt(self, rule):
        '''
        /news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm ->
        /news/\d{6}/[a-zA-Z]\d{8}_\d{6}.htm
        '''
        str = rule
        ret = ''
        digit = '\d'
        double_digit = '\d\d'
        word = '[a-zA-Z]'
        double_word = '[a-zA-Z][a-zA-Z]'
        cnt = 0
        pos = 0
        while len(str) > 0:
            if str.find(digit) < str.find(word):
                pos = str.find(digit)
                if pos > 0:
                    ret = ret + digit
                    cnt = cnt + 1
                    str = str[pos + len(digit):]
                else:
                    cnt = 0
                    if cnt > 0:
                        ret = ret + '{' + cnt + '}'
            else:
                pos = str.find(word)
                if pos > 0:
                    ret = ret + word
                    cnt = cnt + 1
                    str = str[pos + len(word):]
                else:
                    cnt = 0
                    if cnt > 0:
                        ret = ret + '{' + cnt + '}'

    def is_list_by_link_density(self, url):
        # print 'is_list_by_link_density start'
        response = self.download(url)
        doc = myreadability.Document(response.content, encoding=self.encoding)
        ret = doc.is_list()  # 链接密度
        # if ret:
        #     print 'is_list_by_link_density[list]',url
        # else:
        #     print 'is_list_by_link_density[detail]',url
        # print 'is_list_by_link_density end'
        return ret

    def extract_detail_rule_1(self):
        # rule1 是由 超过rule0中前10% 积累后转换，需要确定匹配
        print 'extract_detail_rule_1() start'
        rules_0_cnt = self.conn.zcard(self.detail_urls_rule0_zset_key)
        if rules_0_cnt > 100:  # 100 rule0(score>20) -> rule1
            rules_0 = self.conn.zrevrangebyscore(self.detail_urls_rule0_zset_key,
                                                 max=999999, min=20, start=0, num=rules_0_cnt / 10, withscores=True)
            for rule_0, score in dict(rules_0).iteritems():
                print 'rule_0, score:', rule_0, score
                rule_1 = self.convert_path_to_regex(rule_0)
                print 'rule_1', rule_1
                if rule_1:
                    self.conn.zincrby(
                        self.detail_urls_rule1_zset_key, value=rule_1, amount=score)
        print 'extract_detail_rule_1() end'
        return

if __name__ == '__main__':
    mySpider = MySpider()
    path = '/news/201404/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm'
    # print urlparse.urlparse(url).netloc
    # print urlparse.urlparse(url).path
    # # print is_list_by_url_name(url)
    # print mySpider.extract_detail_rule_1()
    # print
    # mySpider.is_list_by_link_density('http://bj.esf.sina.com.cn/detail/203494453')
    print mySpider.convert_regex_cnt('/news/\d\d\d\d\d\d/[a-zA-Z]\d\d\d\d\d\d\d\d_\d\d\d\d\d\d\d.htm')
    # site_domain = 'k618.cn'
    # detail_urls_rule_zset_key = 'detail_rule_urls_zset_%s' % site_domain
    # detail_pages = redis.StrictRedis.from_url('redis://127.0.0.1/8').zcard(detail_urls_rule_zset_key)
    # print detail_pages
    # num = detail_pages/10
    # rules = redis.StrictRedis.from_url('redis://127.0.0.1/8').zrevrangebyscore(detail_urls_rule_zset_key,
    #                             max=detail_pages, min=10, start=0, num=1, withscores=True)
    # print len(rules)
    # for i in rules: print i
    # for regex, score in dict(rules).iteritems():
    #     print regex, score
    #
    # url = 'http://baby.k618.cn/qttj/201409/t20140930_5672327.htm'
    # if re.search(regex, url):
    #     print 'ok'
