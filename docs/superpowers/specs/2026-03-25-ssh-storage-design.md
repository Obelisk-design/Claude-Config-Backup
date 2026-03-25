# SSH 存储功能设计文档

## 概述

**目标**：补全 SSH 存储功能，实现完整的备份/恢复/历史管理闭环。

**方案**：创建 `SSHStorage` 类实现 `StorageBase` 接口，使用 `paramiko` 库通过 SFTP 协议上传/下载文件。

---

## 架构设计

### 文件结构

```
src/storage/
├── base.py           # StorageBase 抽象类（已有）
├── github_storage.py # GitHub 存储（已有）
├── ssh_storage.py    # SSH 存储（新增）
└── cloud_storage.py  # 云存储（预留，付费功能）

集成点：
- backup_tab.py: 备份时调用 SSHStorage.upload()
- restore_tab.py: 恢复时调用 SSHStorage.download()
- history_tab.py: 历史记录调用 SSHStorage.list_files()/delete()
- settings_tab.py: SSH 连接测试调用 SSHStorage.test_connection()
```

### 存储类型对比

| 存储类型 | 状态 | 认证方式 | 历史管理 |
|---------|------|---------|---------|
| GitHub | ✅ 已实现 | OAuth Token | 完整支持 |
| SSH | 🆕 本次实现 | 密码认证 | 完整支持 |
| Local | ✅ 已实现 | 无需认证 | 不适用 |
| Cloud | 🔜 预留 | API Key（付费） | 完整支持 |

---

## SSHStorage 类设计

### 类定义

```python
# src/storage/ssh_storage.py

from paramiko import SSHClient, AutoAddPolicy
from typing import Dict, List, Optional, Tuple, Any
from storage.base import StorageBase
from core.exceptions import BackupError, RestoreError, NetworkError, AuthenticationError

class SSHStorage(StorageBase):
    """SSH/SFTP 存储实现"""

    # 连接配置
    BACKUP_DIR = ".claude-backups"  # 服务器上的固定目录
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 30  # seconds

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._client: Optional[SSHClient] = None
        self._sftp = None

    # 支持上下文管理器
    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._disconnect()
```

### 方法实现

#### 核心方法（实现 StorageBase）

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `upload(local_path, remote_path)` | 上传备份文件 | `bool` |
| `download(remote_path, local_path)` | 下载备份文件 | `bool` |
| `list_files(prefix="")` | 列出备份文件 | `List[Dict[str, Any]]` |
| `delete(remote_path)` | 删除备份文件 | `bool` |
| `get_file_url(remote_path)` | 获取文件URL（SSH无URL） | `None` |

**`list_files()` 返回格式规范**：

```python
def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
    """
    Returns:
        List of dicts with keys:
        - "name": str - 文件名
        - "path": str - 相对路径
        - "size": int - 文件大小（字节）
        - "created_at": Optional[str] - ISO 格式时间（从文件名解析）
        - "download_url": None - SSH 无 HTTP URL
    """
```

#### 辅助方法

| 方法 | 说明 |
|------|------|
| `test_connection()` | 测试 SSH 连接，返回 `(success, message)` |
| `_connect()` | 建立 SSH/SFTP 连接（支持重试） |
| `_disconnect()` | 关闭连接 |
| `_ensure_backup_dir()` | 确保服务器备份目录存在 |
| `_get_remote_path(path)` | 获取完整远程路径 |

**辅助方法实现**：

```python
def _get_remote_path(self, path: str) -> str:
    """获取完整远程路径"""
    return f"{self.BACKUP_DIR}/{path}"

def _connect(self):
    """建立 SSH/SFTP 连接（带重试）"""
    import time
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
            return
        except Exception as e:
            last_error = e
            if attempt < self.MAX_RETRIES - 1:
                time.sleep(self.RETRY_DELAY * (attempt + 1))

    # 认证失败特殊处理
    if "Authentication" in str(last_error):
        raise AuthenticationError(f"SSH authentication failed: {last_error}")
    raise NetworkError(f"SSH connection failed after {self.MAX_RETRIES} retries: {last_error}")

def _disconnect(self):
    """关闭连接"""
    if self._sftp:
        self._sftp.close()
        self._sftp = None
    if self._client:
        self._client.close()
        self._client = None
```

