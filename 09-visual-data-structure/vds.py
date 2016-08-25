#-*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# font   = ImageFont.truetype('Arial.ttf', 36)

class Vds(object):
    MAX_SIZE = 20

    def get_size_with_raise(self):
        size = self.object.get_size()
        if size > self.MAX_SIZE:
            raise Exception('超过最大容量')
        return size

    def get_vds(self, width, height):
        return Image.new('RGB', (width, height), (255, 255, 255))

    def get_drawer(self, vds):
        return ImageDraw.Draw(vds)

    def __init__(self, obj):
        self.object = obj

    def show():
        raise NotImplementedError

class ListVds(Vds):
    PER_HEIGHT = 50
    WIDTH      = 300

    def show(self):
        width  = self.WIDTH
        height = self.get_size_with_raise() * self.PER_HEIGHT + 3
        image  = self.get_vds(width, height + 6)
        draw   = self.get_drawer(image)
        offset = self.PER_HEIGHT

        left  = width / 3
        right = width * 2 / 3

        for i, ele in enumerate(self.object):
            draw.rectangle([left, height - (i + 1) * offset, right, height - i * offset], outline=(0,0,0))
            draw.text([width/2, height - (i + 1) * offset + offset/2], str(ele), fill=(0,0,0))

        image.show()

class StackVds(ListVds):
    pass

class LinkListVds(Vds):
    PER_WIDTH  = 100
    HEIGHT     = 200

    def show(self):
        size   = self.get_size_with_raise()
        width  = size * self.PER_WIDTH + 3
        height = self.HEIGHT

        image  = self.get_vds(width + 6, height)
        draw   = self.get_drawer(image)
        offset = self.PER_WIDTH

        up   = height / 3
        down = height * 2 / 3
        dis  = 10

        for i, node in enumerate(self.object):
            draw.rectangle([width - (i + 1) * offset, up, width - i * offset - dis, down], outline=(0,0,0))
            draw.text([i * offset + offset/2, height/2], str(node), fill=(0,0,0))
            draw.line((width - i * offset - dis, (up + down)/2, width - i * offset, (up + down)/2), fill=(0,0,0))
            i += 1

        image.show()


def _main():
    class List(object):
        def __init__(self, array=None):
            self.array = array if isinstance(array, list) else []

        def get_size(self):
            return len(self.array)

        def __iter__(self):
            return iter(self.array)

        def __getattr__(self, key):
            if hasattr(self.array, key):
                return getattr(self.array, key)
            return super().__getattr__(key)

    class Stack(List):
        def push(self, val):
            self.array.append(val)

        def pop(self):
            return self.array.pop()

        def head(self):
            if self.array:
                return self.array[-1]
            return None

        def clear(self):
            self.array.clear()

        
    class LinkList(object):

        def __init__(self, val, nodes=None):
            self.next = None
            self.val  = val
            if isinstance(nodes, list) and nodes:
                self.mul_add(nodes)

        def add(self, val):
            node = self
            while node.next is not None:
                node = node.next
            child     = LinkList(val)
            node.next = child
            self.childs += 1

        def delete(self, val, all=False):
            node = prev = self
            while node and node.val != val:
                prev = node
                node = node.next
            if node:
                prev.next = node.next
                node = None
                node = prev.next
                if all == True:
                    node.delete(val)

        def mul_add(self, datalist):
            old = self
            for val in datalist:
                node = LinkList(val)
                old.next = node
                old = node

        def __iter__(self):
            node = self
            while node:
                yield node
                node = node.next

        def get_size(self):
            size = 1
            node = self
            while node.next is not None:
                node = node.next
                size += 1
            return size

        def __str__(self):
            return str(self.val)

    s = Stack([1,24,23,423])
    tracer = StackVds(s)
    tracer.show()
    s.pop()
    tracer.show()

    l = LinkList(1, [2,3,4,3])
    tracer = LinkListVds(l)
    tracer.show()
    l.delete(3, all=True)
    tracer.show()


if __name__ == '__main__':
    _main()
