from flask import Blueprint, render_template, request, url_for, g
import json

args = Blueprint('arg', __name__)  # 蓝图


@args.route('/api/arg', methods=['GET'])
def post_arg():
    with open('aliyun_version.txt', 'r', encoding='utf-8') as fp:
        data = json.loads(fp.read())
    fp.close()

    projectname = data['project_name']
    if projectname:
        data['project_name'] = None
        with open('aliyun_version.txt', 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(data))
        fp.close()

    # 数据封装
    response = {
        'data': {'project_name': projectname},
        'response_code': 0,
        'response_msg': 'ok'
    }
    return response