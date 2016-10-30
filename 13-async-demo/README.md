# async_demo.py

基于异步io的爬虫演示。

# 使用

```
from async_demo import AsyncWorker, AsyncRequest

def fetch(url):
    request = AsyncRequest('www.baidu.com', url, 80)
    data = yield from request.process()
    return data

def get_page(url):
    page = yield from fetch(url)
    return page

def print_content_length(data):
    print(len(data))

async_worker = AsyncWorker(get_page, workers=20, loop_timeout=5)
async_worker.add_result_callback(print_content_length)
for i in range(15):
    async_worker.put('/s?wd={}'.format(i))
async_worker.work()
```
