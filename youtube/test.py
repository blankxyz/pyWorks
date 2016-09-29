import gdata.youtube
import gdata.youtube.service
# import psycopg2
import MySQLdb
import sys
from datetime import datetime
import time
import re

try:
    # you should read these from a config file
    # conn = MySQLdb.connect(host='localhost', database='youtube', user='root', password='root')
    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', port=3306, charset='utf8')
    conn.select_db('youtube')
    conn.autocommit = True
    cursor = conn.cursor()
except Exception, e:
    print 'Error %s' % e
    sys.exit(1)


def since_epoch(date_string):
    return int(time.mktime(datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()) * 1000)


def comments_generator(client, video_id):
    comment_feed = client.GetYouTubeVideoCommentFeed(video_id=video_id)
    while comment_feed is not None:
        for comment in comment_feed.entry:
            yield comment
        next_link = comment_feed.GetNextLink()
        if next_link is None:
            comment_feed = None
        else:
            comment_feed = client.GetYouTubeVideoCommentFeed(next_link.href)


def search_and_store_comments(client, keyword, video_id):
    query = "SELECT MAX(updated) FROM yt_comments WHERE keyword = %s AND video_id = %s"
    cursor.execute(query, (keyword, video_id))
    result = cursor.fetchone()
    if len(result) > 0:
        last_update = result[0]
    if last_update is None:
        last_update = '0'
    if last_update == '':
        last_update = '0'
    for comment in comments_generator(client, video_id):
        author_name = comment.author[0].name.text.strip()
        text = comment.content.text.strip()
        update_time = comment.updated.text.strip()
        update_time = since_epoch(update_time)
        if update_time <= int(last_update):
            break
        print (keyword, video_id, author_name, text, update_time)
        try:
            cursor.execute(
                "INSERT INTO yt_comments (keyword, video_id, author, text, updated) VALUES (%s, %s, %s, %s, %s)",
                (keyword, video_id, author_name, text, update_time))
        except Exception, e:
            print 'Error %s' % e


def search_yt(keyword):
    client = gdata.youtube.service.YouTubeService()

    vid_pat = re.compile(r'videos/(.*?)/comments')
    vid_list = []

    for start_index in range(1, 1000, 50):
        query = gdata.youtube.service.YouTubeVideoQuery()
        query.vq = keyword
        query.max_results = 50
        query.start_index = start_index
        query.orderby = 'relevance'
        print start_index,query
        feed = client.YouTubeQuery(query)

        if len(feed.entry) == 0:
            break

        for entry in feed.entry:
            if entry.comments is None:
                continue
            comment_url = entry.comments.feed_link[0].href
            result = re.findall(vid_pat, comment_url)
            if len(result) > 0:
                video_id = result[0]
            else:
                continue
            if video_id not in vid_list:
                vid_list.append(video_id)
            print video_id

        time.sleep(1)

    vid_list = list(set(vid_list))
    for vid in vid_list:
        search_and_store_comments(client, keyword, vid)


def main():
    query = "SELECT keyword FROM yt_keywords"
    cursor.execute(query)
    result = cursor.fetchall()
    for item in result:
        keyword = item[0]
        print "Searching for keyword:", keyword
        search_yt(keyword)
        time.sleep(1)


if __name__ == "__main__":
    main()
    print "done"