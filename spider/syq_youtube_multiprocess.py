# coding:utf-8
import datetime
import re
from  multiprocessing import Pool
import time
import requests
import redis
import htmlparser
import urllib2

REDIS_SERVER = 'redis://127.0.0.1/12'

# Filters: 1)Upload date: today  2)Sort by: Upload date
PRE_SEARCH_URL = 'https://www.youtube.com/results?sp=CAISAggC&q='

siteName = 'youtube'
site_domain = 'www.youtube.com'
info_flag = '07'
encoding = 'utf-8'
conn = redis.StrictRedis.from_url(REDIS_SERVER)
keyword_zset_key = '%s_keyword_zset' % siteName
search_result_urls_zset_key = '%s_search_result_urls_zset' % siteName
video_info_hset_key = '%s_video_info_hset' % siteName
todo_flg = -1
start_flg = 0


def time_convert(ago_time_str):
    '''
    Args:
        ago_time_str: 例：'1 hour ago' or '2 minutes ago'
    Returns:
        计算XX时间之前的结果
        注意：英文中的复数形式匹配：结尾加s
    '''
    ret_time = datetime.datetime.now()
    if ago_time_str is None:
        return ret_time

    num_str = re.match(re.compile(r"(\d+)\s[a-zA-Z]+"), ago_time_str)
    if num_str:
        num = int(num_str.group(1))
        if 'second' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(seconds=num))
        if 'minute' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(minutes=num))
        if 'hour' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(hours=num))
        if 'day' in ago_time_str:
            ret_time = (ret_time - datetime.timedelta(days=num))

    return ret_time.strftime("%Y-%m-%d %H:%M:%S")


def download(url):
    proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'q=0.6,en-US;q=0.4,en;q=0.2',
               'Connection': 'keep-alive',
               'Cookie': 'PREF=f1=1222&cvdm=list',  # must be set 'list'
               'Host': 'www.youtube.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'
               }
    try:
        resp = requests.get(url, proxies=proxies, headers=headers)
        return resp.content
    except Exception, e:
        print 'get_html() error', e
        return None


def get_start_urls(i):
    print 'get_start_urls() start.'
    urls = []
    keywords = conn.zrangebyscore(keyword_zset_key,
                                  min=todo_flg,
                                  max=todo_flg,
                                  withscores=False)
    for keyword in keywords[:5]:
        # url = PRE_SEARCH_URL + urllib2.quote(keyword)
        url = PRE_SEARCH_URL + keyword
        urls.append(url)
        print 'get_start_urls() keyword: %s' % keyword
        conn.zadd(keyword_zset_key, start_flg, keyword)

    page_num_urls = []
    for url in urls:
        (url_list, _, _) = parse(url)
        page_num_urls.extend(url_list)

    print 'get_start_urls() end.'
    return page_num_urls


def parse(url):
    '''
    根据keyword的检索结果（结果件数），生成带页数信息的url。
    '''
    url_list = []
    cnt = 0

    try:
        print 'parse() start.', url
        html_content = download(url)
        if html_content is None:
            return (url_list, None, None)

        data = htmlparser.Parser(html_content)
        cnt_str = data.xpath('''//p[contains(@class,"num-results")]''')
        cnt_str = cnt_str.text().strip()

        print 'parse() debug:', cnt_str

        cnt_str = re.match(re.compile(r"(About\s)(.+?)(\sfiltered results)"), cnt_str)
        if cnt_str:
            cnt_str = cnt_str.group(2)
            cnt_str = re.sub(r",", "", cnt_str)
            cnt = int(cnt_str)

        if cnt > 0:
            pages = (cnt / 20) + 1
            if pages > 20:
                pages = 2

            for page in range(1, pages + 1):
                request_url = url + '&page=%d' % page
                url_list.append(request_url)

                conn.zadd(search_result_urls_zset_key, todo_flg, request_url)

    except Exception, e:
        print "parse(): error %s" % e
        return (url_list, None, None)

    print 'parse() end.', url, 'has [ %d ] pages' % len(url_list)
    return (url_list, None, None)


