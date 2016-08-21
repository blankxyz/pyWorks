# coding:utf-8
'''
url及文本判断过滤
'''
import re
import json
import urllib
import datetime
import urlparse
import requests
import redis

import traceback

class myexc(Exception):
    def __init__(self, error_info):
        super(Exception, self).__init__()
        self.error_info = error_info

    def __str__(self):
        return 'use defined exceptions %s' % self.error_info


class Cleaner(object):
    def __init__(self, site_domain, black_domain_list, conn=None):
        self.site_domain = site_domain
        self.conn = conn
        if self.conn is None:
            self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/14')
        # 域名正则黑名单
        self.now_year = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y'), '%Y')
        self.hash_black_path_regex_key = 'hash_black_path_regex'
        self.black_path_regex = []
        self.black_domain_regex = self.get_black_path_regex(black_domain_list)  # black_domain_list 以 ; 分割的字符串

    def get_black_path_regex(self, black_domain_list):
        '''路径正则黑名单
        @ 匹配到的路径应为 非列表页url
        '''
        default_regex = ['/', '^$']
        compile_list = []
        for regex_str in black_domain_list.split('@'):
            if regex_str != '': compile_list.append(regex_str)

        compile_list.extend(default_regex)

        return compile_list

    def in_black_list(self, url):
        '''域名黑名单'''
        for regex in self.black_domain_regex:
            if re.match(re.compile(regex), urlparse.urlparse(url).netloc):
                print regex
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

    def is_suffixes_ok(self, url):  # syq
        p = urlparse.urlparse(url).path
        for fix in ['.apk', '.doc', '.xls', '.csv', '.avi', '.rmvb', '.jpg', '.mp3', '.pdf', '.rar','.png']:
            if p.find(fix) > 0:
                return False
        return True

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
                print '[ERROR]is_detail_by_regex()', e
                continue
        return is_detail

    def url_sort(self, url):
        try:
            '''url参数排序'''
            if isinstance(url, unicode):
                url = url.encode('utf8')

            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            keyvals = urlparse.parse_qsl(query, keep_blank_values=1)
            keyvals.sort()
            query = urllib.urlencode(keyvals)
            return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
        except Exception as e:
            print '[ERROR]url_sort()',url, e
            # print traceback.format_exc()
            return url

    def url_clean(self, urls):
        new_urls = []
        url = ''
        try:
            '''清洗无效参数并排序'''
            for url in urls:
                # 清理锚 # 之后的
                url = url.split('#')[0]
                # 汉字参数转义
                # url = urllib.unquote(url)
                # 参数排序
                url = self.url_sort(url)
                # 去'/'
                # url = url.strip('/')
                #
                new_urls.append(url)
        except Exception as e:
            print '[ERROR]url_clean()', url, e

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
    url = u'http://bbs.tianya.cn/compose.jsp?item=107&sub=全部&aaa=777'
    print url
    cleaner = Cleaner(site_domain='bbs.tianya.cn', black_domain_list='blog.tianya.cn')
    print cleaner.url_sort(url)
