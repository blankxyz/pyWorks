#!/usr/bin/env python
# coding=utf-8
from bs4 import BeautifulSoup, Comment
import requests
import re,os
import urlparse
from multiprocessing import Process

# run
def run_spider():
    os.chdir("D:\workspace\pyWorks\spider")
    execfile("syq_url_rule_manual.py")
    # time.sleep(times)
    # print time.localtime()

def start_spider(func):
    p = Process(target=func)
    p.start()
    p.join()

if __name__ == '__main__':
    # start_spider(run_spider)
    import subprocess
    subprocess.call(["run_spider.bat"], shell=True)
