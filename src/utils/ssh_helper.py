# -*- coding: utf-8 -*-
"""SSH 存储辅助函数"""

from typing import Optional, Dict, Any
from security.crypto import Crypto
from storage.ssh_storage import SSHStorage


def get_ssh_storage(config) -> Optional[SSHStorage]:
    """根据配置创建 SSHStorage 实例

    自动处理密码解密和配置读取。

    Args:
        config: 配置对象，需要支持 get() 方法

    Returns:
        SSHStorage 实例，如果配置不完整则返回 None

    Example:
        >>> with get_ssh_storage(config) as storage:
        ...     storage.upload(local_path, remote_name)
    """
    ssh_host = config.get("ssh.host", "")
    ssh_port = config.get("ssh.port", 22)
    ssh_user = config.get("ssh.user", "")

    # 获取密码（优先使用加密存储的密码）
    password = config.get("ssh.password", "")
    password_encrypted = config.get("ssh.password_encrypted", "")

    if password_encrypted:
        try:
            crypto = Crypto()
            password = crypto.decrypt(password_encrypted)
        except Exception:
            # 解密失败，使用明文密码
            pass

    # 检查必需参数
    if not ssh_host or not ssh_user or not password:
        return None

    return SSHStorage(
        host=ssh_host,
        port=ssh_port,
        user=ssh_user,
        password=password
    )


def get_ssh_config_dict(config) -> Dict[str, Any]:
    """获取 SSH 配置字典（用于 Worker 线程）

    Args:
        config: 配置对象

    Returns:
        包含 SSH 配置的字典
    """
    return {
        "host": config.get("ssh.host", ""),
        "port": config.get("ssh.port", 22),
        "user": config.get("ssh.user", ""),
        "password": config.get("ssh.password", ""),
        "password_encrypted": config.get("ssh.password_encrypted", "")
    }


def decrypt_ssh_password(ssh_config: Dict[str, Any]) -> str:
    """解密 SSH 密码

    Args:
        ssh_config: SSH 配置字典

    Returns:
        解密后的密码
    """
    password = ssh_config.get("password", "")
    if ssh_config.get("password_encrypted"):
        try:
            crypto = Crypto()
            password = crypto.decrypt(ssh_config["password_encrypted"])
        except Exception:
            pass
    return password


# SSH 错误消息映射
SSH_ERROR_MESSAGES = {
    # 认证错误
    "Authentication failed": "用户名或密码错误，请检查凭据",
    "AuthenticationException": "用户名或密码错误，请检查凭据",
    "permission denied": "权限被拒绝，请检查用户权限",

    # 连接错误
    "Connection refused": "无法连接到服务器，请检查地址和端口是否正确",
    "Connection reset": "连接被重置，请检查网络连接",
    "Network is unreachable": "网络不可达，请检查网络连接",
    "No route to host": "无法访问主机，请检查服务器地址",

    # 超时错误
    "timed out": "连接超时，请检查服务器状态或网络连接",
    "Timeout": "连接超时，请检查服务器状态或网络连接",

    # 主机密钥错误
    "Host key verification failed": "服务器密钥验证失败",
    "not in known_hosts": "服务器密钥未在已知主机列表中",

    # 通用错误
    "Name or service not known": "无法解析服务器地址，请检查主机名",
    "gaierror": "无法解析服务器地址，请检查主机名",
}


def get_friendly_ssh_error(error_message: str) -> str:
    """将 SSH 错误转换为用户友好的中文消息

    Args:
        error_message: 原始错误消息

    Returns:
        用户友好的中文错误消息
    """
    error_lower = error_message.lower()

    # 检查是否有匹配的错误模式
    for pattern, friendly_msg in SSH_ERROR_MESSAGES.items():
        if pattern.lower() in error_lower:
            return friendly_msg

    # 如果没有匹配，返回通用消息
    return f"SSH 操作失败：{error_message}"