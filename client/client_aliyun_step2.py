import json
import os
import subprocess
import requests
import re
import configparser
import shutil
import datetime
import time


class Connection:
    class Server:
        def __init__(self, ip, port):
            self.ip = ip
            self.port = port

    def __init__(self, project, region):
        self.project = project
        self.region = region

    # 发送参数及线上版本信息给服务端
    def send_request_to_server(self, ip, port, project):
        server = self.Server(ip, port)
        url = 'http://{}:{}/api/online'.format(server.ip, server.port)

        # 读取数据
        with open('updated_services', 'r', encoding='utf-8') as fp:
            x = json.loads(fp.read())
        fp.close()
        # x = {"ngcv-alarm": "3.1.7-20230103055345.20580"}

        # 数据封装
        data = {}
        data['project'] = project
        data['service'] = x

        # http请求发送封装好的数据
        session = requests.session()
        res = session.post(url=url, json=data)
        session.close()
        return res.json()

    # 修改线上ansible的配置文件
    def modify_ansible_configfile(self, sourcedata):
        file = '/etc/ansible/group_vars/k8s'
        with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
            for HH in f1:
                f2.write(re.sub('true', 'false', HH))
        os.remove(file)
        os.rename("%s.bak" % file, file)

        with open(file, "r", encoding="utf-8") as f1, open("%s.bak" % file, "w", encoding="utf-8") as f2:
            for HH in f1:
                print('=====', HH)
                if HH.split(':')[0].replace(' ', '')[1:] in sourcedata.keys():
                    print("----------", HH.split(':')[0].replace(' ', '')[1:])
                    HH = HH.replace('false', 'true')
                    print(HH)
                f2.write(HH)
        os.remove(file)
        os.rename("%s.bak" % file, file)


if __name__ == '__main__':
    # 实例化ConfigParser,读取config.ini
    config = configparser.ConfigParser()
    config.read("config.ini")

    # 读取 [arg] 分组下的 project 的值
    HOST = config.get("arg", "host")
    PORT = config.get("arg", "port")
    Project = config.get("arg", "project")
    Region = config.get("arg", "region")

    c = Connection(Project, Region)

    # 发送参数给服务端
    print("发送请求给服务端")
    result = c.send_request_to_server(HOST, PORT, Project)
    print("请求的返回结果", result)

    # 修改线上ansible的配置文件
    # print("开始修改ansible配置文件")
    # c.modify_ansible_configfile(result)

    # 归档配置文件
    # shutil.copyfile("config.ini", "config.ini_{}".format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))



