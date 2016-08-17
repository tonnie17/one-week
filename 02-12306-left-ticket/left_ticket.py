#!/usr/bin/python
#-*- coding:utf-8 -*-

import argparse
import os
import json
import urllib2
import ssl
import sys
import re
import socket
from datetime import datetime

PURPOSE_CODES   = ['ADULT', '0X00'] # 成人票，学生票
CITY_CACHE      = None
CITY_CACHE_FILE = '.cities'
CITY_LIST_URL   = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
ACTION_URL      = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes={ticket_type}&queryDate={train_time}&from_station={from_city}&to_station={to_city}'

# 对月份进行补零
def add_zero(month):
    if int(month) < 10:
        month = '0' + str(int(month))
    return month

# 默认为今天
def default_date():
    now = datetime.now()
    return '-'.join([str(now.year), str(add_zero(now.month)), str(now.day)])

# 格式化输入日期
# 如：
# 8-14 -> 2016-08-14
# 2016:8:14 -> 2016-08-14
#  -> 2016-08-14
def date_format(input_date):
    if not input_date:
        return default_date()
    res = re.match(r'(([0-9]{4})[-|\\|:])?([0-9]{1,2})[-|\\|:]([0-9]{2})', input_date)
    if res:
        year = res.group(2)
        month = res.group(3)
        day = res.group(4)
        
        now = datetime.now()
        if not year:
            year = now.year
        if not month:
            month = now.month
        if not day:
            day = now.day
        return '-'.join([str(year), add_zero(str(month)), str(day)])
    else:
        print ('输入日期格式错误')
        sys.exit(-1)

# 加载城市信息
def load_cities():
    global CITY_CACHE
    if CITY_CACHE is not None:
        return CITY_CACHE
    cache_file  = os.path.join(os.path.dirname(os.path.abspath(__file__)), CITY_CACHE_FILE)
    need_relaod = False
    cities      = {}
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as fp:
            cities = json.load(fp)
        if not cities:
            need_relaod = True
    else:
        need_relaod = True

    if need_relaod is True:
        info    = urllib2.urlopen(CITY_LIST_URL, context=ssl_ctx).read()
        for res in re.finditer(r'@[a-z]{3}\|(.+?)\|([A-Z]{3})\|[a-z]+?\|[a-z]+?\|', info):
            city         = res.group(1)
            code         = res.group(2)
            cities[city] = code
        with open(cache_file, 'w') as fp:
            json.dump(cities, fp)
    CITY_CACHE = cities
    return cities

# 查询操作
def search(from_city, to_city, train_time, ticket_type='ADULT'):
    ssl_ctx     = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    cities      = load_cities()

    try:
        from_code = cities[from_city.decode('utf-8')]
    except KeyError:
        print('指定起始城市%s不存在' % from_city)
        sys.exit(-1)
    try:
        to_code   = cities[to_city.decode('utf-8')]
    except KeyError:
        print('指定目标城市%s不存在' % to_city)
        sys.exit(-1)

    url = ACTION_URL.format(from_city=from_code, to_city=to_code, train_time=train_time, ticket_type=ticket_type)
    ret = json.loads(urllib2.urlopen(url, context=ssl_ctx, timeout=10).read())
    if not ret or ret == -1 or not ret['data'].has_key('datas') or len(ret['data']['datas']) == 0:
        print('没查询到相关的车次信息')
        sys.exit(-1)

    print ('车次序号     起始站 出发站 终点站 时间 一等座 二等座')
    for r in ret['data']['datas']:
        if (not r['zy_num'].encode('utf-8').isdigit() 
            and not r['ze_num'].encode('utf-8').isdigit()
            or r['from_station_name'].encode('utf-8') != from_city):
            continue
        print (u'%s %s->%s->%s %s  %s   %s' %(
            r['train_no'],
            r['start_station_name'],
            r['from_station_name'],
            r['to_station_name'],
            r['arrive_time'],
            r['zy_num'],
            r['ze_num']
        ))

# 获取ip
def getip():
    url    = 'http://ip.chinaz.com/'
    opener = urllib2.urlopen(url, timeout=5)
    if url == opener.geturl():
        info = opener.read()
        res  = re.search('\d+\.\d+\.\d+\.\d+',info)
        if res:
            return res.group(0)
    return None

# 根据ip获取地址
def getaddr(fresh=False):
    addr_cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.addr')
    if not fresh and os.path.exists(addr_cache_file):
        addr = None
        with open(addr_cache_file, 'rb') as fp:
            addr = fp.read()
        if addr:
            return addr
    ip   = getip()

    if not ip:
        return None
    url  = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s' % ip
    info = urllib2.urlopen(url, timeout=5).read()
    city = None
    if info:
        info = json.loads(info)
        city = info['data']['city']
        city = city.encode('utf-8').replace('市', '')
        with open(addr_cache_file, 'w') as fp:
            fp.write(city)
    return city

def get_yn_input(msg):
    while True:
        res = raw_input('%s，是请按回车，不是请输入n：' % msg)
        if res in ('', 'n'):
            break
    return True if res == None else False

# 默认模式
def guide():
    try:
        cities = load_cities()
        city   = getaddr()
    except socket.timeout:
        print ('请求超时')
        sys.exit(-1)

    if city and cities.has_key(city.decode('utf-8')):
        from_city = raw_input('请输入起始城市（输入回车为%s）：' % city)
        if not from_city:
            from_city = city
    else:
        from_city = raw_input('请输入起始城市：')
    while True:
        to_city = raw_input('请输入目的城市：')
        if to_city:
            break

    dd         = default_date()
    train_time = raw_input('请输入出发日期（输入回车为%s）：' % dd)
    if not train_time:
        train_time = dd
    else:
        train_time = date_format(train_time)
    ticket_type = 'ADULT' if get_yn_input('是否成人票') else '0X00'
    print('正在查询...\n')
    search(from_city, to_city, train_time, ticket_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='查询12306车次余票.')
    parser.add_argument('-f', '--from_city', type=str, help='起始城市')
    parser.add_argument('-t', '--to_city', type=str, help='目标城市')
    parser.add_argument('-d', '--date', type=str, help='日期，格式如：2016-08-14')
    parser.add_argument('-s', '--student', action='store_true', help='学生票')
    parser.add_argument('-l', '--list_city', action='store_true', help='查看支持城市列表')

    args        = parser.parse_args()
    from_city   = args.from_city
    to_city     = args.to_city
    train_time  = date_format(args.date)
    ticket_type = PURPOSE_CODES[1] if args.student is True else PURPOSE_CODES[0]
    list_city   = args.list_city
    
    if from_city is None and to_city is None and list_city is False:
        guide()
    else:
        if list_city:
            for city, code in load_cities().items():
                print city,
        elif from_city and to_city and ticket_type:
            search(from_city, to_city, train_time, ticket_type)
        else:
            print ('参数错误')

