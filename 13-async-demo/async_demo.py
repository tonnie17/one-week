import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

selector = DefaultSelector()

class StopError(BaseException):
    pass

class SelectTimeout(BaseException):
    pass

class EventLoop:
    stopped = False
    select_timeout = 5

    def run_until_complete(self, coros):
        tasks = [Task(coro) for coro in coros]
        try:
            self.run_forever()
        except StopError:
            pass

    def run_forever(self):
        while not self.stopped:
            events = selector.select(self.select_timeout)
            if not events:
                raise SelectTimeout('轮询超时')
            for event_key, event_mask in events:
                callback = event_key.data
                callback(event_key, event_mask)

    def close(self):
        self.stopped = True

__ev_loop = EventLoop()

def get_event_loop():
    return __ev_loop

class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        for fn in self._callbacks:
            fn(self)

class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
            if next_future is None:
                return
        except StopIteration as exc:
            self.set_result(exc.value)
            return
        next_future.add_done_callback(self.step)

def read(sock):
    f = Future()

    def on_readable(key, mask):
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield f
    selector.unregister(sock.fileno())
    return chunk


def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)
    return b''.join(response)


class AsyncRequest:
    def __init__(self, host, url, port, timeout=5):
        self.sock = socket.socket()
        self.sock.settimeout(timeout)
        self.sock.setblocking(False)
        self.host = host
        self.url = url
        self.port = port
        self.method = None

    def get(self):
        self.method = 'GET'
        self.request = '{} {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.method, self.url, self.host)
        return self

    def process(self):
        if self.method is None:
            self.get()
        try:
            self.sock.connect((self.host, self.port))
        except BlockingIOError:
            pass
        self.f = Future()
        selector.register(self.sock.fileno(),
                      EVENT_WRITE,
                      self.on_connected)
        yield self.f
        selector.unregister(self.sock.fileno())

        self.sock.send(self.request.encode('ascii'))

        chunk = yield from read_all(self.sock)
        return chunk

    def on_connected(self, key, mask):
        self.f.set_result(None)

def fetch(url):
    request = AsyncRequest('www.baidu.com', url, 80)
    data = yield from request.process()
    return data

def get_page(url):
    page = yield from fetch(url)
    return page

# def async_way():
#     ev_loop = get_event_loop()
#     ev_loop.run_until_complete([
#         get_page('/s?wd={}'.format(i)) for i in range(100)
#     ])

# def sync_way():
#     for i in range(100):
#         sock = socket.socket()
#         sock.connect(('www.baidu.com', 80))
#         print('connected')
#         request = 'GET {} HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n'.format('/s?wd={}'.format(i))
#         sock.send(request.encode('ascii'))
#         response = b''
#         chunk = sock.recv(4096)
#         while chunk:
#             response += chunk
#             chunk = sock.recv(4096)
#         print('done!!')

# from time import time
# start = time()

# async_way() # Cost 3.534296989440918 seconds
# sync_way()  #Cost 47.757508993148804 seconds

# end = time()
# print ('Cost {} seconds'.format(end - start))

from collections import deque

class Queue:
    def __init__(self):
        self._q = deque()
        self.size = 0

    def put(self, item):
        self.size += 1
        self._q.append(item)

    def get(self):
        item = self._q.popleft()
        return item

    def task_done(self):
        self.size -= 1
        if self.size == 0:
            self.empty_callback()

class AsyncWorker(Queue):
    def __init__(self, coroutine, workers=10, loop_timeout=5):
        super().__init__()
        self.func = coroutine
        self.stopped = False
        self.ev_loop = get_event_loop()
        self.ev_loop.select_timeout = loop_timeout
        self.workers = workers
        self.result_callbacks = []

    def work(self):
        def _work():
            while not self.stopped:
                item = None
                try:
                    item = self.get()
                except IndexError:
                    yield None
                    self.stopped = True
                result = yield from self.func(item)
                self.task_done()
                for rcb in self.result_callbacks:
                    rcb(result)
        self.tasks = []
        for _ in range(self.workers):
            self.tasks.append(_work())
        self.ev_loop.run_until_complete(self.tasks)

    def add_result_callback(self, func):
        self.result_callbacks.append(func)

    def empty_callback(self):
        self.ev_loop.close()

def print_content_length(data):
    print(len(data))

async_worker = AsyncWorker(get_page, workers=20)
async_worker.add_result_callback(print_content_length)
for i in range(15):
    async_worker.put('/s?wd={}'.format(i))
async_worker.work()
