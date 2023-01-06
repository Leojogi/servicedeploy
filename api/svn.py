from flask import Blueprint, render_template, request, url_for
import json
svn_version = Blueprint('svn', __name__)  # 蓝图


@svn_version.route('/api/svn', methods=['POST'])
def get_service_version_svn():
    print('request.values=========', request.values)
    print('request.json===========', request.json)
    dic = json.loads(request.json)
    project_version = dic['project']
    svn_service_version = dic['service']
    need_deploy = match(svn_service_version, project_version)
    print("有更新的列表==============", need_deploy)

    # 将待执行列表写入need_to_deploy.txt
    with open('need_to_deploy.txt', 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(need_deploy))
    fp.close()

    # 数据封装
    response = {
        'data': {},
        'response_code': 0,
        'response_msg': 'ok'
    }
    return response


# 将svn中与线上的版本比较
def match(svn_service_version, project_version) -> dict:
    with open('aliyun_version.txt', 'r', encoding='utf-8') as fp:
        online_service_version = json.loads(fp.read())['service_version']
    fp.close()

    need_to_deploy = {}
    for key_svn, value_svn in svn_service_version.items():
        if key_svn in online_service_version.keys():
            if value_svn > online_service_version[key_svn]:
                # 如果有变化
                need_to_deploy[key_svn] = value_svn         # 待上线的微服务
        else:
            need_to_deploy[key_svn] = value_svn             # 待上线的微服务
    dic = {}
    dic['project_version'] = project_version
    dic['need_to_deploy'] = need_to_deploy

    return dic
