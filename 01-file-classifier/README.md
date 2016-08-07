# classify.py

目录文件分类工具。

支持分类：

- 扩展名
- 修改时间

## 用法

按扩展名分类

```
python classify.py --ext 目录路径 
```

效果：

├── DS_Store
├── bat
├── bin
├── css
├── db
├── default
├── gif
├── gitattributes
├── gitignore
├── htaccess
├── jar
├── js
├── json
├── lib
├── log
├── md
├── php
├── plex
├── png
├── sql
├── sublime-project
├── sublime-workspace
├── tpl
├── txt
├── xml
├── y
└── yml

按修改时间分类

```
python classify.py --mtime 目录路径
```

效果：

├── 2014
│   └── 10
│       └── 24
├── 2015
│   └── 12
│       └── 21
└── 2016
    ├── 6
    │   ├── 28
    │   ├── 29
    │   └── 30
    ├── 7
    │   ├── 1
    │   └── 26
    └── 8
        ├── 6
        └── 7

还原目录

```
python classify.py --backup 目录路径
```
效果：

├── assets
│   ├── 2e015166
│   ├── 4893405d
│   │   ├── detailview
│   │   ├── gridview
│   │   └── listview
│   ├── 4a5213fe
│   └── a2744ecd
│       ├── autocomplete
│       ├── jui
│       │   ├── css
│       │   │   └── base
│       │   │       └── images
│       │   └── js
│       ├── rating
│       ├── treeview
│       │   └── images
│       └── yiitab
├── css
├── protected
│   ├── commands
│   ├── components
│   ├── config
│   ├── controllers
│   ├── data
│   ├── extensions
│   │   └── smarty
│   │       ├── demo
│   │       │   ├── plugins
│   │       │   └── templates
│   │       ├── lexer
│   │       └── libs
│   │           ├── plugins
│   │           └── sysplugins
│   ├── filters
│   ├── messages
│   │   └── zh_cn
│   ├── models
│   ├── runtime
│   ├── sql_source
│   ├── tests
│   │   ├── functional
│   │   └── unit
│   └── views
│       ├── blog
│       ├── layouts
│       ├── login
│       ├── postadmin
│       └── useradmin
└── themes
    └── classic
        └── views