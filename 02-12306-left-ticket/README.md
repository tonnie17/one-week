# left_ticket.py

12306余票查询工具。


## 用法

```
usage: left_ticket.py [-h] [-f FROM_CITY] [-t TO_CITY] [-d DATE] [-s]

查询12306车次余票.

optional arguments:
  -h, --help            show this help message and exit
  -f FROM_CITY, --from_city FROM_CITY
                        起始城市
  -t TO_CITY, --to_city TO_CITY
                        目标城市
  -d DATE, --date DATE  日期，格式如：2016-08-14，无指定即为当天
  -s, --student         学生票
```

查询车票

```
python left_ticket.py -f 唐家湾 -t 广州南 -d 8-26 # 年份默认为今年
```

输出

```
车次序号     起始站 出发站 终点站 时间 一等座 二等座
6e000C761003 珠海->唐家湾->广州南 09:48  54   257
6e000C762202 珠海->唐家湾->广州南 11:43  39   235
6e000C763002 珠海->唐家湾->广州南 13:40  43   307
6e000C763802 珠海->唐家湾->广州南 14:45  58   329
6e000C764602 珠海->唐家湾->广州南 16:43  57   312
6e000C765802 珠海->唐家湾->广州南 18:38  62   356
6e000C766202 珠海->唐家湾->广州南 19:45  55   357
6e000C767602 珠海->唐家湾->广州南 22:10  64   389
6e000C767802 珠海->唐家湾->广州南 22:33  64   384
```
