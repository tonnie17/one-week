#-*- coding:utf-8 -*-
import textwrap
import requests
import math
import re

keyStr    = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

login_url = 'http://e.zhbit.com/jsxsd/xk/LoginToXk'

def encode_inp(inp):
  output = ""
  chr1   = chr2 = chr3 = ""
  enc1   = enc2 = enc3 = enc4 = ""
  i = 0;
  l  = len(inp)
  while i < l:
    try:
      chr1 = ord(inp[i])
    except:
      chr1 = 0
    try:
      chr2 = ord(inp[i + 1])
    except:
      chr2 = 0
    try:  
      chr3 = ord(inp[i + 2])
    except:
      chr3 = 0
    i += 3
    enc1 = chr1 >> 2;
    enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
    enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
    enc4 = chr3 & 63;
    if chr2 == 0:
        enc3 = enc4 = 64
    elif chr3 == 0:
        enc4 = 64
    output = output + keyStr[enc1] + keyStr[enc2] + keyStr[enc3] + keyStr[enc4]
    chr1 = chr2 = chr3 = ""
    enc1 = enc2 = enc3 = enc4 = ""
  return output

def get_login_payload(username, password):
  encoded = encode_inp(username) + "%%%" + encode_inp(password)
  return {'encoded' : encoded}

# 显示课表
def show_classes(session):
  r = session.get('http://e.zhbit.com/jsxsd/xskb/xskb_list.do')
  data = r.content
  classes = [['     ' for j in range(14)] for i in range(7)]
  for i, f in enumerate(re.finditer(r'.*kbcontent1.*?>(.+?)<', data)):
    day  = i % 7
    time = i / 7
    classes[day][time] = f.group(1)

  for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']:
    print (day.center(27)),
  print

  i = 0
  for time in range(14):
    for day in range(7):
      cls = classes[day][time]
      if cls == '&nbsp;':
        cls = ''
      print (cls.center(26)),
    print
    i += 1

def _main():
  import getpass
  username = raw_input('输入学号：')
  password = getpass.getpass('输入密码：')
  payload  = get_login_payload(username, password)
  s = requests.Session()
  r = s.post(login_url, payload)
  if not r.status_code == 200:
    raise
  show_classes(s)

if __name__ == '__main__':
  _main()
