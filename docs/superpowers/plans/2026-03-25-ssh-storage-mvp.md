# SSH 存储功能实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 SSH 存储功能，支持通过 SFTP 协议上传/下载/管理备份文件，完成备份恢复完整闭环。

**Architecture:** 创建 `SSHStorage` 类实现 `StorageBase` 接口，使用 `paramiko` 库建立 SFTP 连接。通过 QThread 异步执行上传操作，支持连接重试和密码加密存储。

**Tech Stack:** Python 3.10+, paramiko 3.0+, PyQt5 QThread

---

## 文件结构

```
新增文件:
├── src/storage/ssh_storage.py      # SSH 存储核心实现
├── src/storage/cloud_storage.py    # 云存储预留占位
└── tests/test_ssh_storage.py       # 单元测试

修改文件:
├── src/gui/tabs/backup_tab.py      # 添加 SSH 上传 Worker 和逻辑
├── src/gui/tabs/restore_tab.py     # 支持 SSH 恢复源
├── src/gui/tabs/history_tab.py     # 支持 SSH 历史管理
├── src/gui/tabs/settings_tab.py    # 实现连接测试和密码加密
├── config/settings.yaml            # 添加云存储预留配置
└── src/security/crypto.py          # 添加密码加密辅助函数（如需要）
```

---

## Chunk 1: SSHStorage 核心实现

### Task 1.1: 测试框架搭建

**Files:**
- Create: `tests/test_ssh_storage.py`

- [ ] **Step 1: 创建测试文件骨架**

```python
# tests/test_ssh_storage.py
# -*- coding: utf-8 -*-
"""SSH 存储单元测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 占位导入，后续实现后取消注释
# from storage.ssh_storage import SSHStorage
# from core.exceptions import AuthenticationError, NetworkError, BackupError, RestoreError


class TestSSHStorageInit:
    """测试初始化"""

    def test_init_with_valid_params(self):
        """测试有效参数初始化"""
        # storage = SSHStorage("192.168.1.1", 22, "user", "password")
        # assert storage.host == "192.168.1.1"
        # assert storage.port == 22
        # assert storage.user == "user"
        # assert storage.password == "password"
        pass

    def test_default_port(self):
        """测试默认端口"""
        # storage = SSHStorage("192.168.1.1", 22, "user", "password")
        # assert storage.port == 22
        pass
```

- [ ] **Step 2: 运行测试验证骨架**

Run: `pytest tests/test_ssh_storage.py -v`
Expected: PASS (测试为空通过)

- [ ] **Step 3: 提交测试骨架**

```bash
git add tests/test_ssh_storage.py
git commit -m "test: 添加 SSH 存储测试骨架"
```

---

### Task 1.2: SSHStorage 初始化和上下文管理器

**Files:**
- Create: `src/storage/ssh_storage.py`
- Modify: `tests/test_ssh_storage.py`

- [ ] **Step 1: 编写初始化和上下文管理器测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

