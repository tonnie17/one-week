# pyboa.py

python web微型框架

实现功能：

+ 解析请求和产生响应（基于WebOb）
+ 路由解析（基于正则匹配）
+ 模版渲染（基于jinja2)

## 使用

```
from pyboa import PyBoa, render_template
import time

app = PyBoa()


@app.route('/', methods=['GET', 'POST'])
def index(req):
    # 获取请求方法
    print("req.method: {}".format(req.method))
    # 获取请求参数
    print("req.params: {}".format(req.params))
    # 获取GET参数
    print("req.GET: {}".format(req.GET))
    # 获取POST参数
    print("req.POST: {}".format(req.POST))
    # 获取Environ参数
    print("req.environ: {}".format(req.environ))

    return render_template("index.html", time=time.time())


@app.route('/page')
def page(req):
    return 'page'

# 这条语句会导致循环导入
# app.add_route('/page/{year:\d\d\d\d}', controller='test:page')
app.add_route('/page/{year:\d\d\d\d}', controller=page)

if __name__ == '__main__':
    app.run()
```
