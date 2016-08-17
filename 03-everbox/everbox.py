#!usr/bin/python
#-*- coding:utf-8 -*-
import argparse
import binascii
import hashlib
import os
import sys
from datetime import datetime, date

try:
    import evernote
    from evernote.api.client import EvernoteClient
    import evernote.edam.type.ttypes as Types
    import evernote.edam.notestore.ttypes as NoteTypes
except:
    print ('未安装evernote的扩展，请安装后重试')
    sys.exit(-1)

try:
    import socket
    s = socket.create_connection(('sandbox.evernote.com', 80), 5)
except Exception,e:
    print('无法连接到evernote，请检查网络连接')
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

get_client    = LazyGet(lambda : EvernoteClient(token=dev_token), '初始化组件...', '初始化成功', '初始化失败')
get_box_store = LazyGet(lambda : get_client().get_note_store(), '连接evernote...', '连接成功', '连接失败')
get_boxes     = LazyGet(lambda : get_box_store().listNotebooks(), '获取仓库信息...', '获取仓库成功', '获取失败')

def create_box(name):
    box      = Types.Notebook()
    box.name = name
    return box

def create_file(title, content, box_id='', image_resource=None):
    hash_hex = ''
    file = Types.Note()
    if box_id:
        file.notebookGuid = box_id

    if image_resource:
        (resource, image_hash) = image_resource
        file.resources         = [resource]
        hash_hex               = binascii.hexlify(image_hash)

    file.title = title
    file.content = '''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
    <en-note><caption>%s</caption>''' % content
    if hash_hex:
        file.content += '<en-media type="image/png" hash="%s"/>' % hash_hex
    file.content += '</en-note>'

    return file

def parse_file(content):
    file_content = ''
    try:
        content = content.split('<caption>')[1].split('</caption>')[0]
    except:
        pass

    media_index = content.find('<en-media')
    content = content[:media_index]

    file_lst = content.split('<br/>')
    for content in file_lst:
        file_content += content

    return file_content

def load_file(guid):
    file = None
    try:
        file = get_box_store().getNote(dev_token, guid, True, True, False, False)
    except Exception, e:
        return None

    file_content = parse_file(file.content)
    return {
        'title': file.title,
        'content': file_content,
        'created': date.fromtimestamp(file.created / 100).strftime('%d/%m/%Y')
    }

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
    if not id_or_name:
        return ''
    box = get_box_by_id(args.box)
    if not box:
        box = get_box_by_name(args.box)
    if not box:
        print ('指定仓库不存在')
        sys.exit(-1)
    return box

def push_to_box(note):
    note = get_box_store().createNote(dev_token, note)
    return note

def get_yn_input(msg):
    while True:
        res = raw_input('%s，是请按y，不是请输入n：' % msg)
        if res in ('y', 'n'):
            break
    return True if res == 'y' else False

def get_abs_dir(directory):
    dest_dir = directory or os.path.abspath('.')
    if not os.path.exists(dest_dir) or not os.path.isdir(dest_dir):
        print ('指定目录不存在')
        sys.exit(-1)
    dest_dir = os.path.abspath(os.path.normpath(os.path.expanduser(dest_dir)))
    return dest_dir

def datetime_format(time):
    return datetime.fromtimestamp(int(str(time)[:-3])).strftime('%Y-%m-%d %H:%M:%S')

def init(args):
    boxname = args.box
    box     = create_box(boxname)        
    try:
        box     = get_box_store().createNotebook(dev_token, box)
        if not box:
            raise
        print ('创建成功，id为：%s' % box.guid)
    except Exception,e:
        print ('创建失败')