class TestSSHStorageContext:
    """测试上下文管理器"""

    @patch('storage.ssh_storage.SSHClient')
    def test_context_manager_connect_disconnect(self, mock_ssh_client):
        """测试上下文管理器自动连接和断开"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        storage = SSHStorage("192.168.1.1", 22, "user", "password")

        with storage as s:
            assert s is storage
            mock_client.connect.assert_called_once()

        # 退出上下文后应断开连接
        mock_sftp.close.assert_called_once()
        mock_client.close.assert_called_once()

    def test_context_manager_properties(self):
        """测试类属性"""
        from storage.ssh_storage import SSHStorage

        storage = SSHStorage("host", 2222, "user", "pass")
        assert storage.BACKUP_DIR == ".claude-backups"
        assert storage.MAX_RETRIES == 3
        assert storage.RETRY_DELAY == 2
        assert storage.TIMEOUT == 30
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_ssh_storage.py -v`
Expected: FAIL (模块不存在)

- [ ] **Step 3: 实现 SSHStorage 初始化和上下文管理器**

```python
# src/storage/ssh_storage.py
# -*- coding: utf-8 -*-
"""SSH/SFTP storage implementation for backup files"""

import time
from paramiko import SSHClient, AutoAddPolicy
import paramiko
from typing import Dict, List, Optional, Tuple, Any

from storage.base import StorageBase
from core.exceptions import BackupError, RestoreError, NetworkError, AuthenticationError
from utils.logger import logger


class SSHStorage(StorageBase):
    """SSH/SFTP 存储实现"""

    BACKUP_DIR = ".claude-backups"
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    TIMEOUT = 30

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._client: Optional[SSHClient] = None
        self._sftp = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._disconnect()

    def _connect(self):
        """建立 SSH/SFTP 连接（带重试）"""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                self._client = SSHClient()
                self._client.load_system_host_keys()
                self._client.set_missing_host_key_policy(AutoAddPolicy())

                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password,
                    timeout=self.TIMEOUT
                )
                self._sftp = self._client.open_sftp()
                logger.info(f"SSH connected to {self.host}:{self.port}")
                return

            except paramiko.AuthenticationException as e:
                logger.error(f"SSH authentication failed: {e}")
                raise AuthenticationError(f"SSH authentication failed: {e}")

            except Exception as e:
                last_error = e
                logger.warning(f"SSH connection attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        raise NetworkError(f"SSH connection failed after {self.MAX_RETRIES} retries: {last_error}")

    def _disconnect(self):
        """关闭连接"""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None

        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

        logger.debug("SSH connection closed")
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_ssh_storage.py -v`
Expected: PASS

- [ ] **Step 5: 提交初始化实现**

```bash
git add src/storage/ssh_storage.py tests/test_ssh_storage.py
git commit -m "feat: 实现 SSHStorage 初始化和上下文管理器"
```

---

### Task 1.3: 辅助方法实现

**Files:**
- Modify: `src/storage/ssh_storage.py`
- Modify: `tests/test_ssh_storage.py`

- [ ] **Step 1: 编写辅助方法测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

class TestSSHStorageHelpers:
    """测试辅助方法"""

    def test_get_remote_path(self):
        """测试远程路径生成"""
        from storage.ssh_storage import SSHStorage

        storage = SSHStorage("host", 22, "user", "pass")
        assert storage._get_remote_path("backup.ccb") == ".claude-backups/backup.ccb"
        assert storage._get_remote_path("subdir/file.ccb") == ".claude-backups/subdir/file.ccb"

    @patch('storage.ssh_storage.SSHClient')
    def test_ensure_backup_dir_exists(self, mock_ssh_client):
        """测试备份目录已存在"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        # 模拟目录已存在
        mock_sftp.stat.return_value = MagicMock()

        with SSHStorage("host", 22, "user", "pass") as storage:
            storage._ensure_backup_dir()
            # 目录存在时不创建
            mock_sftp.mkdir.assert_not_called()

    @patch('storage.ssh_storage.SSHClient')
    def test_ensure_backup_dir_not_exists(self, mock_ssh_client):
        """测试备份目录不存在时创建"""
        from storage.ssh_storage import SSHStorage

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client

        # 模拟目录不存在
        mock_sftp.stat.side_effect = FileNotFoundError()

        with SSHStorage("host", 22, "user", "pass") as storage:
            storage._ensure_backup_dir()
            mock_sftp.mkdir.assert_called_once_with(".claude-backups")
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageHelpers -v`
Expected: FAIL (方法不存在)

- [ ] **Step 3: 实现辅助方法**

```python
# src/storage/ssh_storage.py - 添加到 _disconnect 方法之后

    def _get_remote_path(self, path: str) -> str:
        """获取完整远程路径"""
        return f"{self.BACKUP_DIR}/{path}"

    def _ensure_backup_dir(self):
        """确保服务器备份目录存在"""
        if not self._sftp:
            return

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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageHelpers -v`
Expected: PASS

- [ ] **Step 5: 提交辅助方法**

```bash
git add src/storage/ssh_storage.py tests/test_ssh_storage.py
git commit -m "feat: 实现 SSHStorage 辅助方法"
```

---

### Task 1.4: upload 方法

**Files:**
- Modify: `src/storage/ssh_storage.py`
- Modify: `tests/test_ssh_storage.py`

- [ ] **Step 1: 编写 upload 测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

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
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageUpload -v`
Expected: FAIL (方法不存在)

- [ ] **Step 3: 实现 upload 方法**

```python
# src/storage/ssh_storage.py - 添加到 _ensure_backup_dir 方法之后

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
        from core.exceptions import BackupError

        try:
            self._ensure_backup_dir()
            remote_full_path = f"{self.BACKUP_DIR}/{remote_path}"
            self._sftp.put(local_path, remote_full_path)
            logger.info(f"Upload successful: {local_path} -> {remote_full_path}")
            return True
        except FileNotFoundError as e:
            raise BackupError(f"Local file not found: {local_path}")
        except Exception as e:
            raise BackupError(f"Upload failed: {e}")
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageUpload -v`
Expected: PASS

