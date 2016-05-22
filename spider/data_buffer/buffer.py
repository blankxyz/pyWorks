# Embedded file name: /work/build/source/athena/utils/data_buffer/buffer.py
import redis
from urllib2 import urlparse
import cPickle as pickle
import ujson

class Buffer:

    def __init__(self, uri):
        self.uri = uri

    def push(self, data):
        pass

    def pop(self):
        return None

    def pushall(self, data_list):
        pass


class RedisBuffer(Buffer):

    def __init__(self, uri):
        self.host = uri.hostname
        self.port = uri.port or 6379
        self.db, self.key_name = filter(lambda x: x != '', uri.path.split('/'))[:2]
        self.conn = redis.Redis(host=self.host, port=self.port, db=self.db)

    def push(self, data, dest_json = False):
        if dest_json:
            push_data = ujson.dumps(data)
        else:
            push_data = pickle.dumps(data)
        self.conn.lpush(self.key_name, push_data)

    def pushall(self, data_list, dest_json = False):
        pipe = self.conn.pipeline()
        for data in data_list:
            if dest_json:
                dest_data = ujson.dumps(data)
            else:
                dest_data = pickle.dumps(data)
            pipe.lpush(self.key_name, dest_data)

        pipe.execute()

    def pop(self, src_json = False):
        src_data = self.conn.rpop(self.key_name)
        if src_json:
            if src_data is None:
                return
            return ujson.loads(src_data)
        elif src_data is None:
            return
        else:
            return pickle.loads(src_data)
            return


class BufferFactory:

    def create(self, url):
        uri = urlparse.urlparse(url)
        if uri.scheme not in ('redis', 'mysql', 'mongodb'):
            raise Exception, '\xe7\xb1\xbb\xe5\x9e\x8b\xe5\xbc\x82\xe5\xb8\xb8\xef\xbc\x8c \xe5\xbf\x85\xe9\xa1\xbb\xe6\x98\xafredis, mysql\xe6\x88\x96\xe8\x80\x85mongodb'
        if uri.scheme == 'redis':
            return RedisBuffer(uri)


if __name__ == '__main__':
    data_buffer = BufferFactory().create('redis://192.168.2.122/0/test')
    print data_buffer.pop()