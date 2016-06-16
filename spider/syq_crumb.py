#!/usr/bin/env python
# coding=utf-8

import re
import time
import datetime
import urlparse
import redis
from bs4 import BeautifulSoup, Comment
import spider
import setting
import htmlparser
import requests
import myreadability
import HTMLParser
import syq_clean_url
import cStringIO, urllib2, Image
import lxml.html


class MySpider(spider.Spider):

    def __init__(self,
                 proxy_enable=setting.PROXY_ENABLE,
                 proxy_max_num=setting.PROXY_MAX_NUM,
                 timeout=setting.HTTP_TIMEOUT,
                 cmd_args=None):
        spider.Spider.__init__(
            self, proxy_enable, proxy_max_num, timeout=timeout, cmd_args=cmd_args)
        # 网站名称
        self.siteName = "k618"
        # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎
        self.info_flag = "01"
        self.start_urls = 'http://www.k618.cn/'
        # self.start_urls = 'http://bj.esf.sina.com.cn/'
        # self.encoding = 'utf-8'
        self.encoding = 'utf-8'
        # self.site_domain = 'sina.com.cn'
        self.site_domain = 'k618.cn'
        self.conn = redis.StrictRedis.from_url('redis://127.0.0.1/8')
        self.crumbs_urls_zset_key = 'crumbs_urls_zset_%s' % self.site_domain
        self.hub_todo_urls_zset_key = 'hub_todo_urls_zset_%s' % self.site_domain
        self.hub_level_urls_zset_key = 'hub_level_urls_zset_%s' % self.site_domain
        self.todo_flg = -1
        self.done_flg = 0
        self.todo_urls_limits = 10
        self.max_level = 5  # 最大级别
        self.dedup_key = None
        self.cleaner = syq_clean_url.Cleaner(
            self.site_domain, redis.StrictRedis.from_url('redis://127.0.0.1/5'))

    def convert_path_to_rule0(self, url):
        '''
        http://baike.k618.cn/thread-3327665-1-1.html ->
        /[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]-\d\d\d\d\d\d\d-\d-\d.html
        '''
        parse = urlparse.urlparse(url)
        path = parse.path
        pos1 = path.rfind('/')
        pos2 = path.find('.')
        if pos2 < 0:
            pos2 = len(path)
        tag = re.sub(r'[a-zA-Z]', '[a-zA-Z]', path[pos1 + 1:pos2])
        tag = re.sub(r'\d', '\d', tag)
        return  parse.scheme + '://' + parse.netloc + '/' + path[:pos1 + 1] + tag + path[pos2:]

    def filter_links(self, urls):
        # print 'filter_links() all',len(urls)
        # 下载页
        # urls = filter(lambda x: not self.cleaner.is_download(x), urls)
        # print 'filter_links() is_download', len(urls)
        # 错误url识别
        urls = filter(lambda x: not self.cleaner.is_error_url(x), urls)
        # print 'filter_links() is_error_url', len(urls)
        # 清洗无效参数#?
        urls = self.cleaner.url_clean(urls)
        # 跨域检查
        urls = filter(lambda x: self.cleaner.check_cross_domain(x), urls)
        # print 'filter_links() check_cross_domain', len(urls)
        #过滤详情页
        # urls = filter(lambda x: not self.cleaner.is_detail_by_regex(x), urls)
        # 黑名单过滤
        urls = filter(lambda x: not self.cleaner.in_black_list(x), urls) # bbs. mail.
        # print 'filter_links() in_black_list', len(urls)
        # 链接时间过滤
        # urls = filter(lambda x: not self.cleaner.is_old_url(x), urls)
        # 非第一页链接过滤
        # urls = filter(lambda x: not self.cleaner.is_next_page(x), urls)
        # print 'filter_links() is_next_page', len(urls)

        # ' http://news.k618.cn/zxbd/201606/t20160612_7703993.html'
        # ' http://news.k618.cn/zxbd/201606/t20160612_7703952.html' 视为同一url
        rule_lst = []
        urls_tmp = []
        for url in urls:
            if url.rfind('.htm')>0 or url.rfind('.shtm')>0:
                rule0 = self.convert_path_to_rule0(url)
                if rule0 not in rule_lst:
                    rule_lst.append(rule0)
                    urls_tmp.append(url)
        urls = urls_tmp
        # print 'filter_links() rule0', len(urls)

        # 去重
        urls = list(set(urls))
        # print 'filter_links() set', len(urls)
        # 404
        # urls = filter(lambda x: not self.cleaner.is_not_found(x), urls)
        # print 'filter_links()', len(urls)
        return urls

    def get_start_urls(self, data=None):
        if self.conn.zrank(self.hub_todo_urls_zset_key, self.start_urls) is None:
            self.conn.zadd(self.hub_todo_urls_zset_key, self.todo_flg, self.start_urls)
        if self.conn.zrank(self.hub_level_urls_zset_key, self.start_urls) is None:
            self.conn.zadd(self.hub_level_urls_zset_key, 0, self.start_urls)
        return [self.start_urls]

    def get_page_valid_urls(self, data, org_url):
        urls = []
        links = data.xpathall("//a/@href | //iframe/@src")

        for link in links:
            url = urlparse.urljoin(org_url, link.text().strip())
            urls.append(url)
        urls = self.filter_links(urls)
        return urls

    def header_maker(self):
        header = {'Proxy-Connection': 'keep-alive',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                  'Accept-Encoding': 'gzip, deflate, sdch',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
                  }
        return header

    def get_clean_soup(self,url):
        headers = self.header_maker()
        try:
            data = requests.get(url, headers=headers, timeout=5)
        except:
            print("[ERROR] connect:",url)
            return None
        soup = BeautifulSoup(data.content, 'lxml')
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [s.extract() for s in soup('script')]
        [input.extract() for input in soup('input')]
        [input.extract() for input in soup('form')]
        [blank.extract() for blank in soup(text=re.compile("^\s*?\n*?$"))]
        # [foot.extract() for foot in soup(attrs={'class': 'footer'})]
        [foot.extract() for foot in soup(attrs={'class': 'bottom'})]
        [s.extract() for s in soup('style')]
        return soup

    def marge_url(self, url, href):
        # print 'marge_url() start'
        if url is None:
            ret = None
        elif href is None or href == '#':
            ret = url
        elif href.find('javascript') >= 0:
            ret = None
        elif href[:2] == './':
            ret = url + href[2:]
        elif href.count('../') > 0:
            cnt = href.count('../')
            href_split = urlparse.urlparse(url).path.split('/')
            href_split = href_split[:-(cnt+1)]
            new = '/'.join(href_split)
            ret = urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc + new
        elif urlparse.urlparse(href).scheme:
            ret = href
        else:
            netloc = urlparse.urlparse(url).netloc
            if netloc[-1] != '/':
                netloc += '/'
            ret = urlparse.urlparse(url).scheme + '://'  + netloc + href
        if ret:
            if ret[-1]=='/': ret = ret[:-1]
        return ret

    def find_breadcrumbs(self, url):
        '''
        1）"breadcrumb"
        //div[contains(@class,"bread")]
        //div[contains(@class,"crumb")]
        2）'>' ‘>>’ '›'
        3）//div[contains(@class,'nav')] or
           Nav NAV
        4) 文字长度小于7
        '''
        crumbs = []
        soup = self.get_clean_soup(url)
        if not soup:
            return False

        div_tag = soup.find('div',class_=re.compile(r'\w?crumb[s]?', re.U))
        if div_tag:
            # print 'div tag:',div_tag
            soup = div_tag

        a_tags = soup.findAll('a')
        for a_tag in a_tags:
            tags = a_tag.parent.findAll(text=re.compile(r'^\s*[>›]+\s*$', re.U))
            if tags:
                for a in a_tag.parent.findAll('a'):
                    marge_url = self.marge_url(url, a.get('href'))
                    # print url, a.get('href'), '->', marge_url
                    if marge_url:
                        crumbs.append(marge_url)

                break # 防止邻近非兄弟<a>节点混入

        return list(set(crumbs))
        # tags2 = soup.findAll(text=re.compile(r'(正文|当前位置|当前的位置)\s*$', re.U))
        # print tags2

    def find_content_div(self, url):
        soup = self.get_clean_soup(url)
        # //div[contains(@class,'footer')]
        footer_div = soup.find('div',class_='footer')
        divs = footer_div.find_previous_siblings('div',recursive=False)
        for div in divs:
            p_score, imgs_score, a_score = self.div_info_score(url,div)
            print '<div id={} class={}>'.format(div.get('id'),div.get('class')), '<p>', p_score, '<img>', imgs_score, '<a>(p,img)', a_score

    def div_info_score(self, url, div):
        #<p>
        p_text = []
        p_tags = div.findAll('p')
        for p_tag in p_tags:
            text_without_blank = re.compile(r"\s+", re.I | re.M | re.S).sub('', p_tag.text)
            p_text.append(text_without_blank)
        p_score = len(''.join(p_text))

        #<img>
        imgs_score = 0
        img_tags = div.findAll('img')
        for img_tag in img_tags:
            img_src = img_tag.get('src')
            if img_src:
                format, size, mode = self.get_img_info(url, img_src)
                imgs_score += self.convert_img_info_score(size)
            else:
                print '0,0'
                imgs_score += 0

        #<a>
        a_score_p, a_score_img = 0, 0
        a_tags = div.findAll('a')
        for a_tag in a_tags:
            # 文字
            text_without_blank = re.compile(r"\s+", re.I | re.M | re.S).sub('', a_tag.text)
            a_score_p += len(text_without_blank)
            # 图片
            img_tag = a_tag.find('img')
            if img_tag:
                img_src = img_tag.get('src')
                if img_src:
                    format, size, mode = self.get_img_info(url, img_src)
                    a_score_img += self.convert_img_info_score(size)
                else:
                    print '0,0'
                    a_score_img += 0
        a_score = (a_score_p, a_score_img)

        return p_score, imgs_score, a_score

    def convert_img_info_score(self, size):
        # 70 * 70 = 1 汉字 转换
        (img_width,img_high) = size
        return img_width*img_high/(80*80)

    # def to_string(self,elem):
    #     return lxml.html.tostring(elem, encoding='utf8', method='text').strip()

    def get_img_info(self, url, img_src):
        try:
            if img_src:
                if img_src.find('http://') < 0:
                    img_url = self.marge_url(url, img_src)
                else:
                    img_url = img_src
                req = urllib2.Request(img_url, headers=self.header_maker())
                file = urllib2.urlopen(req, timeout=30)
                tmpIm = cStringIO.StringIO(file.read())
                im = Image.open(tmpIm)
                return im.format, im.size, im.mode
        except Exception, e:
            # print '[ERROR]get_img_info()',img_url
            return None, (0,0), None

    def parse(self, response):
        urls = []
        try:
            urls = self.conn.zrangebyscore(self.hub_todo_urls_zset_key, self.todo_flg, self.todo_flg)
            if len(urls) > self.todo_urls_limits:
                urls = urls[0:self.todo_urls_limits]
            for url in urls:
                self.conn.zadd(self.hub_todo_urls_zset_key, self.done_flg, url)
        except Exception, e:
            print "[ERROR] parse(): %s" % e
        return urls, None, None


    def parse_detail_page(self, response=None, url=None):
        result = []
        if response is None:
            return result
        try:
            unicode_html_body = response.content
            data = htmlparser.Parser(unicode_html_body)
            valid_urls = self.get_page_valid_urls(data, response.url)
            # for valid_url in valid_urls:
            #     # 取得（没有的话，父节点+1）/记录（有记录的话） hub 的 level
            #     if self.conn.zrank(self.hub_level_urls_zset_key, valid_url) is None:
            #         # child.score = parent.score +1
            #         score = self.conn.zscore(self.hub_level_urls_zset_key, response.url)
            #         if score is None: score = 0
            #         self.conn.zadd(self.hub_level_urls_zset_key, score + 1, valid_url)
            #     else:
            #         score = self.conn.zscore(self.hub_level_urls_zset_key, valid_url)
            #
            #     # 超过 max_level 则done
            #     if self.conn.zrank(self.hub_todo_urls_zset_key, valid_url) is None:
            #         if score <= self.max_level:
            #             self.conn.zadd(self.hub_todo_urls_zset_key, self.todo_flg, valid_url)
            #         # else:
            #         #     self.conn.zadd(self.hub_todo_urls_zset_key, self.done_flg, valid_url)

            for valid_url in valid_urls:
                crumbs = self.find_breadcrumbs(valid_url)
                if crumbs:
                    # save to redis
                    for crumb in crumbs:
                        if self.conn.zrank(self.crumbs_urls_zset_key, crumb) is None:
                            self.conn.zadd(self.crumbs_urls_zset_key, 0, crumb)

                    # 此url的todo状态设为done
                    self.conn.zadd(self.hub_todo_urls_zset_key, self.done_flg, valid_url)
                else:
                    if self.conn.zrank(self.hub_todo_urls_zset_key, valid_url) is None:
                        self.conn.zadd(self.hub_todo_urls_zset_key, self.todo_flg, valid_url)

        except Exception, e:
            # self.conn.zadd(self.hub_urls_zset_key, self.done_flg, response.url)
            print "[ERROR] parse_detail_page(): %s" % e

        return result

