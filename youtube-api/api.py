import youtube_dl

ydl = youtube_dl.YoutubeDL({})

with ydl:
    result = ydl.extract_info(
        'http://www.youtube.com/watch?v=QOFGyoiBeEw',
        download=False  # We just want to extract the info
    )

if 'entries' in result:
    # Can be a playlist or a list of videos
    video_info = result['entries'][0]
else:
    # Just a video
    video_info = result

print video_info
print 'title:', video_info['title']
print 'creator:', video_info['creator']
print 'view_count:', video_info['view_count']
print 'like_count:', video_info['like_count']
print 'dislike_count:', video_info['dislike_count']
print 'categories:', video_info['categories']
print 'description:', video_info['description']
print 'uploader:', video_info['uploader']
