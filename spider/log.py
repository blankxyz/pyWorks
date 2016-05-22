#!/usr/bin/env python
#coding=utf-8

#############################################################################
# Copyright (c) 2014  - Beijing Intelligent Star, Inc.  All rights reserved


'''
文件名：setting.py
功能：爬虫多线程运行配置文件；从配置文件spider.cfg读取配置选项和值

代码历史：
2014-06-05：庞 威，创建代码
'''
import os
import sys
import logging
import logging.handlers


def get_current_file_path():
    '''
    获取当前文件所在路径
    '''
    path = os.path.dirname(os.path.abspath(sys.path[0]))
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

logger = logging.getLogger()

current_file_path = get_current_file_path()
log_path = current_file_path + "/log/"

if os.path.isdir(log_path) == False:
    os.makedirs(current_file_path +"/log/")

fp = logging.handlers.RotatingFileHandler(log_path+"debug.log", maxBytes=10*1024*1024,  mode='a', backupCount=100) 
logger.addHandler(fp)

std = logging.StreamHandler(sys.stderr)
logger.addHandler(std)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s] [%(lineno)d] - %(message)s")
fp.setFormatter(formatter)
std.setFormatter(formatter)

logger.setLevel(logging.NOTSET)