def pull(args):
    dest_dir   = get_abs_dir(args.directory)
    skip_cover = args.yes
    finished   = 0
    for f in args.files:
        try:
            flag       = os.path.basename(f)
            file       = load_file(flag)
            if not file:
                box         = get_box(args.box)
                file_filter = NoteTypes.NoteFilter()
                if box:
                    file_filter.notebookGuid = box.guid
                file_filter.title = flag
                files             = get_box_store().findNotes(dev_token, file_filter, 0, 100).notes
                file              = load_file(files[-1].guid)
            if not file:
                raise
            ouput_file = os.path.join(dest_dir, file['title'])
            if os.path.exists(ouput_file):
                if not skip_cover:
                    if not get_yn_input('文件 %s 已存在，是否覆盖' % ouput_file):
                        continue
            with open(ouput_file, 'w') as fp:
                fp.write(file['content'])
            finished += 1
            sys.stdout.write('已拉取：%s个文件\r' % finished)
            sys.stdout.flush()
        except Exception,e:
            print e
            print ('文件：%s拉取失败，跳过..' % f)
    print('成功拉取：%s个文件' % finished)

def list(args):
    def list_box(box):
        file_filter              = NoteTypes.NoteFilter()
        file_filter.notebookGuid = box.guid
        files                    = get_box_store().findNotes(dev_token, file_filter, 0, 100).notes

        if not files:
            print '仓库没有任何文本'
        else:
            print ('| 文本id                           | 文本名称 | 创建时间')
            for f in reversed(files):
                print "%s %s %s" %(f.guid, f.title, datetime_format(f.created))

    # 没有指定仓库，则列出所有仓库
    if args.box is None:
        boxes = get_boxes()
        print ('| 仓库id                           | 仓库名称 | 创建时间')
        for box in boxes:
            print box.guid, box.name, box.serviceCreated
    else:
        box = get_box(args.box)
        list_box(box)

def push(args):
    box      = get_box(args.box)
    abs_path = os.path.abspath(os.path.normpath(args.file))
    if not os.path.exists(abs_path):
        print ('文本路径不存在')
        return
    try:
        with open(abs_path, 'rb') as fp:
            title = os.path.basename(abs_path)
            if args.box:
                box  = get_box(args.box)
                file = create_file(title, fp.read(), box.guid, '')
            else:
                print ('无指定仓库，将使用默认仓库')
                file = create_file(title, fp.read(), None, '')
            push_to_box(file)
            print ('%s 上传成功' % abs_path)
    except Exception, e:
        print ('上传%s时，发生异常' % f)

def pushall(args):
    files  = args.files
    to_add = []
    for f in files:
        abs_path = os.path.abspath(os.path.normpath(f))
        if not os.path.exists(abs_path):
            print ('%s：文本路径不存在' %f)
            break
        if os.path.getsize(abs_path) > 1000 * 1000 * 10: # 10M
            print ('%s: 文本体积大于10M' %f)
            break
        to_add.append(os.path.abspath(os.path.normpath(f)))
    else:
        total    = len(to_add)
        finished = 0
        for f in to_add:
            try:
                with open(f, 'rb') as fp:
                    title = os.path.basename(f)
                    if args.box:
                        box  = get_box(args.box)
                        file = create_file(title, fp.read(), box.guid, '')
                    else:
                        print ('无指定仓库，将使用默认仓库')
                        file = create_file(title, fp.read(), None, '')
                    push_to_box(file)
                    finished += 1
                    sys.stdout.write('已上传(%s/%s)个文本\r' % (finished, total))
                    sys.stdout.flush()
            except Exception, e:
                print ('上传%s时，发生异常' % f)
        print('已上传(%s/%s)个文本' % (finished, total))

def remove(args):
    guid = args.guid
    try:
        get_box_store().deleteNote(dev_token, guid)
        print ('删除成功')
    except:
        print ('删除失败')

def drop(args):
    box = get_box(args.box)
    try:
        get_box_store().expungeNotebook(dev_token, box.guid)
        print ('删除成功')
    except:
        print ('删除失败')

