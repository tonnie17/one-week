#-*- coding:utf-8 -*-
import argparse
import urllib2
import re
import json
from prettytable import PrettyTable

API_KEY = '5092e0ce602c4585e06316bfc3158ea2'

def getip():
    url    = 'http://jsonip.com'
    opener = urllib2.urlopen(url, timeout=5)
    if url == opener.geturl():
        info = opener.read()
        res  = re.search('\d+\.\d+\.\d+\.\d+',info)
        if res:
            return res.group(0)
    return None

# {"status":"1","info":"OK","infocode":"10000","province":"广东省","city":"珠海市","adcode":"440400","rectangle":"113.0991626,21.9335713;113.7227333,22.39738989"}
def get_geo():
    ip  = getip()
    ret = urllib2.urlopen('http://restapi.amap.com/v3/ip?ip=%s&output=json&key=%s' %(ip, API_KEY)).read()
    return json.loads(ret)

def get_around_keyword(location, keyword):
    ret = urllib2.urlopen('http://restapi.amap.com/v3/place/around?key=%s&location=%s&output=json&radius=10000&keywords=%s' %(location, API_KEY, keyword)).read()
    return json.loads(ret)

def get_city(args):
    city    = args.city
    if not city:
        city = get_geo()['city']
    if isinstance(city, unicode):
        city = city.encode('utf-8')
    return city

def get_place(keyword, city):
    ret = urllib2.urlopen('http://restapi.amap.com/v3/place/text?&keywords={}&city={}&output=json&offset=100&page=1&key={}&extensions=all'.format(keyword, city, API_KEY)).read()
    if not ret:
        return None
    res = json.loads(ret)
    return res

def place(args):
    city    = get_city(args)
    keyword = args.keyword
    res = get_place(keyword, city)
    t   = PrettyTable(['名称', '地址', '电话'])
    for r in res['pois']:
        t.add_row([r['name'], r['address'], r['tel']])
    print (t)

def bus(args):
    start = args.start
    end   = args.end
    city  = get_city(args)

    res = get_place(start, city)
    if not res['pois']:
        print ('无法找到起始位置')
        return
    start_point = res['pois'][0]['location']
    res = get_place(end, city)
    if not res['pois']:
        print ('无法找到目的位置')
        return
    end_point = res['pois'][0]['location']
    ret       = urllib2.urlopen('http://restapi.amap.com/v3/direction/transit/integrated?origin=%s&destination=%s&city=010&output=json&key=%s' %(start_point, end_point, API_KEY)).read()
    if not ret:
        return
    res = json.loads(ret)
    t   = PrettyTable(['路线', '上车站', '下车站', '途径站数', '预计时间', '步行距离'])
    end = False
    count = 1
    for transit in res['route']['transits']:
        t.add_row(['方案%s' %str(count),'','','','','%s公里' % ( int(transit['walking_distance']) / 1000.0)])
        count += 1
        for segment in transit.get('segments', []):
            if not segment['bus']['buslines']:
                end = True
                t.add_row(['','','','','',''])
            else:
                names     = []
                d_stops   = []
                a_stops   = []
                durations = []
                stops = []
                for bus in segment['bus']['buslines']:
                    names.append(bus['name'])
                    d_stops.append(bus['departure_stop']['name'])
                    a_stops.append(bus['arrival_stop']['name'])
                    durations.append(bus['duration'])
                    stops.append(bus['via_num'])

                t.add_row([
                    '\n'.join(names), 
                    # '\n'.join([stop['name'] for stop in bus['via_stops']]), 
                    '\n'.join(d_stops),
                    '\n'.join(a_stops),
                    '\n'.join(stops),
                    '\n'.join(['%s分钟' %(int(d)/60) for d in durations]),
                    '',
                ])
                if end == True:
                    end = False
                    t.add_row([
                        '---换乘---', 
                        '',
                        '',
                        '',
                        '',
                        ''
                    ])
    print t
            # for walk in segment['walking']['steps']:
            #     print walk['instruction']
    
def info(args):
    city = get_city(args)
    ret = urllib2.urlopen('http://www.baike.com/wiki/%s' % city).read()
    if not ret:
        return
    summary = re.findall(r'<div class="summary">([\s\S]*?)</p>', ret)[0]
    summary = re.sub(r'<.*?>', '', summary)
    print (summary)

def _main():
    parser = argparse.ArgumentParser(description='城市信息查询.')
    subparsers = parser.add_subparsers(title='操作命令')

    parser.add_argument('-k', '--keyword', type=str, help='关键词')

    info_cmd = subparsers.add_parser('info', help='查询城市简介', description='查询城市简介')
    info_cmd.add_argument('city', nargs='?', help='查询城市')
    info_cmd.set_defaults(func=info)

    place_cmd = subparsers.add_parser('place', help='查询城市信息', description='查询城市信息')
    place_cmd.add_argument('keyword', help='查询的关键词')
    place_cmd.add_argument('city', nargs='?', help='查询城市')
    place_cmd.set_defaults(func=place)

    bus_cmd = subparsers.add_parser('bus', help='查询公交信息', description='查询公交信息')
    bus_cmd.add_argument('start', help='出发地')
    bus_cmd.add_argument('end', help='目的地')
    bus_cmd.add_argument('city', nargs='?', help='查询城市')
    bus_cmd.set_defaults(func=bus)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    _main()


