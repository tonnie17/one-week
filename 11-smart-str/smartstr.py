#-*- coding:utf-8 -*-
import re
try:
    import cPickle as pickle
except:
    import pickle
import json

class SmartStr(object):
    def __init__(self, string):
        assert isinstance(string, str) or isinstance(string, unicode)
        self.str = string.encode('utf-8') if isinstance(string, unicode) else string

    def get(self):
        return self

    def int(self):
        return int(self.str)

    def json(self):
        return json.loads(self.str)

    def object(self):
        return pickle.loads(self.str)

    def serialize(self, obj):
        assert isinstance(obj, object)
        self.str = pickle.dumps(object)
        return self

    def unserialize(self):
        self.str = pickle.loads(self.str)
        return self

    def reverse(self):
        self.str = self.str[::-1]
        return self

    def exists(self, pattern):
        return re.match(pattern, self.str) is not None

    def findAll(self, pattern, flags=0):
        return re.findall(pattern, self.str, flags)

    def split(self, pattern, maxsplit=0, flags=0):
        self.str = re.split(pattern, self.str, maxsplit, flags)
        return self

    def sub(self, pattern, repl, count=0, flags=0):
        self.str = re.sub(pattern, repl, self.str, count, flags)
        return self

    def __str__(self):
        return self.str

    def __call__(self, *args, **kws):
        if callable(self.str):
            self.str = self.str()
        return self

    def __getattr__(self, key):
        if key in dir(str):
            self.str = getattr(self.str, key)
            return self
        self.str = super(SmartStr, self).__getattr__(key)
        return self

    __repr__ = __str__

    def __getitem__(self, given):
        if isinstance(given, slice):
            self.str = self.str[given.start: given.stop: given.step]
        else:
            self.str = self.str[given]
        return self

s = SmartStr('{"name" : "mike"}')
print s[2:6].upper().reverse().sub('MA', '').exists('EN')
