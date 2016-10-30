# coding:utf-8

import re
import urllib
import redis
from bs4 import BeautifulSoup, Comment
import requests
import subprocess
import youtube_dl

REDIS_SERVER = 'redis://127.0.0.1/13'
CONFIG_ID = '9999'
INFO_FLG = '07'  # 类别码，01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.video_id_zset_key = 'video_id_zset_%s' % self.site_domain  # 状态管理
        self.json_hset_key = 'json_hset_%s' % self.site_domain  # --print-json 结果保存
        self.result_hset_key = 'result_hset_%s' % self.site_domain  # 最终结果保存
        self.todo_flg = -1
        self.done_info_flg = 0
        self.done_sbutitle_flg = 1

    def add_todo(self, video_id):
        return self.conn.zadd(self.video_id_zset_key, self.todo_flg, video_id)

    def set_info_done(self, video_id, post):
        self.conn.hset(self.result_hset_key, video_id, post)
        return self.conn.zadd(self.video_id_zset_key, self.done_info_flg, video_id)

    def set_subtitle_done(self, video_id):
        return self.conn.zadd(self.video_id_zset_key, self.done_sbutitle_flg, video_id)

    def get_todo_videoIds(self):
        return self.conn.zrangebyscore(self.video_id_zset_key, self.todo_flg, self.todo_flg, withscores=False)


class KeywordSearch(object):
    def __init__(self):
        pass

    def get_html(self, url):
        page = urllib.urlopen(url)
        html = page.read()
        return html

    def get_video_id(self, html):
        reg = r"(?<=a\shref=\"/watch\?v\=).+?(?=\")"
        # reg = r"(?<=a\shref=\"/watch).+?(?=\")"
        urlre = re.compile(reg)
        urllist = re.findall(urlre, html)
        redis_db = RedisDrive()
        # format = "https://www.youtube.com/watch%s\n"
        # f = open("search_keyword.log", 'a')
        for url in urllist:
            redis_db.add_todo(url)
            # result = (format % url)
            # f.write(result)
            # f.close()

    def get_info_by_video_id(self, video_id):
        if video_id is None: return {}

        url = 'http://www.youtube.com/watch?v=%s' % video_id
        # ydl_opts = {
        #     'format': 'bestaudio/best',
        #     'extractaudio': True,
        #     'audioformat': 'mp3',
        #     'outtmpl': '%(id)s',  # name the file the ID of the video
        #     'noplaylist': True,
        #     'nocheckcertificate': True,
        #     'postprocessors': [{
        #         'key': 'FFmpegExtractAudio',
        #         'preferredcodec': 'mp3',
        #         'preferredquality': '192',
        #     }]
        # }

        # --write-auto-sub: Write automatic subtitle file (YouTube only)
        # writeautomaticsub: Write the automatically generated subtitles to a file
        ydl_opts = {'writeautomaticsub': True,
                    'subtitleslangs': 'en',
                    'subtitlesformat': 'vtt'}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:

            result = ydl.extract_info(
                url,
                download=False  # We just want to extract the info
            )

            if 'entries' in result:
                # Can be a playlist or a list of videos
                video_info = result['entries'][0]
            else:
                # Just a video
                video_info = result

            title = video_info['title']
            creator = video_info['creator']
            view_count = video_info['view_count']
            like_count = video_info['like_count']
            dislike_count = video_info['dislike_count']
            categories = video_info['categories']
            description = video_info['description']
            uploader = video_info['uploader']

        post = {'config_id': CONFIG_ID,
                'info_flg': INFO_FLG,
                'url': url,
                'title': title,
                'view_count': view_count,
                'like_count': like_count,
                'dislike_count': dislike_count,
                'categories': categories,
                'description': description,
                'uploader': uploader,
                'author': creator
                }

        return post

    def get_download_result(self):
        redis_db = RedisDrive()
        video_id_list = redis_db.get_todo_videoIds()
        print video_id_list
        for video_id in video_id_list:
            # subprocess.Popen("youtube-dl", )
            # p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
            # server_log_list = p.stdout.readlines()
            post = self.get_info_by_video_id(video_id)
            # print post
            redis_db.set_info_done(video_id, post)

        return True


class Channels(object):
    def __init__(self):
        # self.start_url = 'https://www.youtube.com/channels'
        self.start_url = 'https://www.youtube.com/results?search_query=lion'

    def header_maker(self):
        header = {'Proxy-Connection': 'keep-alive',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                  'Accept-Encoding': 'gzip, deflate, sdch',
                  'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
                  }
        return header

    def get_clean_soup(self, url):
        headers = self.header_maker()
        try:
            data = requests.get(url, headers=headers, timeout=30)
            # data = open('channels.html')
        except:
            print("[ERROR] connect:", url)
            return None

        soup = BeautifulSoup(data.content, 'lxml')
        # print soup.prettify()

        # soup = BeautifulSoup(data, 'lxml')
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

    def get_video_info(self):
        video_info_list = []
        soup = self.get_clean_soup(self.start_url)
        # page_data = urllib.urlopen(self.start_url).read()
        # soup = BeautifulSoup(page_data, 'lxml')
        # soup = BeautifulSoup(open('channels.html'), "lxml")
        if soup is None: return False

        # print soup.prettify()
        a_tags = soup.findAll('a', class_="yt-uix-tile-link")
        print 'a_tags:', len(a_tags), a_tags

        for a_tag in a_tags:
            href = a_tag.get('href')
            # print 'find:', channels_url
            # < a href = "video_id=Y3JiCOzawYg&amp;"
            # class ="yt-uix-sessionlink yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2" data-url="video_id=Y3JiCOzawYg&amp;" title="Top 10 Creepy Creatures Fisherma..."> Top 10 Creepy Creatures Fisherma...< / a >

            if '/channels/' in href:
                # print 'ok:', channels_url
                video_info_list.append(href)

        print video_info_list
        return list(set(video_info_list))

    def get_channels2(self):
        html = urllib.urlopen(self.start_url).read()
        # print html
        urlre = re.compile(r'(href=\"/channel/).+?(\")')
        channels = re.findall(urlre, html)

        print channels


##########################################################################################
def main2():
    keySearch = KeywordSearch()
    pages = 2
    keyword = 'china+beijing'
    for i in range(1, pages):
        # china+beijing&lclk=short&filters=short
        print(i)
        html = keySearch.get_html("https://www.youtube.com/results?search_query=%s&page=%s" % (keyword, i))
        keySearch.get_video_id(html)
        i += 1

    keySearch.get_download_result()


def main():
    channels = Channels()
    channels.get_video_info()


##########################################################################################
if __name__ == '__main__':
    main()