- [ ] **Step 5: 提交 upload 实现**

```bash
git add src/storage/ssh_storage.py tests/test_ssh_storage.py
git commit -m "feat: 实现 SSHStorage upload 方法"
```

---

### Task 1.5: download 方法

**Files:**
- Modify: `src/storage/ssh_storage.py`
- Modify: `tests/test_ssh_storage.py`

- [ ] **Step 1: 编写 download 测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

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
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageDownload -v`
Expected: FAIL (方法不存在)

- [ ] **Step 3: 实现 download 方法**

```python
# src/storage/ssh_storage.py - 添加到 upload 方法之后

    def download(self, remote_path: str, local_path: str) -> bool:
        """从 SSH 服务器下载文件

        Args:
            remote_path: 远程文件路径（相对于备份目录）
            local_path: 本地保存路径

        Returns:
            True 如果下载成功

        Raises:
            RestoreError: 下载失败
        """
        if not self._sftp:
            raise RestoreError("SFTP connection not established")

        try:
            full_remote_path = self._get_remote_path(remote_path)
            self._sftp.get(full_remote_path, local_path)
            logger.info(f"Downloaded {full_remote_path} to {local_path}")
            return True

        except FileNotFoundError as e:
            logger.error(f"Remote file not found: {e}")
            raise RestoreError(f"Remote file not found: {remote_path}")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise RestoreError(f"Failed to download file: {e}")
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageDownload -v`
Expected: PASS

- [ ] **Step 5: 提交 download 实现**

```bash
git add src/storage/ssh_storage.py tests/test_ssh_storage.py
git commit -m "feat: 实现 SSHStorage download 方法"
```

---

### Task 1.6: list_files 和 delete 方法

**Files:**
- Modify: `src/storage/ssh_storage.py`
- Modify: `tests/test_ssh_storage.py`

- [ ] **Step 1: 编写 list_files 测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

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

        # 模拟返回的文件列表
        mock_file1 = MagicMock()
        mock_file1.filename = "20260325_120000.ccb"
        mock_file1.st_size = 1024
        mock_file1.st_mtime = 1742880000

        mock_file2 = MagicMock()
        mock_file2.filename = "20260325_130000.ccb"
        mock_file2.st_size = 2048
        mock_file2.st_mtime = 1742883600

        mock_sftp.listdir_attr.return_value = [mock_file1, mock_file2]

        with SSHStorage("host", 22, "user", "pass") as storage:
            files = storage.list_files()
            assert len(files) == 2
            assert files[0]["name"] == "20260325_130000.ccb"  # 按时间倒序
            assert files[0]["size"] == 2048
            assert files[0]["download_url"] is None

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
```

- [ ] **Step 2: 编写 delete 测试**

```python
# tests/test_ssh_storage.py - 添加到文件末尾

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
        """测试删除不存在的文件"""
        from storage.ssh_storage import SSHStorage
        from core.exceptions import BackupError

        mock_client = MagicMock()
        mock_sftp = MagicMock()
        mock_client.open_sftp.return_value = mock_sftp
        mock_ssh_client.return_value = mock_client
        mock_sftp.remove.side_effect = FileNotFoundError()

        with pytest.raises(BackupError):
            with SSHStorage("host", 22, "user", "pass") as storage:
                storage.delete("nonexistent.ccb")
```

