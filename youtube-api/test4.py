# import urllib2
#
# img_href = 'https://i.ytimg.com/vi/xggBiWhm2m4/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=m4q0mV8INRuK5dDZErWjZknWunQ'
#
# img_id = img_href[len('https://i.ytimg.com/vi/'):len('https://i.ytimg.com/vi/') + len('aPmh2meR9vQ')]
# print img_id
#
# img_file = urllib2.urlopen(img_href)
# fd = open(img_id+'.jpg', 'wb')
# fd.write(img_file.read())
# fd.flush()
# fd.close()

import re

views_cnt = re.match(re.compile(r"(.+?)(\sview+)"), 'no view')
print views_cnt.group(1)
