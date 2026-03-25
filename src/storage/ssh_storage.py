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

    # 上下文管理器支持
    def __enter__(self):
        """进入上下文时建立连接"""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭连接"""
        self._disconnect()
        return False

    def _connect(self):
        """建立 SSH/SFTP 连接（带重试）"""
        import time
        import paramiko

        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                self._client = SSHClient()
                # 安全策略：优先加载系统 known_hosts
                self._client.load_system_host_keys()
                # 警告：AutoAddPolicy 会自动接受新主机密钥，存在 MITM 风险
                # 用户应确保首次连接到可信服务器
                self._client.set_missing_host_key_policy(AutoAddPolicy())

                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password,
                    timeout=self.TIMEOUT
                )
                self._sftp = self._client.open_sftp()
                logger.info(f"SSH connected: {self.host}:{self.port}")
                return
            except paramiko.AuthenticationException as e:
                # 认证失败不重试
                raise AuthenticationError(f"SSH authentication failed: {e}")
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    # 线性退避：2s, 4s, 6s
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        raise NetworkError(f"SSH connection failed after {self.MAX_RETRIES} retries: {last_error}")

    def _disconnect(self):
        """关闭连接"""
        if self._sftp:
            self._sftp.close()
            self._sftp = None
        if self._client:
            self._client.close()
            self._client = None
        logger.debug("SSH connection closed")

    # 辅助方法
    def _get_remote_path(self, path: str) -> str:
        """获取完整远程路径

        Args:
            path: 相对路径

        Returns:
            完整的远程路径
        """
        return f"{self.BACKUP_DIR}/{path}"

    def _ensure_backup_dir(self):
        """确保服务器备份目录存在"""
        try:
            self._sftp.stat(self.BACKUP_DIR)
        except FileNotFoundError:
            try:
                self._sftp.mkdir(self.BACKUP_DIR)
                logger.info(f"Created backup directory: {self.BACKUP_DIR}")
            except Exception as e:
                logger.warning(f"Failed to create backup directory: {e}")
        except Exception as e:
            logger.debug(f"Error checking backup directory: {e}")

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