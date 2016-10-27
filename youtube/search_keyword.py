# coding:utf-8

import re
import urllib
import redis
import subprocess
import youtube_dl

REDIS_SERVER = 'redis://127.0.0.1/13'


##################################################################################################
class RedisDrive(object):
    def __init__(self):
        self.site_domain = 'youtube.com'
        self.conn = redis.StrictRedis.from_url(REDIS_SERVER)
        self.keyword_zset_key = 'keyword_zset_%s' % self.site_domain  # 状态管理
        self.json_hset_key = 'json_hset_%s' % self.site_domain  # --print-json 结果保存
        self.result_hset_key = 'result_hset_%s' % self.site_domain  # 最终结果保存
        self.todo_flg = -1
        self.videoId_flg = 0
        self.getJson_flg = 1

    def add_video_id(self, video_id):
        return self.conn.zadd(self.keyword_zset_key, self.todo_flg, video_id)

    def get_todo_videos(self):
        return self.conn.zrangebyscore(self.keyword_zset_key, self.todo_flg, self.todo_flg, withscores=False)


class KeywordSearch(object):
    def getHtml(self, url):
        page = urllib.urlopen(url)
        html = page.read()
        return html

    def getVideoId(self, html):
        reg = r"(?<=a\shref=\"/watch\?v\=).+?(?=\")"
        # reg = r"(?<=a\shref=\"/watch).+?(?=\")"
        urlre = re.compile(reg)
        urllist = re.findall(urlre, html)
        redis_db = RedisDrive()
        # format = "https://www.youtube.com/watch%s\n"
        # f = open("search_keyword.log", 'a')
        for url in urllist:
            redis_db.add_video_id(url)
            # result = (format % url)
            # f.write(result)
            # f.close()

    def getJsonInfo(self):
        redis_db = RedisDrive()
        video_id_list = redis_db.get_todo_videos()
        for video_id in video_id_list:
            subprocess.Popen("youtube-dl", )
            # p = subprocess.Popen(['/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
            # server_log_list = p.stdout.readlines()


##########################################################################################
def main():
    keySearch = KeywordSearch()
    pages = 2
    for i in range(1, pages):
        # china+beijing&lclk=short&filters=short
        print(i)
        html = keySearch.getHtml("https://www.youtube.com/results?search_query=china+beijing&page=%s" % i)
        keySearch.getVideoId(html)
        i += 1


##########################################################################################
if __name__ == '__main__':
    # main()
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
    ydl_opts = {
        'audioformat': 'mp3',
        'outtmpl': '%(id)s',  # name the file the ID of the video
        'noplaylist': True,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    info_file = 'search_keyword.log'
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download_with_info_file(video_id, info_file)
