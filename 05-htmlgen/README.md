# htmlgen.py

轻量级的html生成器（纯python）。

## 用法

```
from htmlgen import h

h('html') # <html></html>
```

更深入的例子

```
datas = [
    ['1 + 1', 2],
    ['1 + 2', 3],
    ['2 + 2', 4]
]
```

参数语法

```
build(h('html', c=[
        h('head', c=[
            h('title', 'My Title'),
            h('meta', charset='utf-8'),
            hc('This is comment'),
            hcss('test.css')
        ]),
        h('body#main.class1 class2', c=[
            h('h1', 'HtmlGen') * 2,
            h('ul', extra=1, c=[
                hmap('li', 'I am {?}!', [1,2,3,4,5])
            ]),
            h('ul', c=[
                hfor(5, lambda i: h('li', '{}').format(chr(ord(str(i)) + 17)))
            ]),
            h('table', c=[
                h('tr', c=[
                    h('td'),
                    heach(dict(name='result'), lambda k, v: h('td', v))
                ]),
                heach(datas, lambda k, v:
                    h('tr', c=[
                        heach(v, lambda k, v: h('td', v, style='border:1px solid black;')),
                    ])
                )
            ]),
            ~ hjs('test.js')
        ]),
    ]), 'test.html')
```

注入语法

```
build(h('html') <= [
        h('head') <= [
            h('title', 'My Title'),
            h('meta', charset='utf-8'),
            hc('This is comment'),
            hcss('test.css')
        ],
        h('body#main.class1 class2') <= [
            h('h1', 'HtmlGen') * 2,
            h('ul', extra=1) <= [
                hmap('li', 'I am {?}!', [1,2,3,4,5])
            ],
            h('ul') <= [
                hfor(5, lambda i: h('li', '{}').format(chr(ord(str(i)) + 17)))
            ],
            h('table') <= [
                h('tr') <= [
                    h('td'),
                    heach({'name': 'result'}, lambda k, v: h('td', v))
                ],
                heach(datas, lambda v:
                    h('tr') <= [
                        heach(v, lambda v: h('td', v, style='border:1px solid black;')),
                    ]
                )
            ],
            ~ hjs('test.js') # comment,too
        ],
    ], 'test.html')
```    

以上代码会生成如下html：

```
<html>

<head>
    <title>My Title</title>
    <meta charset="utf-8"></meta>
    <!-- This is comment -->
    <link rel="stylesheet" type="text/css" href="test.css">
</head>

<body id="main" class="class1 class2">
    <h>HtmlGen</h>
    <h>HtmlGen</h>
    <ul extra="1">
        <li>I am 1!</li>
        <li>I am 2!</li>
        <li>I am 3!</li>
        <li>I am 4!</li>
        <li>I am 5!</li>
    </ul>
    <ul>
        <li>A</li>
        <li>B</li>
        <li>C</li>
        <li>D</li>
        <li>E</li>
    </ul>
    <table>
        <tr>
            <td></td>
            <td>result</td>
        </tr>
        <tr>
            <td style="border:1px solid black;">1 + 1</td>
            <td style="border:1px solid black;">2</td>
        </tr>
        <tr>
            <td style="border:1px solid black;">1 + 2</td>
            <td style="border:1px solid black;">3</td>
        </tr>
        <tr>
            <td style="border:1px solid black;">2 + 2</td>
            <td style="border:1px solid black;">4</td>
        </tr>
    </table>
    <!-- <script type="text/javascript" src="test.js"></script> -->
</body>

</html>
```


