#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-6 16:52
# @Author  : Allen Yang
# @Site    : 
# @File    : IPMIScript3.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com
# @E-mail  : allenyangvip@126.com


import subprocess
import pickle
import time
import stat
import os
#


def time_diff(c_time):
    '''
    将当前时间与过期时间做对比，
    如果过期时间大于等于当前时间，这返回True，代表该数据任然有效
    如果过期时间小于当前时间，说明数据已然过期，返回False，代表数据不可用，需要重新获取数据
    :param c_time:
    :return:
    '''
    if float(c_time) >= float(time.time()):
        return True
    else:
        return False


def make_time_stemp(exp):
    '''
    创建过期时间
    exp 过期秒数（由于监控需要实时，所以过期时间不会太长所以采用秒数即可）
    :return:
    '''
    exp_datetime = float(time.time()) + int(exp)
    return exp_datetime


def set_cache(c_time, results, file_path):
    '''
    将获取到的数据按和当前时间进行序列化，并缓存
    :param c_time:
    :param token:
    :param file_path:
    :return:
    '''
    if os.path.exists(file_path):
        os.remove(file_path)
    try:
        w_data = {}
        w_data['c_time'] = c_time
        w_data['data'] = results
        with open(file_path, 'w') as f:
            f.write(pickle.dumps(w_data))
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    except Exception as e:
        print(e)
        return False
    return True


def get_cache(file_path):
    u'''
        从给定的文件路径读取需要的文件，如果存在则读取，不存在活读取中出现错误，报告错误
        :param file_path:
        :return:
    '''
    try:
        with open(file_path, 'r') as f:
            r_data = pickle.loads(f.read())
        if r_data:
            return r_data['c_time'], r_data['data']
    except Exception as e:
        return "ERROR",e


def l2d(lst):
    u'''
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
    将所有列值转换为组合值为字典
    :param lst:
    :return:
    '''
    make_dict = {}
    # if lst[0].split()[0].strip() == '0x00':
    #     make_dict['value'] = '0'
    #     make_dict['status'] = lst[1].strip()
    # elif lst[0].split()[0].strip() == 'Not':
    #     make_dict['value'] = '0'
    #     make_dict['status'] = '无法读取'
    # elif lst[0].split()[0].strip() == 'no':
    #     make_dict['value'] = '0'
    #     make_dict['status'] = '未读'
    # else:
    #     make_dict['value'] = lst[0].split()[0].strip()
    #     make_dict['status'] = lst[1].strip()
    # status 取值:
    #  0:No Reading 获取其他
    #  1:OK
    if lst[1].strip().lower() == "ok":
        make_dict['status'] = 1
        # 判断是否有数字在最后一项中则过滤数字为value
        # 否则value值为字符串其内容如果为空的话显示null
        if filter(str.isdigit, lst[-1].strip()):
            make_dict['value'] = lst[-1].strip().split()[0]
        else:
            make_dict['value'] = 0
    else:
        # 不是OK的话，其实存在两种状况，一种是没有这个设备，一种是出现问题。
        # 而出现问题现在不能判断。所以就先做不存在这个设备的问题

        make_dict['value'] = 0
        make_dict['status'] = 0
    return make_dict


def get_datas(host, user, pwd, openstion):
    '''

    :param host:
    :param user:
    :param pwd:
    :param openstion:
    :return:
    '''
    cmd_lines = "ipmitool -I lanplus -H %s -U %s -P %s %s " % (host, user, pwd, openstion)
    source_data = subprocess.Popen(cmd_lines, shell=True, stdout=subprocess.PIPE)
    clean_da = source_data.stdout.read().splitlines()
    # 存放结果
    result = {}
    for i in clean_da:
        mid_data = i.split("|")
        result[mid_data[0].strip()] = l2d(mid_data[1:])
    return result


def main(host, user, pwd, openstion, exp_time):
    '''
    通过获取用户名、密码、IP、和执行参数调用命令执行并取得数据。
    1.将获取到的数据进行缓存。默认过期时间是180秒
    2.进入函数时，先读取缓存数据，并判断是否过期，如果过期，则重新缓存。
    3.为过期直接读取数据，然后返回。
    :param host:
    :param user:
    :param pwd:
    :param openstion:
    :return:
    '''
    file_path = "/tmp/ipmi%s.pkl" % host
    if os.path.exists(file_path):
        c_time, t_data = get_cache(file_path)
        if c_time != 'ERROR':
            if not time_diff(c_time):
                exp_time = make_time_stemp(exp_time)
                data = get_datas(host, user, pwd, openstion)
                set_cache(exp_time, data, file_path)

            else:
                return dict(t_data)
    else:
        exp_time = make_time_stemp(exp_time)
        data = get_datas(host, user, pwd, openstion)
        set_cache(exp_time, data, file_path)
    return dict(data)


if __name__ == '__main__':
    '''
    本脚本接受用户提供的参数：
    ： 参数1：host -- 需要监控的IP
    ： 参数2：user -- 登录被监控端的用户名
    ： 参数3：pwd  -- 登录被监控端的密码
    ： 参数4：name -- 监控数据的监控项
    ： 参数5：arg  -- 监控项的列名(例如：name='Avg Power' arg= 'value' 即获取监控项为Avg Power的值)
    实例：
        check_item.py["192.168.70.126","USERID","PASSW0RD","Avg Power","status" ]（本实例为Zabbix监控中外部检查的键值）
    '''
    import sys
    args = sys.argv
    try:
        # host = '192.168.5.80'
        host = args[1]
        # user = 'USERID'
        user = args[2]
        # pwd = 'PASSW0RD'
        pwd = args[3]
        name = args[4]
        arg = args[5]
        openstion = 'sdr elist'
        ipmi = main(host, user, pwd, openstion,100)
        print(ipmi)
        # print(ipmi[name][arg])

    except Exception as e:
        print(e)
        print('err')

