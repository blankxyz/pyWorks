# Embedded file name: /work/build/source/athena/utils/db/db.py
"""
\xe7\x94\xa8\xe4\xba\x8e\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe7\x9b\xb8\xe5\x85\xb3\xe7\x9a\x84\xe4\xb8\x80\xe4\xba\x9b\xe6\x96\xb9\xe6\xb3\x95
delete
update
find
\xe6\x94\xaf\xe6\x8c\x81\xe8\xbf\x9e\xe8\xb4\xaf\xe6\x93\x8d\xe4\xbd\x9c
    
\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4\xef\xbc\x9a2013-10-24\xef\xbc\x8c\xe4\xbd\x9c\xe8\x80\x85\xef\xbc\x9a\xe8\xb4\xba\xe4\xbc\x9f\xe5\x88\x9a

"""
import ConfigParser
import os
import urlparse
from abc import ABCMeta, abstractmethod

def get_current_path():
    return os.path.dirname(__file__)


class DbOpt:
    """\xe6\x8a\xbd\xe8\xb1\xa1\xe6\xa1\x86\xe6\x9e\xb6"""
    __metaclass__ = ABCMeta

    def __init__(self, setting_dict):
        self.setting_dict = setting_dict

    @abstractmethod
    def delete(self):
        return self

    @abstractmethod
    def where(self, condition):
        return self

    @abstractmethod
    def table(self, table_str):
        return self

    @abstractmethod
    def add(self, data_dicts):
        pass

    @abstractmethod
    def update(self, data_dict):
        pass

    @abstractmethod
    def find(self):
        pass

    @abstractmethod
    def limit(self, count, start = 0):
        pass

    @abstractmethod
    def count(self):
        pass

    @abstractmethod
    def order(self, order_dict):
        pass

    @abstractmethod
    def close(self):
        pass


class DB:
    """
    \xe5\xbd\x93\xe4\xbe\x8b\xe8\xbf\x9e\xe6\x8e\xa5\xe7\x9a\x84\xe6\x96\xb9\xe6\xb3\x95\xef\xbc\x8c\xe6\x94\xaf\xe6\x8c\x81mysql\xe5\x92\x8cmongo\xe7\xad\x89\xef\xbc\x8c\xe6\x97\xa0\xe9\x9c\x80\xe7\x94\xa8sql\xe6\x88\x96\xe8\x80\x85js\xef\xbc\x8c\xe7\x9b\xb4\xe6\x8e\xa5CRUD\xe6\x93\x8d\xe4\xbd\x9c
    """

    def __init__(self):
        pass

    def create(self, conn_str):
        if conn_str is None:
            raise Exception('\xe5\x8f\x82\xe6\x95\xb0\xe4\xb8\xba\xe7\xa9\xba')
        self.conn_str = conn_str
        import re
        if re.match('(\\w+://)', conn_str) is None:
            cfg = ConfigParser.ConfigParser()
            try:
                cfg.read(get_current_path() + '/db.conf')
                self.conn_str = cfg.get('connections', conn_str)
            except:
                raise Exception('\xe9\x85\x8d\xe7\xbd\xae\xe6\x96\x87\xe4\xbb\xb6db.conf\xe4\xb8\xad\xe6\xb2\xa1\xe6\x9c\x89\xe7\x9b\xb8\xe5\xba\x94\xe9\xa1\xb9\xef\xbc\x8c\xe6\x88\x96\xe8\x80\x85\xe9\x94\x99\xe8\xaf\xaf')

        db_setting_uri = urlparse.urlparse(self.conn_str)
        setting_dict = {}
        setting_dict['type'] = db_setting_uri.scheme
        setting_dict['host'] = db_setting_uri.hostname
        setting_dict['port'] = db_setting_uri.port
        setting_dict['username'] = db_setting_uri.username
        setting_dict['password'] = db_setting_uri.password
        setting_dict['db'] = db_setting_uri.path.strip('/')
        setting_dict['params'] = db_setting_uri.query
        if setting_dict['type'] == 'mysql':
            import db_mysql
            self.db_opt = db_mysql.MySQLOpt(setting_dict)
        elif setting_dict['type'] == 'mongo':
            import db_mongo
            self.db_opt = db_mongo.MongoOpt(db_setting_uri)
        else:
            raise Exception('\xe6\x9c\xaa\xe7\x9f\xa5\xe7\x9a\x84\xe5\x8d\x8f\xe8\xae\xae\xef\xbc\x9a%s' % setting_dict['type'])
        return self.db_opt


if __name__ == '__main__':
    db = DB().create('local')
    result = db.table('users').where('id>50').fields('id,username').order({'id': 1}).find()
    print result
    db.close()