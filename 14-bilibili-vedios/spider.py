import requests
import re
import json
import threading
import pymongo

mongo = pymongo.MongoClient('localhost', 27017)
db = mongo.bilibili
col = db.video

def get_vedio_url(aid):
    url = 'http://www.bilibili.com/video/av%s' % aid
    return url

def get_stat_url(aid):
    url = 'http://api.bilibili.com/archive_stat/stat?aid=%s' % aid
    return url

def get_danmu_url(cid):
    url = 'http://comment.bilibili.com/%s.xml' % cid
    return url

def get_player_url(aid, cid):
    url = 'http://interface.bilibili.com/player?id=cid:%s&aid=%s' % (cid, aid)
    return url

def get_comment_url(cid, page=1):
    url = 'http://api.bilibili.com/x/v2/reply?callback=jQuery17202870352235622704_1482889079904&jsonp=jsonp&pn=%d&type=1&oid=%s&sort=0&_=1482889773903' % (page, cid)
    return url

session = requests.Session()
session.mount(adapter=requests.adapters.HTTPAdapter(max_retries=3), prefix='/')

cid_pattern = re.compile(r'cid=([\d]+)?&')
dm_pattern = re.compile(r'<d.*>(.*)</d>')
cm_pattern = re.compile(r'jQuery.*?\((.*)\).*')
tt_pattern = re.compile(r'<h1 title.*?>(.*)</h1>')
tp_pattern = re.compile(r'property="v:title">(.*?)</a>')
us_pattern = re.compile(r'<div class="usname"><a.*?mid="(.*?)".*?>(.*?)</a>')

def crawl(aid):
    try:
        aid = str(aid)
        response = session.get(get_vedio_url(aid))
        content = response.content.decode()
        grp = re.search(cid_pattern, content)
        if not grp:
            return False
        cid = grp.group(1)
        title = re.search(tt_pattern, content).group(1)
        types = re.findall(tp_pattern, content)
        uid = re.search(us_pattern, content).group(1)
        user = re.search(us_pattern, content).group(2)

        # response = session.get(get_danmu_url(cid))
        # danmu_list = re.findall(dm_pattern, response.content.decode())

        response = session.get(get_stat_url(aid))
        av_data = json.loads(response.content.decode())

        response = session.get(get_comment_url(aid, 1))
        comment_list = json.loads(re.match(cm_pattern, response.content.decode()).group(1))
        comments = []
        if 'hots' in comment_list['data']:
            replies = comment_list['data']['hots']
            if replies:
                for comment in replies:
                    comments.append(comment['content']['message'])
                    # print(comment['content']['message'])
        data = {
            'aid': aid,
            'cid': cid,
            'title': title,
            'types': types,
            'uid': uid,
            'user': user,
            # 'danmus': danmu_list,
            'hot_comments': comments
        }
        data.update(av_data['data'])
        col.insert_one(data)
    finally:
        return

def work(_range):
    for aid in _range:
        crawl(aid)

from time import time
start = time()
threads = []
batch = 200000

for i in range(50):
    t = threading.Thread(target=work, args=[range(i * batch, (i + 1) * batch ) ])
    threads.append(t)
for t in threads:
    t.start()
for t in threads:
    t.join()

end = time()
with open('./total', 'w') as fp:
    fp.write(str(end - start))
