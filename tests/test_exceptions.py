# tests/test_exceptions.py
import pytest
import sys
sys.path.insert(0, 'src')

from core.exceptions import (
    ClaudeBackupError,
    NetworkError,
    TimeoutError,
    GitHubAPIError,
    RateLimitError,
    AuthenticationError,
    TokenExpiredError,
    BackupError,
    RestoreError,
    CorruptedFileError,
    VersionMismatchError,
)


class TestExceptions:
    def test_base_exception(self):
        """测试基础异常"""
        err = ClaudeBackupError("test error")
        assert str(err) == "test error"
        assert isinstance(err, Exception)

    def test_network_error(self):
        """测试网络错误"""
        err = NetworkError("connection failed")
        assert isinstance(err, ClaudeBackupError)

    def test_rate_limit_error(self):
        """测试速率限制错误"""
        err = RateLimitError(reset_time=1711281000)
        assert err.reset_time == 1711281000
        assert isinstance(err, GitHubAPIError)

    def test_token_expired_error(self):
        """测试 Token 过期错误"""
        err = TokenExpiredError()
        assert isinstance(err, AuthenticationError)

    def test_corrupted_file_error(self):
        """测试文件损坏错误"""
        err = CorruptedFileError("/path/to/file.ccb")
        assert err.file_path == "/path/to/file.ccb"
        assert isinstance(err, RestoreError)

    def test_version_mismatch_error(self):
        """测试版本不兼容错误"""
        err = VersionMismatchError("1.0", "2.0")
        assert err.expected == "1.0"
        assert err.actual == "2.0"