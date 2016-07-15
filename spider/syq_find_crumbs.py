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
import allsite_clean_url
import cStringIO, urllib2, Image
import lxml.html
import urllib


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
        # self.encoding = 'gbk'
        # self.encoding = 'utf-8'
        # self.site_domain = 'sina.com.cn'
        self.site_domain = 'k618.cn'


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

    def find_breadcrumbs(self, url):
        '''
        1）"breadcrumb"
        //div[contains(@class,"bread")]
        //div[contains(@class,"crumb")]
        2）'>' ‘>>’ '›'
        3）//div[contains(@class,'nav')] or
           Nav NAV
        4) 文字长度小于7
        # tags2 = soup.findAll(text=re.compile(r'(正文|当前位置|当前的位置)\s*$', re.U))
        '''
        crumbs = []
        soup = self.get_clean_soup(url)
        if not soup:
            return False

        tags2 = soup.findAll(text=re.compile(u'(正文|当前位置|当前的位置)\s*$', re.U))
        print tags2

        # div_tag = soup.find('div',class_=re.compile(r'[\w\W]?(position|bread|crumb[s]?)', re.U))
        # if div_tag:
        #     print 'div tag:', div_tag
        #     soup = div_tag

        # div_tag = soup.find('div', text=re.compile(r'当前位置', re.U))
        # if div_tag:
        #     print u'正文|当前位置|当前的位置:', div_tag
        #     soup = div_tag
        #     print soup

        # a_tags = soup.findAll('a')
        # for a_tag in a_tags:
        #     tags = a_tag.parent.findAll(text=re.compile(r'^\s*[>›]+\s*$', re.U))
        #     # tags = div_tag.find(text=re.compile(r'(正文|当前位置|当前的位置)\s*$'))
        #     if tags:
        #         print tags
        #         for a in tags.parent.findAll('a'):
        #             print a.get('href')
        #         break # 防止邻近非兄弟<a>节点混入


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

    def is_current_page(self, org_url):
        response = mySpider.download(org_url)
        char = re.search(r'charset=(.*)>',response.text)
        if char:
            if re.search("utf", char.group(1), re.I):
                encode = "utf8"
            elif re.search("gb", char.group(1), re.I):
                encode = "gbk"
            elif re.search('big5', char.group(1), re.I):
                encode = "big5"
        else:
            encode = "utf8"

        response.encoding = encode
        unicode_html_body = response.text  # unicode
        parse = htmlparser.Parser(data=unicode_html_body)
        # parse = htmlparser.Parser(data=parse.data, encoding=encode)

        nav_links = parse.replace('[\n\r]','').regexall(u'<div.*?正文.*?div>')
        print 'nav_links:',nav_links
        for nav in nav_links:
            nav = nav.data[nav.data.rfind('<div'):]
            # print nav
            if nav.count('</a>') >0:
                hrefs = re.findall(r'href=\"(.*?)\"', nav)
                for href in hrefs:
                    scheme, netloc, path, params, query, fragment = urlparse.urlparse(href)
                    if scheme:
                        url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
                    else:
                        href = urlparse.urlunparse(('', '', path, params, query, ''))
                        url = urlparse.urljoin(org_url, href)
                    print 'urljoin:',url
                return True
        return False

    def find_bread(self,org_url):
        response = mySpider.download(org_url)
        char = re.search(r'charset=(.*)>',response.text)
        if char:
            if re.search("utf", char.group(1), re.I):
                encode = "utf8"
            elif re.search("gb", char.group(1), re.I):
                encode = "gbk"
            elif re.search('big5', char.group(1), re.I):
                encode = "big5"
        else:
            encode = "utf8"

        response.encoding = encode
        unicode_html_body = response.text  # unicode
        parse = htmlparser.Parser(data=unicode_html_body)
        nav_links = parse.replace('[\n\r]', '').regexall(u'<div.*?class=".*?bread.*?".*?div>')
        print nav_links
        for nav in nav_links:
            nav = nav.data[nav.data.rfind('<div'):]
            hrefs = re.findall(r'href=\"(.*?)\"', nav)
            for href in hrefs:
                scheme, netloc, path, params, query, fragment = urlparse.urlparse(href)
                if scheme:
                    url = urlparse.urlunparse((scheme, netloc, path, params, query, ''))
                else:
                    href = urlparse.urlunparse(('', '', path, params, query, ''))
                    url = urlparse.urljoin(org_url, href)
                print 'urljoin:', url


if __name__ == '__main__':
    url = 'http://www.yangtse.com/wenyu/2014-10-07/302874.html' #gbk
    # url = 'http://nt.yangtse.com/Micro/video/96412.html' #utf8
    # url = 'http://nt.yangtse.com/news/house/2015/12/31/1451521665107307.html' #utf8
    url = 'http://nt.yangtse.com/news/house/2015/12/31/1451521664107302.html'
    url = 'http://liuyan.people.com.cn/index.php?fid=4'
    # url = 'http://127.0.0.1:5000/'
    mySpider = MySpider()
    mySpider.proxy_enable = False
    mySpider.init_dedup()
    mySpider.init_downloader()
    # response.encoding = mySpider.encoding
    print url

    print 'is_current_page()'
    mySpider.is_current_page(url)
    #
    # print 'find_bread()'
    # mySpider.find_bread(url)

    # print 'find_breadcrumbs()'
    # mySpider.find_breadcrumbs(url)
