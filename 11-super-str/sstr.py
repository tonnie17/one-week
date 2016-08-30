#-*- coding:utf-8 -*-
import re
try:
    import cPickle as pickle
except:
    import pickle
import json
import itertools
from collections import Counter

class SuperStr(object):
    def __init__(self, string=''):
        assert isinstance(string, str) or isinstance(string, unicode)
        self._str = string.encode('utf-8') if isinstance(string, unicode) else string

    def get(self):
        return self._str

    def int(self):
        return int(self._str)

    def json(self):
        return json.loads(self._str)

    def object(self):
        return pickle.loads(self._str)

    def list(self):
        return list(self._str)

    def reverse(self):
        self._str = self._str[::-1]
        return self

    def most_common(self, n):
        if hasattr(self, 'counter'):
            return self.counter.most_common(n)
        self.counter = Counter(self._str)
        return self.counter.most_common(n)

    def exists(self, pattern):
        return re.search(pattern, self._str) is not None

    def findall(self, pattern, flags=0):
        return re.findall(pattern, self._str, flags)

    def split(self, pattern, maxsplit=0, flags=0):
        return re.split(pattern, self._str, maxsplit, flags)

    def sub(self, pattern, repl, count=0, flags=0):
        self._str = re.sub(pattern, repl, self._str, count, flags)
        return self

    def count(self, char):
        if hasattr(self, 'counter'):
            return self.counter[char]
        self.counter = Counter(self._str)
        return self.counter[char]

    def permutations(self, r=None):
        return itertools.permutations(self, r)

    def sort(self):
        self._str = ''.join(sorted(self._str))
        return self

    def __str__(self):
        return self._str

    __repr__ = __str__

    def __call__(self, *args, **kws):
        if callable(self._str):
            self._str = self._str()
        return self

    def __getattr__(self, key):
        if key in dir(str):
            self._str = getattr(self._str, key)
            return self
        self._str = super(SuperStr, self).__getattr__(key)
        return self

    def __radd__(self, s):
        self._str += str(s)
        return self

    __add__ = __radd__

    def __mul__(self, num):
        return str(self) * 2

    def __getitem__(self, given):
        self._str = self._str[given.start: given.stop: given.step] if isinstance(given, slice) else self._str[given]
        return self

if __name__ == '__main__':
    print SuperStr('{"name" : "mike"}').json() # {u'name': u'mike'}
    print SuperStr('1').int() # 1
    print SuperStr(pickle.dumps(object())).object() # <object object at 0x1043330d0>
    print SuperStr('123').list() # ['1', '2', '3']
    print SuperStr('aabbbc').most_common(2) # [('b', 3), ('a', 2)]
    print SuperStr('exists').exists('t') # True
    print SuperStr('ababab').findall('ab') # ['ab', 'ab', 'ab']
    print SuperStr('ab,ab,ab').split(',') # ['ab', 'ab', 'ab']
    print SuperStr('ab,ab,ab').sub(',', '') # ababab
    print SuperStr('ab,ab,ab').count('a') # 3
    print SuperStr('reverse').sort().reverse() # vsrreee
    print SuperStr('abc').permutations() # <itertools.permutations object at 0x1046a7830>
    # capitalize
    # center
    # count
    # decode
    # encode
    # endswith
    # expandtabs
    # find
    # format
    # index
    # isalnum
    # isalpha
    # isdigit
    # islower
    # isspace
    # istitle
    # isupper
    # join
    # ljust
    # lower
    # lstrip
    # partition
    # replace
    # rfind
    # rindex
    # rjust
    # rpartition
    # rsplit
    # rstrip
    # split
    # splitlines
    # startswith
    # strip
    # swapcase
    # title
    # translate
    # upper
    # zfill
