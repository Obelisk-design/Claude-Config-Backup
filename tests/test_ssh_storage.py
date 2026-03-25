# tests/test_ssh_storage.py
"""SSH 存储测试"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, 'src')


class TestSSHStorageInit:
    """测试初始化"""

    def test_init_with_required_params(self):
        """测试使用必需参数初始化"""
        from storage.ssh_storage import SSHStorage

        storage = SSHStorage("host", 22, "user", "pass")
        assert storage.host == "host"
        assert storage.port == 22
        assert storage.user == "user"
        assert storage.password == "pass"
        assert storage._client is None
        assert storage._sftp is None

    def test_init_with_default_port(self):
        """测试默认端口"""
        from storage.ssh_storage import SSHStorage

        storage = SSHStorage("host", None, "user", "pass")
        assert storage.port == 22

    def test_class_constants(self):
        """测试类常量"""
        from storage.ssh_storage import SSHStorage

        assert SSHStorage.BACKUP_DIR == ".claude-backups"
        assert SSHStorage.MAX_RETRIES == 3
        assert SSHStorage.RETRY_DELAY == 2
        assert SSHStorage.TIMEOUT == 30