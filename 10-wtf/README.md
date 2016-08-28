# wtf.py

![???](http://ww2.sinaimg.cn/large/65e4f1e6gw1f79l56lwn4j2050050a9y.jpg)

## 准备工作

```
pip install stackit
```

```
alias ???='python /path/to/wtf.py $(fc -ln -1);'
```

## 使用

测试脚本：error.py

```
root@vagrant-ubuntu-precise-64:/code# python error.py

Traceback (most recent call last):
  File "error.py", line 2, in <module>
    print(a[1])
IndexError: list index out of range
```

```
$ ???
```

输出

```
Searching for: IndexError: list index out of range...
Tags:
1
Question: How to define two-dimensional array in python
Answer:You're technically trying to index an uninitialized array. You have to first
initialize the outer list with lists before adding items; Pytho...

2
Question: Why list doesn&#39;t have safe &quot;get&quot; method like dictionary?
Answer:

Ultimately it probably doesn't have a safe `.get` method because a `dict` is
an associative collection (values are associated with names) ...

3
Question: IndexError: list assignment index out of range
Answer:

`j` is an empty list, but you're attempting to write to element `[0]` in the
first iteration, which doesn't exist yet.

Try the following ...

4
Question: How can I find the last element in a List&lt;&gt; ?
Answer:

If you just want to access the last item in the list you can do



    var item = integerList[integerList.Count - 1];


to get...

5
Question: Getting a default value on index out of range in Python
Answer:

In the Python spirit of "ask for forgiveness, not permission", here's one way:



    try:
        b = a[4]
    except IndexError:...

Enter m for more, a question number to select, or q to quit:
```