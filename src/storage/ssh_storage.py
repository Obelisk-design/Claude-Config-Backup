# -*- coding: utf-8 -*-
"""SSH/SFTP 存储实现"""

from typing import Optional, Any, Dict, List
from paramiko import SSHClient, AutoAddPolicy

from storage.base import StorageBase
from core.exceptions import BackupError, RestoreError, NetworkError, AuthenticationError
from utils.logger import logger


class SSHStorage(StorageBase):
    """SSH/SFTP 存储实现

    使用 SFTP 协议上传/下载备份文件到远程服务器。
    """

    # 连接配置
    BACKUP_DIR = ".claude-backups"  # 服务器上的固定目录
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 30  # seconds

    def __init__(self, host: str, port: int, user: str, password: str):
        """初始化 SSH 存储实例

        Args:
            host: SSH 服务器地址
            port: SSH 端口（默认 22）
            user: 用户名
            password: 密码
        """
        self.host = host
        self.port = port or 22
        self.user = user
        self.password = password
        self._client: Optional[SSHClient] = None
        self._sftp = None

    # StorageBase 抽象方法实现（后续任务中完善）
    def upload(self, local_path: str, remote_path: str) -> bool:
        raise NotImplementedError("upload method not implemented")

    def download(self, remote_path: str, local_path: str) -> bool:
        raise NotImplementedError("download method not implemented")

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        raise NotImplementedError("list_files method not implemented")

    def delete(self, remote_path: str) -> bool:
        raise NotImplementedError("delete method not implemented")

    def get_file_url(self, remote_path: str) -> Optional[str]:
        return None  # SSH 没有 HTTP URL