### 错误处理

```python
# 复用现有异常体系
from core.exceptions import BackupError, RestoreError, NetworkError, AuthenticationError

# 认证失败
if "Authentication" in str(e):
    raise AuthenticationError(f"SSH authentication failed: {e}")

# 网络错误
raise NetworkError(f"SSH connection failed: {e}")

# 备份/恢复操作失败
raise BackupError(f"Upload failed: {e}")
raise RestoreError(f"Download failed: {e}")
```

**异常映射**：

| SSH 错误类型 | 抛出异常 |
|-------------|---------|
| Authentication failed | `AuthenticationError` |
| Connection timeout | `NetworkError` |
| Host unreachable | `NetworkError` |
| SFTP operation failed | `BackupError` / `RestoreError` |

---

## 数据流设计

### 备份流程

```
用户点击备份
    ↓
读取 storage.type 配置
    ↓
if storage_type == "ssh":
    读取 SSH 配置 (host, port, user, password)
    创建 SSHStorage 实例
    ↓
BackupManager.create_backup() 生成本地 .ccb 文件
    ↓
SSHStorage.upload() 上传到服务器 ~/.claude-backups/
    ↓
显示成功/失败消息
```

### 恢复流程

```
用户进入恢复页面
    ↓
if storage_type == "ssh" and logged_in:
    SSHStorage.list_files() 获取备份列表
    显示在列表中
    ↓
用户选择文件，点击恢复
    ↓
SSHStorage.download() 下载到本地缓存
    ↓
RestoreManager.restore() 解压恢复
    ↓
清理缓存文件
```

### 历史管理

```
用户进入历史页面
    ↓
if storage_type == "ssh":
    SSHStorage.list_files() 获取备份列表
    显示表格：文件名、大小、修改时间、操作按钮
    ↓
操作：
- 恢复：跳转恢复页面
- 下载：SSHStorage.download() 到用户指定位置
- 删除：确认后 SSHStorage.delete()
```

---

## UI 集成

### 设置页面

现有 SSH 配置 UI 已就绪，需要实现：

1. **连接测试**：`_test_ssh_connection()` 调用 `SSHStorage.test_connection()`
2. **密码加密存储**：

```python
# settings_tab.py 保存设置时
from security.crypto import encrypt_password, decrypt_password

def _save_settings(self):
    # 加密密码后存储
    encrypted_password = encrypt_password(self.ssh_password.text())
    self.config.set("ssh.password_encrypted", encrypted_password)
    # 不再存储明文密码
    # self.config.set("ssh.password", "")  # 清空明文

# 使用时解密
def _get_ssh_password(self):
    encrypted = self.config.get("ssh.password_encrypted", "")
    if encrypted:
        return decrypt_password(encrypted)
    return ""
```

### 备份页面

修改 `_on_backup_finished()` 方法：

```python
elif storage_type == "ssh":
    # 创建 SSH 上传工作线程
    ssh_config = {
        "host": self.config.get("ssh.host"),
        "port": self.config.get("ssh.port", 22),
        "user": self.config.get("ssh.user"),
        "password": self.config.get("ssh.password")
    }
    self.worker = SSHUploadWorker(ssh_config, backup_file_path, remote_name)
    self.worker.finished.connect(...)
    self.worker.start()
```

### 恢复/历史页面

根据 `storage_type` 判断使用 `GitHubStorage` 还是 `SSHStorage`。

**`test_connection()` 方法说明**：

此方法不属于 `StorageBase` 接口，是 SSH 存储特有的功能，仅在设置页面调用。

