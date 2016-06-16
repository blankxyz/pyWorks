#encoding=utf-8

import cStringIO, urllib2, Image

url = 'http://n.sinaimg.cn/tech/crawl/20160616/atKC-fxtfrrf0440265.jpg'

file = urllib2.urlopen(url, timeout=30)

tmpIm = cStringIO.StringIO(file.read())

im = Image.open(tmpIm)

print im.format, im.size, im.mode

