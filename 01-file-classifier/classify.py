#!/usr/bin/python
#-*- coding:utf-8 -*-
import argparse
import os
import json
import shutil
import sys
import time
from uuid import uuid4

DEFAULT_KEY = 'default'
BACKUP_FILE = '.backup.json'

# 防止迁移的时候出现文件重名的情况
def unique_covert(file_path):
    new_path = '|'.join(file_path.split(os.sep)[:-1])
    if not new_path:
        return file_path
    return os.path.basename(file_path) + ' (' + new_path + ')'

def coroutine(gen):
    def wrapper(*arg, **kws):
        coroutine = gen(*arg, **kws)
        next(coroutine)
        return coroutine
    return wrapper

@coroutine
def save_back_up(target_dir):
    string_len   = len(target_dir)
    back_up_file = os.path.join(target_dir, BACKUP_FILE)
    if os.path.exists(back_up_file):
        go_back(target_dir)
    back_up_tree = {}
    while True:
        tup = yield
        if not tup:
            break
        (now, prev) = tup
        back_up_tree[now] = prev
    with open(back_up_file, 'w') as buf:
        json.dump(back_up_tree, buf, indent=4)        

# 按扩展名分类
def classify_by_ext(target_dir, tmp_dir):
    from collections import defaultdict
    ext_files = defaultdict(list)
    for dir_ in os.walk(target_dir):
        for f in dir_[2]:
            exts = f.split('.')
            key  = exts[-1] if len(exts) != 1 else DEFAULT_KEY
            ext_files[key].append(os.path.join(dir_[0], f))
    for ext, file_list in ext_files.items():
        dest_dir = os.path.join(tmp_dir, ext)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        for file_path in file_list:
            filename      = unique_covert(os.path.relpath(file_path, target_dir))
            dest          = os.path.join(dest_dir, filename)
            rel_file_path = os.path.relpath(file_path, target_dir)
            shutil.move(file_path, dest)
            yield (os.path.join(ext, filename), rel_file_path)
    yield None

# 按修改时间分类
def classify_by_mtime(target_dir, tmp_dir):
    for dir_ in os.walk(target_dir):
        base_dir = dir_[0]
        for f in dir_[2]:
            abs_file_path = os.path.join(base_dir, f)
            rel_file_path = os.path.relpath(abs_file_path, target_dir)
            if os.path.islink(abs_file_path):
                rel_dest_dir = 'link'
                dest_dir     = os.path.join(tmp_dir, 'link')
            else:
                mtime        = os.stat(abs_file_path)[8]
                (y, m, d)    = map(str, time.localtime(mtime)[:3])
                rel_dest_dir = os.path.join(y, m, d)
                dest_dir     = os.path.join(tmp_dir, rel_dest_dir)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            filename  = unique_covert(rel_file_path)
            dest_file = os.path.join(dest_dir, filename)
            shutil.move(abs_file_path, dest_file)
            yield (os.path.join(rel_dest_dir, filename), rel_file_path)
    yield None

# 按字母分类
def classify_by_first_letter(target_dir, tmp_dir):
    for dir_ in os.walk(target_dir):
        base_dir = dir_[0]
        for f in dir_[2]:
            abs_file_path = os.path.join(base_dir, f)
            rel_file_path = os.path.relpath(abs_file_path, target_dir)
            first_char = f[0]
            if first_char.isalnum():
                dest_dir = os.path.join(tmp_dir, first_char)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                filename  = unique_covert(rel_file_path)
                dest_file = os.path.join(dest_dir, filename)
                shutil.move(abs_file_path, dest_file)
                yield (os.path.join(first_char, filename), rel_file_path)
            else:
                shutil.move(abs_file_path, os.path.join(tmp_dir, f))
                yield (f, rel_file_path)
    yield None


def go_back(target_dir):
    target_dir = target_dir.decode('utf-8')
    tmp_dir    = os.path.join(os.path.dirname(os.path.dirname(target_dir)), str(uuid4()))
    os.mkdir(tmp_dir)
    back_up_tree = {}
    back_up_file = os.path.join(target_dir, BACKUP_FILE)
    if not os.path.exists(back_up_file):
        raise Exception('已经是初始状态')
    with open(back_up_file, 'rb') as buf:
        back_up_tree = json.load(buf)
    if not back_up_tree:
        raise Exception('备份文件已损坏或不存在')
    for src, old in back_up_tree.items():
        src_file  = os.path.join(target_dir, src)
        dest_file = os.path.join(tmp_dir, old)
        dest_dir  = os.path.dirname(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.move(src_file, dest_file)

    shutil.rmtree(target_dir, ignore_errors=False)
    os.rename(tmp_dir, target_dir)

def run(target_dir, classify_func):
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(target_dir)), str(uuid4()))
    os.mkdir(tmp_dir)

    save_backup_gen = save_back_up(target_dir)
    classify_gen    = classify_func(target_dir, tmp_dir)
    finished        = 0
    begin           = time.time()
    while True:
        tup      = classify_gen.send(None)
        finished += 1
        sys.stdout.write(u'已完成%s个文件\r' % finished)
        sys.stdout.flush()
        if not tup:
            break
        save_backup_gen.send(tup)
    print(u'已完成%s个文件，耗时%s秒' % (finished, time.time() - begin))

    shutil.rmtree(target_dir, ignore_errors=False)
    os.rename(tmp_dir, target_dir)
    try:
        save_backup_gen.send(None)
    except StopIteration:
        pass

def _main():
    parser = argparse.ArgumentParser(description='对目录进行文件整理归类.')
    parser.add_argument('directory', type=str, help='目标目录路径')
    parser.add_argument('-t', '--type', type=str, default='ext', choices=['ext', 'mtime', 'word', 'back'], help='分类方式')

    args       = parser.parse_args()
    target_dir = args.directory
    op         = args.type

    if op == 'ext':
        run(target_dir, classify_by_ext)
    elif op == 'mtime':
        run(target_dir, classify_by_mtime)
    elif op == 'word':
        run(target_dir, classify_by_first_letter)
    elif op == 'back':
        go_back(target_dir)
        print ('恢复完成')
    else:
        raise Exception('参数错误')

if __name__ == '__main__':
    _main()
