import redis

r = redis.Redis(host='localhost',port=6379,db=0)
r.set('guo','shuai')
r.get('guo')
r.keys()
print r.dbsize()
r.delete('guo')
r.save()
r.get('guo')
r.flushdb()