```python
def test_connection(self) -> Tuple[bool, str]:
    """测试 SSH 连接

    Returns:
        (success, message): 成功返回 (True, "连接成功")，失败返回 (False, 错误信息)
    """
    try:
        with self:  # 使用上下文管理器
            return True, f"连接成功：{self.host}:{self.port}"
    except AuthenticationError as e:
        return False, f"认证失败：请检查用户名和密码"
    except NetworkError as e:
        return False, f"连接失败：{e}"
    except Exception as e:
        return False, f"未知错误：{e}"
```

---

## 云存储扩展预留

### 存储类型枚举

```yaml
# config/settings.yaml
storage:
  type: "github"  # "github" | "ssh" | "local" | "cloud"

# 预留云存储配置
cloud:
  provider: ""  # "oss" | "cos" | "s3" | custom
  endpoint: ""
  bucket: ""
  access_key: ""
  secret_key: ""
  is_premium: true  # 付费功能标记
```

### 扩展点

1. **StorageBase 接口**：已定义标准接口，新增存储类型只需实现该接口
2. **工厂模式**：未来可创建 `StorageFactory` 根据 type 返回对应实例
3. **设置页面**：预留云存储配置 UI（隐藏状态）

### 云存储占位结构

```python
# src/storage/cloud_storage.py
"""云存储预留实现（付费功能）"""

from typing import Dict, List, Optional, Any
from storage.base import StorageBase
from core.exceptions import BackupError


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

### SSH 密钥认证预留

当前版本仅支持密码认证。未来可扩展支持 SSH 密钥认证：

```yaml
# config/settings.yaml 预留配置
ssh:
  host: ""
  port: 22
  user: ""
  password: ""  # 密码认证
  password_encrypted: ""  # 加密后的密码
  # 密钥认证（预留）
  key_file: ""  # 私钥文件路径，如 ~/.ssh/id_rsa
  key_passphrase: ""  # 私钥密码（可选）
  auth_type: "password"  # "password" | "key"
```

---

## 测试计划

### 单元测试

- `tests/test_ssh_storage.py`
  - 连接测试
  - 上传/下载测试
  - 文件列表测试
  - 删除测试
  - 错误处理测试

### 集成测试

- 完整备份/恢复流程
- SSH 连接失败重试
- 大文件上传测试

---

## 实现优先级

| 优先级 | 任务 | 依赖 |
|-------|------|------|
| P0 | SSHStorage 核心实现 | paramiko |
| P0 | 备份页面集成 | SSHStorage |
| P0 | 恢复页面集成 | SSHStorage |
| P0 | 历史页面集成 | SSHStorage |
| P1 | 连接测试功能 | SSHStorage |
| P1 | 密码加密存储 | crypto.py |
| P2 | 云存储预留接口 | 无 |

---

## 文件清单

### 新增文件

- `src/storage/ssh_storage.py` - SSH 存储实现
- `src/storage/cloud_storage.py` - 云存储预留（空实现）
- `tests/test_ssh_storage.py` - 单元测试

### 修改文件

- `src/gui/tabs/backup_tab.py` - 添加 SSH 上传逻辑
- `src/gui/tabs/restore_tab.py` - 支持 SSH 恢复
- `src/gui/tabs/history_tab.py` - 支持 SSH 历史管理
- `src/gui/tabs/settings_tab.py` - 实现连接测试
- `config/settings.yaml` - 添加云存储预留配置

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| SSH 连接不稳定 | 重试机制（3次，指数退避）+ 超时设置（30秒） |
| 密码明文存储 | 使用 AES 加密，config 中只存储加密后密码 |
| 大文件上传慢 | 进度显示 + 异步上传（QThread） |
| 服务器目录不存在 | 自动创建 ~/.claude-backups/ |
| MITM 攻击风险 | 文档说明 AutoAddPolicy 风险，建议首次连接可信服务器 |
| 认证失败 | 区分 AuthenticationError，给出明确错误提示 |

### 安全注意事项

**AutoAddPolicy 风险说明**：

`AutoAddPolicy` 会自动接受未知的主机密钥，存在中间人攻击风险。缓解措施：

1. 文档中明确告知用户风险
2. 优先加载系统 `known_hosts`（已实现）
3. 未来可添加"严格模式"选项，仅接受 known_hosts 中的主机