- [ ] **Step 3: 运行测试验证失败**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageListFiles tests/test_ssh_storage.py::TestSSHStorageDelete -v`
Expected: FAIL (方法不存在)

- [ ] **Step 4: 实现 list_files 和 delete 方法**

```python
# src/storage/ssh_storage.py - 添加到 download 方法之后

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """列出备份目录中的文件

        Args:
            prefix: 可选的文件前缀过滤

        Returns:
            文件信息列表，每个元素包含 name, path, size, created_at, download_url
        """
        if not self._sftp:
            return []

        try:
            backup_dir = self._get_remote_path(prefix).rstrip("/")

            # 检查目录是否存在
            try:
                self._sftp.stat(backup_dir)
            except FileNotFoundError:
                return []

            # 获取文件列表
            files = []
            for attr in self._sftp.listdir_attr(backup_dir):
                if attr.filename.endswith('.ccb'):
                    files.append({
                        "name": attr.filename,
                        "path": attr.filename,
                        "size": attr.st_size,
                        "created_at": self._extract_created_at(attr.filename),
                        "download_url": None,
                    })

            # 按文件名（时间戳）倒序排列
            files.sort(key=lambda x: x["name"], reverse=True)
            logger.info(f"Listed {len(files)} files from SSH storage")
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def _extract_created_at(self, filename: str) -> Optional[str]:
        """从文件名提取创建时间"""
        from datetime import datetime
        import re

        # 尝试匹配时间戳格式 YYYYMMDD_HHMMSS
        match = re.search(r'(\d{8}_\d{6})', filename)
        if match:
            try:
                dt = datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
                return dt.isoformat()
            except ValueError:
                pass
        return None

    def delete(self, remote_path: str) -> bool:
        """删除远程文件

        Args:
            remote_path: 远程文件路径（相对于备份目录）

        Returns:
            True 如果删除成功

        Raises:
            BackupError: 删除失败
        """
        if not self._sftp:
            raise BackupError("SFTP connection not established")

        try:
            full_path = self._get_remote_path(remote_path)
            self._sftp.remove(full_path)
            logger.info(f"Deleted remote file: {full_path}")
            return True

        except FileNotFoundError:
            raise BackupError(f"File not found: {remote_path}")
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise BackupError(f"Failed to delete file: {e}")
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_ssh_storage.py::TestSSHStorageListFiles tests/test_ssh_storage.py::TestSSHStorageDelete -v`
Expected: PASS

- [ ] **Step 6: 实现 get_file_url 和 test_connection 方法**

```python
# src/storage/ssh_storage.py - 添加到 delete 方法之后

    def get_file_url(self, remote_path: str) -> Optional[str]:
        """获取文件 URL（SSH 不支持 HTTP URL）"""
        return None

    def test_connection(self) -> Tuple[bool, str]:
        """测试 SSH 连接

        Returns:
            (success, message): 成功返回 (True, "连接成功")，失败返回 (False, 错误信息)
        """
        try:
            with self:
                return True, f"连接成功：{self.host}:{self.port}"
        except AuthenticationError:
            return False, "认证失败：请检查用户名和密码"
        except NetworkError as e:
            return False, f"连接失败：{str(e)}"
        except Exception as e:
            return False, f"未知错误：{str(e)}"
```

- [ ] **Step 7: 提交完整 SSHStorage 实现**

```bash
git add src/storage/ssh_storage.py tests/test_ssh_storage.py
git commit -m "feat: 完成 SSHStorage 所有核心方法实现"
```

---

### Task 1.7: 云存储预留占位

**Files:**
- Create: `src/storage/cloud_storage.py`

- [ ] **Step 1: 创建云存储占位文件**

```python
# src/storage/cloud_storage.py
# -*- coding: utf-8 -*-
"""Cloud storage placeholder for premium feature"""

from typing import Dict, List, Optional, Any

from storage.base import StorageBase
from core.exceptions import BackupError
from utils.logger import logger


class CloudStorage(StorageBase):
    """云存储实现（付费功能预留）

    支持的云服务商：
    - 阿里云 OSS
    - 腾讯云 COS
    - AWS S3
    - 自定义服务端
    """

    PREMIUM_REQUIRED = "云存储功能需要订阅付费套餐"

    def __init__(self, provider: str, endpoint: str, bucket: str,
                 access_key: str, secret_key: str):
        self.provider = provider
        self.endpoint = endpoint
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

    def upload(self, local_path: str, remote_path: str) -> bool:
        raise NotImplementedError(self.PREMIUM_REQUIRED)

    def download(self, remote_path: str, local_path: str) -> bool:
        raise NotImplementedError(self.PREMIUM_REQUIRED)

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        raise NotImplementedError(self.PREMIUM_REQUIRED)

    def delete(self, remote_path: str) -> bool:
        raise NotImplementedError(self.PREMIUM_REQUIRED)

    def get_file_url(self, remote_path: str) -> Optional[str]:
        raise NotImplementedError(self.PREMIUM_REQUIRED)
