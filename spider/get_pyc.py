#coding:utf8
import py_compile
import compileall
import os

f_list = [u'/argsparser.py', u'/db.py', u'/db_mysql.py', u'/downloader.py', u'/htmlparser.py', u'/log.py', u'/proxy.py', u'/run.py', u'/setting.py', u'/spider.py', u'/spiderById.py', u'/spiderDefault.py', u'/spiderTopic.py', u'/util.py', u'/data_buffer/buffer.py', u'/data_buffer/test.py', u'/data_buffer/__init__.py', u'/db/db.py', u'/db/db_mysql.py', u'/db/__init__.py', u'/dedup/clean_dedup.py', u'/dedup/core.py', u'/dedup/dedup.py', u'/dedup/util.py', u'/dedup/__init__.py', u'/dedup/online/clean_dedup.py', u'/dedup/online/log.py', u'/myreadability/cleaners.py', u'/myreadability/encoding.py', u'/myreadability/find_date.py', u'/myreadability/htmlparser.py', u'/myreadability/myreadability.py', u'/myreadability/test.py', u'/myreadability/__init__.py']
f_list += [u'/find_date.py']

def compile_file():
    #compileall.compile_dir("/work/spider", force=1)
    for f in f_list:
        f = u'/work/spider' + f
        if os.path.exists(f):
            py_compile.compile(f)
    return


def delete_py():
    for root, dirs, files in os.walk('/work/spider'):
        for file_name in files:
            abs_file = os.path.join(root, file_name)
            if file_name.endswith('.py'):
                if abs_file.replace("/work/spider", "") in f_list:
                    os.remove(abs_file)
    return

def delete_pyc():
    for root, dirs, files in os.walk('/work/spider'):
        for file_name in files:
            abs_file = os.path.join(root, file_name)
            if file_name.endswith('.pyc'):
                if abs_file.replace("/work/spider", "").replace(".pyc", ".py") in f_list:
                    continue
                os.remove(abs_file)
    return

def get_all_files():
    f_list = []
    for root, dirs, files in os.walk(u'E:\FPAN\配置模版变更监测\spider'):
        for file_name in files:
            abs_file = os.path.join(root, file_name)
            if file_name.endswith('.py'):
                f_list.append(abs_file.replace(u"E:\FPAN\配置模版变更监测\spider", ""
                                               ).replace("\\", "/"
                                                   ))
    return f_list


if __name__ == "__main__":
    #delete_pyc()
    compile_file()
    delete_py()
    #print get_all_files()
            


