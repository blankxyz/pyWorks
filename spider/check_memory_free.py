#!/usr/bin/python
#coding:utf8
import time
import os

mem_stat = {}
def memory_stat():
    content = ''
    with open("/proc/meminfo") as f:
        content = f.readlines()
    for line in content:
        item = line.split()
        mem_stat[item[0].strip(':')] = item[1]

def get_mem_free():
    memory_stat()
    return int(mem_stat.get('MemFree', 1000000))

print get_mem_free()

def record():
    with open("/work/log/restart.txt","w") as f:
        f.write("%s"%time.strftime("%Y-%m-%d %H:%M:%S"))

def restart_test():
    mem_free = get_mem_free()
    if mem_free < 300000:
        os.system("python /work/spider/run.pyc --stop")
        time.sleep(100)
        os.system("killall screen")
        time.sleep(5)
        #os.system("screen python /work/spider/run.pyc --start")
        os.system("screen python /work/spider/start.py")
        print u"重启结束"
    record()

def restart():
    mem_free = get_mem_free()
    if mem_free < 300000:
        os.system("python /work/spider/run.pyc --stop")
        time.sleep(120)
        os.system("python /work/spider/run.pyc --stop")
        time.sleep(5)
        #os.system("screen python /work/spider/run.pyc --start")
        os.system("python /work/spider/run.pyc --start")
        print u"重启结束"
    record()

restart()
