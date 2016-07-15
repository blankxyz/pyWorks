import re

detail_manual_regexs = [u'/[a-zA-Z]{1}/[a-zA-Z]{7}/d{4}/d{4}/d{3}.html', u'/[a-zA-Z]{1}/[a-zA-Z]{13}/[a-zA-Z]{12}/d{4}/d{4}/d{3}.html']
list_manual_regexs = [u'/$', u'*list*']

r1 = re.search(r'[a-zA-Z]{1}/[a-zA-Z]{7}/d{4}/d{4}/d{3}','/a/keyanchengguo/keyanxiangmu/2013/0414/109.html')
print r1

r2 = re.search(r'[a-zA-Z]{1}\/[a-zA-Z]{13}\/[a-zA-Z]{12}\d{4}\d{4}\d{3}','/a/keyanchengguo/keyanxiangmu/2013/0414/109.html')
print r2

r3 = re.search(r'/$', '/a/keyanchengguo/keyanxiangmu/2013/0414/109.html')
print r3

r4 = re.search(r'list', '/a/keyanchengguo/keyanxiangmu/2013/0414/109.html')
print r4