```

- [ ] **Step 2: 提交云存储占位**

```bash
git add src/storage/cloud_storage.py
git commit -m "feat: 添加云存储预留占位（付费功能）"
```

---

## Chunk 2: UI 集成 - 备份页面

### Task 2.1: SSHUploadWorker 实现

**Files:**
- Modify: `src/gui/tabs/backup_tab.py`

- [ ] **Step 1: 添加 SSHUploadWorker 类**

在 `backup_tab.py` 中 `UploadWorker` 类之后添加：

```python
# src/gui/tabs/backup_tab.py - 在 UploadWorker 类之后添加

class SSHUploadWorker(QThread):
    """SSH 上传工作线程"""
    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, ssh_config: dict, backup_file_path: str, remote_name: str):
        super().__init__()
        self.ssh_config = ssh_config
        self.backup_file_path = backup_file_path
        self.remote_name = remote_name

    def run(self):
        try:
            from storage.ssh_storage import SSHStorage
            from pathlib import Path

            self.progress.emit("正在连接 SSH 服务器...")

            storage = SSHStorage(
                host=self.ssh_config["host"],
                port=self.ssh_config["port"],
                user=self.ssh_config["user"],
                password=self.ssh_config["password"]
            )

            with storage:
                self.progress.emit("正在上传备份文件...")
                storage._ensure_backup_dir()
                success = storage.upload(self.backup_file_path, self.remote_name)

            if success:
                backup_file = Path(self.backup_file_path)
                size_kb = backup_file.stat().st_size / 1024
                self.finished.emit(
                    True,
                    f"文件：{self.remote_name}\n大小：{size_kb:.1f} KB\n已上传到 SSH 服务器"
                )
            else:
                self.error.emit("上传失败")

        except Exception as e:
            self.error.emit(str(e))
```

- [ ] **Step 2: 添加 _get_ssh_password 方法**

在 `BackupTab` 类中添加：

```python
# src/gui/tabs/backup_tab.py - 在 BackupTab 类中添加

    def _get_ssh_password(self) -> str:
        """获取解密后的 SSH 密码"""
        from security.crypto import decrypt_password

        encrypted = self.config.get("ssh.password_encrypted", "")
        if encrypted:
            try:
                return decrypt_password(encrypted)
            except Exception:
                pass
        return self.config.get("ssh.password", "")
```

- [ ] **Step 3: 修改 _on_backup 方法支持 SSH**

找到 `_on_backup` 方法中的存储类型判断部分，修改为：

```python
# src/gui/tabs/backup_tab.py - 修改 _on_backup 方法

    def _on_backup(self):
        """执行备份"""
        from pathlib import Path

        storage_type = self.config.get("storage.type", "github")

        # GitHub 存储需要登录
        if storage_type == "github":
            token = self.token_manager.load_token()
            if not token:
                QMessageBox.warning(self, "提示", "GitHub 存储需要先登录")
                return

        # SSH 存储需要配置
        if storage_type == "ssh":
            host = self.config.get("ssh.host", "")
            if not host:
                QMessageBox.warning(self, "提示", "请先在设置中配置 SSH 服务器")
                return

        modules = self.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        user_info = self.token_manager.load_user_info()
        username = user_info.get("login", "unknown") if user_info else "unknown"

        # 确定输出路径
        output_path = None
        if storage_type == "local":
            local_path = self.config.get("local.path", "")
            if local_path:
                output_path = Path(local_path)
            else:
                output_path = Path.home() / "Documents" / "ClaudeBackups"
            output_path.mkdir(parents=True, exist_ok=True)

        # 禁用按钮
        self.backup_btn.setEnabled(False)
        self.backup_btn.setText("⏳ 备份中...")

        # 创建备份工作线程
        self.worker = BackupWorker(
            self.backup_manager,
            modules,
            self.description_input.text(),
            username,
            output_path
        )
        self.worker.finished.connect(lambda bid, bfile: self._on_backup_finished(bid, bfile, storage_type))
        self.worker.error.connect(self._on_backup_error)
        self.worker.start()
