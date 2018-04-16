#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-4-16 上午10:21
# @Author  : Allen Yang
# @Site    : 
# @File    : test.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com
import threading
import Queue
from IPMIScript import main as test

TEST_MQ = Queue.Queue


def put_msg(msg):
    TEST_MQ.put(msg)

if __name__ == '__main__':

    for i in xrange(50):
        t = threading.Thread(target=test, args=("192.168.5.80", "USERID", "PASSW0RD", "CPU1 VR Temp", "value"))

        t.start()
        print('开始第%s个线程。。。。。。。' %i)

    for i in xrange(50):
        t.join()


    # while TEST_MQ.qsize() > 0:
    #     print(TEST_MQ.get())

