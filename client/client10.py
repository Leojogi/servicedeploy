import json
import socket
import time

import requests
import subprocess

class Connection:
    class Server:
        def __init__(self, ip, port):
            self.ip = ip
            self.port = port

    def __init__(self, project=None, region=None):
        self.project = project
        self.region = region

    def get_arg(self):
        server = self.Server(HOST, PORT)
        url = r'http://{}:{}/api/arg'.format(server.ip, server.port)

        session = requests.session()
        r = session.get(url=url, verify=False)
        print("get_arg======", r.json())
        project_name = r.json()['data']['project_name']
        session.close()
        return project_name

    def send_request_to_server(self, data):
        server = self.Server(HOST, PORT)
        url = r'http://{}:{}/api/svn'.format(server.ip, server.port)

        # http请求发送封装好的数据
        session = requests.session()
        r = session.post(url=url, json=json.dumps(data))
        print('send_request_to_server的结果=====', r)
        # print("send_request_to_server======", r.json())
        session.close()
        return r.json()


class Project:
    def __init__(self, project):
        self.project_name = project
        self.service_version_dic = {}

    def get_service_version_svn(self):
        mic_service_lst = []

        # 如果项目是sandbox
        if self.project_name == 'sandbox':
            release_url = self.get_release_url()
            project_version = self.get_latest_version(release_url)
            path_base = self.get_release_url() + "/sandbox/service/"
            print("sandbox url", path_base)
            service_lst = self.get_service_name(path_base)
            for service_name in service_lst:
                path = path_base + service_name
                print("===========", path)
                r = self.is_mic_service(path, service_name)
                # if_mic_service如果判断否，会返回None
                if r:
                    mic_service_lst.append(r)
            for item in mic_service_lst:
                path = path_base + item
                self.service_version_dic[item.replace('_', '-')] = self.get_latest_version(path)  # 微服务名字格式处理

        # 如果项目是tip
        if self.project_name == 'tip':
            release_url = self.get_release_url()
            project_version = self.get_latest_version(release_url)
            path_base = self.get_release_url() + "/threat_intelligence/service/"
            print("tip url", path_base)
            service_lst = self.get_service_name(path_base)
            for service_name in service_lst:
                path = path_base + service_name
                print("===========", path)
                r = self.is_mic_service(path, service_name)
                # if_mic_service如果判断否，会返回None
                if r:
                    mic_service_lst.append(r)
            for item in mic_service_lst:
                path = path_base + item
                self.service_version_dic[item.replace('_', '-')] = self.get_latest_version(path)  # 微服务名字格式处理

        # 如果项目是cloudview
        if self.project_name == 'cloudview':
            release_url = self.get_release_url()
            project_version = self.get_latest_version(release_url)
            path_base = self.get_release_url()
            print("cloudview url", path_base)
            service_lst = self.get_service_name(path_base + "/components/")
            for i in ['Cloud_AppServer', 'Cloud_Self_Client', 'Cloud_Self_Server', 'Cloud_WebServer']:
                service_lst.append(i)

            print('微服务列表=====', service_lst)

            for service_name in service_lst:
                if service_name == "Cloud_AppServer" or service_name == "Cloud_WebServer":
                    path = path_base + "/" + service_name
                    print("===========", path)
                    r = self.is_mic_service(path, service_name)
                    # if_mic_service如果判断否，会返回None
                    if r:
                        mic_service_lst.append(r)
                elif service_name == "Cloud_Self_Client" or service_name == "Cloud_Self_Server":
                    path = path_base + "/Cloud_Self_Component/" + service_name
                    print("===========", path)
                    r = self.is_mic_service(path, service_name)
                    if r:
                        mic_service_lst.append(r)
                else:
                    path = path_base + "/components/" + service_name
                    print("===========", path)
                    r = self.is_mic_service(path, service_name)
                    # if_mic_service如果判断否，会返回None
                    if r:
                        mic_service_lst.append(r)

            for item in mic_service_lst:
                if item == "Cloud_AppServer" or item == "Cloud_WebServer":
                    path = path_base + "/" + item
                    self.service_version_dic[item] = self.get_latest_version(path)
                elif item == "Cloud_Self_Client" or item == "Cloud_Self_Server":
                    path = path_base + "/Cloud_Self_Component/" + item
                    self.service_version_dic[item] = self.get_latest_version(path)
                else:
                    path = path_base + "/components/" + item
                    self.service_version_dic[item.replace('_', '-')] = self.get_latest_version(path)  # 微服务名字格式处理

        # 如果项目是cps
        if self.project_name == 'cps':
            release_url = self.get_release_url()
            project_version = self.get_latest_version(release_url)
            path_base = self.get_release_url() + "/cloud_platform_service/service/"
            print("cps url", path_base)
            service_lst = self.get_service_name(path_base)
            for service_name in service_lst:
                path = path_base + service_name
                print("===========", path)
                r = self.is_mic_service(path, service_name)
                # if_mic_service如果判断否，会返回None
                if r:
                    mic_service_lst.append(r)
            for item in mic_service_lst:
                path = path_base + item
                self.service_version_dic[item.replace('_', '-')] = self.get_latest_version(path)  # 微服务名字格式处理

        # 如果项目是ngcv
        if self.project_name == 'ngcv':
            release_url = self.get_release_url()
            project_version = self.get_latest_version(release_url)
            path_base = self.get_release_url() + "/NG-cloudview/service/"
            print("ngcv url", path_base)
            service_lst = self.get_service_name(path_base)
            for service_name in service_lst:
                path = path_base + service_name
                print("===========", path)
                r = self.is_mic_service(path, service_name)
                # if_mic_service如果判断否，会返回None
                if r:
                    mic_service_lst.append(r)
            for item in mic_service_lst:
                path = path_base + item
                self.service_version_dic[item.replace('_', '-')] = self.get_latest_version(path)  # 微服务名字格式处理

        return self.service_version_dic, project_version

    def get_release_url(self):
        release_url = r"https://10.200.8.201/%s/branches/%s" % (self.get_svn_name(), self.get_release_name())
        return release_url

    # 拿到svn库中最新的版本
    def get_latest_version(self, path) -> str:
        cmd = "svn log -l 1 %s" % path
        r = subprocess.getoutput(cmd)
        raws = r.split('\n')
        version_r = raws[1].split('|')[0]
        version = version_r[1:-1]
        return version

    # 获取微服务名
    def get_service_name(self, path) -> list:
        service_list = []
        cmd = "svn list %s" % path
        result = subprocess.getoutput(cmd)
        raws = result.split('\n')
        for raw in raws:
            if raw[-1] == '/':
                service_list.append(raw[:-1])
        return service_list

    # 判断是否是微服务，有chart和docker文件夹说明是微服务
    def is_mic_service(self, path, service_name1):
        path = path + "/src/main/"
        cmd = "svn list %s" % path
        result = subprocess.getoutput(cmd)
        raws = result.split('\n')
        if 'chart/' in raws and 'docker/' in raws:
            return service_name1

    # 获取release name
    def get_release_name(self):
        project_release_name = "ERROR"
        if "sandbox" == self.project_name.lower():
            project_release_name = "CLOUDSANDBOX_REL"
        if "tip" == self.project_name.lower():
            project_release_name = "CLOUDTIP_REL"
        if "cloudview" == self.project_name.lower():
            project_release_name = "CLOUDVIEW_REL"
        if "cps" == self.project_name.lower():
            project_release_name = "CPS_REL"
        if "ngcv" == self.project_name.lower():
            project_release_name = "NG_CV_REL"
        return project_release_name

    # 拿到snv name
    def get_svn_name(self):  # 拿到snv name
        project_svn_name = "ERROR"
        if "sandbox" == self.project_name.lower():
            project_svn_name = "Cloud_Sandbox"
        if "tip" == self.project_name.lower():
            project_svn_name = "Cloud_TIP"
        if "cloudview" == self.project_name.lower():
            project_svn_name = "Cloud_Intelligence"
        if "cps" == self.project_name.lower():
            project_svn_name = "Cloud_Intelligence"
        if "ngcv" == self.project_name.lower():
            project_svn_name = "Cloud_Intelligence"
        return project_svn_name


if __name__ == '__main__':
    HOST = '10.182.138.221'
    PORT = 5005

    while True:
        # 实例化
        c = Connection()
        # 获取Project_name
        Project_name = c.get_arg()
        print("Project_name=======", Project_name)

        # 如果拿到的Project_ame不是空，则获取Svn代码库中对应的版本
        if Project_name:
            # 获取svn版本信息
            p = Project(Project_name)
            service_version_dic, proj_version = p.get_service_version_svn()
            dic = {}
            dic['project'] = proj_version
            dic['service'] = service_version_dic
            print('将要返回的结果service_version_dic', dic)
            result = c.send_request_to_server(dic)
            print("请求的返回的svn结果", result)
        time.sleep(30)