```

- [ ] **Step 4: 修改 _on_backup_finished 支持 SSH 上传**

找到 `_on_backup_finished` 方法，修改 SSH 分支：

```python
# src/gui/tabs/backup_tab.py - 修改 _on_backup_finished 方法

    def _on_backup_finished(self, backup_id, backup_file_path, storage_type):
        """备份完成"""
        from pathlib import Path
        backup_file = Path(backup_file_path)

        if storage_type == "github":
            token = self.token_manager.load_token()
            remote_name = backup_file.name

            self.worker = UploadWorker(token, backup_file_path, remote_name)
            self.worker.finished.connect(lambda success, msg: self._on_upload_finished(success, msg, backup_file))
            self.worker.error.connect(self._on_backup_error)
            self.worker.start()

        elif storage_type == "ssh":
            ssh_config = {
                "host": self.config.get("ssh.host"),
                "port": self.config.get("ssh.port", 22),
                "user": self.config.get("ssh.user"),
                "password": self._get_ssh_password()
            }
            remote_name = backup_file.name

            self.worker = SSHUploadWorker(ssh_config, backup_file_path, remote_name)
            self.worker.finished.connect(lambda success, msg: self._on_upload_finished(success, msg, backup_file))
            self.worker.error.connect(self._on_backup_error)
            self.worker.start()

        elif storage_type == "local":
            size_kb = backup_file.stat().st_size / 1024
            self._reset_backup_button()
            QMessageBox.information(
                self, "备份成功",
                f"文件：{backup_file.name}\n大小：{size_kb:.1f} KB\n已保存到本地"
            )

        else:
            self._reset_backup_button()
```

- [ ] **Step 5: 验证代码可加载**

Run: `python -c "from gui.tabs.backup_tab import BackupTab, SSHUploadWorker; print('OK')"`
Expected: `OK`

- [ ] **Step 6: 提交备份页面 SSH 集成**

```bash
git add src/gui/tabs/backup_tab.py
git commit -m "feat: 备份页面集成 SSH 存储"
```

---

## Chunk 3: UI 集成 - 恢复和历史页面

### Task 3.1: 恢复页面 SSH 支持

**Files:**
- Modify: `src/gui/tabs/restore_tab.py`

- [ ] **Step 1: 添加存储类型判断**

修改 `_load_cloud_backups` 方法：

```python
# src/gui/tabs/restore_tab.py - 修改 _load_cloud_backups 方法

    def _load_cloud_backups(self):
        """加载云端备份列表"""
        from utils.config import get_config

        config = get_config()
        storage_type = config.get("storage.type", "github")

        if storage_type == "github":
            token = self.token_manager.load_token()
            if not token:
                self._refresh_source_ui()
                return

            self.storage = GitHubStorage(token)

        elif storage_type == "ssh":
            from storage.ssh_storage import SSHStorage
            from security.crypto import decrypt_password

            host = config.get("ssh.host", "")
            if not host:
                self._refresh_source_ui()
                return

            encrypted = config.get("ssh.password_encrypted", "")
            password = ""
            if encrypted:
                try:
                    password = decrypt_password(encrypted)
                except Exception:
                    password = config.get("ssh.password", "")

            self.storage = SSHStorage(
                host=host,
                port=config.get("ssh.port", 22),
                user=config.get("ssh.user", ""),
                password=password
            )

        else:
            self._refresh_source_ui()
            return

        # 获取文件列表
        files = self.storage.list_files()

        self.backup_list.clear()
        self.selected_cloud_file = None

        for f in files:
            item = QListWidgetItem(
                f"{f['name']} · {f['size'] / 1024:.1f} KB"
            )
            item.setData(Qt.UserRole, f)
            self.backup_list.addItem(item)

        if self.backup_list.count() > 0:
            self.backup_list.setCurrentRow(0)
        else:
            QMessageBox.information(self, "提示", "当前云端还没有可恢复的备份")
```

- [ ] **Step 2: 修改 _resolve_backup_file 方法**

```python
# src/gui/tabs/restore_tab.py - 修改 _resolve_backup_file 方法

    def _resolve_backup_file(self):
        """解析当前选择的备份文件"""
        if self.local_radio.isChecked():
            if not self.selected_file:
                QMessageBox.warning(self, "提示", "请选择备份文件")
                return None, None
            return Path(self.selected_file), None

        if not self.selected_cloud_file:
            QMessageBox.warning(self, "提示", "请选择云端备份")
            return None, None

        # 云端备份下载到缓存
        cache_path = self.restore_manager.cache_dir / self.selected_cloud_file["name"]

        # 确保缓存目录存在
        self.restore_manager.cache_dir.mkdir(parents=True, exist_ok=True)

        # 使用 SSH 或 GitHub 下载
        if self.storage:
            self.storage.download(self.selected_cloud_file["path"], str(cache_path))

        return cache_path, cache_path
