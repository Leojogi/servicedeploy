#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, render_template
from autodeployservice.api import online
from autodeployservice.api import svn
from autodeployservice.api import arg
from autodeployservice.api import push_image

# 实例一个app
app = Flask(__name__)


urls = [online.online_version, svn.svn_version, arg.args, push_image.push_image]   # 将三个路由构建数组
for url in urls:
    app.register_blueprint(url)   # 将三个路由均实现蓝图注册到主app应用上


@app.route('/')
def index():
    msg = 'this is a main page!!'
    return render_template('index.html', data=msg)


if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0', port=5005)
