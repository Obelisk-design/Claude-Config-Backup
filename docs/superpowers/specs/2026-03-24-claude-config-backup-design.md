# Claude Config Backup 产品设计文档

## 产品概述

**产品名称**：Claude Config Backup（暂定）

**产品定位**：Claude Code 配置备份工具（商业产品）

**目标用户**：国内使用 Claude Code 的开发者（使用国产模型代理）

**核心价值**：解决配置丢失、迁移困难、多设备同步等问题

---

## 技术架构

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| GUI 框架 | Python + PyQt5 |
| 后端服务 | Python FastAPI（预留） |
| 数据库 | MySQL 8.0 |
| 存储方案 | GitHub 私有仓库（主）、SSH 服务器、COS（预留） |
| 认证方式 | GitHub OAuth 2.0 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     客户端 (PyQt GUI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 备份模块 │ │ 恢复模块 │ │ 登录模块 │ │ 设置模块 │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│                      业务逻辑层                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              备份模块管理器 (插件化架构)               │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │ Core   │ │ Skills │ │Memory  │ │ MCP    │ ...    │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      存储抽象层                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐   │
│  │ GitHub   │ │   SSH    │ │ 腾讯云 COS (预留)        │   │
│  │ 存储驱动 │ │  上传    │ │                          │   │
│  └──────────┘ └──────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     服务端 (MySQL)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  users   │ │ backups  │ │subscriptions│ │user_configs│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 登录模块

### GitHub OAuth 登录流程

```
用户点击 "GitHub 登录"
    ↓
打开浏览器 → GitHub 授权页面
    ↓
用户授权（需要 repo 权限）
    ↓
回调本地 HTTP 服务 → 获取 access_token
    ↓
加密存储 token → 获取用户信息
    ↓
显示登录状态
```

### OAuth 权限说明

| 权限范围 | 用途 | 授权提示 |
|---------|------|---------|
| `read:user` | 获取用户信息 | 读取您的 GitHub 用户信息 |
| `repo` | 创建仓库、上传文件 | 创建和更新您的仓库（用于存储备份文件） |

### 本地存储结构

```
~/.claude-backup/
├── token.enc                 # 加密的 GitHub Token
├── user.json                 # 用户信息缓存
└── config.json               # 应用配置
```

---

## 备份模块（插件化架构）

### 模块接口定义

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

class BackupModule(ABC):
    """备份模块基类"""

    # 模块元信息
    name: str                    # 模块名称
    description: str             # 模块描述
    icon: str = "📦"             # 模块图标
    is_premium: bool = False     # 是否付费模块（预留）

    @abstractmethod
    def get_files(self) -> List[Path]:
        """获取要备份的文件列表"""
        pass

    @abstractmethod
    def get_size(self) -> int:
        """获取总大小（字节）"""
        pass

    def validate(self) -> bool:
        """验证模块是否可用"""
        return True

    def pre_backup(self) -> None:
        """备份前钩子"""
        pass

    def post_restore(self) -> None:
        """恢复后钩子"""
        pass
```

### 模块配置文件

采用 YAML 配置文件驱动，方便扩展和维护。

**配置文件路径**：`config/modules.yaml`

```yaml
# 备份模块配置文件
version: "1.0"

# 模块定义
modules:
  core:
    name: "核心配置"
    description: "settings.json、config.json 等核心配置文件"
    icon: "⚙️"
    is_premium: false
    enabled: true
    paths:
      - pattern: "settings.json"
        required: true
      - pattern: "settings.local.json"
        required: false
      - pattern: "config.json"
        required: true
      - pattern: ".credentials.json"
        required: false
    exclude:
      - "*.bak"
      - "*.backup.*"

  skills:
    name: "技能文件"
    description: "自定义技能文件和符号链接"
    icon: "🎯"
    is_premium: false
    enabled: true
    paths:
      - pattern: "skills/**/*"
        required: false
    follow_symlinks: true
    exclude:
      - "__pycache__"
      - "*.pyc"
      - "node_modules"

  commands:
    name: "自定义命令"
    description: "自定义斜杠命令"
    icon: "💬"
    is_premium: false
    enabled: true
    paths:
      - pattern: "commands/**/*.md"
        required: false

  memory:
    name: "记忆文件"
    description: "Claude 记忆系统文件"
    icon: "🧠"
    is_premium: false
    enabled: true
    paths:
      - pattern: "memory/**/*"
        required: false
    exclude:
      - "*.tmp"

  mcp_servers:
    name: "MCP 服务器"
    description: "MCP 服务器配置和脚本"
    icon: "🔌"
    is_premium: false
    enabled: true
    paths:
      - pattern: "mcp-servers/**/*"
        required: false
    exclude:
      - "__pycache__"
      - "node_modules"
      - "*.log"
      - "*.db"

  tools:
    name: "自定义工具"
    description: "自定义工具脚本"
    icon: "🔧"
    is_premium: false
    enabled: true
    paths:
      - pattern: "tools/**/*"
        required: false
    exclude:
      - "__pycache__"
      - "node_modules"

  hooks:
    name: "钩子配置"
    description: "事件钩子配置（存储在 settings.json 中）"
    icon: "🪝"
    is_premium: false
    enabled: true
    type: "partial"
    source_file: "settings.json"
    json_path: "$.hooks"

  agents:
    name: "Agent 配置"
    description: "自定义 Agent 配置"
    icon: "🤖"
    is_premium: false
    enabled: true
    paths:
      - pattern: "agents/**/*"
        required: false

# 付费模块（预留）
premium_modules:
  history_diff:
    name: "历史记录对比"
    description: "对比不同备份之间的差异"
    icon: "📊"
    is_premium: true
    enabled: false

  auto_backup:
    name: "自动定时备份"
    description: "按计划自动执行备份"
    icon: "⏰"
    is_premium: true
    enabled: false

# 用户自定义模块目录
custom_modules_dir: "custom_modules"
```

### 模块类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `full` | 完整目录/文件备份（默认） | skills、commands |
| `partial` | 部分文件内容提取 | hooks（从 settings.json 提取） |

### 路径模式语法

| 模式 | 说明 |
|------|------|
| `filename` | 根目录下的单个文件 |
| `dir/**/*` | 目录下所有文件（递归） |
| `dir/*.md` | 目录下特定类型文件 |
| `*.json` | 根目录下匹配的文件 |

### 模块加载器

```python
# core/module_loader.py
import yaml
from pathlib import Path
from typing import List, Dict, Any

class ModuleLoader:
    """模块配置加载器"""

    def __init__(self, config_path: str = "config/modules.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.claude_dir = Path.home() / ".claude"

    def _load_config(self) -> Dict:
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_all_modules(self) -> List[Dict[str, Any]]:
        """获取所有模块（包含付费模块）"""
        modules = []

        # 内置模块
        for module_id, module_config in self.config.get("modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        # 付费模块（预留）
        for module_id, module_config in self.config.get("premium_modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        # 用户自定义模块
        custom_dir = Path(self.config.get("custom_modules_dir", "custom_modules"))
        if custom_dir.exists():
            for config_file in custom_dir.glob("*.yaml"):
                with open(config_file, "r", encoding="utf-8") as f:
                    custom = yaml.safe_load(f)
                    custom["id"] = config_file.stem
                    custom["is_custom"] = True
                    modules.append(custom)

        return modules

    def get_enabled_modules(self) -> List[Dict[str, Any]]:
        """获取启用的模块"""
        return [m for m in self.get_all_modules() if m.get("enabled", True)]

    def get_free_modules(self) -> List[Dict[str, Any]]:
        """获取免费模块"""
        return [m for m in self.get_enabled_modules() if not m.get("is_premium", False)]

    def resolve_paths(self, module: Dict) -> List[Path]:
        """解析模块的实际文件路径"""
        paths = []
        for path_config in module.get("paths", []):
            pattern = path_config["pattern"]
            if "**" in pattern:
                # glob 模式
                paths.extend(self.claude_dir.glob(pattern))
            else:
                # 单个文件
                full_path = self.claude_dir / pattern
                if full_path.exists():
                    paths.append(full_path)
        return [p for p in paths if p.is_file()]
```

### 用户自定义模块示例

用户可在 `custom_modules/my_module.yaml` 创建自定义模块：

```yaml
name: "我的项目配置"
description: "特定项目的 Claude 配置"
icon: "📁"
is_premium: false
enabled: true
paths:
  - pattern: "projects/my-project/**/*"
    required: false
exclude:
  - "*.log"
  - "node_modules"
```

### 模块注册机制

```python
# modules/__init__.py
import os
import importlib
from pathlib import Path

class ModuleRegistry:
    def __init__(self):
        self.modules = {}

    def scan(self, module_dir: str = "modules"):
        """自动扫描并注册模块"""
        for file in Path(module_dir).glob("*.py"):
            if file.name.startswith("_"):
                continue
            module = importlib.import_module(f"modules.{file.stem}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BackupModule) and obj != BackupModule:
                    self.register(obj())

    def register(self, module: BackupModule):
        self.modules[module.name] = module

    def get_enabled_modules(self, selected: List[str]) -> List[BackupModule]:
        return [self.modules[name] for name in selected if name in self.modules]
```

---

## 备份文件格式

### 文件结构

```
{timestamp}_{username}_{hash}.ccb (ZIP 压缩包)
├── manifest.json              # 备份元信息
├── snapshot.json              # 文件快照（用于对比）
├── checksum.json              # 文件校验
└── data/                      # 实际数据
    ├── core/
    │   ├── settings.json
    │   └── config.json
    ├── skills/
    ├── commands/
    ├── memory/
    ├── mcp_servers/
    └── tools/
```

### manifest.json

```json
{
  "version": "1.0",
  "app_version": "1.0.0",
  "created_at": "2026-03-24T15:30:00+08:00",
  "username": "zihai",
  "description": "日常备份",
  "modules": [
    {"name": "core", "files": 3, "size": 2048},
    {"name": "skills", "files": 15, "size": 10240}
  ],
  "total_files": 18,
  "total_size": 12288,
  "platform": "windows",
  "claude_version": "2.1.81"
}
```

### snapshot.json

```json
{
  "backup_id": "20260324_153000",
  "modules": {
    "core": {
      "files": [
        {"path": "settings.json", "size": 40167, "hash": "sha256:abc123", "mtime": "2026-03-24"},
        {"path": "config.json", "size": 116, "hash": "sha256:def456", "mtime": "2026-03-18"}
      ]
    }
  }
}
```

### checksum.json

```json
{
  "algorithm": "sha256",
  "files": {
    "data/core/settings.json": "abc123def456...",
    "data/core/config.json": "789xyz012..."
  }
}
```

---

## 存储方案

### 存储选项

| 方案 | 描述 | 限制 | 状态 |
|------|------|------|------|
| GitHub 私有仓库 | 自动创建 claude-config-backup 仓库 | 单文件 100MB，仓库 1GB | ✅ 主方案 |
| SSH 服务器上传 | 上传到用户自己的服务器 | 无限制 | ✅ 支持 |
| 腾讯云 COS | 对象存储 | 按量付费 | 🔜 预留 |
| 仅本地 | 只保存到本地 | 无限制 | ✅ 支持 |

### GitHub 存储流程

```
1. 用户选择 GitHub 存储
    ↓
2. 检查是否存在 claude-config-backup 仓库
   - 不存在 → 自动创建私有仓库
   - 存在 → 直接使用
    ↓
3. 备份时
   - 打包 .ccb 文件
   - 上传到仓库 backups/ 目录
    ↓
4. 恢复时
   - 获取仓库文件列表
   - 下载指定备份
   - 解压恢复
```

### GitHub API 调用

```python
# 创建仓库
POST https://api.github.com/user/repos
Body: {"name": "claude-config-backup", "private": true}

# 上传文件
PUT https://api.github.com/repos/{owner}/claude-config-backup/contents/backups/{filename}
Body: {
    "message": "Backup 2026-03-24",
    "content": "<base64 encoded file>"
}

# 获取文件列表
GET https://api.github.com/repos/{owner}/claude-config-backup/contents/backups

# 下载文件
GET https://api.github.com/repos/{owner}/claude-config-backup/contents/backups/{filename}
```

---

## 数据库设计

### 连接信息

| 配置项 | 值 |
|--------|-----|
| 主机 | 43.153.156.249 |
| 数据库 | claude_backup |
| 字符集 | utf8mb4 |

### 表结构

#### users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| github_id | VARCHAR(50) | GitHub 用户ID，唯一 |
| github_login | VARCHAR(100) | GitHub 用户名 |
| github_avatar | VARCHAR(500) | 头像URL |
| github_email | VARCHAR(200) | 邮箱 |
| user_type | ENUM | 用户类型：free/premium |
| premium_expire_at | DATETIME | 付费到期时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### backups（备份记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| user_id | BIGINT | 用户ID，外键 |
| backup_id | VARCHAR(50) | 备份唯一标识 |
| storage_type | ENUM | 存储类型：github/ssh/cos/local |
| storage_path | VARCHAR(500) | 存储路径 |
| file_size | BIGINT | 文件大小（字节） |
| file_hash | VARCHAR(64) | 文件SHA256哈希 |
| description | VARCHAR(500) | 备份说明 |
| modules | JSON | 备份模块列表 |
| total_files | INT | 总文件数 |
| platform | VARCHAR(20) | 平台：windows/macos/linux |
| claude_version | VARCHAR(50) | Claude Code版本 |
| status | ENUM | 状态：pending/completed/failed |
| created_at | DATETIME | 创建时间 |

#### subscriptions（付费订阅表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| user_id | BIGINT | 用户ID，外键 |
| plan_type | ENUM | 套餐：monthly/yearly/lifetime |
| status | ENUM | 状态：active/expired/cancelled |
| started_at | DATETIME | 开始时间 |
| expired_at | DATETIME | 到期时间 |
| amount | DECIMAL(10,2) | 支付金额 |
| payment_method | VARCHAR(50) | 支付方式 |
| payment_id | VARCHAR(100) | 支付流水号 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### user_configs（用户配置表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| user_id | BIGINT | 用户ID，外键，唯一 |
| default_modules | JSON | 默认备份模块 |
| local_backup_path | VARCHAR(500) | 本地备份路径 |
| ssh_host | VARCHAR(100) | SSH服务器地址 |
| ssh_port | INT | SSH端口 |
| ssh_user | VARCHAR(100) | SSH用户名 |
| ssh_password_encrypted | TEXT | SSH密码（加密） |
| auto_backup_enabled | TINYINT | 自动备份开关 |
| auto_backup_interval | INT | 自动备份间隔（小时） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### login_logs（登录日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| user_id | BIGINT | 用户ID |
| github_login | VARCHAR(100) | GitHub用户名 |
| ip_address | VARCHAR(50) | IP地址 |
| user_agent | VARCHAR(500) | 用户代理 |
| login_at | DATETIME | 登录时间 |

---

## 界面设计

### 主窗口布局

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Config Backup                              [- □ ×]  │
├─────────────────────────────────────────────────────────────┤
│  👤 zihai (GitHub)                            [退出登录]    │
├─────────────────────────────────────────────────────────────┤
│  [📦 备份]  [📥 恢复]  [📜 历史]  [⚙️ 设置]               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     (Tab 内容区域)                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  📢 广告位（预留）                                          │
└─────────────────────────────────────────────────────────────┘
```

### 备份界面

- 模块选择列表（勾选框）
- 备份说明输入框
- 存储位置选择
- 开始备份按钮

### 恢复界面

- 来源选择：本地文件 / 云端列表
- 备份列表（云端时）
- 恢复选项：备份当前配置、跳过已存在文件
- 开始恢复按钮

### 历史界面

- 云端备份列表
- 操作按钮：恢复、下载、删除
- 对比功能（付费）

### 设置界面

- 服务器配置（SSH）
- 存储类型选择
- 备份配置
- 其他设置

---

## 付费点设计

### 免费功能

- ✅ 无限数量备份到 GitHub
- ✅ 核心配置备份
- ✅ Skills / Commands / Memory 等基础模块
- ✅ 本地备份
- ✅ SSH 服务器备份

### 付费功能（预留）

| 功能 | 说明 |
|------|------|
| 历史记录对比 | 元数据快速对比 + 详细内容对比 |
| 自动定时备份 | 按小时/天/周自动备份 |
| 多配置方案 | 工作/个人配置切换 |
| 云端服务器备份 | 备份到我们的服务器 |
| 高级模块 | 预留付费模块 |
| 优先技术支持 | 专属客服 |

---

## CEO Review 扩展功能

以下功能通过 CEO Review（SELECTIVE EXPANSION 模式）确认加入：

### 1. 离线模式支持

**工作量**：S | **风险**：低

**实现方案**：
- 本地 SQLite 数据库缓存用户信息和备份记录
- 离线时操作本地缓存，上线后自动同步到 MySQL
- 冲突解决：以最新时间戳为准

```python
# 本地缓存结构
~/.claude-backup/
├── cache.db              # SQLite 本地缓存
│   ├── users             # 用户信息缓存
│   ├── backups           # 备份记录缓存
│   └── pending_sync      # 待同步队列
└── sync_status.json      # 同步状态
```

### 2. 配置导入/导出

**工作量**：S | **风险**：低

**实现方案**：
- 支持导入 .ccb 备份文件
- 支持从其他用户分享的配置包导入
- 导入时进行版本兼容性检查

### 3. 敏感信息脱敏

**工作量**：M | **风险**：低

**实现方案**：
- 业务逻辑层实现 `SensitiveFilter` 类
- 自动识别敏感字段（Token、Password、Secret 等）
- 用户可选择：脱敏、排除、或保留原值

```yaml
# 敏感字段配置 (config/sensitive_fields.yaml)
patterns:
  - pattern: "*_TOKEN"
    action: mask        # mask | exclude | keep
  - pattern: "*_PASSWORD"
    action: mask
  - pattern: "*_SECRET"
    action: mask
  - pattern: "ANTHROPIC_AUTH_TOKEN"
    action: exclude
```

### 4. 版本检测与自动更新

**工作量**：M | **风险**：低

**实现方案**：
- 启动时检查 GitHub Releases 最新版本
- 显示更新提示，支持自动下载
- 可配置自动安装更新

### 5. 备份预览功能

**工作量**：S | **风险**：低

**实现方案**：
- 备份前显示预览对话框
- 展示：文件列表、总大小、敏感信息警告
- 用户确认后执行备份

### 6. 多语言支持

**工作量**：M | **风险**：低

**实现方案**：
- PyQt 国际化（i18n）支持
- 先实现中文、英文
- 语言包存放在 `locales/` 目录

```
locales/
├── zh_CN.ts    # 中文翻译
└── en_US.ts    # 英文翻译
```

### 7. 错误恢复与回滚

**工作量**：S | **风险**：低

**实现方案**：
- 恢复前自动备份当前配置
- 恢复失败时自动回滚
- 支持手动回滚到之前状态

---

## 错误处理规范

### 异常类定义

```python
# core/exceptions.py

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
    def __init__(self, reset_time: int):
        self.reset_time = reset_time  # 限制重置时间戳

class AuthenticationError(ClaudeBackupError):
    """认证错误"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token 过期"""
    pass

class BackupError(ClaudeBackupError):
    """备份错误"""
    pass

class RestoreError(ClaudeBackupError):
    """恢复错误"""
    pass

class CorruptedFileError(RestoreError):
    """文件损坏"""
    pass

class VersionMismatchError(RestoreError):
    """版本不兼容"""
    pass
```

### 错误处理策略

| 错误类型 | 重试 | 回退 | 用户提示 |
|---------|------|------|---------|
| NetworkError | 3次，指数退避 | 本地缓存 | "网络异常，已切换离线模式" |
| RateLimitError | 等待到 reset_time | 提示等待 | "请求频繁，X分钟后重试" |
| TokenExpiredError | 否 | 重新登录 | "登录已过期，请重新登录" |
| CorruptedFileError | 否 | 回滚 | "备份文件损坏，已恢复原配置" |

---

## 日志与监控

### 日志规范

```python
# 日志级别
DEBUG   # 详细调试信息
INFO    # 正常操作记录
WARNING # 警告信息
ERROR   # 错误信息
CRITICAL # 严重错误

# 日志格式
[时间] [级别] [模块] 消息 {上下文JSON}

# 示例
[2026-03-24 15:30:00] [INFO] [backup] 开始备份 {"user": "zihai", "modules": ["core", "skills"]}
[2026-03-24 15:30:05] [ERROR] [github] 上传失败 {"error": "RateLimitError", "reset_time": 1711281000}
```

### 日志文件位置

```
~/.claude-backup/
└── logs/
    ├── app.log          # 应用日志
    ├── backup.log       # 备份操作日志
    ├── restore.log      # 恢复操作日志
    └── sync.log         # 同步日志
```

---

## 开发计划（更新）

### 阶段一：MVP（最小可用产品）

- [ ] PyQt 基础框架搭建
- [ ] GitHub OAuth 登录
- [ ] 核心备份模块实现
- [ ] GitHub 私有仓库存储
- [ ] 基础恢复功能
- [ ] **备份预览功能（新增）**
- [ ] **敏感信息脱敏（新增）**

### 阶段二：功能完善

- [ ] 所有备份模块实现
- [ ] SSH 服务器存储
- [ ] 历史记录管理
- [ ] 设置界面完善
- [ ] 本地备份
- [ ] **离线模式支持（新增）**
- [ ] **配置导入/导出（新增）**
- [ ] **错误恢复与回滚（新增）**
- [ ] **多语言支持（新增）**

### 阶段三：商业化

- [ ] 付费系统接入
- [ ] 高级功能实现
- [ ] 自动定时备份
- [ ] 配置对比功能
- [ ] 广告系统
- [ ] **版本检测与自动更新（新增）**

---

## 安全考虑

### 敏感信息加密

- GitHub Token 使用 AES-256 加密存储
- SSH 密码加密存储
- 本地密钥派生自用户机器特征

### 敏感信息脱敏（新增）

- 自动识别敏感字段（Token、Password、Secret 等）
- 用户可选择：脱敏（显示 ***）、排除、或保留原值
- 备份预览时高亮显示敏感信息

### 备份文件安全

- 备份文件不包含明文密码
- 可选：备份时排除敏感配置
- 恢复时提示用户检查配置
- **SHA256 校验确保文件完整性（新增）**

### 数据库安全

- 用户密码字段不存储（GitHub OAuth）
- 敏感配置加密存储
- 定期备份用户数据

---

## 附录

### 服务器文件存储结构

```
/backup-data/
├── users/
│   └── github_zihai/
│       ├── config.json
│       └── backups/
│           ├── 2026-03-24_001.zip
│           └── 2026-03-25_001.zip
└── system/
    └── auth.db
```

### 客户端目录结构

```
claude-config-backup/
├── src/
│   ├── main.py              # 程序入口
│   ├── gui/                 # GUI 界面
│   │   ├── main_window.py
│   │   ├── backup_tab.py
│   │   ├── restore_tab.py
│   │   ├── history_tab.py
│   │   └── settings_tab.py
│   ├── modules/             # 备份模块
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── core.py
│   │   ├── skills.py
│   │   └── ...
│   ├── storage/             # 存储驱动
│   │   ├── base.py
│   │   ├── github.py
│   │   ├── ssh.py
│   │   └── cos.py
│   ├── auth/                # 认证模块
│   │   ├── github_oauth.py
│   │   └── token_manager.py
│   └── utils/               # 工具函数
│       ├── crypto.py
│       ├── backup.py
│       └── config.py
├── requirements.txt
└── README.md
```