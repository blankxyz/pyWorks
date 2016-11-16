#!/usr/bin/env python
# -*- coding:utf-8 -*-
from  multiprocessing import Process, Pool
import time


def Foo(i):
    # time.sleep(1)
    print i


if __name__ == '__main__':
    t_start=time.time()
    pool = Pool(5)

    for i in range(10):
        pool.apply(Foo, (i,))

    pool.close()
    pool.join()  # 进程池中进程执行完毕后再关闭，如果注释，那么程序直接关闭。
    t_end=time.time()
    t=t_end-t_start
    print 'the program time is :%s' %t