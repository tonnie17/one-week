import socket
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

selector = DefaultSelector()

class StopError(BaseException):
    """Raised to stop the event loop."""
    pass

def stop_callback(future):
    raise StopError


class EventLoop:
    stopped = False

    def run_until_complete(self, coros):
        self.unfinished_tasks = len(coros)
        tasks = [Task(coro) for coro in coros]
        try:
            self.run_forever()
        except StopError:
            pass

    def run_forever(self):
        while not self.stopped:
            events = selector.select()
            for event_key, event_mask in events:
                callback = event_key.data
                callback(event_key, event_mask)

    def task_finish(self):
        self.unfinished_tasks -= 1
        if self.unfinished_tasks == 0:
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
        except StopIteration as exc:
            get_event_loop().task_finish()
            self.set_result(exc.value)
            return
        next_future.add_done_callback(self.step)

def read(sock):
    f = Future()

    def on_readable(key, mask):
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield f  # Read one chunk.
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

    def process(self):
        chunk = yield from self.gen()
        return chunk

    def get(self):
        self.method = 'GET'
        self.request = '{} {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(self.method, self.url, self.host)
        return self

    def gen(self):
        if self.method is None:
            self.get()
        self.connected = False
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
        print('connected')

        self.sock.send(self.request.encode('ascii'))

        chunk = yield from read_all(self.sock)
        return chunk

    def on_connected(self, key, mask):
        self.connected = True
        self.f.set_result(None)

def fetch(url):
    request = AsyncRequest('www.baidu.com', url, 80)
    data = yield from request.process()
    return data

def get_page(url):
    page = yield from fetch(url)
    print('done!!')

def async_way():
    ev_loop = get_event_loop()
    ev_loop.run_until_complete([
        get_page('/s?wd={}'.format(i)) for i in range(100)
    ])    

def sync_way():
    for i in range(100):
        sock = socket.socket()
        sock.connect(('www.baidu.com', 80))
        print('connected')
        request = 'GET {} HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n'.format('/s?wd={}'.format(i))
        sock.send(request.encode('ascii'))
        response = b''
        chunk = sock.recv(4096)
        while chunk:
            response += chunk
            chunk = sock.recv(4096)
        print('done!!')

from time import time
# start = time()

async_way() # Cost 3.534296989440918 seconds
sync_way()  #Cost 47.757508993148804 seconds

# end = time()
# print ('Cost {} seconds'.format(end - start))
