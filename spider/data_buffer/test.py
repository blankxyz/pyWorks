# Embedded file name: /work/build/source/athena/utils/data_buffer/test.py
import data_buffer
result = data_buffer.create('redis://192.168.110.140/3/data_test')
data = result.pop()
print data
print data['url']
print data['title']
print data['ctime']
print data['gtime']
print data['siteName']
print data['content']