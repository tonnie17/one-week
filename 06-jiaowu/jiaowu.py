import requests
import math
import cookielib
import urllib2
import urllib

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

def _main():
  username = ''
  password = ''
  payload  = get_login_payload(username, password)
  s = requests.Session()
  r = s.post(login_url, payload)
  r = s.get('http://e.zhbit.com/jsxsd/xskb/xskb_list.do')
  print r.content

if __name__ == '__main__':
  _main()