def parse_detail_page(urls):
    '''
    解析带有页数信息的URL的内容，取得各个项目内容
    '''
    result = []
    # urls = conn.zrangebyscore(search_result_urls_zset_key,
    #                           min=todo_flg,
    #                           max=todo_flg,
    #                           start=0,
    #                           num=1,
    #                           withscores=False)
    print 'parse_detail_page() start. [urls] ', urls

    if len(urls) == 0:
        print 'parse_detail_page() nothing.'
        return result

    try:
        for url in urls:
            conn.zadd(search_result_urls_zset_key, start_flg, url)
            keyword = url[len(PRE_SEARCH_URL):]
            keyword = re.match(re.compile(r"(.*)(&page=\d+)"), keyword).group(1)
            keyword = urllib2.unquote(keyword)

            html_content = download(url)
            data = htmlparser.Parser(html_content)
            # 需要包含各个视频信息左侧的图片div
            divs = data.xpathall('''//div[contains(@class,"yt-lockup-video")]''')
            for div in divs:
                ad = div.xpath('''//span[contains(@class,"yt-badge-ad")]''').text().strip()
                if ad == 'Ad':  # 去除广告
                    continue

                channel = div.xpath('''//div[contains(@class,"yt-lockup-byline")]/a''').text().strip()  # class中会有空格
                channel_url = div.xpath('''//div[contains(@class,"yt-lockup-byline")]/a/@href''').text().strip()

                title = div.xpath('''//h3''').text().strip()

                upload_time_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[1]''').text().strip()
                upload_time = time_convert(upload_time_str)

                thumb_img_src = div.xpath('''//span[contains(@class,"yt-thumb-simple")]/img/@src''').text().strip()

                video_href = div.xpath('''//h3/a/@href''').text().strip()
                video_id = video_href[len('/watch?v='):]  # /watch?v=Wza_nSeLH9M

                views = None
                views_str = div.xpath('''//ul[contains(@class,"yt-lockup-meta-info")]/li[last()]''').text().strip()
                if views_str:
                    views = re.match(re.compile(r"(.*)(\sview+)"), views_str)
                    if views:
                        views = views.group(1)
                        views = re.sub(r",", "", views)
                        if views == 'No':
                            views = 0

                description = div.xpath('''//div[contains(@class,"yt-lockup-description")]''')
                if description._root is not None:
                    description = description.text().strip()
                else:
                    description = ''

                video_info = {'info_flag': info_flag,
                              'url': 'https://www.youtube.com' + video_href,
                              'video_id': video_id,
                              'title': title.decode('utf8'),
                              'pic_urls': [thumb_img_src],
                              'video_urls': ['https://www.youtube.com' + video_href],
                              'content': description.decode('utf8'),
                              'visitCount': views,
                              'channel': channel.decode('utf8'),
                              'channel_url': channel_url,
                              'ctime': upload_time,
                              'site_domain': site_domain,
                              'siteName': siteName,
                              }

                conn.hset(video_info_hset_key, video_info['video_id'], video_info)
                result.append(video_info)

            print 'parse_detail_page() end. [keyword] %s, [result cnt] %d' % (keyword, len(result))
            conn.zincrby(keyword_zset_key, value=keyword, amount=len(result))

    except Exception, e:
        print "parse_detail_page() error. %s" % e

    return None


def Foo(i):
    time.sleep(0.1)
    return i + 100


def Bar(arg):
    print 'Bar', arg


if __name__ == '__main__':
    pool = Pool()
    for i in range(100):
        # pool.apply_async(func=Foo, args=(i,), callback=Bar)
        pool.apply_async(func=get_start_urls, args=(i,), callback=parse_detail_page)

    pool.close()
    pool.join()
    pool.terminate()