if __name__ == '__main__':
    unit_test = True
    if unit_test is not True: # spider simulation
        for cnt in range(1000):
            print '[loop]',cnt,'[time]',datetime.datetime.utcnow()
            detail_job_list = []  # equal to run.py detail_job_queue
            # ---equal to run.py get_detail_page_urls(spider, urls, func, detail_jo
            def __detail_page_urls(urls, func):
                next_page_url = None
                if func is not None:
                    if urls:
                        for url in urls:
                            response = mySpider.download(url)
                            try:
                                list_urls, callback, next_page_url = func(
                                    response)  # parse()
                                for url in list_urls:
                                    detail_job_list.append(url)
                            except Exception, e:
                                print '[ERROR] main() Exception:', e
                                list_urls, callback, next_page_url = [], None, None

                            __detail_page_urls(list_urls, callback)

                            if next_page_url is not None:
                                print 'next_page_url'
                                __detail_page_urls([next_page_url], func)

            # --equal to run.py list_page_thread() -------------------------
            mySpider = MySpider()
            mySpider.proxy_enable = False
            mySpider.init_dedup()
            mySpider.init_downloader()
            start_urls = mySpider.get_start_urls()  # get_start_urls()
            __detail_page_urls(start_urls, mySpider.parse)  # parse()

            # --equal to run.py detail_page_thread() -------------------------
            ret = []
            for url in detail_job_list:
                resp = mySpider.download(url)
                ret = mySpider.parse_detail_page(resp, url)  # parse_detail_page()
                for item in ret:
                    for k, v in item.iteritems():
                        print k, v
    else: # -------- unit test -------------------
        # url = 'http://news.k618.cn/zxbd/201606/t20160613_7705874.html' # [样式A]
        # url = 'http://news.k618.cn/yl_37061/201508/t20150822_6103876.html' # [样式A]
        # url = 'http://comic.k618.cn/dmgc/201412/t20141230_5796348.htm'  # [样式A]
        # url = 'http://liuxue.k618.cn/kuaibao1/201504/t20150417_5930210.html' # [样式A]
        # url = 'http://bbs.jjh.k618.cn/thread-3327506-1-10.html' # [样式B] bug
        url = 'http://tech.sina.com.cn/mobile/n/n/2016-06-16/doc-ifxtfrrc3668316.shtml'
        # url = 'http://127.0.0.1:5000/'
        url = 'http://www.k618.cn/'
        mySpider = MySpider()
        mySpider.proxy_enable = False
        mySpider.init_dedup()
        mySpider.init_downloader()
        print mySpider.find_content_div(url)
        # print mySpider.marge_url(url,href)