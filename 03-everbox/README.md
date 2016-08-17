# everbox.py

evernote as a file sandbox!

## 用法

```
usage: everbox.py [-h] {init,push,pushall,list,pull,log} ...

文本备份助手.

optional arguments:
  -h, --help            show this help message and exit

操作命令:
  {init,push,pushall,list,pull,log}
    init                新建一个仓库
    push                添加文本到仓库
    pushall             添加批量文本到仓库
    list                列出仓库或文本
    pull                从仓库拉取文本
    log                 查看文本记录信息
```

## 准备工作

安装evernote sdk for python

```
pip install evernote
```

登录[Evernote开发者](http://sandbox.evernote.com)，获取开发Token，把获取到的token替换掉代码中的dev_token。

## 基本操作

### init 新建一个仓库

```
usage: everbox.py init [-h] box

新建一个仓库

positional arguments:
  box         仓库名字
```

```
python everbox.py init test
```

```
创建成功，id为：0c6e25c4-538c-4008-87e2-7efe32e18280
```

### list 列出仓库或文本

```
usage: everbox.py list [-h] [box]

列出仓库文本

positional arguments:
  box         仓库id或仓库名字
```

获取所有仓库

```
python everbox.py list
```

```
| 文本id          | 仓库名称 |
6da27e72-ad2d-4cd0-a05a-f1fc12d9e44c 我的第一个笔记本
1902a691-62f3-4edc-a8bb-4db6d949da50 示例笔记本
```

获取仓库文本

```
python everbox.py list 6da2
```

```
| 文本id          | 文本名称 |
b00204f8-41d0-43bb-8fc3-17b3a654360f README.md
f7c7b2be-c247-4c2a-8001-186d27942cce README.md
```


### pushall 推送所有文本

```
usage: everbox.py pushall [-h] [-b BOX] [files [files ...]]

添加批量文本到仓库

positional arguments:
  files              文本路径，多个以空格间隔

optional arguments:
  -h, --help         show this help message and exit
  -b BOX, --box BOX  仓库id或仓库名字
```

```
python everbox.py pushall -b 6da2 README.md
```

```
已上传(1/1)个文本
```

```
python everbox.py pushall README.md
```

```
无指定仓库，将使用默认仓库
已上传(1/1)个文本
```


### log 查看文件在仓库中的记录

```
usage: everbox.py log [-h] file

查看文本记录信息

positional arguments:
  file        文本名称
```

```
python everbox.py log README.md
```

输出

```
| 文本id          | 文本名称 | 仓库  | 创建时间
b00204f8-41d0-43bb-8fc3-17b3a654360f README.md 我的第一个笔记本 2016-08-16 17:14:07
f7c7b2be-c247-4c2a-8001-186d27942cce README.md 我的第一个笔记本 2016-08-16 17:15:02
```

### pull 从仓库中拉取文件

```
usage: everbox.py pull [-h] [-b BOX] [-y] [files [files ...]] directory

从仓库拉取文本

positional arguments:
  files              文本guid或名称（若用名称则取最新的同名
                     )，多个以空格间隔
  directory          拉取目录

optional arguments:
  -h, --help         show this help message and exit
  -b BOX, --box BOX  仓库id或仓库名字
  -y, --yes          忽略覆盖提示
```

```
python everbox.py pull b00204f8-41d0-43bb-8fc3-17b3a654360f  .
```

输出

```
文件 /Users/tonnie/github/one-week/03-everbox/README.md 已存在，是否覆盖，是请按y，不是请输入n：y
成功拉取：1个文件
```
