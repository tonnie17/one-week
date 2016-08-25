# vds.py

使用PIL的可视化数据结构。

## 栈

```
from vds import Stack

s = Stack([1,24,23,423])
s.show()
s.pop()
s.show()
```

![Stack](http://ww3.sinaimg.cn/large/006tNc79jw1f75ubfky98j31kw0eedh1.jpg)

## 链表

```
from vds import LinkList

l = LinkList(1, [2,3,4,3])
l.show()
l.delete(3, all=True)
l.show()
```

![Linklist](http://ww3.sinaimg.cn/large/006tNc79jw1f75ubfxl1cj31kw0ea75p.jpg)
