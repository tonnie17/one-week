#-*- coding:utf-8 -*-

import re

tag_flg = re.compile(r'(?P<tag>[a-z]+)(\#(?P<id>[\w]+))(\.(?P<class>[\w\s]+))')

def h(tag, content='', **attrs):
    if tag:
        m = re.match(tag_flg, tag)
        if m:
            groups =  m.groupdict()
            attrs['id'] = groups['id']
            attrs['class'] = groups['class']
            tag = groups['tag']
    childs     = attrs.pop('c', [])
    child_html = ''.join(childs)
    attrs      = ' '.join(['{}="{}"'.format(k, v) for k, v in attrs.items()])
    
    html       = '<{tag}{attrs}>{content}{childs}</{tag}>'.format(
        tag=tag,
        content=content,
        attrs=' {}'.format(attrs) if attrs else '',
        childs=child_html
    )
    return html

def hmap(tag, content='', datas=None, **attrs):
    if datas is None:
        datas = []
    htmls = []
    for data in datas:
        html = '<{tag}{attrs}>{content}</{tag}>'.format(
            tag=tag,
            content=content.replace('{?}', str(data)),
            attrs=' {}'.format(attrs) if attrs else '',
        )
        htmls.append(html)
    return ''.join(htmls)

def hcss(path):
    return '<link rel="stylesheet" type="text/css" href="{}">'.format(path)

def hjs(path):
    return '<script type="text/javascript" src="{}"></script>'.format(path)

def hc(html):
    return '<!-- {} -->'.format(html)

def heach(iterable, func):
    res = []
    if isinstance(iterable, list):
        for value in iterable:
            res.append(func(None, value))
    elif isinstance(iterable, dict):
        for key, value in iterable.items():
            res.append(func(key, value))
    return ''.join(res)

def hfor(times, func, **injects):
    res = []
    for i in range(times):
        res.append(func(i))
    return ''.join(res)

def build(html, path):
    with open(path, 'w') as fp:
        fp.write(html)

def _main():
    datas = [
        ['1 + 1', 2],
        ['1 + 2', 3],
        ['2 + 2', 4]
    ]
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
                    hfor(5, lambda i: '<li>{}</li>'.format(chr(ord(str(i)) + 17)))
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
                hjs('test.js')
            ]),
        ]), 'test.html')

if __name__ == '__main__':
    _main()
