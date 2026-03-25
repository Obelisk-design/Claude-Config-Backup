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


class TestSSHStorageHelpers:
    """测试辅助方法"""

    def test_get_remote_path(self):
        """测试远程路径拼接"""
        from storage.ssh_storage import SSHStorage

        storage = SSHStorage("host", 22, "user", "pass")
        result = storage._get_remote_path("backup.ccb")
        assert result == ".claude-backups/backup.ccb"

    @patch('storage.ssh_storage.SSHClient')
    def test_ensure_backup_dir_exists(self, mock_ssh_client):
        """测试备份目录已存在"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        with SSHStorage("host", 22, "user", "pass") as storage:
            storage._ensure_backup_dir()
            mock_sftp.mkdir.assert_not_called()

    @patch('storage.ssh_storage.SSHClient')
    def test_ensure_backup_dir_create(self, mock_ssh_client):
        """测试创建备份目录"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.stat.side_effect = FileNotFoundError()

        with SSHStorage("host", 22, "user", "pass") as storage:
            storage._ensure_backup_dir()
            mock_sftp.mkdir.assert_called_once_with(".claude-backups")


class TestSSHStorageUpload:
    """测试上传功能"""

    @patch('storage.ssh_storage.SSHClient')
    def test_upload_success(self, mock_ssh_client, tmp_path):
        """测试上传成功"""
        from storage.ssh_storage import SSHStorage

        # 创建测试文件
        test_file = tmp_path / "test.ccb"
        test_file.write_text("test content")

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        with SSHStorage("host", 22, "user", "pass") as storage:
            result = storage.upload(str(test_file), "test.ccb")
            assert result is True
            mock_sftp.put.assert_called_once()

    @patch('storage.ssh_storage.SSHClient')
    def test_upload_creates_backup_dir(self, mock_ssh_client, tmp_path):
        """测试上传时自动创建备份目录"""
        from storage.ssh_storage import SSHStorage

        test_file = tmp_path / "test.ccb"
        test_file.write_text("test")

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.stat.side_effect = FileNotFoundError()

        with SSHStorage("host", 22, "user", "pass") as storage:
            storage.upload(str(test_file), "test.ccb")
            mock_sftp.mkdir.assert_called()


class TestSSHStorageDownload:
    """测试下载功能"""

    @patch('storage.ssh_storage.SSHClient')
    def test_download_success(self, mock_ssh_client, tmp_path):
        """测试下载成功"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        dest_file = tmp_path / "downloaded.ccb"

        with SSHStorage("host", 22, "user", "pass") as storage:
            result = storage.download("backup.ccb", str(dest_file))
            assert result is True
            mock_sftp.get.assert_called_once()

    @patch('storage.ssh_storage.SSHClient')
    def test_download_file_not_found(self, mock_ssh_client, tmp_path):
        """测试下载文件不存在"""
        from storage.ssh_storage import SSHStorage
        from core.exceptions import RestoreError

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.get.side_effect = FileNotFoundError("No such file")

        dest_file = tmp_path / "downloaded.ccb"

        with pytest.raises(RestoreError):
            with SSHStorage("host", 22, "user", "pass") as storage:
                storage.download("nonexistent.ccb", str(dest_file))


class TestSSHStorageListFiles:
    """测试文件列表功能"""

    @patch('storage.ssh_storage.SSHClient')
    def test_list_files_success(self, mock_ssh_client):
        """测试获取文件列表"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        # 模拟文件列表
        file1 = MagicMock()
        file1.filename = "backup1.ccb"
        file1.st_size = 1024
        file1.st_mtime = 1711281000

        file2 = MagicMock()
        file2.filename = "backup2.ccb"
        file2.st_size = 2048
        file2.st_mtime = 1711282000

        mock_sftp.listdir_attr.return_value = [file1, file2]

        with SSHStorage("host", 22, "user", "pass") as storage:
            files = storage.list_files()
            assert len(files) == 2
            # 按时间降序排序，backup2.ccb 时间更新
            assert files[0]["name"] == "backup2.ccb"
            assert files[0]["size"] == 2048
            assert files[1]["name"] == "backup1.ccb"

    @patch('storage.ssh_storage.SSHClient')
    def test_list_files_empty(self, mock_ssh_client):
        """测试空目录"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.listdir_attr.return_value = []

        with SSHStorage("host", 22, "user", "pass") as storage:
            files = storage.list_files()
            assert files == []

    @patch('storage.ssh_storage.SSHClient')
    def test_list_files_dir_not_found(self, mock_ssh_client):
        """测试目录不存在"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.listdir_attr.side_effect = FileNotFoundError()

        with SSHStorage("host", 22, "user", "pass") as storage:
            files = storage.list_files()
            assert files == []


class TestSSHStorageDelete:
    """测试删除功能"""

    @patch('storage.ssh_storage.SSHClient')
    def test_delete_success(self, mock_ssh_client):
        """测试删除成功"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        with SSHStorage("host", 22, "user", "pass") as storage:
            result = storage.delete("backup.ccb")
            assert result is True
            mock_sftp.remove.assert_called_once()

    @patch('storage.ssh_storage.SSHClient')
    def test_delete_file_not_found(self, mock_ssh_client):
        """测试删除文件不存在"""
        from storage.ssh_storage import SSHStorage
        from core.exceptions import BackupError

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.remove.side_effect = FileNotFoundError("No such file")

        with pytest.raises(BackupError):
            with SSHStorage("host", 22, "user", "pass") as storage:
                storage.delete("nonexistent.ccb")