```

- [ ] **Step 3: 验证代码可加载**

Run: `python -c "from gui.tabs.restore_tab import RestoreTab; print('OK')"`
Expected: `OK`

- [ ] **Step 4: 提交恢复页面集成**

```bash
git add src/gui/tabs/restore_tab.py
git commit -m "feat: 恢复页面集成 SSH 存储"
```

---

### Task 3.2: 历史页面 SSH 支持

**Files:**
- Modify: `src/gui/tabs/history_tab.py`

- [ ] **Step 1: 修改 _load_backups 方法**

```python
# src/gui/tabs/history_tab.py - 修改 _load_backups 方法开头

    def _load_backups(self):
        """加载备份列表"""
        from utils.config import get_config

        config = get_config()
        storage_type = config.get("storage.type", "github")

        # 根据存储类型创建 storage 实例
        if storage_type == "github":
            token = self.token_manager.load_token()
            if not token:
                self.table.setRowCount(0)
                self.stack.setCurrentWidget(self.login_state)
                return
            self.storage = GitHubStorage(token)

        elif storage_type == "ssh":
            from storage.ssh_storage import SSHStorage
            from security.crypto import decrypt_password

            host = config.get("ssh.host", "")
            if not host:
                self.table.setRowCount(0)
                self.stack.setCurrentWidget(self.empty_state)
                return

            encrypted = config.get("ssh.password_encrypted", "")
            password = ""
            if encrypted:
                try:
                    password = decrypt_password(encrypted)
                except Exception:
                    password = config.get("ssh.password", "")

            self.storage = SSHStorage(
                host=host,
                port=config.get("ssh.port", 22),
                user=config.get("ssh.user", ""),
                password=password
            )

        else:
            # 本地存储不支持历史管理
            self.table.setRowCount(0)
            self.stack.setCurrentWidget(self.empty_state)
            return

        # 显示加载状态
        self.stack.setCurrentWidget(self.loading_state)
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ 刷新中...")

        # ... 后续代码保持不变
```

- [ ] **Step 2: 验证代码可加载**

Run: `python -c "from gui.tabs.history_tab import HistoryTab; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交历史页面集成**

```bash
git add src/gui/tabs/history_tab.py
git commit -m "feat: 历史页面集成 SSH 存储"
```

---

## Chunk 4: 设置页面和密码加密

### Task 4.1: 密码加密辅助函数

**Files:**
- Modify: `src/security/crypto.py`

- [ ] **Step 1: 添加密码加密函数**

```python
# src/security/crypto.py - 添加到文件末尾

def encrypt_password(password: str) -> str:
    """加密密码

    Args:
        password: 明文密码

    Returns:
        加密后的密码（Base64 编码）
    """
    if not password:
        return ""

    key = _get_or_create_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')


def decrypt_password(encrypted_password: str) -> str:
    """解密密码

    Args:
        encrypted_password: 加密后的密码

    Returns:
        明文密码

    Raises:
        ValueError: 解密失败
    """
    if not encrypted_password:
        return ""

    key = _get_or_create_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_password.encode('utf-8'))
    return decrypted.decode('utf-8')
```

- [ ] **Step 2: 验证加密函数**

Run: `python -c "from security.crypto import encrypt_password, decrypt_password; p=encrypt_password('test'); assert decrypt_password(p)=='test'; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交加密函数**

```bash
git add src/security/crypto.py
git commit -m "feat: 添加密码加密辅助函数"
```

---

### Task 4.2: 设置页面 SSH 连接测试

**Files:**
- Modify: `src/gui/tabs/settings_tab.py`

- [ ] **Step 1: 实现 _test_ssh_connection 方法**

```python
# src/gui/tabs/settings_tab.py - 修改 _test_ssh_connection 方法

    def _test_ssh_connection(self):
        """测试 SSH 连接"""
        from storage.ssh_storage import SSHStorage

        host = self.ssh_host.text()
        user = self.ssh_user.text()
        password = self.ssh_password.text()
        port = self.ssh_port.value()

        if not host or not user:
            QMessageBox.warning(self, "提示", "请填写服务器地址和用户名")
            return

        # 禁用按钮
        sender = self.sender()
        sender.setEnabled(False)
        sender.setText("测试中...")

        try:
            storage = SSHStorage(host, port, user, password)
            success, message = storage.test_connection()

            if success:
                QMessageBox.information(self, "连接成功", message)
            else:
                QMessageBox.warning(self, "连接失败", message)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试失败：{str(e)}")

        finally:
            sender.setEnabled(True)
            sender.setText("🔗 测试连接")
