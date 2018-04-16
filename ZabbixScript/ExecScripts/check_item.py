#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-4-13 下午4:18
# @Author  : Allen Yang
# @Site    : 
# @File    : check_item.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com

import subprocess


def l2d(lst):
    '''
    sensor名称
    读取值
    单位
    阈值状态
    Lower Non-Recoverable
    Lower Critical
    Lower Non-Critical
    Upper Non-Critical
    Upper Critical
    Upper Non-Recoverable
    :param lst:
    :return:
    '''
    make_dict = {}
    title_list = ['value', 'unit', 'status', 'LNR', 'LC', 'LNC', 'UNC', 'UC', 'UNR']
    for i in xrange(len(title_list)):
        make_dict[title_list[i]]= lst[i].strip()
    return make_dict


def main(host, user, pwd, openstion):
    cmd_lines = "ipmitool -I lanplus -H %s -U %s -P %s %s " % (host, user, pwd, openstion)
    source_data = subprocess.Popen(cmd_lines, shell=True, stdout=subprocess.PIPE)
    clean_da = source_data.stdout.read().splitlines()
    # 存放结果
    result = {}

    for i in clean_da:
        # print "======================"
        mid_data = i.split("|")
        result[mid_data[0].strip()] = l2d(mid_data[1:])
        # print()
        # print "----------------------"
    return result


if __name__ == '__main__':
    import sys
    args = sys.argv

    # host = '192.168.5.80'
    host = args[1]
    # user = 'USERID'
    user = args[2]
    # pwd = 'PASSW0RD'
    pwd = args[3]
    name = args[4]
    arg = args[5]
    openstion = 'sensor list'
    data = main(host, user, pwd, openstion)
    print(data.keys())
    print(data[name][arg])