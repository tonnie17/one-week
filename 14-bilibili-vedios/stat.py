from prettytable import PrettyTable
import pymongo
import jieba

mongo = pymongo.MongoClient('localhost', 27017)
db = mongo.bilibili
vedio = db.video

top_10_view = vedio.find({'view': {'$ne': '--'}}).sort('view', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '点击量', '用户', '分类'])
for doc in top_10_view:
    table.add_row([doc['aid'], doc['title'], doc['view'], doc['user'], '-'.join(doc['types']) ])
print (table)

top_10_fav = vedio.find({}).sort('favorite', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '收藏数', '用户', '分类'])
for doc in top_10_fav:
    table.add_row([doc['aid'], doc['title'], doc['favorite'], doc['user'], '-'.join(doc['types']) ])
print (table)

top_10_dm = vedio.find({}).sort('danmaku', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '弹幕数', '用户', '分类'])
for doc in top_10_dm:
    table.add_row([doc['aid'], doc['title'], doc['danmaku'], doc['user'], '-'.join(doc['types']) ])
print (table)

top_10_cn = vedio.find({}).sort('coin', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '硬币数', '用户', '分类'])
for doc in top_10_cn:
    table.add_row([doc['aid'], doc['title'], doc['coin'], doc['user'], '-'.join(doc['types']) ])
print (table)

top_10_us = vedio.find({}).sort('share', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '分享数', '用户', '分类'])
for doc in top_10_us:
    table.add_row([doc['aid'], doc['title'], doc['share'], doc['user'], '-'.join(doc['types']) ])
print (table)

top_10_cm = vedio.find({}).sort('reply', pymongo.DESCENDING).limit(10)
table = PrettyTable(['AV', '标题', '评论数', '用户', '分类'])
for doc in top_10_cm:
    table.add_row([doc['aid'], doc['title'], doc['reply'], doc['user'], '-'.join(doc['types']) ])
print (table)

comments = []
c = Counter(comments)
for i, doc in enumerate(vedio.find({ 'hot_comments': { '$gt': [] } }, {'hot_comments': 1, '_id': False})):
    for comment in doc['hot_comments']:
        for word in jieba.cut(comment):
            if len(word) > 1:
                c[word] += 1
                # comments.append(word)
print (c.most_common(100))

