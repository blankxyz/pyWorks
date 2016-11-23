import datetime
import re
import redis

k = '12404766082711236659'

REDIS_SERVER = 'redis://127.0.0.1/10'

conn = redis.StrictRedis.from_url('redis://127.0.0.1/10')

weixin_info_hset_patch_key = 'weixin_info_hset_patch_key'

v = conn.hget(weixin_info_hset_patch_key, k)

print v

print u'\u671d\u9633'
