from flask import Blueprint, request
from autodeployservice.utils import sshclient
import subprocess
import json
import shutil
import time


push_image = Blueprint('push_image', __name__)  # 蓝图

@push_image.route('/api/push_image', methods=['GET','POST'])
def push_image():
    project = json.loads(request.json)['project']
    service = json.loads(request.json)['service']
    # {"ngcv-alarm": "3.1.7-20230103055345.20580"}
    projectname = get_project_name(project)
    code = 0
    for key, value in service.items():
        filename = projectname + '-deployment.' + value
        docker_version = value
        tmp = list(docker_version)
        tmp[docker_version.rfind('.')] = '-'
        helm_version = ''.join(tmp)

        # 封装上线文件的数据
        x = 'domain:cloud/{}\ndocker_version:{}\nhelm_version:{}\n'.format(projectname, docker_version, helm_version)
        content = x + '{}:{}\n'.format(key, key)

        # 生成上线文件
        with open('/root/mmcheng/autodeployservice/pushimage/{}'.format(filename), 'w', encoding='utf-8') as fp:
            fp.write(content)
        fp.close()

        # 推送镜像
        cmd = '/root/push_online.sh /root/mmcheng/autodeployservice/pushimage/{}'.format(filename)
        obj = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = obj.wait()
        print("推送镜像的命令执行结果=====", r)
        code = code + r
        # 保留上线文件
        if not r:
            shutil.copyfile('/root/mmcheng/autodeployservice/pushimage/{}'.format(filename),
                        '/root/mmcheng/autodeployservice/pushimage/{}_{}'.format(filename, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))
        else:
            return '{}推送失败'.format(key)
            break

    if code == 0:
        return '镜像推送成功!'
    else:
        return '镜像推送失败！'

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
