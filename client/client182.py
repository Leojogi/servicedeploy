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

    def __init__(self, project, region, service):
        self.project = project
        self.region = region
        self.service = service

    # 发送参数及线上版本信息给服务端
    def send_request_to_server(self, ip, port, service_version):
        server = self.Server(ip, port)
        url = 'http://{}:{}/api/online'.format(server.ip, server.port)

        # 封装数据
        data = {}
        data['project_name'] = self.project
        data['region'] = self.region
        data['service'] = self.service
        data['service_version'] = service_version

        # http请求发送封装好的数据
        session = requests.session()
        res = session.post(url=url, json=json.dumps(data))
        session.close()
        return res.json()

    # 获取到线上的版本信息
    def get_service_version_aliyun(self):
        cmd = 'helm list'
        output = subprocess.getoutput(cmd)
        online_version = {}
        raws = output.split('\n')
        raws = raws[1:]
        for raw in raws:
            arrays = raw.split()
            online_version[arrays[0]] = arrays[-2].split('-')[-1]
        return online_version

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
    x = config.get("arg", "service")
    if not x:
        Service = []
    else:
        Service = x.split(',')
    print("指定的service=====", Service)

    c = Connection(Project, Region, Service)

    # 获取到线上的版本信息
    online_service = c.get_service_version_aliyun()
    print("online_service============", online_service)

    # 发送参数及线上版本信息给服务端
    print("发送请求给服务端")
    result = c.send_request_to_server(HOST, PORT, online_service)
    print("请求的返回的待执行列表结果", result)

    # 修改线上ansible的配置文件
    print("开始修改ansible配置文件")
    c.modify_ansible_configfile(result)

    # 归档配置文件
    shutil.copyfile("config.ini", "config.ini_{}".format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))



