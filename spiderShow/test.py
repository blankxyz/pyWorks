#!/usr/bin/env python
# coding=utf-8
import re,os
from multiprocessing import Process
import subprocess


# # run
# def run_spider():
#     os.chdir("D:\workspace\pyWorks\spider")
#     execfile("syq_url_rule_manual.py")
#     # time.sleep(times)
#     # print time.localtime()
#
# def start_spider(func):
#     p = Process(target=func)
#     p.start()
#     p.join()

if __name__ == '__main__':
    # start_spider(run_spider)
    subprocess.call(["run_spider.bat"], shell=True)
