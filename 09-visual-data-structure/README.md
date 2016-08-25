# vds.py

使用PIL的可视化数据结构。

## 数据结构类需要实现的接口

```
def __iter__(self) => obj # 遍历容器元素的方法
def get_size(self) => int # 获取容器元素数量的方法
```

## 栈

```
from vds import StackVds

s = Stack([1,24,23,423])
tracer = StackVds(s)
tracer.show()
s.pop()
tracer.show()
```

![Stack](http://ww3.sinaimg.cn/large/006tNc79jw1f75ubfky98j31kw0eedh1.jpg)

## 链表

```
from vds import LinkListVds

l = LinkList(1, [2,3,4,3])
tracer = LinkListVds(l)
tracer.show()
l.delete(3, all=True)
tracer.show()
```

![Linklist](http://ww3.sinaimg.cn/large/006tNc79jw1f75ubfxl1cj31kw0ea75p.jpg)

## 二维数组

```
from vds import MatrixVds

arr = [
    [1,2],
    [3,4,5,6],
    [7,8,9]
]
tracer = MatrixVds(arr)
tracer.show()
```

![Matrix](http://ww2.sinaimg.cn/large/006tNc79gw1f767ck6lehj30uo0kkab7.jpg)
