#-*- coding:utf-8 -*-

import re

class Piece(object):
    _html = '<{tag}{attrs}>{content}{childs}</{tag}>'

    def __init__(self, tag='', attrs={}, content='', childs='', raw=None):
        self.raw     = raw            
        self.tag     = tag
        self.attrs   = attrs
        self.content = content
        self.childs  = childs

    def resolve(self):
        if self.raw:
            return self.raw
        attrs = make_attrs(self.attrs)
        self.html = self._html.format(tag=self.tag, attrs=attrs, content=self.content, childs=self.childs)
        return self.html

    def format(self, *args, **kws):
        return self.resolve().format(*args, **kws)

    def __str__(self):
        return self.resolve()

    def __invert__(self):
        return '<!-- {} -->'.format(self.resolve()) 

    # child's inject
    def __le__(self, childs):
        self.childs = ''.join([str(o) for o in childs])
        return self

    def __mul__(self, num):
        return str(self) * 2

    def __getattr__(self, attr):
        return self.attrs.get(attr, None)

    __repr__ = __str__

def make_attrs(attrs):
    attrs = '' + ' '.join(['{}="{}"'.format(k, v) for k, v in attrs.items()])
    attrs = ' {}'.format(attrs) if attrs else ''
    return attrs

tag_flg = re.compile(r'(?P<tag>[\w]+)(\#(?P<id>[\w]+))?(\.(?P<class>[\w\s]+))?')

def h(tag, content='', **attrs):
    if tag:
        m = re.match(tag_flg, tag)
        if m:
            groups =  m.groupdict()
            if groups['id'] is not None:
                attrs['id'] = groups['id']
            if groups['class'] is not None:
                attrs['class'] = groups['class']
            if groups['tag'] is not None:
                tag = groups['tag']
    childs     = attrs.pop('c', [])
    child_html = ''.join([str(c) for c in childs])
    
    return Piece(tag, attrs, content, child_html)

def hmap(tag, content='', datas=None, **attrs):
    if datas is None:
        datas = []
    htmls = []
    for data in datas:
        html = Piece._html.format(
            tag=tag,
            attrs=make_attrs(attrs),
            content=content.replace('{?}', str(data)),
            childs=''
        )
        htmls.append(html)
    return ''.join(htmls)

def hcss(path):
    return Piece(raw='<link rel="stylesheet" type="text/css" href="{}">'.format(path))

def hjs(path):
    return Piece(raw='<script type="text/javascript" src="{}"></script>'.format(path))

def hc(comment):
    return '<!-- {} -->'.format(comment)

def heach(iterable, func):
    res = []
    if isinstance(iterable, list):
        for value in iterable:
            res.append(str(func(value)))
    elif isinstance(iterable, dict):
        for key, value in iterable.items():
            res.append(str(func(key, value)))
    return ''.join(res)

def hfor(times, func, **injects):
    res = []
    for i in range(times):
        res.append(func(i))
    return ''.join(res)


def _main():
    def build(piece, path):
        buf = piece.resolve()
        with open(path, 'w') as fp:
            fp.write(buf)

    datas = [
        ['1 + 1', 2],
        ['1 + 2', 3],
        ['2 + 2', 4]
    ]
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

if __name__ == '__main__':
    _main()
