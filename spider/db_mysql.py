#encoding=utf-8
'''
用于MySQL数据库相关的一些方法
   
创建时间：2013-10-24，作者：贺伟刚
'''

import db
import MySQLdb
import datetime

class MySQLOpt(db.DbOpt):
    
    connection_list = {}
    
    def __init__(self, setting_dict):
        
        db.DbOpt.__init__(self, setting_dict)
        
        self.key = repr(setting_dict)
        if self.key not in MySQLOpt.connection_list.keys():
            self.conn, self.cursor = self.GetCursor()
            MySQLOpt.connection_list[self.key] = (self.conn, self.cursor)
        else:
            self.conn, self.cursor = MySQLOpt.connection_list[self.key]
        
        self.sql = {}
        self.clear()
        
    def clear(self):
        '''
        清空where和tables等设置，以便于下次执行sql后重新生成
        '''        
        self.sql["where"] = ""
        self.sql["tables"] = ""
        self.sql["fields"] = ""
        self.sql["limit"] = (0, 0)
        self.sql["order"] = {}

    def GetCursor(self):
        '''
        mysql获取cursor
        '''
        db_user = self.setting_dict["username"]
        db_passwd = self.setting_dict["password"] 
        db_host = self.setting_dict["host"]
        db_port = self.setting_dict["port"]
        if db_port is None:
            db_port =3306
        db_default = self.setting_dict["db"]
        
        try:
            conn = MySQLdb.connect(host=db_host,
                                   user=db_user,
                                   passwd=db_passwd,
                                   db=db_default)
            conn.autocommit(True)
            conn.query("set names 'utf8'")
    
        except MySQLdb.MySQLError, e:
            raise Exception("Mysql 数据库连接错误：%s, %s"%(e, self.setting_dict))
            return None,None
    
        return conn, conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def where(self, condition):
        self.sql["where"] = condition
        return self
    
    def get_where(self):
        if self.sql["where"] == "":
            return ""
        else:
            return " where " + self.sql["where"]
     
    def table(self, table_str):
        self.sql["tables"] = table_str
        return self
           
    def delete(self):
        if self.sql["tables"] =="":
            self.clear()
            raise Exception("缺少table名称")
        
        self.cursor.execute("delete from " +self.sql["tables"] +  self.get_where())
        self.clear()
    
    def add(self, data_dicts):
        if self.sql["tables"] =="":
            raise Exception("缺少table名称")
        
        import types
        if type(data_dicts) is types.DictType:
            #只有一行数据
            tmp = data_dicts
            data_dicts = []
            data_dicts.append(tmp)
        else:
            if type(data_dicts) is not types.ListType:
                self.clear()
                raise Exception("输入变量必须为字典或者字典列表")
        
        row_count = len(data_dicts)
        if row_count == 0:
            self.clear()
            raise Exception("数据为空")
        
        keys = data_dicts[0].keys()
        
        column_count = len(keys)
        if column_count  == 0:
            self.clear()
            raise Exception("数据为空")
        
        #字段名称
        sql = "insert ignore into %s (%s) "%(self.sql["tables"],  ','.join(keys))
        
        #数据
        all_row_list = []
        for row_dict in data_dicts:
            row_list = []
            for value in row_dict.values():
                if  type(value) == type("some"):
                    #字符串
                    row_list.append('\'%s\''%value)
                elif type(value) == type(None):
                    #空
                    row_list.append('null')
                elif type(value) == type(datetime.datetime.now()):
                    #时间
                    row_list.append('\'%s\''%value)
                elif type(value) == type(datetime.date.today()):
                    #日期
                    row_list.append('\'%s\''%value)
                else:
                    #整数和浮点等
                    row_list.append(str(value))
            
            one_row_data =  " ( " + ','.join(row_list) + ")"

            all_row_list.append(one_row_data)
            
        sql += " values" +  ','.join(all_row_list)

        self.cursor.execute(sql)
        self.clear()
        
    def update(self, data_dict):
        if self.sql["tables"] =="":
            self.clear()
            raise Exception("缺少table名称")
        
        update_data_list = []
        for key, value in data_dict.items():
            if  type(value) == type("some"):
                #字符串
                update_data_list.append('%s=\'%s\''%(key, value))
            elif type(value) == type(None):
                #空
                update_data_list.append('%s=null'%key)
            elif type(value) == type(datetime.datetime.now()):
                #时间
                update_data_list.append('%s=\'%s\''%(key, value))
            elif type(value) == type(datetime.date.today()):
                #日期
                update_data_list.append('%s=\'%s\''%(key,value))
            else:
                #整数和浮点等
                update_data_list.append('%s=%s'%(key, str(value)))
            
        sql = "update %s set "%self.sql["tables"] + ",".join(update_data_list) + self.get_where()
        self.cursor.execute(sql)
        self.clear()
    
    def fields(self, fields_str):
        self.sql["fields"] = fields_str
        return self
            
    def find(self):
        '''
        返回结果字典列表
        '''
        if self.sql["tables"] =="":
            self.clear()
            raise Exception("缺少table名称")
        
        sql = "select "
        if self.sql["fields"] == "":
            sql += "* "
        else:
            sql += self.sql["fields"]
        
        sql += " from "+self.sql["tables"] + self.get_where() + self.get_order()+ self.get_limit()
         
        self.cursor.execute(sql)
        self.clear()
        return self.cursor.fetchall()
        
         
    def limit(self, count, start=0):
        self.sql["limit"] = (count, start)
        
        return self
    
    def get_limit(self):
        count, start =  self.sql["limit"]
        if count<=0:
            return ""
        return " limit %d, %d "%(start, count)
    
    def count(self):
        if self.sql["tables"] =="":
            self.clear()
            raise Exception("缺少table名称")
        
        sql = "select "
        sql += " count(*)  "

        
        sql += " from "+self.sql["tables"] + self.get_where() + self.get_limit()
         
        self.cursor.execute(sql)
        self.clear()
        
        return self.cursor.fetchone()["count(*)"]
    
    def order(self, order_dict):
        self.sql["order"] = order_dict
        return self
    
    def get_order(self):
        if self.sql["order"]:
            #有数据
            order_list = []
            for key, value in self.sql["order"].items():
                order = " asc"
                if value<0:
                    order = " desc"
                order_item = key + order
                order_list.append(order_item)
            return " order by " + ",".join(order_list) + " "
        else:
            return ""
        
    def close(self):
        self.cursor.close()
        self.conn.close()
        
