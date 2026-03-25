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


class TestSSHStorageContext:
    """测试上下文管理器"""

    @patch('storage.ssh_storage.SSHClient')
    def test_context_manager_connect(self, mock_ssh_client):
        """测试上下文管理器连接"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        with SSHStorage("host", 22, "user", "pass") as storage:
            assert storage._client is not None
            assert storage._sftp is not None

        # 退出上下文后关闭连接
        mock_sftp.close.assert_called_once()
        mock_client.close.assert_called_once()

    @patch('storage.ssh_storage.SSHClient')
    def test_context_manager_auth_error(self, mock_ssh_client):
        """测试认证失败"""
        from storage.ssh_storage import SSHStorage
        from core.exceptions import AuthenticationError
        import paramiko

        mock_ssh_client.side_effect = paramiko.AuthenticationException("Auth failed")

        with pytest.raises(AuthenticationError):
            with SSHStorage("host", 22, "user", "wrong_pass"):
                pass