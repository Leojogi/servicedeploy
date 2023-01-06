import paramiko
import sys

class SSHClient:
    def __init__(self, host, username, password, port=22):
        # 创建ssh客户端
        client = paramiko.SSHClient()
        # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接SSH服务端，以用户名和密码进行认证
        try:
            client.connect(hostname=host, port=port, username=username, password=password)
        except Exception as err:
            print("服务器连接失败")
            print(err)
            sys.exit()

        self.ssh = client

    def close(self):
         self.ssh.close()
