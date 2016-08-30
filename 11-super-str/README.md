# sstr.py

100行的加强型字符串。

## 使用

```
from sstr import SuperStr

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

```