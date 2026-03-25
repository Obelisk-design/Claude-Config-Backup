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

    # StorageBase 抽象方法实现
    def upload(self, local_path: str, remote_path: str) -> bool:
        """上传备份文件到 SSH 服务器

        Args:
            local_path: 本地文件路径
            remote_path: 远程相对路径

        Returns:
            bool: 上传是否成功

        Raises:
            BackupError: 上传失败
        """
        try:
            self._ensure_backup_dir()
            remote_full_path = self._get_remote_path(remote_path)
            self._sftp.put(local_path, remote_full_path)
            logger.info(f"Upload successful: {local_path} -> {remote_full_path}")
            return True
        except FileNotFoundError as e:
            raise BackupError(f"Local file not found: {local_path}")
        except Exception as e:
            raise BackupError(f"Upload failed: {e}")

    def download(self, remote_path: str, local_path: str) -> bool:
        """从 SSH 服务器下载备份文件

        Args:
            remote_path: 远程相对路径
            local_path: 本地保存路径

        Returns:
            bool: 下载是否成功

        Raises:
            RestoreError: 下载失败
        """
        try:
            remote_full_path = self._get_remote_path(remote_path)
            self._sftp.get(remote_full_path, local_path)
            logger.info(f"Download successful: {remote_full_path} -> {local_path}")
            return True
        except FileNotFoundError as e:
            raise RestoreError(f"Remote file not found: {remote_path}")
        except Exception as e:
            raise RestoreError(f"Download failed: {e}")

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """列出 SSH 服务器上的备份文件

        Args:
            prefix: 路径前缀（暂不使用）

        Returns:
            List[Dict]: 文件信息列表，每项包含:
                - name: 文件名
                - path: 相对路径
                - size: 文件大小（字节）
                - created_at: ISO 格式时间（从文件名解析）
                - download_url: None（SSH 无 HTTP URL）
        """
        from datetime import datetime

        try:
            files = self._sftp.listdir_attr(self.BACKUP_DIR)
            result = []
            for f in files:
                # 跳过目录
                if f.st_mode and (f.st_mode & 0o170000) == 0o040000:
                    continue

                file_info = {
                    "name": f.filename,
                    "path": f.filename,  # 相对路径就是文件名
                    "size": f.st_size or 0,
                    "created_at": None,
                    "download_url": None
                }

                # 尝试从修改时间解析 created_at
                if f.st_mtime:
                    try:
                        dt = datetime.fromtimestamp(f.st_mtime)
                        file_info["created_at"] = dt.isoformat()
                    except (ValueError, OSError):
                        pass

                result.append(file_info)

            # 按创建时间降序排序
            result.sort(key=lambda x: x.get("created_at") or "", reverse=True)
            return result

        except FileNotFoundError:
            logger.debug(f"Backup directory not found: {self.BACKUP_DIR}")
            return []
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def delete(self, remote_path: str) -> bool:
        """删除 SSH 服务器上的备份文件

        Args:
            remote_path: 远程相对路径

        Returns:
            bool: 删除是否成功

        Raises:
            BackupError: 删除失败
        """
        try:
            remote_full_path = self._get_remote_path(remote_path)
            self._sftp.remove(remote_full_path)
            logger.info(f"Delete successful: {remote_full_path}")
            return True
        except FileNotFoundError as e:
            raise BackupError(f"Remote file not found: {remote_path}")
        except Exception as e:
            raise BackupError(f"Delete failed: {e}")

    def get_file_url(self, remote_path: str) -> Optional[str]:
        return None  # SSH 没有 HTTP URL