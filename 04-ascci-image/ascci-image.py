#-*- coding:utf-8 -*-
from PIL import Image
import sys
import kmeans
import os

# 加上颜色
class BColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

COLORS =  {
   'white': (255, 255, 255),
   'black': (0, 0, 0),
}

def _main():
  pic      = os.path.abspath(sys.argv[1])
  img      = Image.open(pic)
  width    = int(img.size[0])
  height   = int(img.size[1])
  gray_img = img.convert('L')
  scale    = width // 100
  char_lst = ' .:-=+*#%@'
  char_len = len(char_lst)

  arr = []
  for y in range(0, height, scale):
    for x in range(0, width, scale):
      brightness = 0
      r = g = b = 0
      count = 0
      for ix in range(scale):
        for iy in range(scale):
          if (x + ix) == width or (y + iy) == height:
            break
          count += 1
          b = 255 - gray_img.getpixel((x+ix, y+iy))
          brightness += b
      choice = int(char_len * (brightness // count / 255) ** 1.2)
      if choice >= char_len:
        choice = char_len
      sys.stdout.write(char_lst[choice])
    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
  _main()
