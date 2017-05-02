from django.test import TestCase
from django.utils.cache import get_cache_key
# Create your tests here.
from django.core.urlresolvers import reverse
from django.utils.cache import get_cache_key
from django.core.cache import cache
from django.http import HttpRequest

request = HttpRequest()
# request.META = {
#     'SERVER_NAME': '173.16.0.41',
#     'SERVER_PORT ': '8000',
# }
request.META = {'SERVER_NAME': '127.0.0.1', 'SERVER_PORT ': '8000', }

import redis

spider_host = 'redis://192.168.16.223/10'

spider_con = redis.StrictRedis(host='192.168.0.110', port=6379, db=10)
result = spider_con.hgetall('time_1_2017-03-24_d5')
print(result)
