import paramiko
import os
from stat import S_ISDIR

# 服务器信息
HOST = "43.153.156.249"
USER = "root"
PASSWORD = "jingyang@LINUX"
REMOTE_PATH = "/var/www/html/claude-backup"
LOCAL_PATH = "d:/CodeSpace/claudeFi/docs"

def upload_dir(sftp, local_dir, remote_dir):
    """递归上传目录"""
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_item_path = f"{remote_dir}/{item}"

        if os.path.isfile(local_path):
            print(f"上传: {item}")
            sftp.put(local_path, remote_item_path)
        elif os.path.isdir(local_path):
            try:
                sftp.mkdir(remote_item_path)
            except:
                pass
            upload_dir(sftp, local_path, remote_item_path)

def main():
    print(f"连接到 {HOST}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USER, password=PASSWORD)
        print("连接成功!")

        # 创建远程目录
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_PATH}")
        stdout.read()

        # 创建 SFTP
        sftp = ssh.open_sftp()

        # 上传文档
        print("上传文档...")
        upload_dir(sftp, LOCAL_PATH, REMOTE_PATH)

        sftp.close()
        ssh.close()

        print(f"\n部署完成! 访问: http://{HOST}/claude-backup/")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()