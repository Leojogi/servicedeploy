import json
import subprocess
import time
import multiprocessing
import shutil
import datetime

from flask import Blueprint, request

online_version = Blueprint('online', __name__)  # 蓝图

@online_version.route('/api/online', methods=['POST'])
def get_service_version_online():
    print("request.values==========", request.values)
    print("request.json==========", request.json)
    project = json.loads(request.json)['project_name']
    service_list = json.loads(request.json)['service']
    projectname = get_project_name(project)

    # 保存线上aliyun的版本信息
    with open('aliyun_version.txt', 'w', encoding='utf-8') as fp:
        fp.write(request.json)
    fp.close()

    while True:
        # 等到60s，等Svn版本信息就位
        time.sleep(60)
        try:
            with open('need_to_deploy.txt', 'r', encoding='utf-8') as fp:
                need_to_deploy = fp.read()
            fp.close()
            if need_to_deploy:        # 如果获取到了need_to_deploy，则置将need_to_deploy.txt置为空，并跳出循环
                shutil.copyfile("/root/mmcheng/autodeployservice/need_to_deploy.txt",
                                "/root/mmcheng/autodeployservice/need_to_deploy.txt_{}".format(
                                    time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))
                with open('need_to_deploy.txt', 'w', encoding='utf-8') as fp:
                    fp.write('')
                fp.close()
                break
        except FileNotFoundError as e:
            print(e)
            print("please wait a while")

    dic = json.loads(need_to_deploy)
    need_to_deploy = dic['need_to_deploy']
    project_version = dic['project_version']
    print("比较之前的待执行列表=====", need_to_deploy)

    compared = {}
    if service_list:
        for key in need_to_deploy.keys():
            if key in service_list:
                compared[key] = need_to_deploy[key]
    else:
        compared = need_to_deploy
    print("比较过后的待执行列表=====", compared)

    # 推送镜像到线上仓库, 此处为非守护进程，不影响调用进程继续执行
    if compared:
        push_images_to_onlinerepo(projectname, compared, project_version)

    return json.dumps(compared)


def push_images_to_onlinerepo(proname, need_deploy, pro_version):
    cmd_ls = "sshpass -p hillstone2021 ssh 10.182.139.97 'ls -lrt /home/deployment_properity/ | grep {}$'".format(pro_version)
    output = subprocess.getoutput(cmd_ls)
    print("97环境的output====", output)
    filename = output.split('\n')[-1].split(' ')[-1]
    docker_version = filename[filename.find('.')+1:]
    print(docker_version)
    helm_version = docker_version[:docker_version.rfind('.')] + '-' + docker_version[docker_version.rfind('.')+1:]
    print(helm_version)

    # 封装上线文件的数据
    # file_date = {}
    # file_date['domain'] = 'cloud/{}'.format(proj)
    # file_date['docker_version'] = docker_version
    # file_date['helm_version'] = helm_version
    file = 'domain:cloud/{}\ndocker_version:{}\nhelm_version:{}\n'.format(proname, docker_version, helm_version)
    for key in need_deploy.keys():
        file = file + '{}:{}\n'.format(key, key)

    # 生成上线文件
    with open('/root/mmcheng/autodeployservice/push_image_file', 'w', encoding='utf-8') as fp:
        fp.write(file)
    fp.close()

    # 推送镜像
    # cmd = '/root/push_online.sh /root/mmcheng/autodeployservice/push_image_file'
    # result = subprocess.getoutput(cmd)
    # print("推送镜像的结果=====", result)


    # 保留上线文件
    shutil.copyfile("/root/mmcheng/autodeployservice/push_image_file", "/root/mmcheng/autodeployservice/push_image_file_{}".format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))


def get_project_name(project_name):
    project = "ERROR"
    if "sandbox" == project_name.lower():
        project = "sandbox"
    if "tip" == project_name.lower():
        project = "tip"
    if "cloudview" == project_name.lower():
        project = "cloudview"
    if "cps" == project_name.lower():
        project = "cps"
    if "ngcv" == project_name.lower():
        project = "ng-cloudview"
    return project
