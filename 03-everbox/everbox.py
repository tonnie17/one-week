#!usr/bin/python
#-*- coding:utf-8 -*-
import argparse
import binascii
import hashlib
import os
import sys
import md5

try:
    import evernote
    from evernote.api.client import EvernoteClient
    import evernote.edam.type.ttypes as Types
    import evernote.edam.notestore.ttypes as NoteTypes
except:
    print ('未安装evernote的扩展，请安装后重试')
    sys.exit(-1)

dev_token = "S=s1:U=92d14:E=15de8ebccac:C=156913a9da8:P=1cd:A=en-devtoken:V=2:H=ca0bbceb23208c3cde8227aa5912761a"

class LazyGet:
    def __init__(self, construct_func, hint=None, end_hint=None, excp_hint=None):
        self._func      = construct_func
        self._ins       = None
        self._hint      = hint
        self._end_hint  = end_hint
        self._excp_hint = excp_hint

    def __call__(self):
        if self._ins is not None:
            return self._ins
        print (self._hint)
        try:
            self._ins = self._func()
        except Exception, e:
            print (self._excp_hint)
            sys.exit(-1)
        print (self._end_hint)
        return self._ins

get_client    = LazyGet(lambda : EvernoteClient(token=dev_token), '连接evernote...', '连接成功', '连接失败')
get_box_store = LazyGet(lambda : get_client().get_note_store(), '获取数据库...', '获取成功', '获取失败')
get_boxes     = LazyGet(lambda : get_box_store().listNotebooks(), '获取仓库信息...', '获取成功', '获取失败')

def create_box(name):
    box      = Types.Notebook()
    box.name = name
    return box

def create_file(title, content, box_id='', image_resource=None):
    hash_hex = ''
    file = Types.Note()
    if box_id:
        file.box_id = box_id

    if image_resource:
        (resource, image_hash) = image_resource
        file.resources = [resource]
        hash_hex = binascii.hexlify(image_hash)

    file.title = title
    file.content = '''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
    <en-note><caption>%s</caption>''' % content
    if hash_hex:
        file.content += '<en-media type="image/png" hash="%s"/>' % hash_hex
    file.content += '</en-note>'

    return file

# def create_image_resource(image):
#     md5 = hashlib.md5()
#     md5.update(image)
#     image_hash = md5.digest()

#     data = Types.Data()
#     data.size = len(image)
#     data.bodyHash = image_hash
#     data.body = image

#     resource = Types.Resource()
#     resource.mime = 'image/png'
#     resource.data = data

#     return (resource, image_hash)

# def parse_note(content):
#     note_content = ''
#     try:
#         content = content.split('<caption>')[1].split('</caption>')[0]
#     except:
#         pass

#     media_index = content.find('<en-media')
#     content = content[:media_index]

#     note_lst = content.split('<br/>')
#     for content in note_lst:
#         note_content += content

#     return note_content

def get_box_by_id(box_id):
    if len(box_id) < 4:
        print ('id匹配长度至少为4')
        return ''
    for box in get_boxes():
        if box.guid.startswith(box_id):
            return box
    return ''

def get_box_by_name(name):
    for box in get_boxes():
        if box.name == name:
            return box
    return ''

def get_box(id_or_name):
    box = get_box_by_id(args.box)
    if not box:
        box = get_box_by_name(args.box)
    if not box:
        print ('指定仓库不存在')
        sys.exit(-1)
    return box

def push_to_box(note):
    get_box_store().createNote(dev_token, note)

def pull(args):
    print args

def list(args):
    print ('查询中...\n')

    def list_box(box):
        note_filter              = NoteTypes.NoteFilter()
        note_filter.notebookGuid = box.guid
        notes                    = get_box_store().findNotes(dev_token, note_filter, 0, 100).notes

        print ('| 文件id\t\t\t| 文件名称 |')
        for note in notes:
            print "%s %s" %(note.guid, note.title)

    if args.box is None:
        print ('| 文件id\t\t\t| 仓库名称 |')
        for box in get_boxes():
            print box.guid, box.name
            # n.serviceCreated, n.serviceUpdated
    else:
        box = get_box(args.box)
        list_box(box)

def push(args):
    box  = get_box(args.box)
    file = os.path.exists(os.path.abspath(os.path.normpath(args.file)))

def pushall(args):
    box    = get_box(args.box)
    files  = args.files
    to_add = []
    for f in files:
        if not os.path.exists(os.path.abspath(os.path.normpath(f))):
            print ('%s：文件路径不存在' %f)
            break
        to_add.append(os.path.abspath(os.path.normpath(f)))
    else:
        total    = len(to_add)
        finished = 0
        for f in to_add:
            try:
                with open(f, 'rb') as fp:
                    title             = md5.md5(f).hexdigest()
                    file              = create_file(title, fp.read(), box.guid, '')
                    file.notebookGuid = box.guid
                    push_to_box(file)
                    finished += 1
                    sys.stdout.write('已上传(%s/%s)个文件\r' % (finished, total))
                    sys.stdout.flush()
            except Exception, e:
                print (e)
                print ('发生异常，程序退出!')
        print('已上传(%s/%s)个文件' % (finished, total))


def log(args):
    print args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='文本备份助手.')
    subparsers = parser.add_subparsers(title='操作命令')

    push_cmd  = subparsers.add_parser('push', help='添加文件到仓库', description='添加文件到仓库')
    push_cmd.add_argument('box', help='仓库id或仓库名字')
    push_cmd.add_argument('file')
    push_cmd.set_defaults(func=push)

    push_all_cmd  = subparsers.add_parser('pushall', help='添加批量文件到仓库', description='添加批量文件到仓库')
    push_all_cmd.add_argument('box', help='仓库id或仓库名字')
    push_all_cmd.add_argument('files', nargs='*')
    push_all_cmd.set_defaults(func=pushall)

    list_cmd = subparsers.add_parser('list', help='列出仓库文件', description='列出仓库文件')
    list_cmd.add_argument('box', nargs='?')
    list_cmd.set_defaults(func=list)

    pull_cmd = subparsers.add_parser('pull', help='从仓库拉取文件', description='从仓库拉取文件')
    pull_cmd.add_argument('tag')
    pull_cmd.set_defaults(func=pull)

    log_cmd = subparsers.add_parser('log', help='查看文件记录信息', description='查看文件记录信息')
    log_cmd.add_argument('file')
    log_cmd.set_defaults(func=log)

    args = parser.parse_args()
    args.func(args)
    