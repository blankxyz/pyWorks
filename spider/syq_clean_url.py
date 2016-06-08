# coding:utf-8
'''
url及文本判断过滤
'''
import re
import cgi
import json
import urllib
import datetime
import urlparse
import requests

import redis


class myexc(Exception):
    def __init__(self, error_info):
        super(Exception, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return 'use defined exceptions %s' % self.error_info


class Cleaner(object):
    def __init__(self, site_domain, conn=None):
        self.site_domain = site_domain
        self.conn = conn
        if self.conn is None:
            self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/8')
        # 域名正则黑名单
        self.black_domain_regex = (
            'bbs\.',  # syq
        )
        self.now_year = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y'), '%Y')
        self.hash_black_path_regex_key = 'hash_black_path_regex'
        self.black_path_regex = self.get_black_path_regex()

    def get_black_path_regex(self):
        '''路径正则黑名单
        @ 匹配到的路径应为 非列表页url
        '''
        default_regex = (
            re.compile('/'),
            re.compile('^$'),
        )
        regex_list_str = self.conn.hget(self.hash_black_path_regex_key, self.site_domain)
        if regex_list_str is not None:
            regex_list = json.loads(regex_list_str)
        else:
            regex_list = []
        compile_list = []
        for regex_str in regex_list:
            compile_list.append(re.compile(regex_str))
        return tuple(compile_list) + default_regex

    def in_black_list(self, url):
        '''域名黑名单'''
        for regex in self.black_domain_regex:
            if re.match(regex, urlparse.urlparse(url).netloc):
                return True
        return False

    def filter_urls(self, url_list):
        if not isinstance(url_list, (list, tuple)):
            url_list = [url_list]
        # 错误url识别
        # print 'is_error_url',len(url_list)
        url_list = filter(lambda x: not self.is_error_url(x), url_list)
        # print 'url_clean',len(url_list)
        # 清洗
        url_list = self.url_clean(url_list)
        # print 'dedup',len(url_list)
        # 去重
        url_list = list(set(url_list))
        # print 'check_cross_domain',len(url_list)
        # 跨域检查
        url_list = filter(lambda x: self.check_cross_domain(x), url_list)
        # print 'is_detail_by_regex',len(url_list)
        # 过滤详情页
        url_list = filter(lambda x: not self.is_detail_by_regex(x), url_list)
        # print 'in_black_list',len(url_list)
        # 黑名单过滤
        url_list = filter(lambda x: not self.in_black_list(x), url_list)
        # print 'is_old_url',len(url_list)
        # 链接时间过滤
        url_list = filter(lambda x: not self.is_old_url(x), url_list)
        # print 'is_next_page',len(url_list)
        # 非第一页链接过滤
        url_list = filter(lambda x: not self.is_next_page(x), url_list)
        return url_list

    def is_download(self, url):  # syq
        p = urlparse.urlparse(url).netloc
        for fix in ['.apk', '.doc*', '.xls*', '.csv', '.avi', '.rmvb']:
            if p.find(fix) > 0:
                return True
        return False

    def check_cross_domain(self, url):
        '''跨域检查'''
        if self.site_domain in urlparse.urlparse(url).netloc:
            return True
        return False

    def is_detail_by_regex(self, url):
        '''根据正则检测url类别'''
        is_detail = False
        for compile_regex_str in self.black_path_regex:
            try:
                if compile_regex_str.match(urlparse.urlparse(url).path):
                    is_detail = True
                    break
            except Exception as e:
                print e
                continue
        return is_detail

    def url_sort(self, url):
        '''url参数排序'''
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        keyvals = cgi.parse_qsl(query, keep_blank_values=1)
        keyvals.sort()
        query = urllib.urlencode(keyvals)
        return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

    def url_clean(self, urls):
        '''清洗无效参数并排序'''
        new_urls = []
        for url in urls:
            # 清理锚 # 之后的
            url = url.split('#')[0]
            url = url.split('?')[0]  # syq
            # 汉字参数转义
            url = urllib.unquote(url)
            # 参数排序
            url = self.url_sort(url)
            # 去'/'
            # url = url.strip('/')
            #
            new_urls.append(url)
        return new_urls

    def is_next_page(self, url):
        '''是否为非第一页链接'''
        next_page_num_regex = (
            'index_(\d+)\.s?html?',  # syq
            '(?:page|p)=(\d+)',
            '/\D+/(\d{1,3})\.s?html?',  # syq
        )
        for reg in next_page_num_regex:
            m = re.search(reg, url)
            if m:
                page_num = int(m.group(1))
                if page_num > 1:
                    return True
        return False

    def is_error_url(self, url):
        '''错误url判断'''
        if re.search('///', url):
            return True
        elif url.count('//') >= 2:
            return True
        elif url.count('http://') >= 2:
            return True
        elif len(url) > 100:
            return True
        # 正常域名格式
        elif not re.match('^(?:\w+\.){2,}[a-z]+$', urlparse.urlparse(url).netloc):
            return True
        else:
            pass
        return False

    def is_not_found(self, url):
        r = requests.get(url, allow_redirects=False)
        if int(r.status_code) >= 400:
            return False

    def is_old_url(self, url):
        '''判断是否为旧链接'''
        datetimes = self.get_time_from_url(url)
        if not datetimes:
            return False
        if max(datetimes) < self.now_year:
            return True
        return False

    def get_time_from_url(self, url):
        '''从url中获取时间'''
        regex_datetimefmt_list = [
            ('(\d{8})', '%Y%m%d'),
            ('/(\d{4}/\d{4})/', '%Y/%m%d'),
            ('/(20\d\d)\D', '%Y'),
            ('\D(20\d\d)/', '%Y'),
            ('(\d{4}-\d\d-\d\d)', '%Y-%m-%d'),
            ('\D(\d{4})\D', '%Y'),
        ]
        all_datetimes = []
        for regex, fmt in regex_datetimefmt_list:
            m = re.findall(regex, url)
            # print m
            if m:
                try:
                    dt = datetime.datetime.strptime(m[0], fmt)
                    all_datetimes.append(dt)
                except Exception as e:
                    # print e
                    continue
        return all_datetimes

    def is_old_page(self, text):
        '''判断是否为旧页面'''
        datetimes = self.get_time_from_text(text)
        if not datetimes:
            return False
        all_le = len(datetimes)
        datetimes = filter(lambda x: not (x < self.now_year), datetimes)
        f_le = len(datetimes)
        if f_le * 1.0 / all_le < 0.1:
            return True
        return False

    def get_time_from_text(self, text):
        '''从文本中获取时间信息'''
        datetimes = []
        # 清除年月日
        text = re.sub(u'\s*年\s*', '-', text)
        text = re.sub(u'\s*月\s*', '-', text)
        text = re.sub(u'\s*日\s*', ' ', text)
        text = re.sub(u'/', '-', text)
        text = re.sub(u'(\d{4})(\d{2})(\d{2})', '\\1-\\2-\\3', text)
        dt_strs = re.findall('\d{4}-\d{1,2}-\d{1,2}', text)
        for dtstr in dt_strs:
            try:
                dt = datetime.datetime.strptime(dtstr, '%Y-%m-%d')
                datetimes.append(dt)
            except:
                pass
        return datetimes

    def is_error_page(self, text, special_regex_404_list=[]):
        '''判断是否为404等错误页面'''
        if not isinstance(text, unicode):
            raise myexc(u"is_error_page() error: not a unicode text")
        default_regex_404_list = [
            u'页面不存在',
            u'404\s*not\s*found',
            u'页面.{0,5}删除',
            u'页面不见.',
            u'页面.{0,10}(劫持|火星)',
        ]
        regex_404_list = default_regex_404_list + special_regex_404_list
        for regex_404 in regex_404_list:
            if not isinstance(regex_404, unicode):
                try:
                    regex_404 = regex_404.decode('utf8')
                except:
                    pass
            if re.search(regex_404, text, re.I | re.S):
                print regex_404
                return True
        return False


def get_unicode_page(url, encoding):
    response = requests.get(url)
    response.encoding = encoding
    return response.text


if __name__ == '__main__':
    sina_clean = Cleaner('news.sina.com.cn')
    # print sina_clean.is_old_url('http://roll.news.sina.com.cn/s_2012nobel_all/index.shtml')
    # print sina_clean.in_black_list('http://tags.news.sina.com.cn/')
    # print sina_clean.is_next_page('http://news.sina.com.cn/911anni/photo/21.shtml')
    # print sina_clean.is_next_page('http://news.sina.com.cn/911anni/photo/21.shtml')
    # print sina_clean.filter_urls(['http://news.sina.com.cn/richtalk/news/society/society_beijingribao.html'])
    # print sina_clean.is_detail_by_regex('http://news.sina.com.cn/richtalk/news/society/society_beijingribao.html')
    text = get_unicode_page('http://bbs.yuloo.com/404.html', 'gbk')
    print sina_clean.is_error_page(text)
    print sina_clean.is_old_page(text)
