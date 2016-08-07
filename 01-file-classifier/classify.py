#-*- coding:utf-8 -*-
from collections import defaultdict
import os
import sys
import json
import shutil
from uuid import uuid4

DEFAULT_KEY = 'default'
BACKUP_FILE = 'backup.json'

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
        do_back_up(target_dir)
    back_up_tree = {}
    while True:
        tup = yield
        if not tup:
            break
        (now, prev) = tup
        back_up_tree[now] = prev
    with open(back_up_file, 'w') as buf:
        json.dump(back_up_tree, buf, indent=4)        

@coroutine
def classify_by_ext(target_dir, tmp_dir):
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
            src = '-'.join(file_path.split('/'))
            dest = os.path.join(dest_dir, src)
            shutil.move(file_path, dest)
            yield (os.path.join(target_dir, ext, src), os.path.relpath(file_path, target_dir))
    yield None

@coroutine
def classify_by_mtime(target_dir, tmp_dir):
    import time
    for dir_ in os.walk(target_dir):
        path = dir_[0]
        for f in dir_[2]:
            file_path = os.path.join(path, f)
            mtime     = os.stat(file_path)[8]
            (y, m, d) = map(str, time.localtime(mtime)[:3])
            dest_dir  = os.path.join(tmp_dir, y, m, d)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            src = '-'.join(file_path.split('/'))
            dest = os.path.join(dest_dir, src)
            shutil.move(file_path, dest)
            yield (os.path.join(target_dir, y, m, d, src), os.path.relpath(file_path, target_dir))
    yield None


def do_back_up(target_dir):
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(target_dir)), str(uuid4()))
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
        dest     = os.path.join(tmp_dir, old)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.move(src, dest)

    shutil.rmtree(target_dir, ignore_errors=False)
    os.rename(tmp_dir, target_dir)

def run(target_dir, classify_func):
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(target_dir)), str(uuid4()))
    os.mkdir(tmp_dir)

    save_backup_gen = save_back_up(target_dir)
    classify_gen = classify_func(target_dir, tmp_dir)
    while True:
        tup = classify_gen.send(None)
        if not tup:
            break
        save_backup_gen.send(tup)

    shutil.rmtree(target_dir, ignore_errors=False)
    os.rename(tmp_dir, target_dir)
    try:
        save_backup_gen.send(None)
    except StopIteration:
        pass

def _main():
    op         = sys.argv[1]
    target_dir = sys.argv[2]
    DIR_CACHE  = list(os.walk(target_dir))
    if op == '--ext':
        run(target_dir, classify_by_ext)
    elif op == '--mtime':
        run(target_dir, classify_by_mtime)
    elif op == '--backup':
        do_back_up(target_dir)
    else:
        raise Exception('参数错误')

if __name__ == '__main__':
    _main()

