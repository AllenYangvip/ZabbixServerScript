#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-11 10:00
# @Author  : Allen Yang
# @Site    : 
# @File    : IPMIScript6.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com
# @E-mail  : allenyangvip@126.com


import subprocess
import pickle
import time
import stat
import os
import re

#
"""
这已经是第五个版本了：
    更新第五个版本的原因：
        1.出现服务器掉电后我们的设备链接不上！网络不可达！
        2.网络线路问题，导致网络不可达！
    根据这两个问题出现的监控项获取超时现象是不允许有的。
    所以我定制除了一个方案：
        即在获取服务超时后，我们反馈给服务器的监控项为：
        key:{"status":2, "value":3}以此来判定网络不可达！
    监控项数据点：
        key: {"status":num, "value":num}
        status取值：
            0===> ns    即无状态
            1===> ok    即状态正常
            2===> null  即网络不可达
        value取值：
            有数字：
                该数字===> 正常情况：  
                3===> 网络不可达
            无数字：
                0===>No Reading、Device Absent或者为空/Unknown Progress
                1===>
                2===>Drive Present, In Failed Array或 err   出错
                3===> 网络不可达

"""


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
        return "ERROR", e


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
    value值：
        含数字
        不含数字：
            不存在的：
                No Reading
                Device Absent    status值为：OK
            存在的：
                Present
                Connected
                Drive Present
                Presence Detected
                Transition to OK
                Limit Not Exceeded
                Fully Redundant

            存在，错误的：
                Drive Present, In Failed Array
            可更换设备：
                Logical FRU xxxx
    status 值：
        OK：正常的
        ns：未知或不存在    value值：No Reading

    设置：
        设备状态---status值：
            ok   ===>   1
            ns   ===>   0
        设备返回值：--- value值
            1.有数字，返回数字
            2.没数字：
                包含：
                Present、Connected、Drive Present、Presence Detected
                Transition to OK、Limit Not Exceeded、Fully Redundant的返回1
                包含：No Reading、Device Absent或者为空/Unknown Progress===>0
                包含：Drive Present, In Failed Array  /  Disabled ===> 2
                包含：Power off/down  关机状态   ===> "Power off/down"
    :param lst:
    :return:
    '''
    make_dict = dict()
    if lst[1].strip().lower() == "ok":
        make_dict['status'] = 1
    else:
        make_dict['status'] = 0

    # 判断value值
    if re.findall(r"^\d+.*", lst[-1].strip()):
        make_dict['value'] = lst[-1].strip().split()[0]
    else:
        #     包含：No Reading、Device Absent或者为空===>0
        if "no reading" in lst[-1].strip().lower() or "absent" in lst[-1].strip().lower() \
                or lst[-1].strip().lower() == "" or "unknown" in lst[-1].strip().lower() or "disabled" in lst[-1].strip().lower():
            make_dict['value'] = 0
        elif "failed" in lst[-1].strip().lower() or "err" in lst[-1].strip().lower():
            make_dict['value'] = 2
        else:
            if make_dict['status'] == 1:
                make_dict['value'] = 1
            else:
                make_dict['value'] = 0
    return make_dict


def get_datas(host, user, pwd, openstion, time_out=10):
    '''

    :param host:
    :param user:
    :param pwd:
    :param openstion:
    :return:
    '''
    start_time = time.time()
    cmd_lines = "ipmitool -I lanplus -H %s -U %s -P %s %s " % (host, user, pwd, openstion)
    source_data = subprocess.Popen(cmd_lines, shell=True, stdout=subprocess.PIPE, close_fds=True)
    while True:
        if source_data.poll() is not None:
            break
        seconds_passed = time.time() - start_time
        if time_out and seconds_passed > time_out:
            source_data.terminate()
            return {}
        time.sleep(0.1)

    if source_data == "Error: Unable to establish IPMI v2 / RMCP+ session":
        return {}
    clean_da = source_data.stdout.read().splitlines()
    # 存放结果
    result = {}
    for i in clean_da:
        mid_data = i.split("|")
        if result.has_key(mid_data[0].strip()):
            # print("重复：%s"%mid_data[0].strip())
            # 防止出现重复值
            continue
        result[mid_data[0].strip()] = l2d(mid_data[1:])
    # if time.time() - start_time > 30
    # # source_data.kill
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
                data = get_datas(host, user, pwd, openstion, 15)
                if data:
                    exp_time = make_time_stemp(exp_time)
                    set_cache(exp_time, data, file_path)
            else:
                return dict(t_data)
    else:
        data = get_datas(host, user, pwd, openstion, 15)
        if data:
            exp_time = make_time_stemp(exp_time)
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
        time_out = 45
        # host = '192.168.5.80'
        host = args[1]
        # user = 'USERID'
        user = args[2]
        # pwd = 'PASSW0RD'
        pwd = args[3]
        name = args[4]
        arg = args[5]
        openstion = 'sdr elist all'
        ipmi = main(host, user, pwd, openstion, time_out)
        # print(ipmi)
        print(ipmi[name][arg])

    except Exception as e:
        # print(e)
        # print('err')
        # key:{"status":2, "value":111111}以此来判定网络不可达！
        ipmi = dict()
        ipmi['status'] = 2
        ipmi['value'] = 3
        print(ipmi[arg])