```

- [ ] **Step 2: 修改 _save_settings 加密密码**

```python
# src/gui/tabs/settings_tab.py - 修改 _save_settings 方法

    def _save_settings(self):
        """保存设置"""
        from security.crypto import encrypt_password

        self.config.set("github.client_id", self.client_id.text())
        self.config.set("github.client_secret", self.client_secret.text())
        self.config.set("github.redirect_port", self.redirect_port.value())
        self.config.set("ssh.host", self.ssh_host.text())
        self.config.set("ssh.port", self.ssh_port.value())
        self.config.set("ssh.user", self.ssh_user.text())

        # 加密 SSH 密码
        ssh_password = self.ssh_password.text()
        if ssh_password:
            encrypted = encrypt_password(ssh_password)
            self.config.set("ssh.password_encrypted", encrypted)
            self.config.set("ssh.password", "")  # 清空明文密码

        # 保存本地存储路径
        self.config.set("local.path", self.local_path_input.text())

        # 保存存储类型
        if self.github_radio.isChecked():
            self.config.set("storage.type", "github")
        elif self.ssh_radio.isChecked():
            self.config.set("storage.type", "ssh")
        else:
            self.config.set("storage.type", "local")

        self.config.save()

        QMessageBox.information(self, "成功", "设置已保存")
        logger.info("用户设置已保存")
        self.settings_changed.emit()
```

- [ ] **Step 3: 修改 _load_settings 加载加密密码**

```python
# src/gui/tabs/settings_tab.py - 修改 _load_settings 方法中的 SSH 部分

    def _load_settings(self):
        """加载设置"""
        from security.crypto import decrypt_password

        self.client_id.setText(self.config.get("github.client_id", ""))
        self.client_secret.setText(self.config.get("github.client_secret", ""))
        self.redirect_port.setValue(self.config.get("github.redirect_port", 18080))
        self.ssh_host.setText(self.config.get("ssh.host", ""))
        self.ssh_port.setValue(self.config.get("ssh.port", 22))
        self.ssh_user.setText(self.config.get("ssh.user", ""))

        # 加载加密的 SSH 密码
        encrypted = self.config.get("ssh.password_encrypted", "")
        if encrypted:
            try:
                self.ssh_password.setText(decrypt_password(encrypted))
            except Exception:
                pass

        # ... 后续代码保持不变
```

- [ ] **Step 4: 验证代码可加载**

Run: `python -c "from gui.tabs.settings_tab import SettingsTab; print('OK')"`
Expected: `OK`

- [ ] **Step 5: 提交设置页面集成**

```bash
git add src/gui/tabs/settings_tab.py
git commit -m "feat: 设置页面实现 SSH 连接测试和密码加密"
```

---

### Task 4.3: 更新配置文件

**Files:**
- Modify: `config/settings.yaml`

- [ ] **Step 1: 添加云存储预留配置**

```yaml
# config/settings.yaml - 添加到文件末尾

# SSH 存储配置
ssh:
  host: ""
  port: 22
  user: ""
  password: ""
  password_encrypted: ""

# 云存储预留配置（付费功能）
cloud:
  provider: ""
  endpoint: ""
  bucket: ""
  access_key: ""
  secret_key: ""
  is_premium: true

# 存储类型: "github" | "ssh" | "local" | "cloud"
storage:
  type: "github"
```

- [ ] **Step 2: 提交配置更新**

```bash
git add config/settings.yaml
git commit -m "feat: 添加 SSH 和云存储配置预留"
```

---

## 完成检查清单

- [ ] SSHStorage 核心实现完成
- [ ] 单元测试通过
- [ ] 备份页面 SSH 上传功能正常
- [ ] 恢复页面 SSH 下载功能正常
- [ ] 历史页面 SSH 管理功能正常
- [ ] 设置页面连接测试功能正常
- [ ] 密码加密存储功能正常
- [ ] 云存储占位文件创建完成

---

## 测试验证

```bash
# 运行所有测试
pytest tests/test_ssh_storage.py -v

# 运行应用手动测试
python src/main.py
```

---

*计划生成时间：2026-03-25*
*设计文档：docs/superpowers/specs/2026-03-25-ssh-storage-design.md*