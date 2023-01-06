import json
import time
import shutil
from autodeployservice.utils import sshclient

from flask import Blueprint, request

online_version = Blueprint('online', __name__)  # 蓝图

@online_version.route('/api/online', methods=['POST'])
def get_service_version_online():
    print("request.values==========", request.values)
    print("request.json==========", request.json)
    project = json.loads(request.json)['project_name']
    # service_list = json.loads(request.json)['service']
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

    c = sshclient.SSHClient("10.182.139.97", "root", "hillstone2021", 22)
    cmd = 'ls -lrt /home/deployment_properity/ | grep {} | grep {}$'.format(projectname, project_version)

    # 打开一个Channel并执行命令
    stdin, stdout, stderr = c.ssh.exec_command(cmd)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
    output = stdout.read().decode('utf-8')
    if output:
        print(output)
    else:
        output = stderr.read().decode('utf-8')
        print(output)

    filename = []
    for item in output.split('\n')[:-1]:
        filename.append(item.split(' ')[-1])
    filename.reverse()
    # ['ng-cloudview-deployment.3.1.6-202212270523.20509', 'ng-cloudview-deployment.3.1.6-202212270241.20509']

    need_to_deploy_new = {}
    for key in need_to_deploy.keys():
        need_to_deploy_new[key] = 'null'
        for file in filename:
            cmd = 'grep {} /home/deployment_properity/{}'.format(key, file)
            print(cmd)
            stdin, stdout, stderr = c.ssh.exec_command(cmd)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
            output = stdout.read().decode('utf-8')
            if output:
                print(output)
                need_to_deploy_new[key] = file[file.find('.') + 1:]
                break
            else:
                output = stderr.read().decode('utf-8')
                print(output)
    c.close()
    print("need_to_deploy_new========", need_to_deploy_new)

    # print("比较之前的待执行列表=====", need_to_deploy)
    # compared = {}
    # if service_list:
    #     for key in need_to_deploy.keys():
    #         if key in service_list:
    #             compared[key] = need_to_deploy[key]
    # else:
    #     compared = need_to_deploy
    #
    # print("比较过后的待执行列表=====", compared)
    #
    # # 推送镜像到线上仓库, 此处为非守护进程，不影响调用进程继续执行
    # if compared:
    #     push_images_to_onlinerepo(projectname, compared, project_version)
    # return json.dumps(compared)
    return json.dumps(need_to_deploy_new)

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