def drag(args):
    dest_dir = get_abs_dir(args.directory)
    file     = load_file(args.guid)
    if not file:
        print ('文件拉取失败')
    output_file = os.path.join(os.path.join(dest_dir, file['title']));
    if os.path.exists(output_file):
        if not get_yn_input('文件 %s 已存在，是否覆盖' % output_file):
            return
    with open(output_file, 'w') as fp:
        fp.write(file['content'])
    print ('拉取完成')
    remove(args)

def log(args):
    file     = args.file
    abs_path = os.path.abspath(os.path.normpath(file))
    if not os.path.exists(abs_path):
        print ('文件不存在!')
        return
    file_name         = os.path.basename(abs_path)
    file_filter       = NoteTypes.NoteFilter()
    file_filter.title = file_name
    files             = get_box_store().findNotes(dev_token, file_filter, 0, 100).notes
    if not files:
        print ('仓库中不存在该文件的记录')
        return
    print ('| 文本id                           | 文本名称 | 仓库\t | 创建时间')
    for f in files:
        print '%s %s %s %s' %(f.guid, f.title, get_box_by_id(f.notebookGuid).name, datetime_format(f.created))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='文本备份助手.')
    subparsers = parser.add_subparsers(title='操作命令')

    init_cmd  = subparsers.add_parser('init', help='新建一个仓库', description='新建一个仓库')
    init_cmd.add_argument('box', help='仓库名字')
    init_cmd.set_defaults(func=init)

    push_cmd  = subparsers.add_parser('push', help='添加文本到仓库', description='添加文本到仓库')
    push_cmd.add_argument('-b', '--box', help='仓库id或仓库名字')
    push_cmd.add_argument('file')
    push_cmd.set_defaults(func=push)

    push_all_cmd  = subparsers.add_parser('pushall', help='添加批量文本到仓库', description='添加批量文本到仓库')
    push_all_cmd.add_argument('-b', '--box', help='仓库id或仓库名字')
    push_all_cmd.add_argument('files', nargs='*', help='文本路径，多个以空格间隔')
    push_all_cmd.set_defaults(func=pushall)

    list_cmd = subparsers.add_parser('list', help='列出仓库或文本', description='列出仓库或文本')
    list_cmd.add_argument('box', nargs='?', help='仓库id或仓库名字')
    list_cmd.set_defaults(func=list)

    drop_cmd = subparsers.add_parser('drop', help='删除一个仓库', description='删除一个仓库')
    drop_cmd.add_argument('box', help='仓库id或仓库名字')
    drop_cmd.set_defaults(func=drop)

    drag_cmd = subparsers.add_parser('drag', help='从远程拉取一个文件同时删除记录', description='从远程拉取一个文件同时删除记录')
    drag_cmd.add_argument('guid', help='文本guid')
    drag_cmd.add_argument('directory', type=str, help='拉取目录')
    drag_cmd.set_defaults(func=drag)

    remove_cmd = subparsers.add_parser('remove', help='从仓库删除指定id的文本', description='从仓库删除指定id的文本')
    remove_cmd.add_argument('guid', help='文本guid')
    remove_cmd.set_defaults(func=remove)

    pull_cmd = subparsers.add_parser('pull', help='从仓库拉取文本', description='从仓库拉取文本')
    pull_cmd.add_argument('-b', '--box', help='仓库id或仓库名字')
    pull_cmd.add_argument('-y', '--yes', action='store_true', help='忽略覆盖提示')
    pull_cmd.add_argument('files', nargs='*', help='文本guid或名称（若用名称则取最新的同名），多个以空格间隔')
    pull_cmd.add_argument('directory', type=str, help='拉取目录')
    pull_cmd.set_defaults(func=pull)

    log_cmd = subparsers.add_parser('log', help='查看文本记录信息', description='查看文本记录信息')
    log_cmd.add_argument('file', help='文本名称')
    log_cmd.set_defaults(func=log)

    args = parser.parse_args()
    args.func(args)
    