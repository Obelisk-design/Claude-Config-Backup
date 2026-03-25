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
from typing import Dict, List, Optional, Tuple
from storage.base import StorageBase
from core.exceptions import BackupError, RestoreError, NetworkError

class SSHStorage(StorageBase):
    """SSH/SFTP 存储实现"""

    BACKUP_DIR = ".claude-backups"  # 服务器上的固定目录

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self._client: Optional[SSHClient] = None
        self._sftp = None
```

### 方法实现

#### 核心方法（实现 StorageBase）

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `upload(local_path, remote_path)` | 上传备份文件 | `bool` |
| `download(remote_path, local_path)` | 下载备份文件 | `bool` |
| `list_files(prefix="")` | 列出备份文件 | `List[Dict]` |
| `delete(remote_path)` | 删除备份文件 | `bool` |
| `get_file_url(remote_path)` | 获取文件URL（SSH无URL） | `None` |

#### 辅助方法

| 方法 | 说明 |
|------|------|
| `test_connection()` | 测试 SSH 连接，返回 `(success, message)` |
| `_connect()` | 建立 SSH/SFTP 连接 |
| `_disconnect()` | 关闭连接 |
| `_ensure_backup_dir()` | 确保服务器备份目录存在 |
| `_get_remote_path(path)` | 获取完整远程路径 |

### 错误处理

```python
# 复用现有异常体系
try:
    self._connect()
except Exception as e:
    raise NetworkError(f"SSH connection failed: {e}")

try:
    self._sftp.put(local_path, remote_path)
except Exception as e:
    raise BackupError(f"Upload failed: {e}")
```

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
2. **密码加密存储**：使用 `security/crypto.py` 加密保存密码

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
| SSH 连接不稳定 | 重试机制 + 超时设置 |
| 密码明文存储 | 使用 AES 加密 |
| 大文件上传慢 | 进度显示 + 异步上传 |
| 服务器目录不存在 | 自动创建 ~/.claude-backups/ |