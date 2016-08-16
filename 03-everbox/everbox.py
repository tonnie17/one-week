#!usr/bin/python
#-*- coding:utf-8 -*-
import os
import argparse
import hashlib
import binascii

try:
    import evernote
    from evernote.api.client import EvernoteClient
    import evernote.edam.type.ttypes as Types
    import evernote.edam.notestore.ttypes as NoteTypes
except:
    import sys
    print ('未安装evernote的扩展，请安装后重试')
    sys.exit(-1)

dev_token  = "S=s1:U=92d14:E=15de8ebccac:C=156913a9da8:P=1cd:A=en-devtoken:V=2:H=ca0bbceb23208c3cde8227aa5912761a"

print ('everbox正在初始化...')
client     = EvernoteClient(token=dev_token)
note_store = client.get_note_store()
notebooks  = note_store.listNotebooks()
print ('初始化完成!\n')

def create_repo(name):
    repo      = Types.Notebook()
    repo.name = name
    return repo

# def create_note(title, content, notebook_guid='', image_resource=None):
#     hash_hex = ''
#     note = Types.Note()
#     if notebook_guid:
#         note.notebookGuid = notebook_guid

#     if image_resource:
#         (resource, image_hash) = image_resource
#         note.resources = [resource]
#         hash_hex = binascii.hexlify(image_hash)

#     note.title = title
#     note.content = '''<?xml version="1.0" encoding="UTF-8"?>
#     <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
#     <en-note><caption>%s</caption>''' % content
#     if hash_hex:
#         note.content += '<en-media type="image/png" hash="%s"/>' % hash_hex
#     note.content += '</en-note>'

#     return note

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

def pull(args):
    print args

def list(args):
    print ('查询中...\n')

    def list_repo(repo_id):
        note_filter              = NoteTypes.NoteFilter()
        note_filter.notebookGuid = repo_id
        notes                    = note_store.findNotes(dev_token, note_filter, 0, 100).notes

        print ('| 文件id\t\t\t| 文件名称 |')
        for note in notes:
            print "%s %s" %(note.guid, note.title)

    if args.repo is None:
        print ('| 仓库名称 |')
        for nb in notebooks:
            print nb.guid, nb.name
            # n.serviceCreated, n.serviceUpdated
    else:
        for nb in notebooks:
            if nb.name == args.repo:
                list_repo(nb.guid)

def add(args):
    print args

def log(args):
    print args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='文本备份助手.')
    subparsers = parser.add_subparsers(title='操作命令')

    add_cmd  = subparsers.add_parser('add', help='添加文件到仓库', description='添加文件到仓库')
    add_cmd.add_argument('files', nargs='*')
    add_cmd.set_defaults(func=add)

    list_cmd = subparsers.add_parser('list', help='列出仓库文件', description='列出仓库文件')
    list_cmd.add_argument('repo', nargs='?')
    list_cmd.set_defaults(func=list)

    pull_cmd = subparsers.add_parser('pull', help='从仓库拉取文件', description='从仓库拉取文件')
    pull_cmd.add_argument('tag')
    pull_cmd.set_defaults(func=pull)

    log_cmd = subparsers.add_parser('log', help='查看文件记录信息', description='查看文件记录信息')
    log_cmd.add_argument('file')
    log_cmd.set_defaults(func=log)

    args = parser.parse_args()
    args.func(args)
    