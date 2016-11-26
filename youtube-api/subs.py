import opml
import feedparser
import youtube_dl
from glob import glob
from pprint import pprint

from time import time, mktime, strptime
from datetime import datetime

if len(glob('last.txt')) == 0:
    f = open('last.txt', 'w')
    f.write(str(time()))
    print('Initialized a last.txt file with current timestamp.')
    f.close()

else:
    f = open('last.txt', 'r')
    content = f.read()
    f.close()
    #  https://www.youtube.com/subscription_manager?action_takeout=1
    outline = opml.parse('subscription_manager.xml')
    ptime = datetime.utcfromtimestamp(float(content))
    ftime = time()

    urls = []

    for i in range(0, len(outline[0])):
        urls.append(outline[0][i].xmlUrl)
    print(urls)

    videos = []
    for i in range(0, len(urls)):
        # print('Parsing through channel ' + str(i + 1) + ' out of ' + str(len(urls)), end='\\r')
        feed = feedparser.parse(urls[i])
        print(feed) # URLError(error(10060, '')
        for j in range(0, len(feed['items'])):
            timef = feed['items'][j]['published_parsed']
            dt = datetime.fromtimestamp(mktime(timef))
            # if dt > ptime:
            print(timef)
            videos.append(feed['items'][j]['link'])

    if len(videos) == 0:
        print('Sorry, no new video found')
    else:
        print(str(len(videos)) + ' new videos found')
        print(videos)

    ydl_opts = {}
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

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videos)

    f = open('last.txt', 'w')
    f.write(str(ftime))
    f.close()
