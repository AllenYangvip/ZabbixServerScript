#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 
# @Author  : Allen Yang
# @Site    : 
# @File    : check_item.py
# @Software: PyCharm
# @E-mail  : yangjh@szkingdom.com

import ConfigParser
import datetime
import urllib2
import json
import stat
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

"""

"""


def get_token(corpid, corpsecret):
    '''
    获取token函数
    通过用户提供的corpid, corpsecret获取其token反馈给调用者
    :param corpid:
    :param corpsecret:
    :return:
    '''
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + corpid + "&corpsecret=" + corpsecret
    html = json.loads(urllib2.urlopen(url).read().decode())
    token = html["access_token"]
    return token


def send_msg(token, touser, toparty, agentid, msg, safe=0, totag=" @all", msgtype='text'):
    '''
    微信报警，返送数据函数。
    :param token:   微信token
    :param touser:  通过微信接口发送信息的接受用户
    :param toparty: 发送消息接收范围（部门）
    :param agentid: 授权方应用id
    :param msg:     发送的消息
    :param safe:
    :param totag:   标签名
    :param msgtype: 消息类型
    :return:
    '''
    countent_url = " https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + token
    data = {
        "touser": touser,
        "toparty": toparty,
        "totag": totag,
        "msgtype": msgtype,
        "agentid": agentid,
        "text": {
            "content": msg
        },
        "safe": safe
    }
    send_data = json.dumps(data, ensure_ascii=False).encode()
    r = urllib2.urlopen(countent_url, data=send_data)


def get_cache(file_path):
    '''
    根据用户提供的缓存文件路径，获取具体缓存内容，
    即时反馈给用户。
    :param file_path:    保存文件缓存的路径
    :return:    正确时：返回缓存时间戳，和缓存token   错误时：返回 “ERROR” 和错误信息
    '''
    try:
        conf = ConfigParser.ConfigParser()
        conf.read(cf_path)
        cache_time = conf.get('WeChatCache', 'cache_time')
        cache_token = conf.get('WeChatCache', 'cache_token')
        return cache_time,cache_token
    except Exception as e:
        return "ERROR",e


def set_cache(c_time, token, file_path):
    '''
    通过用户传递过来的参数进行缓存，
    本缓存采用文件形式缓存数据。节省内存空间，且数据持久化，得到有效的保证
    ： 通过用户传递的时间戳、token、文件存放路径，来进行python的文件缓存
    :param c_time:   到期缓存时间戳
    :param token:    微信token
    :param file_path:  缓存路径
    :return:
    '''
    if os.path.exists(file_path):
        os.remove(file_path)
    try:
        conf = ConfigParser.ConfigParser()
        conf.add_section("WeChatCache")
        conf.set("WeChatCache", "cache_time", c_time)
        conf.set("WeChatCache", "cache_token", token)
        conf.write(open(file_path,'w'))
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    except Exception as e:
        return e
    return True


def time_diff(c_time):
    '''
    对比时间函数
    ： 将传递过来的时间戳，转换为具体时间，与当前时间进行对比
    ： 如果时间戳大于当前时间，意味数据未过期，任然可以用。返回True
    ： 如果小于，意味着数据已经过期，请用户重新获取数据，返回False
    :param c_time:
    :return:
    '''
    if datetime.datetime.strptime(str(c_time), "%Y-%m-%d %H:%M:%S.%f") >= datetime.datetime.now():
        return True
    else:
        return False


def make_time_stemp():
    '''
    制作过期时间，两个小时。
    也可改为变量形式接受用户提供的参数进行调用
    :return:
    '''
    exp_datetime = datetime.datetime.now() + datetime.timedelta(hours=2)
    return exp_datetime


if __name__ == '__main__':
    '''
    '''
    to_user = sys.argv[1]           
    to_party = sys.argv[2]          
    agentid = sys.argv[3]           
    corpid = sys.argv[4]          
    corpsecret = sys.argv[5]      
    msg = sys.argv[6] + 'yjh........'      

    cf_path = '/tmp/WeChatToken.cfg'
    if os.path.exists(cf_path):
        c_time,token = get_cache(cf_path)
        if c_time != 'ERROR':
            if not time_diff(c_time):
                exp_time = make_time_stemp()
                token = get_token(corpid,corpsecret)
                set_cache(exp_time,token,cf_path)
    else:
        exp_time = make_time_stemp()
        token = get_token(corpid, corpsecret)
        set_cache(exp_time, token, cf_path)
    # send_msg(token,touser,toparty,agentid,msg,safe=0,totag=" @all",msgtype='text')
    send_msg(token,to_user,to_party,agentid,msg)




