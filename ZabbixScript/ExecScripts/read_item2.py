#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-8 14:16
# @Author  : Allen Yang
# @Site    : 
# @File    : read_item.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com
#
"""
该脚本为通过指定的ＩＰ获取其缓存数据第二版
原因，当主脚本挂掉以后，辅助脚本其实还是可以监控的，原因是因为它的缓存没有更新，
但任然可以读取缓存值所以做出一下操作
    1.缓存超时后：
        返回key:{"status":2, "value":3}
    2.程序出错后：
        key:{"status":2, "value":3}

"""
import os
import time
import pickle
import traceback


def time_diff(c_time):
    '''
    将当前时间与过期时间做对比，
    如果过期时间大于等于当前时间，这返回True，代表该数据任然有效
    如果过期时间小于当前时间，说明数据已然过期，返回False，代表数据不可用，需要重新获取数据
    :param c_time:
    :return:
    '''

    if float(c_time) + 50 >= float(time.time()):
        return True
    else:
        return False


def get_item(ip, item):
    '''
    通过制定的ＩＰ获取相应的ｉｔｅｍ并返回
    :param ip: 被监控端ＩＰ
    :param item: 监控项
    :return: 监控项详细信息已字典方式显示
    '''
    try:
        from_file_path = "/tmp/ipmi%s.pkl" % ip
        if os.path.exists(from_file_path):
            with open(from_file_path) as f:
                souce_data = pickle.loads(f.read())
            if souce_data:
                return dict(souce_data)
            else:
                return None
        return None
    except Exception as e:
        print(traceback.format_exc())


def main(ip, item_name, item_arg):
    '''
    通过给定的ＩＰ获取相应的监控项的详细信息然后从中过滤要的监控项具体信息
    ：当接受到值的时候立即打印
    ：如果没有接受到值sleep　１秒继续索取值
    :param ip:
    :param item_name:
    :param item_arg:
    :return:
    '''
    flag = 1
    while True:
        result = get_item(ip, item_name)
        if result is not None:
            # print(type(result))c_time
            if not time_diff(result['c_time']):
                data = dict()
                data['status'] = 2
                data['value'] = 3
                print(data[item_arg])
                break
            print(result['data'][item_name][item_arg])
            break
        else:
            time.sleep(1)
            flag += 1
            if flag >= 3:
                data = dict()
                data['status'] = 2
                data['value'] = 3
                print(data[item_arg])
                break


if __name__ == '__main__':
    '''
    接受三个值
    ：１：被监控端　ＩＰ
    ：２：监控项　　　如：PCH Temp
    ：３：监控项的具体项　　　例如：PCH Temp的值value或者状态：status
    用法：使用zabbix外部检查然后在键值中写如下例子
        read_item.py["192.168.70.126","PCH Temp","value" ]
    '''
    import sys
    args = sys.argv
    try:
        main(args[1], args[2], args[3])
    except Exception as e:
        # print e
        # print(traceback.format_exc())
        ipmi = dict()
        ipmi['status'] = 2
        ipmi['value'] = 3
        print(ipmi[args[3]])