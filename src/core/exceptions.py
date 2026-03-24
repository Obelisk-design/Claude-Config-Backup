# -*- coding: utf-8 -*-
"""统一异常体系"""


class ClaudeBackupError(Exception):
    """基础异常类"""
    pass


class NetworkError(ClaudeBackupError):
    """网络错误"""
    pass


class TimeoutError(NetworkError):
    """超时错误"""
    pass


class GitHubAPIError(ClaudeBackupError):
    """GitHub API 错误"""
    pass


class RateLimitError(GitHubAPIError):
    """速率限制错误"""

    def __init__(self, reset_time: int, message: str = "GitHub API rate limit exceeded"):
        self.reset_time = reset_time
        super().__init__(f"{message}, resets at {reset_time}")


class AuthenticationError(ClaudeBackupError):
    """认证错误"""
    pass


class TokenExpiredError(AuthenticationError):
    """Token 过期"""
    def __init__(self, message: str = "GitHub token has expired"):
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """无效 Token"""
    def __init__(self, message: str = "Invalid GitHub token"):
        super().__init__(message)


class BackupError(ClaudeBackupError):
    """备份错误"""
    pass


class RestoreError(ClaudeBackupError):
    """恢复错误"""
    pass


class CorruptedFileError(RestoreError):
    """文件损坏"""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        msg = f"Backup file is corrupted: {file_path}" if file_path else "Backup file is corrupted"
        super().__init__(msg)


class VersionMismatchError(RestoreError):
    """版本不兼容"""

    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Version mismatch: expected {expected}, got {actual}")


class ConfigurationError(ClaudeBackupError):
    """配置错误"""
    pass


class ModuleNotFoundError(ConfigurationError):
    """模块未找到"""
    pass