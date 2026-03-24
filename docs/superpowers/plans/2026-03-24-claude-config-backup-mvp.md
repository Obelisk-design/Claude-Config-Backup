# Claude Config Backup MVP 实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 Claude Code 配置备份工具 MVP，支持 GitHub 登录、备份核心配置到 GitHub 私有仓库、恢复配置。

**Architecture:** PyQt5 GUI + 插件化备份模块 + GitHub OAuth + MySQL 远程数据库 + SQLite 本地缓存。分层架构：GUI 层 → 业务逻辑层 → 存储抽象层 → 数据库层。

**Tech Stack:** Python 3.10+, PyQt5, PyGithub, PyMySQL, SQLite, PyYAML, cryptography

---

## Chunk 1: 项目初始化与基础架构

### Task 1.1: 项目结构初始化

**Files:**
- Create: `src/__init__.py`
- Create: `src/main.py`
- Create: `src/app.py`
- Create: `requirements.txt`
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: 创建项目目录结构**

```bash
mkdir -p src/{gui/{widgets,tabs,dialogs},core,storage,auth,security,database,utils}
mkdir -p config locales tests
touch src/__init__.py src/gui/__init__.py src/gui/widgets/__init__.py
touch src/gui/tabs/__init__.py src/gui/dialogs/__init__.py
touch src/core/__init__.py src/storage/__init__.py src/auth/__init__.py
touch src/security/__init__.py src/database/__init__.py src/utils/__init__.py
```

- [ ] **Step 2: 创建 requirements.txt**

```text
PyQt5>=5.15.0
PyGithub>=2.0.0
PyMySQL>=1.1.0
PyYAML>=6.0
cryptography>=41.0.0
requests>=2.31.0
paramiko>=3.0.0
```

- [ ] **Step 3: 创建 .gitignore**

```text
__pycache__/
*.py[cod]
*.so
.Python
build/
dist/
*.egg-info/
.eggs/
*.egg
.env
*.log
.cache/
.idea/
.vscode/
*.ccb
```

- [ ] **Step 4: 创建 main.py 入口**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Claude Config Backup - Claude Code 配置备份工具"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app import Application


def main():
    """程序入口"""
    app = Application(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 创建 app.py 应用配置**

```python
# -*- coding: utf-8 -*-
"""QApplication 配置"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 应用配置
APP_NAME = "Claude Config Backup"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "ClaudeBackup"

# 路径配置
APP_DIR = Path.home() / ".claude-backup"
CACHE_DIR = APP_DIR / "cache"
LOG_DIR = APP_DIR / "logs"
CONFIG_FILE = APP_DIR / "config.json"


class Application:
    """应用管理器"""

    def __init__(self, argv):
        self.argv = argv
        self.qt_app = None
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要目录存在"""
        for directory in [APP_DIR, CACHE_DIR, LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def run(self):
        """运行应用"""
        # 高 DPI 支持
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.qt_app = QApplication(self.argv)
        self.qt_app.setApplicationName(APP_NAME)
        self.qt_app.setApplicationVersion(APP_VERSION)
        self.qt_app.setOrganizationName(APP_ORGANIZATION)

        # 延迟导入主窗口避免循环依赖
        from gui.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()

        return self.qt_app.exec_()
```

- [ ] **Step 6: 初始化 Git 仓库并提交**

```bash
git init
git add .
git commit -m "chore: 项目初始化"
```

---

### Task 1.2: 异常体系与日志系统

**Files:**
- Create: `src/core/exceptions.py`
- Create: `src/utils/logger.py`
- Create: `tests/test_exceptions.py`

- [ ] **Step 1: 编写异常类测试**

```python
# tests/test_exceptions.py
import pytest
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
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/CodeSpace/claudeFi
pytest tests/test_exceptions.py -v
```
Expected: FAIL (模块不存在)

- [ ] **Step 3: 实现异常类**

```python
# src/core/exceptions.py
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_exceptions.py -v
```
Expected: PASS

- [ ] **Step 5: 实现日志工具**

```python
# src/utils/logger.py
# -*- coding: utf-8 -*-
"""日志工具"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 日志目录
LOG_DIR = Path.home() / ".claude-backup" / "logs"


def setup_logger(
    name: str = "claude-backup",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """设置日志器

    Args:
        name: 日志器名称
        level: 日志级别
        log_file: 日志文件名（不含路径）

    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_path = LOG_DIR / log_file
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(module)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# 默认日志器
logger = setup_logger(log_file="app.log")
```

- [ ] **Step 6: 提交基础架构**

```bash
git add .
git commit -m "feat: 添加异常体系和日志系统"
```

---

### Task 1.3: 配置管理系统

**Files:**
- Create: `src/utils/config.py`
- Create: `config/settings.yaml`
- Create: `tests/test_config.py`

- [ ] **Step 1: 创建默认配置文件**

```yaml
# config/settings.yaml
app:
  name: "Claude Config Backup"
  version: "1.0.0"
  language: "zh_CN"

database:
  host: "43.153.156.249"
  port: 3306
  name: "claude_backup"
  charset: "utf8mb4"

github:
  client_id: ""  # 需要配置
  client_secret: ""  # 需要配置
  redirect_port: 18080
  repo_name: "claude-config-backup"

backup:
  max_file_size_mb: 100
  default_modules:
    - core
    - skills
    - commands
    - memory
  exclude_patterns:
    - "__pycache__"
    - "*.pyc"
    - "node_modules"
    - "*.log"

sensitive_fields:
  patterns:
    - "*_TOKEN"
    - "*_PASSWORD"
    - "*_SECRET"
    - "ANTHROPIC_AUTH_TOKEN"
  action: "mask"  # mask | exclude | keep

update:
  check_on_startup: true
  auto_download: false
  releases_url: "https://api.github.com/repos/{owner}/{repo}/releases/latest"
```

- [ ] **Step 2: 编写配置管理测试**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from utils.config import Config, get_config


class TestConfig:
    def test_load_default_config(self):
        """测试加载默认配置"""
        config = Config()
        assert config.get("app.name") == "Claude Config Backup"
        assert config.get("app.language") == "zh_CN"

    def test_get_nested_value(self):
        """测试获取嵌套值"""
        config = Config()
        assert config.get("database.host") == "43.153.156.249"
        assert config.get("database.port") == 3306

    def test_get_default_value(self):
        """测试获取默认值"""
        config = Config()
        assert config.get("nonexistent.key", "default") == "default"

    def test_set_value(self):
        """测试设置值"""
        config = Config()
        config.set("test.key", "value")
        assert config.get("test.key") == "value"
```

- [ ] **Step 3: 实现配置管理器**

```python
# src/utils/config.py
# -*- coding: utf-8 -*-
"""配置管理"""

import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional

# 配置路径
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
USER_CONFIG_DIR = Path.home() / ".claude-backup"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"


class Config:
    """配置管理器"""

    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置"""
        # 加载默认配置
        default_config_path = CONFIG_DIR / "settings.yaml"
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}

        # 加载用户配置（覆盖默认）
        if USER_CONFIG_FILE.exists():
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                self._deep_merge(self._config, user_config)

    def _deep_merge(self, base: Dict, override: Dict):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点分隔的嵌套键

        Args:
            key: 配置键，如 "database.host"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """保存用户配置"""
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def reload(self):
        """重新加载配置"""
        self._load_config()


def get_config() -> Config:
    """获取配置单例"""
    return Config()
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_config.py -v
```
Expected: PASS

- [ ] **Step 5: 提交配置系统**

```bash
git add .
git commit -m "feat: 添加配置管理系统"
```

---

## Chunk 2: 数据库层

### Task 2.1: MySQL 客户端

**Files:**
- Create: `src/database/mysql_client.py`
- Create: `src/database/sqlite_cache.py`
- Create: `tests/test_mysql_client.py`

- [ ] **Step 1: 编写 MySQL 客户端测试**

```python
# tests/test_mysql_client.py
import pytest
from unittest.mock import patch, MagicMock
from database.mysql_client import MySQLClient


class TestMySQLClient:
    def test_connection_params(self):
        """测试连接参数"""
        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        assert client.host == "localhost"
        assert client.port == 3306

    @patch('pymysql.connect')
    def test_connect(self, mock_connect):
        """测试连接"""
        mock_connect.return_value = MagicMock()
        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        client.connect()
        mock_connect.assert_called_once()
        assert client.is_connected

    @patch('pymysql.connect')
    def test_execute_query(self, mock_connect):
        """测试执行查询"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        client = MySQLClient(
            host="localhost",
            port=3306,
            user="root",
            password="test",
            database="test_db"
        )
        client.connect()
        result = client.execute("SELECT * FROM users")

        assert len(result) == 1
        assert result[0]["name"] == "test"
```

- [ ] **Step 2: 实现 MySQL 客户端**

```python
# src/database/mysql_client.py
# -*- coding: utf-8 -*-
"""MySQL 客户端"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from utils.logger import logger
from core.exceptions import NetworkError


class MySQLClient:
    """MySQL 数据库客户端"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
        connect_timeout: int = 10
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.connect_timeout = connect_timeout

        self._connection: Optional[pymysql.Connection] = None

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        if self._connection is None:
            return False
        try:
            self._connection.ping(reconnect=True)
            return True
        except:
            return False

    def connect(self):
        """建立连接"""
        try:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=DictCursor,
                connect_timeout=self.connect_timeout
            )
            logger.info(f"MySQL 连接成功: {self.host}:{self.port}/{self.database}")
        except pymysql.Error as e:
            logger.error(f"MySQL 连接失败: {e}")
            raise NetworkError(f"数据库连接失败: {e}")

    def disconnect(self):
        """断开连接"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("MySQL 连接已断开")

    @contextmanager
    def cursor(self):
        """获取游标上下文管理器"""
        if not self.is_connected:
            self.connect()

        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"SQL 执行错误: {e}")
            raise
        finally:
            cursor.close()

    def execute(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """执行 SQL 查询

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            查询结果列表
        """
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_one(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """执行 SQL 查询并返回单条结果"""
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据

        Args:
            table: 表名
            data: 数据字典

        Returns:
            插入的 ID
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[tuple] = None
    ) -> int:
        """更新数据

        Args:
            table: 表名
            data: 更新数据
            where: WHERE 条件
            where_params: WHERE 参数

        Returns:
            影响行数
        """
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

        with self.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()) + (where_params or ()))
            return cursor.rowcount
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_mysql_client.py -v
```
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: 添加 MySQL 客户端"
```

---

### Task 2.2: SQLite 离线缓存

**Files:**
- Create: `src/database/sqlite_cache.py`
- Create: `tests/test_sqlite_cache.py`

- [ ] **Step 1: 编写 SQLite 缓存测试**

```python
# tests/test_sqlite_cache.py
import pytest
import tempfile
import os
from database.sqlite_cache import SQLiteCache


class TestSQLiteCache:
    def test_init_database(self):
        """测试初始化数据库"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)
            assert os.path.exists(db_path)

    def test_cache_user(self):
        """测试缓存用户"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)

            user_data = {
                "github_id": "12345",
                "github_login": "testuser",
                "github_email": "test@example.com"
            }
            cache.save_user(user_data)

            user = cache.get_user("12345")
            assert user is not None
            assert user["github_login"] == "testuser"

    def test_cache_backup(self):
        """测试缓存备份记录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cache = SQLiteCache(db_path)

            backup_data = {
                "backup_id": "20260324_001",
                "user_id": 1,
                "storage_type": "github",
                "description": "test backup",
                "status": "completed"
            }
            cache.save_backup(backup_data)

            backups = cache.get_backups(user_id=1)
            assert len(backups) == 1
            assert backups[0]["backup_id"] == "20260324_001"
```

- [ ] **Step 2: 实现 SQLite 缓存**

```python
# src/database/sqlite_cache.py
# -*- coding: utf-8 -*-
"""SQLite 离线缓存"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from utils.logger import logger

# 默认缓存路径
DEFAULT_CACHE_PATH = Path.home() / ".claude-backup" / "cache.db"


class SQLiteCache:
    """SQLite 本地缓存"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DEFAULT_CACHE_PATH)
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 用户缓存表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    github_id TEXT UNIQUE NOT NULL,
                    github_login TEXT NOT NULL,
                    github_avatar TEXT,
                    github_email TEXT,
                    user_type TEXT DEFAULT 'free',
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dirty INTEGER DEFAULT 0
                )
            """)

            # 备份记录缓存表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    storage_type TEXT,
                    storage_path TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    description TEXT,
                    modules TEXT,
                    status TEXT DEFAULT 'pending',
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dirty INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 待同步队列
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_sync (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.debug(f"SQLite 缓存数据库初始化完成: {self.db_path}")

    def save_user(self, user_data: Dict[str, Any]) -> int:
        """保存用户缓存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO users
                (github_id, github_login, github_avatar, github_email, user_type, dirty)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (
                user_data.get("github_id"),
                user_data.get("github_login"),
                user_data.get("github_avatar"),
                user_data.get("github_email"),
                user_data.get("user_type", "free")
            ))

            # 添加到待同步队列
            cursor.execute("""
                INSERT INTO pending_sync (action, table_name, record_id)
                VALUES ('upsert', 'users', ?)
            """, (cursor.lastrowid,))

            conn.commit()
            return cursor.lastrowid

    def get_user(self, github_id: str) -> Optional[Dict[str, Any]]:
        """获取用户缓存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE github_id = ?",
                (github_id,)
            )
            row = cursor.fetchone()

            return dict(row) if row else None

    def save_backup(self, backup_data: Dict[str, Any]) -> int:
        """保存备份记录缓存"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO backups
                (backup_id, user_id, storage_type, storage_path, file_size,
                 file_hash, description, modules, status, dirty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                backup_data.get("backup_id"),
                backup_data.get("user_id"),
                backup_data.get("storage_type"),
                backup_data.get("storage_path"),
                backup_data.get("file_size"),
                backup_data.get("file_hash"),
                backup_data.get("description"),
                json.dumps(backup_data.get("modules", [])),
                backup_data.get("status", "pending")
            ))

            # 添加到待同步队列
            cursor.execute("""
                INSERT INTO pending_sync (action, table_name, record_id)
                VALUES ('upsert', 'backups', ?)
            """, (cursor.lastrowid,))

            conn.commit()
            return cursor.lastrowid

    def get_backups(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的备份列表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM backups
                WHERE user_id = ?
                ORDER BY cached_at DESC
                LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_pending_sync(self) -> List[Dict[str, Any]]:
        """获取待同步队列"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pending_sync ORDER BY created_at")
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def clear_pending_sync(self, record_ids: List[int]):
        """清除已同步的记录"""
        if not record_ids:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            placeholders = ", ".join("?" * len(record_ids))
            cursor.execute(
                f"DELETE FROM pending_sync WHERE id IN ({placeholders})",
                record_ids
            )
            conn.commit()
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_sqlite_cache.py -v
```
Expected: PASS

---

## Chunk 3: 备份模块系统

### Task 3.1: 模块加载器

**Files:**
- Create: `config/modules.yaml`
- Create: `src/core/module_loader.py`
- Create: `tests/test_module_loader.py`

- [ ] **Step 1: 创建模块配置文件**

```yaml
# config/modules.yaml
version: "1.0"

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
    exclude:
      - "*.bak"
      - "*.backup.*"

  skills:
    name: "技能文件"
    description: "自定义技能文件"
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

premium_modules: {}
custom_modules_dir: "custom_modules"
```

- [ ] **Step 2: 编写模块加载器测试**

```python
# tests/test_module_loader.py
import pytest
from core.module_loader import ModuleLoader


class TestModuleLoader:
    def test_load_config(self):
        """测试加载配置"""
        loader = ModuleLoader()
        assert loader.config is not None
        assert loader.config.get("version") == "1.0"

    def test_get_all_modules(self):
        """测试获取所有模块"""
        loader = ModuleLoader()
        modules = loader.get_all_modules()

        assert len(modules) >= 4
        module_ids = [m["id"] for m in modules]
        assert "core" in module_ids
        assert "skills" in module_ids

    def test_get_free_modules(self):
        """测试获取免费模块"""
        loader = ModuleLoader()
        modules = loader.get_free_modules()

        for m in modules:
            assert m.get("is_premium", False) is False

    def test_resolve_paths(self):
        """测试解析路径"""
        loader = ModuleLoader()
        core_module = None
        for m in loader.get_all_modules():
            if m["id"] == "core":
                core_module = m
                break

        assert core_module is not None
        # 路径解析需要 .claude 目录存在
```

- [ ] **Step 3: 实现模块加载器**

```python
# src/core/module_loader.py
# -*- coding: utf-8 -*-
"""备份模块加载器"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from utils.logger import logger
from utils.config import CONFIG_DIR

# Claude 配置目录
CLAUDE_DIR = Path.home() / ".claude"


class ModuleLoader:
    """备份模块加载器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(CONFIG_DIR / "modules.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                logger.debug(f"加载模块配置: {len(config.get('modules', {}))} 个模块")
                return config
        except FileNotFoundError:
            logger.warning(f"模块配置文件不存在: {self.config_path}")
            return {"modules": {}, "premium_modules": {}}

    def get_all_modules(self) -> List[Dict[str, Any]]:
        """获取所有模块"""
        modules = []

        # 内置模块
        for module_id, module_config in self.config.get("modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        # 付费模块
        for module_id, module_config in self.config.get("premium_modules", {}).items():
            module_config["id"] = module_id
            modules.append(module_config)

        # 用户自定义模块
        custom_dir = CLAUDE_DIR / self.config.get("custom_modules_dir", "custom_modules")
        if custom_dir.exists():
            for config_file in custom_dir.glob("*.yaml"):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        custom = yaml.safe_load(f)
                        custom["id"] = config_file.stem
                        custom["is_custom"] = True
                        modules.append(custom)
                except Exception as e:
                    logger.warning(f"加载自定义模块失败: {config_file}, {e}")

        return modules

    def get_enabled_modules(self) -> List[Dict[str, Any]]:
        """获取启用的模块"""
        return [m for m in self.get_all_modules() if m.get("enabled", True)]

    def get_free_modules(self) -> List[Dict[str, Any]]:
        """获取免费模块"""
        return [m for m in self.get_enabled_modules() if not m.get("is_premium", False)]

    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取模块"""
        for m in self.get_all_modules():
            if m["id"] == module_id:
                return m
        return None

    def resolve_paths(self, module: Dict) -> List[Path]:
        """解析模块的实际文件路径

        Args:
            module: 模块配置

        Returns:
            文件路径列表
        """
        paths = []
        exclude_patterns = module.get("exclude", [])

        for path_config in module.get("paths", []):
            pattern = path_config["pattern"]

            if "**" in pattern:
                # glob 模式
                matched = list(CLAUDE_DIR.glob(pattern))
                for p in matched:
                    if self._should_include(p, exclude_patterns):
                        paths.append(p)
            else:
                # 单个文件
                full_path = CLAUDE_DIR / pattern
                if full_path.exists() and self._should_include(full_path, exclude_patterns):
                    paths.append(full_path)

        return [p for p in paths if p.is_file()]

    def _should_include(self, path: Path, exclude_patterns: List[str]) -> bool:
        """检查路径是否应该被包含"""
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                # 后缀匹配
                if path_str.endswith(pattern[1:]):
                    return False
            elif pattern in path_str:
                return False
        return True

    def get_module_size(self, module: Dict) -> int:
        """获取模块总大小（字节）"""
        total = 0
        for path in self.resolve_paths(module):
            try:
                total += path.stat().st_size
            except:
                pass
        return total
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_module_loader.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add .
git commit -m "feat: 添加备份模块加载器"
```

---

### Task 3.2: 备份管理器

**Files:**
- Create: `src/core/backup_manager.py`
- Create: `tests/test_backup_manager.py`

- [ ] **Step 1: 编写备份管理器测试**

```python
# tests/test_backup_manager.py
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from core.backup_manager import BackupManager


class TestBackupManager:
    def test_create_backup_id(self):
        """测试生成备份 ID"""
        manager = BackupManager()
        backup_id = manager._generate_backup_id()
        assert backup_id.startswith("20")  # 年份开头
        assert len(backup_id) == 15  # YYYYMMDD_HHMMSS

    def test_collect_files(self):
        """测试收集文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "settings.json"
            test_file.write_text('{"test": true}')

            manager = BackupManager()
            # 这里需要 mock CLAUDE_DIR

    def test_create_manifest(self):
        """测试创建清单"""
        manager = BackupManager()
        manifest = manager._create_manifest(
            username="testuser",
            description="test backup",
            modules=["core"],
            total_files=5,
            total_size=1024
        )

        assert manifest["version"] == "1.0"
        assert manifest["username"] == "testuser"
        assert manifest["description"] == "test backup"
        assert "created_at" in manifest
```

- [ ] **Step 2: 实现备份管理器**

```python
# src/core/backup_manager.py
# -*- coding: utf-8 -*-
"""备份管理器"""

import json
import hashlib
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils.logger import logger
from utils.config import get_config
from core.module_loader import ModuleLoader
from core.exceptions import BackupError
from security.sensitive_filter import SensitiveFilter

# 路径配置
CLAUDE_DIR = Path.home() / ".claude"
CACHE_DIR = Path.home() / ".claude-backup" / "cache"


class BackupManager:
    """备份管理器"""

    def __init__(self):
        self.config = get_config()
        self.module_loader = ModuleLoader()
        self.sensitive_filter = SensitiveFilter()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        modules: List[str],
        description: str = "",
        username: str = "",
        include_sensitive: bool = False
    ) -> Path:
        """创建备份

        Args:
            modules: 要备份的模块 ID 列表
            description: 备份说明
            username: 用户名
            include_sensitive: 是否包含敏感信息

        Returns:
            备份文件路径
        """
        backup_id = self._generate_backup_id()
        backup_file = CACHE_DIR / f"{backup_id}_{username}.ccb"

        logger.info(f"开始创建备份: {backup_id}, 模块: {modules}")

        # 收集文件
        all_files = self._collect_files(modules)

        # 创建清单
        manifest = self._create_manifest(
            username=username,
            description=description,
            modules=modules,
            total_files=len(all_files),
            total_size=sum(f[1].stat().st_size for f in all_files)
        )

        # 创建快照
        snapshot = self._create_snapshot(all_files)

        # 创建校验
        checksum_data = {}

        # 写入备份文件
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 写入清单
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

            # 写入快照
            zf.writestr("snapshot.json", json.dumps(snapshot, ensure_ascii=False, indent=2))

            # 写入文件
            for module_id, file_path in all_files:
                # 计算相对路径
                rel_path = file_path.relative_to(CLAUDE_DIR)
                archive_path = f"data/{module_id}/{rel_path}"

                # 读取内容
                content = file_path.read_bytes()

                # 敏感信息处理
                if not include_sensitive and file_path.suffix == ".json":
                    try:
                        data = json.loads(content)
                        data = self.sensitive_filter.filter(data)
                        content = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
                    except:
                        pass

                # 计算校验
                file_hash = hashlib.sha256(content).hexdigest()
                checksum_data[archive_path] = file_hash

                # 写入
                zf.writestr(archive_path, content)

        # 写入校验
        checksum = {"algorithm": "sha256", "files": checksum_data}
        with zipfile.ZipFile(backup_file, 'a') as zf:
            zf.writestr("checksum.json", json.dumps(checksum, indent=2))

        logger.info(f"备份创建完成: {backup_file}, 大小: {backup_file.stat().st_size} 字节")
        return backup_file

    def _generate_backup_id(self) -> str:
        """生成备份 ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _collect_files(self, module_ids: List[str]) -> List[tuple]:
        """收集要备份的文件

        Returns:
            [(module_id, file_path), ...]
        """
        all_files = []

        for module_id in module_ids:
            module = self.module_loader.get_module_by_id(module_id)
            if not module:
                logger.warning(f"模块不存在: {module_id}")
                continue

            files = self.module_loader.resolve_paths(module)
            for f in files:
                all_files.append((module_id, f))

        logger.debug(f"收集到 {len(all_files)} 个文件")
        return all_files

    def _create_manifest(
        self,
        username: str,
        description: str,
        modules: List[str],
        total_files: int,
        total_size: int
    ) -> Dict[str, Any]:
        """创建备份清单"""
        return {
            "version": "1.0",
            "app_version": self.config.get("app.version", "1.0.0"),
            "created_at": datetime.now().isoformat(),
            "username": username,
            "description": description,
            "modules": [{"id": m} for m in modules],
            "total_files": total_files,
            "total_size": total_size,
            "platform": self._get_platform()
        }

    def _create_snapshot(self, files: List[tuple]) -> Dict[str, Any]:
        """创建文件快照"""
        snapshot = {
            "backup_id": self._generate_backup_id(),
            "modules": {}
        }

        for module_id, file_path in files:
            if module_id not in snapshot["modules"]:
                snapshot["modules"][module_id] = {"files": []}

            rel_path = file_path.relative_to(CLAUDE_DIR)
            file_info = {
                "path": str(rel_path),
                "size": file_path.stat().st_size,
                "hash": hashlib.sha256(file_path.read_bytes()).hexdigest()[:16],
                "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            snapshot["modules"][module_id]["files"].append(file_info)

        return snapshot

    def _get_platform(self) -> str:
        """获取平台信息"""
        import platform
        system = platform.system().lower()
        return {"darwin": "macos", "windows": "windows", "linux": "linux"}.get(system, system)

    def get_preview(self, modules: List[str]) -> Dict[str, Any]:
        """获取备份预览

        Returns:
            {
                "modules": [...],
                "total_files": int,
                "total_size": int,
                "sensitive_files": [...]
            }
        """
        all_files = self._collect_files(modules)

        preview = {
            "modules": [],
            "total_files": len(all_files),
            "total_size": 0,
            "sensitive_files": []
        }

        module_stats = {}
        for module_id, file_path in all_files:
            size = file_path.stat().st_size
            preview["total_size"] += size

            if module_id not in module_stats:
                module_stats[module_id] = {"files": 0, "size": 0}
            module_stats[module_id]["files"] += 1
            module_stats[module_id]["size"] += size

            # 检测敏感文件
            if file_path.suffix == ".json":
                try:
                    data = json.loads(file_path.read_text())
                    if self.sensitive_filter.has_sensitive(data):
                        preview["sensitive_files"].append(str(file_path.relative_to(CLAUDE_DIR)))
                except:
                    pass

        preview["modules"] = [
            {"id": k, "files": v["files"], "size": v["size"]}
            for k, v in module_stats.items()
        ]

        return preview
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_backup_manager.py -v
```
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: 添加备份管理器"
```

---

## Chunk 4: 安全层

### Task 4.1: 敏感信息过滤器

**Files:**
- Create: `config/sensitive_fields.yaml`
- Create: `src/security/sensitive_filter.py`
- Create: `tests/test_sensitive_filter.py`

- [ ] **Step 1: 创建敏感字段配置**

```yaml
# config/sensitive_fields.yaml
patterns:
  - pattern: "*_TOKEN"
    action: "mask"
  - pattern: "*_PASSWORD"
    action: "mask"
  - pattern: "*_SECRET"
    action: "mask"
  - pattern: "ANTHROPIC_AUTH_TOKEN"
    action: "exclude"
  - pattern: "mysql_password"
    action: "mask"
  - pattern: "ssh_password*"
    action: "mask"

mask_value: "***MASKED***"
```

- [ ] **Step 2: 编写过滤器测试**

```python
# tests/test_sensitive_filter.py
import pytest
from security.sensitive_filter import SensitiveFilter


class TestSensitiveFilter:
    def test_mask_token(self):
        """测试 Token 脱敏"""
        filter = SensitiveFilter()
        data = {
            "API_TOKEN": "secret123",
            "normal_field": "value"
        }
        result = filter.filter(data)

        assert result["API_TOKEN"] == "***MASKED***"
        assert result["normal_field"] == "value"

    def test_exclude_token(self):
        """测试排除字段"""
        filter = SensitiveFilter()
        data = {
            "ANTHROPIC_AUTH_TOKEN": "sk-xxx",
            "other": "value"
        }
        result = filter.filter(data)

        assert "ANTHROPIC_AUTH_TOKEN" not in result
        assert result["other"] == "value"

    def test_nested_data(self):
        """测试嵌套数据"""
        filter = SensitiveFilter()
        data = {
            "env": {
                "DB_PASSWORD": "pass123",
                "DB_HOST": "localhost"
            }
        }
        result = filter.filter(data)

        assert result["env"]["DB_PASSWORD"] == "***MASKED***"
        assert result["env"]["DB_HOST"] == "localhost"

    def test_has_sensitive(self):
        """测试检测敏感信息"""
        filter = SensitiveFilter()

        assert filter.has_sensitive({"API_TOKEN": "xxx"}) is True
        assert filter.has_sensitive({"normal": "value"}) is False
```

- [ ] **Step 3: 实现过滤器**

```python
# src/security/sensitive_filter.py
# -*- coding: utf-8 -*-
"""敏感信息过滤器"""

import yaml
import fnmatch
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy

from utils.logger import logger
from utils.config import CONFIG_DIR


class SensitiveFilter:
    """敏感信息过滤器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(CONFIG_DIR / "sensitive_fields.yaml")
        self.patterns = []
        self.mask_value = "***MASKED***"
        self._load_config()

    def _load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                self.patterns = config.get("patterns", [])
                self.mask_value = config.get("mask_value", "***MASKED***")
                logger.debug(f"加载敏感字段配置: {len(self.patterns)} 个规则")
        except FileNotFoundError:
            # 默认规则
            self.patterns = [
                {"pattern": "*_TOKEN", "action": "mask"},
                {"pattern": "*_PASSWORD", "action": "mask"},
                {"pattern": "*_SECRET", "action": "mask"},
            ]

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """检查 key 是否匹配模式"""
        return fnmatch.fnmatch(key.upper(), pattern.upper())

    def _get_action(self, key: str) -> Optional[str]:
        """获取字段的处理动作"""
        for rule in self.patterns:
            if self._match_pattern(key, rule["pattern"]):
                return rule.get("action", "mask")
        return None

    def filter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤敏感信息

        Args:
            data: 原始数据

        Returns:
            过滤后的数据
        """
        result = {}
        for key, value in data.items():
            action = self._get_action(key)

            if action == "exclude":
                # 排除该字段
                continue
            elif action == "mask":
                # 脱敏处理
                if isinstance(value, dict):
                    result[key] = self.filter(value)
                else:
                    result[key] = self.mask_value
            else:
                # 保留原值
                if isinstance(value, dict):
                    result[key] = self.filter(value)
                else:
                    result[key] = value

        return result

    def has_sensitive(self, data: Dict[str, Any]) -> bool:
        """检查数据是否包含敏感信息

        Args:
            data: 数据字典

        Returns:
            是否包含敏感信息
        """
        for key, value in data.items():
            if self._get_action(key):
                return True
            if isinstance(value, dict) and self.has_sensitive(value):
                return True
        return False

    def get_sensitive_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """获取所有敏感字段的路径

        Args:
            data: 数据字典
            prefix: 路径前缀

        Returns:
            敏感字段路径列表
        """
        keys = []
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if self._get_action(key):
                keys.append(path)
            if isinstance(value, dict):
                keys.extend(self.get_sensitive_keys(value, path))
        return keys
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_sensitive_filter.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add .
git commit -m "feat: 添加敏感信息过滤器"
```

---

### Task 4.2: 加密工具

**Files:**
- Create: `src/security/crypto.py`
- Create: `tests/test_crypto.py`

- [ ] **Step 1: 编写加密工具测试**

```python
# tests/test_crypto.py
import pytest
from security.crypto import Crypto


class TestCrypto:
    def test_encrypt_decrypt(self):
        """测试加密解密"""
        crypto = Crypto()
        original = "my_secret_token"

        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        assert decrypted == original
        assert encrypted != original

    def test_different_encryption(self):
        """测试相同内容不同加密结果（随机 IV）"""
        crypto = Crypto()
        original = "same_content"

        encrypted1 = crypto.encrypt(original)
        encrypted2 = crypto.encrypt(original)

        # 相同内容，不同加密结果
        assert encrypted1 != encrypted2
        # 但都能正确解密
        assert crypto.decrypt(encrypted1) == original
        assert crypto.decrypt(encrypted2) == original
```

- [ ] **Step 2: 实现加密工具**

```python
# src/security/crypto.py
# -*- coding: utf-8 -*-
"""加密工具"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from utils.logger import logger


class Crypto:
    """AES-256 加密工具"""

    def __init__(self, key: str = None):
        """初始化

        Args:
            key: 加密密钥，如果不提供则从机器特征生成
        """
        if key:
            self.key = self._derive_key(key)
        else:
            self.key = self._generate_machine_key()

    def _derive_key(self, password: str) -> bytes:
        """从密码派生密钥"""
        return hashlib.sha256(password.encode()).digest()

    def _generate_machine_key(self) -> bytes:
        """从机器特征生成密钥"""
        import platform

        # 组合机器特征
        features = [
            platform.node(),  # 主机名
            platform.system(),  # 操作系统
            os.path.expanduser("~"),  # 用户目录
        ]

        combined = "|".join(features)
        return hashlib.sha256(combined.encode()).digest()

    def encrypt(self, plaintext: str) -> str:
        """加密字符串

        Args:
            plaintext: 明文

        Returns:
            Base64 编码的密文
        """
        # 生成随机 IV
        iv = os.urandom(16)

        # 创建加密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # PKCS7 填充
        data = plaintext.encode('utf-8')
        padding_len = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_len] * padding_len)

        # 加密
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # 组合 IV 和密文，Base64 编码
        result = base64.b64encode(iv + ciphertext).decode('utf-8')
        return result

    def decrypt(self, ciphertext: str) -> str:
        """解密字符串

        Args:
            ciphertext: Base64 编码的密文

        Returns:
            明文
        """
        # Base64 解码
        data = base64.b64decode(ciphertext.encode('utf-8'))

        # 分离 IV 和密文
        iv = data[:16]
        actual_ciphertext = data[16:]

        # 创建解密器
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # 解密
        padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

        # 去除 PKCS7 填充
        padding_len = padded_data[-1]
        plaintext = padded_data[:-padding_len].decode('utf-8')

        return plaintext
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_crypto.py -v
```
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: 添加加密工具"
```

---

## Chunk 5: 执行计划

MVP 阶段剩余任务请使用 superpowers:subagent-driven-development 执行。

### MVP 任务清单

| Chunk | Task | 状态 |
|-------|------|------|
| 1 | 项目初始化 | ✅ 计划完成 |
| 1 | 异常体系与日志 | ✅ 计划完成 |
| 1 | 配置管理 | ✅ 计划完成 |
| 2 | MySQL 客户端 | ✅ 计划完成 |
| 2 | SQLite 缓存 | ✅ 计划完成 |
| 3 | 模块加载器 | ✅ 计划完成 |
| 3 | 备份管理器 | ✅ 计划完成 |
| 4 | 敏感信息过滤器 | ✅ 计划完成 |
| 4 | 加密工具 | ✅ 计划完成 |
| 5 | GitHub OAuth | 待规划 |
| 5 | GitHub 存储 | 待规划 |
| 5 | 恢复管理器 | 待规划 |
| 5 | GUI 主窗口 | 待规划 |
| 5 | GUI Tabs | 待规划 |
| 5 | 集成测试 | 待规划 |

---

## Chunk 5: GitHub 认证与存储

### Task 5.1: GitHub OAuth 登录

**Files:**
- Create: `src/auth/github_oauth.py`
- Create: `src/auth/token_manager.py`
- Create: `tests/test_github_oauth.py`

- [ ] **Step 1: 编写 OAuth 测试**

```python
# tests/test_github_oauth.py
import pytest
from unittest.mock import patch, MagicMock
from auth.github_oauth import GitHubOAuth


class TestGitHubOAuth:
    def test_generate_auth_url(self):
        """测试生成授权 URL"""
        oauth = GitHubOAuth(client_id="test_id", client_secret="test_secret")
        url = oauth.get_authorization_url()

        assert "github.com/login/oauth/authorize" in url
        assert "client_id=test_id" in url
        assert "scope=repo,read:user" in url

    @patch('requests.post')
    def test_exchange_code(self, mock_post):
        """测试用 code 换取 token"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        oauth = GitHubOAuth(client_id="test_id", client_secret="test_secret")
        token = oauth.exchange_code("test_code")

        assert token == "test_token"

    @patch('requests.get')
    def test_get_user_info(self, mock_get):
        """测试获取用户信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://example.com/avatar.png"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        oauth = GitHubOAuth(client_id="test_id", client_secret="test_secret")
        user = oauth.get_user_info("test_token")

        assert user["login"] == "testuser"
```

- [ ] **Step 2: 实现 GitHub OAuth**

```python
# src/auth/github_oauth.py
# -*- coding: utf-8 -*-
"""GitHub OAuth 认证"""

import urllib.parse
import requests
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

from utils.logger import logger
from core.exceptions import AuthenticationError, TokenExpiredError


class GitHubOAuth:
    """GitHub OAuth 认证器"""

    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API = "https://api.github.com/user"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_port: int = 18080,
        scope: str = "repo,read:user"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_port = redirect_port
        self.scope = scope
        self._callback_code = None

    def get_authorization_url(self, state: str = None) -> str:
        """生成授权 URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": f"http://localhost:{self.redirect_port}/callback",
            "scope": self.scope,
            "response_type": "code"
        }
        if state:
            params["state"] = state

        return f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, code: str) -> str:
        """用授权码换取 access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code
        }
        headers = {"Accept": "application/json"}

        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise AuthenticationError(f"GitHub OAuth 错误: {result['error']}")

        return result["access_token"]

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """获取用户信息"""
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(self.USER_API, headers=headers)
        response.raise_for_status()

        return response.json()

    def start_callback_server(self, timeout: int = 300) -> Optional[str]:
        """启动回调服务器等待授权

        Args:
            timeout: 超时时间（秒）

        Returns:
            授权码，超时返回 None
        """
        self._callback_code = None

        class CallbackHandler(BaseHTTPRequestHandler):
            def __init__(self, request, client_address, server):
                self.oauth = server.oauth
                super().__init__(request, client_address, server)

            def do_GET(self):
                if self.path.startswith("/callback"):
                    query = urllib.parse.urlparse(self.path).query
                    params = urllib.parse.parse_qs(query)

                    if "code" in params:
                        self.oauth._callback_code = params["code"][0]
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(b"""
                            <html><body>
                            <h1>授权成功！</h1>
                            <p>您可以关闭此页面并返回应用。</p>
                            </body></html>
                        """)
                    else:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"Authorization failed")

        server = HTTPServer(("localhost", self.redirect_port), CallbackHandler)
        server.oauth = self
        server.timeout = timeout

        logger.info(f"启动 OAuth 回调服务器: http://localhost:{self.redirect_port}")

        # 处理请求直到获取 code 或超时
        start_time = time.time()
        while not self._callback_code:
            server.handle_request()
            if time.time() - start_time > timeout:
                logger.warning("OAuth 授权超时")
                return None

        server.server_close()
        return self._callback_code
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_github_oauth.py -v
```
Expected: PASS

- [ ] **Step 4: 实现 Token 管理器**

```python
# src/auth/token_manager.py
# -*- coding: utf-8 -*-
"""Token 管理器"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from security.crypto import Crypto
from utils.logger import logger

# Token 存储路径
TOKEN_FILE = Path.home() / ".claude-backup" / "token.enc"
USER_FILE = Path.home() / ".claude-backup" / "user.json"


class TokenManager:
    """Token 管理器"""

    def __init__(self):
        self.crypto = Crypto()
        self._token: Optional[str] = None
        self._user_info: Optional[dict] = None

    def save_token(self, token: str):
        """保存 Token（加密）"""
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        encrypted = self.crypto.encrypt(token)
        TOKEN_FILE.write_text(encrypted)
        self._token = token
        logger.info("Token 已保存")

    def load_token(self) -> Optional[str]:
        """加载 Token"""
        if self._token:
            return self._token

        if not TOKEN_FILE.exists():
            return None

        try:
            encrypted = TOKEN_FILE.read_text()
            self._token = self.crypto.decrypt(encrypted)
            return self._token
        except Exception as e:
            logger.error(f"Token 解密失败: {e}")
            return None

    def clear_token(self):
        """清除 Token"""
        self._token = None
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        if USER_FILE.exists():
            USER_FILE.unlink()
        logger.info("Token 已清除")

    def save_user_info(self, user_info: dict):
        """保存用户信息"""
        USER_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USER_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_info, f, ensure_ascii=False, indent=2)
        self._user_info = user_info

    def load_user_info(self) -> Optional[dict]:
        """加载用户信息"""
        if self._user_info:
            return self._user_info

        if not USER_FILE.exists():
            return None

        with open(USER_FILE, 'r', encoding='utf-8') as f:
            self._user_info = json.load(f)
            return self._user_info

    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self.load_token() is not None
```

- [ ] **Step 5: 提交**

```bash
git add .
git commit -m "feat: 添加 GitHub OAuth 认证"
```

---

### Task 5.2: GitHub 存储

**Files:**
- Create: `src/storage/base.py`
- Create: `src/storage/github_storage.py`
- Create: `tests/test_github_storage.py`

- [ ] **Step 1: 创建存储基类**

```python
# src/storage/base.py
# -*- coding: utf-8 -*-
"""存储基类"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional


class StorageBase(ABC):
    """存储基类"""

    @abstractmethod
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """上传文件"""
        pass

    @abstractmethod
    def download(self, remote_path: str, local_path: Path) -> bool:
        """下载文件"""
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """列出文件"""
        pass

    @abstractmethod
    def delete(self, remote_path: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    def get_file_url(self, remote_path: str) -> Optional[str]:
        """获取文件 URL"""
        pass
```

- [ ] **Step 2: 实现 GitHub 存储**

```python
# src/storage/github_storage.py
# -*- coding: utf-8 -*-
"""GitHub 存储驱动"""

import base64
from pathlib import Path
from typing import List, Dict, Any, Optional

from github import Github, GithubException
from github.Repository import Repository

from storage.base import StorageBase
from utils.logger import logger
from core.exceptions import BackupError, RateLimitError


class GitHubStorage(StorageBase):
    """GitHub 私有仓库存储"""

    BACKUP_DIR = "backups"
    DEFAULT_REPO_NAME = "claude-config-backup"

    def __init__(self, token: str, repo_name: str = None):
        self.token = token
        self.repo_name = repo_name or self.DEFAULT_REPO_NAME
        self._client: Optional[Github] = None
        self._repo: Optional[Repository] = None

    @property
    def client(self) -> Github:
        """获取 GitHub 客户端"""
        if not self._client:
            self._client = Github(self.token)
        return self._client

    def get_or_create_repo(self) -> Repository:
        """获取或创建仓库"""
        if self._repo:
            return self._repo

        user = self.client.get_user()

        # 尝试获取现有仓库
        try:
            self._repo = user.get_repo(self.repo_name)
            logger.info(f"使用现有仓库: {self.repo_name}")
            return self._repo
        except GithubException:
            pass

        # 创建新仓库
        self._repo = user.create_repo(
            self.repo_name,
            private=True,
            description="Claude Code 配置备份"
        )
        logger.info(f"创建新仓库: {self.repo_name}")
        return self._repo

    def upload(self, local_path: Path, remote_path: str) -> bool:
        """上传文件到仓库"""
        repo = self.get_or_create_repo()

        # 读取文件内容
        content = local_path.read_bytes()
        encoded_content = base64.b64encode(content).decode('utf-8')

        full_path = f"{self.BACKUP_DIR}/{remote_path}"

        try:
            # 检查文件是否存在
            try:
                existing = repo.get_contents(full_path)
                # 更新文件
                repo.update_file(
                    full_path,
                    f"Update backup {remote_path}",
                    encoded_content,
                    existing.sha
                )
                logger.info(f"更新文件: {full_path}")
            except:
                # 创建新文件
                repo.create_file(
                    full_path,
                    f"Add backup {remote_path}",
                    encoded_content
                )
                logger.info(f"创建文件: {full_path}")

            return True

        except GithubException as e:
            if e.status == 403 and 'rate limit' in str(e).lower():
                raise RateLimitError(reset_time=0)
            logger.error(f"上传失败: {e}")
            return False

    def download(self, remote_path: str, local_path: Path) -> bool:
        """从仓库下载文件"""
        repo = self.get_or_create_repo()
        full_path = f"{self.BACKUP_DIR}/{remote_path}"

        try:
            content = repo.get_contents(full_path)
            decoded = base64.b64decode(content.content)

            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(decoded)

            logger.info(f"下载文件: {full_path}")
            return True

        except GithubException as e:
            logger.error(f"下载失败: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """列出备份文件"""
        repo = self.get_or_create_repo()
        path = f"{self.BACKUP_DIR}/{prefix}" if prefix else self.BACKUP_DIR

        try:
            contents = repo.get_contents(path)

            files = []
            for content in contents:
                if content.type == "file":
                    files.append({
                        "name": content.name,
                        "path": content.path,
                        "size": content.size,
                        "sha": content.sha,
                        "url": content.download_url
                    })

            return files

        except GithubException as e:
            logger.error(f"列出文件失败: {e}")
            return []

    def delete(self, remote_path: str) -> bool:
        """删除文件"""
        repo = self.get_or_create_repo()
        full_path = f"{self.BACKUP_DIR}/{remote_path}"

        try:
            content = repo.get_contents(full_path)
            repo.delete_file(
                full_path,
                f"Delete backup {remote_path}",
                content.sha
            )
            logger.info(f"删除文件: {full_path}")
            return True

        except GithubException as e:
            logger.error(f"删除失败: {e}")
            return False

    def get_file_url(self, remote_path: str) -> Optional[str]:
        """获取文件 URL"""
        repo = self.get_or_create_repo()
        full_path = f"{self.BACKUP_DIR}/{remote_path}"

        try:
            content = repo.get_contents(full_path)
            return content.download_url
        except:
            return None
```

- [ ] **Step 3: 编写测试**

```python
# tests/test_github_storage.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from storage.github_storage import GitHubStorage


class TestGitHubStorage:
    def test_upload_file(self, tmp_path):
        """测试上传文件"""
        # 创建测试文件
        test_file = tmp_path / "test.ccb"
        test_file.write_bytes(b"test content")

        with patch('github.Github') as mock_github:
            mock_repo = MagicMock()
            mock_user = MagicMock()
            mock_user.get_repo.return_value = mock_repo
            mock_github.return_value.get_user.return_value = mock_user

            storage = GitHubStorage(token="test_token")
            storage._repo = mock_repo

            result = storage.upload(test_file, "test.ccb")
            assert result is True
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_github_storage.py -v
```
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add .
git commit -m "feat: 添加 GitHub 存储"
```

---

### Task 5.3: 恢复管理器

**Files:**
- Create: `src/core/restore_manager.py`
- Create: `tests/test_restore_manager.py`

- [ ] **Step 1: 编写恢复管理器测试**

```python
# tests/test_restore_manager.py
import pytest
import tempfile
import zipfile
import json
from pathlib import Path
from core.restore_manager import RestoreManager


class TestRestoreManager:
    def test_validate_backup(self, tmp_path):
        """测试验证备份文件"""
        # 创建有效备份
        backup_file = tmp_path / "test.ccb"
        with zipfile.ZipFile(backup_file, 'w') as zf:
            zf.writestr("manifest.json", json.dumps({"version": "1.0"}))
            zf.writestr("checksum.json", json.dumps({"files": {}}))

        manager = RestoreManager()
        assert manager.validate_backup(backup_file) is True

    def test_extract_manifest(self, tmp_path):
        """测试提取清单"""
        backup_file = tmp_path / "test.ccb"
        manifest = {"version": "1.0", "username": "test"}

        with zipfile.ZipFile(backup_file, 'w') as zf:
            zf.writestr("manifest.json", json.dumps(manifest))

        manager = RestoreManager()
        extracted = manager.extract_manifest(backup_file)

        assert extracted["username"] == "test"
```

- [ ] **Step 2: 实现恢复管理器**

```python
# src/core/restore_manager.py
# -*- coding: utf-8 -*-
"""恢复管理器"""

import json
import zipfile
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.logger import logger
from core.exceptions import RestoreError, CorruptedFileError, VersionMismatchError

# 路径配置
CLAUDE_DIR = Path.home() / ".claude"
CACHE_DIR = Path.home() / ".claude-backup" / "cache"
ROLLBACK_DIR = Path.home() / ".claude-backup" / "rollback"


class RestoreManager:
    """恢复管理器"""

    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)

    def validate_backup(self, backup_path: Path) -> bool:
        """验证备份文件完整性

        Args:
            backup_path: 备份文件路径

        Returns:
            是否有效
        """
        if not backup_path.exists():
            raise RestoreError(f"备份文件不存在: {backup_path}")

        if not zipfile.is_zipfile(backup_path):
            raise CorruptedFileError(str(backup_path))

        with zipfile.ZipFile(backup_path, 'r') as zf:
            # 检查必要文件
            namelist = zf.namelist()
            if "manifest.json" not in namelist:
                raise CorruptedFileError(str(backup_path))

            # 验证校验和（可选）
            if "checksum.json" in namelist:
                checksum_data = json.loads(zf.read("checksum.json"))
                # 实际校验可以在这里执行

        return True

    def extract_manifest(self, backup_path: Path) -> Dict[str, Any]:
        """提取备份清单

        Args:
            backup_path: 备份文件路径

        Returns:
            清单数据
        """
        with zipfile.ZipFile(backup_path, 'r') as zf:
            content = zf.read("manifest.json")
            return json.loads(content)

    def create_rollback(self) -> Path:
        """创建当前配置的回滚点

        Returns:
            回滚文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_file = ROLLBACK_DIR / f"pre_restore_{timestamp}.ccb"

        logger.info(f"创建回滚点: {rollback_file}")

        # 这里应该调用 BackupManager 创建备份
        # 简化实现：复制当前配置
        with zipfile.ZipFile(rollback_file, 'w') as zf:
            manifest = {
                "version": "1.0",
                "type": "rollback",
                "created_at": datetime.now().isoformat()
            }
            zf.writestr("manifest.json", json.dumps(manifest))

        return rollback_file

    def restore(
        self,
        backup_path: Path,
        modules: List[str] = None,
        skip_existing: bool = False,
        create_rollback: bool = True
    ) -> Dict[str, Any]:
        """恢复配置

        Args:
            backup_path: 备份文件路径
            modules: 要恢复的模块列表，None 表示全部
            skip_existing: 是否跳过已存在的文件
            create_rollback: 是否创建回滚点

        Returns:
            恢复结果
        """
        result = {
            "success": False,
            "restored_files": [],
            "skipped_files": [],
            "errors": []
        }

        try:
            # 验证备份
            self.validate_backup(backup_path)

            # 创建回滚点
            rollback_file = None
            if create_rollback:
                rollback_file = self.create_rollback()

            # 提取清单
            manifest = self.extract_manifest(backup_path)
            logger.info(f"开始恢复: {manifest.get('username', 'unknown')}")

            # 解压恢复
            with zipfile.ZipFile(backup_path, 'r') as zf:
                for name in zf.namelist():
                    if not name.startswith("data/"):
                        continue

                    # 提取模块名
                    parts = name.split("/")
                    if len(parts) < 3:
                        continue

                    module_id = parts[1]
                    if modules and module_id not in modules:
                        continue

                    # 目标路径
                    rel_path = "/".join(parts[2:])
                    target_path = CLAUDE_DIR / rel_path

                    # 跳过已存在
                    if skip_existing and target_path.exists():
                        result["skipped_files"].append(str(rel_path))
                        continue

                    # 创建目录
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # 写入文件
                    content = zf.read(name)
                    target_path.write_bytes(content)
                    result["restored_files"].append(str(rel_path))

            result["success"] = True
            logger.info(f"恢复完成: {len(result['restored_files'])} 个文件")

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"恢复失败: {e}")

            # 回滚
            if rollback_file and rollback_file.exists():
                logger.info("执行回滚...")
                # 这里应该调用恢复逻辑

        return result

    def list_rollback_points(self) -> List[Dict[str, Any]]:
        """列出所有回滚点"""
        points = []

        for f in ROLLBACK_DIR.glob("pre_restore_*.ccb"):
            try:
                manifest = self.extract_manifest(f)
                points.append({
                    "file": str(f),
                    "created_at": manifest.get("created_at"),
                    "size": f.stat().st_size
                })
            except:
                pass

        return sorted(points, key=lambda x: x["created_at"], reverse=True)
```

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_restore_manager.py -v
```
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: 添加恢复管理器"
```

---

## Chunk 6: GUI 层

### Task 6.1: 主窗口框架

**Files:**
- Create: `src/gui/main_window.py`
- Create: `src/gui/widgets/status_bar.py`
- Create: `tests/test_main_window.py`

- [ ] **Step 1: 实现主窗口**

```python
# src/gui/main_window.py
# -*- coding: utf-8 -*-
"""主窗口"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from gui.tabs.backup_tab import BackupTab
from gui.tabs.restore_tab import RestoreTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.settings_tab import SettingsTab
from gui.dialogs.login_dialog import LoginDialog
from gui.widgets.status_bar import CustomStatusBar
from auth.token_manager import TokenManager
from utils.logger import logger


class MainWindow(QMainWindow):
    """主窗口"""

    login_success = pyqtSignal(dict)
    logout_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.token_manager = TokenManager()
        self.user_info = None

        self._init_ui()
        self._check_login()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Claude Config Backup")
        self.setMinimumSize(800, 600)

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 用户信息栏
        self._create_user_bar(layout)

        # Tab 页面
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Microsoft YaHei", 10))

        # 创建各 Tab
        self.backup_tab = BackupTab()
        self.restore_tab = RestoreTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()

        self.tab_widget.addTab(self.backup_tab, "📦 备份")
        self.tab_widget.addTab(self.restore_tab, "📥 恢复")
        self.tab_widget.addTab(self.history_tab, "📜 历史")
        self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")

        layout.addWidget(self.tab_widget)

        # 状态栏
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)

        # 广告位（预留）
        self._create_ad_bar(layout)

    def _create_user_bar(self, parent_layout):
        """创建用户信息栏"""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 5, 10, 5)

        # 用户标签
        self.user_label = QLabel("未登录")
        self.user_label.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.user_label)

        layout.addStretch()

        # 登录/退出按钮
        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.clicked.connect(self._on_login_click)
        layout.addWidget(self.login_btn)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.clicked.connect(self._on_logout_click)
        self.logout_btn.setVisible(False)
        layout.addWidget(self.logout_btn)

        parent_layout.addWidget(bar)

    def _create_ad_bar(self, parent_layout):
        """创建广告位（预留）"""
        ad_bar = QWidget()
        ad_bar.setFixedHeight(60)
        ad_bar.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        layout = QHBoxLayout(ad_bar)

        ad_label = QLabel("📢 高级功能，即将上线")
        ad_label.setAlignment(Qt.AlignCenter)
        ad_label.setStyleSheet("color: #666;")
        layout.addWidget(ad_label)

        parent_layout.addWidget(ad_bar)

    def _check_login(self):
        """检查登录状态"""
        if self.token_manager.is_logged_in():
            user_info = self.token_manager.load_user_info()
            if user_info:
                self._update_user_info(user_info)

    def _update_user_info(self, user_info: dict):
        """更新用户信息显示"""
        self.user_info = user_info
        username = user_info.get("login", "User")
        avatar = user_info.get("avatar_url", "")

        self.user_label.setText(f"👤 {username} (GitHub)")
        self.login_btn.setVisible(False)
        self.logout_btn.setVisible(True)

        self.login_success.emit(user_info)

    def _on_login_click(self):
        """点击登录"""
        dialog = LoginDialog(self)
        if dialog.exec_():
            user_info = dialog.get_user_info()
            self._update_user_info(user_info)

    def _on_logout_click(self):
        """点击退出"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.token_manager.clear_token()
            self.user_info = None
            self.user_label.setText("未登录")
            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)
            self.logout_success.emit()
```

- [ ] **Step 2: 实现状态栏**

```python
# src/gui/widgets/status_bar.py
# -*- coding: utf-8 -*-
"""自定义状态栏"""

from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtCore import Qt


class CustomStatusBar(QStatusBar):
    """自定义状态栏"""

    def __init__(self):
        super().__init__()

        self.message_label = QLabel()
        self.addWidget(self.message_label, 1)

        self.progress_label = QLabel()
        self.addPermanentWidget(self.progress_label)

        self.show_message("就绪")

    def show_message(self, message: str):
        """显示消息"""
        self.message_label.setText(message)

    def show_progress(self, current: int, total: int, text: str = ""):
        """显示进度"""
        if total > 0:
            percent = int(current / total * 100)
            progress_text = f"{percent}% ({current}/{total})"
            if text:
                progress_text = f"{text} - {progress_text}"
            self.progress_label.setText(progress_text)
        else:
            self.progress_label.clear()

    def clear_progress(self):
        """清除进度"""
        self.progress_label.clear()
```

- [ ] **Step 3: 提交**

```bash
git add .
git commit -m "feat: 添加主窗口框架"
```

---

### Task 6.2: 备份 Tab

**Files:**
- Create: `src/gui/tabs/backup_tab.py`
- Create: `src/gui/widgets/module_list.py`
- Create: `src/gui/dialogs/preview_dialog.py`

- [ ] **Step 1: 实现模块列表控件**

```python
# src/gui/widgets/module_list.py
# -*- coding: utf-8 -*-
"""模块列表控件"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea
from PyQt5.QtCore import pyqtSignal

from core.module_loader import ModuleLoader


class ModuleListWidget(QWidget):
    """模块列表控件"""

    selection_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.module_loader = ModuleLoader()
        self.checkboxes = {}

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("选择备份模块")
        layout.addWidget(title)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 模块列表
        modules = self.module_loader.get_free_modules()
        for module in modules:
            cb = QCheckBox(f"{module.get('icon', '📦')} {module['name']}")
            cb.setToolTip(module.get('description', ''))
            cb.setChecked(True)
            cb.module_id = module['id']

            cb.stateChanged.connect(self._on_state_changed)
            scroll_layout.addWidget(cb)
            self.checkboxes[module['id']] = cb

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _on_state_changed(self, state):
        """选择状态改变"""
        self.selection_changed.emit(self.get_selected_modules())

    def get_selected_modules(self) -> list:
        """获取选中的模块"""
        return [
            module_id for module_id, cb in self.checkboxes.items()
            if cb.isChecked()
        ]

    def select_all(self, checked: bool = True):
        """全选/取消全选"""
        for cb in self.checkboxes.values():
            cb.setChecked(checked)
```

- [ ] **Step 2: 实现备份 Tab**

```python
# src/gui/tabs/backup_tab.py
# -*- coding: utf-8 -*-
"""备份 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

from gui.widgets.module_list import ModuleListWidget
from gui.dialogs.preview_dialog import PreviewDialog
from core.backup_manager import BackupManager
from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager
from utils.logger import logger


class BackupTab(QWidget):
    """备份 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.backup_manager = BackupManager()
        self.token_manager = TokenManager()

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 模块选择
        self.module_list = ModuleListWidget()
        layout.addWidget(self.module_list, 1)

        # 全选按钮
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(lambda: self.module_list.select_all(True))
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(lambda: self.module_list.select_all(False))

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 备份说明
        desc_layout = QHBoxLayout()
        desc_label = QLabel("备份说明：")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("可选，记录本次备份的目的")
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)

        # 存储位置选择
        storage_label = QLabel("存储位置：GitHub 私有仓库")
        layout.addWidget(storage_label)

        # 操作按钮
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self._on_preview)
        action_layout.addWidget(preview_btn)

        self.backup_btn = QPushButton("开始备份")
        self.backup_btn.clicked.connect(self._on_backup)
        self.backup_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        action_layout.addWidget(self.backup_btn)

        layout.addLayout(action_layout)

    def _on_preview(self):
        """预览备份内容"""
        modules = self.module_list.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        preview = self.backup_manager.get_preview(modules)

        dialog = PreviewDialog(preview, self)
        dialog.exec_()

    def _on_backup(self):
        """执行备份"""
        # 检查登录
        token = self.token_manager.load_token()
        if not token:
            QMessageBox.warning(self, "提示", "请先登录")
            return

        modules = self.module_list.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        user_info = self.token_manager.load_user_info()
        username = user_info.get("login", "unknown")

        try:
            # 创建备份
            self.backup_btn.setEnabled(False)
            self.backup_btn.setText("备份中...")

            backup_file = self.backup_manager.create_backup(
                modules=modules,
                description=self.description_input.text(),
                username=username
            )

            # 上传到 GitHub
            storage = GitHubStorage(token)
            remote_name = backup_file.name
            if storage.upload(backup_file, remote_name):
                QMessageBox.information(
                    self,
                    "成功",
                    f"备份完成！\n文件：{remote_name}\n大小：{backup_file.stat().st_size / 1024:.1f} KB"
                )
            else:
                raise Exception("上传失败")

        except Exception as e:
            logger.error(f"备份失败: {e}")
            QMessageBox.critical(self, "错误", f"备份失败：{str(e)}")

        finally:
            self.backup_btn.setEnabled(True)
            self.backup_btn.setText("开始备份")
```

- [ ] **Step 3: 实现预览对话框**

```python
# src/gui/dialogs/preview_dialog.py
# -*- coding: utf-8 -*-
"""备份预览对话框"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt


class PreviewDialog(QDialog):
    """备份预览对话框"""

    def __init__(self, preview_data: dict, parent=None):
        super().__init__(parent)

        self.preview_data = preview_data
        self.setWindowTitle("备份预览")
        self.setMinimumSize(500, 400)

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 摘要信息
        summary = QLabel(
            f"共 {self.preview_data['total_files']} 个文件，"
            f"大小 {self.preview_data['total_size'] / 1024:.1f} KB"
        )
        summary.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(summary)

        # 模块树
        tree = QTreeWidget()
        tree.setHeaderLabels(["模块", "文件数", "大小"])

        for module in self.preview_data.get("modules", []):
            item = QTreeWidgetItem([
                module["id"],
                str(module["files"]),
                f"{module['size'] / 1024:.1f} KB"
            ])
            tree.addTopLevelItem(item)

        layout.addWidget(tree)

        # 敏感信息警告
        sensitive = self.preview_data.get("sensitive_files", [])
        if sensitive:
            warning = QLabel(f"⚠️ 发现 {len(sensitive)} 个敏感文件，将被脱敏处理")
            warning.setStyleSheet("color: orange;")
            layout.addWidget(warning)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("确认备份")
        confirm_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)
```

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "feat: 添加备份 Tab 和预览功能"
```

---

### Task 6.3: 恢复 Tab 和历史 Tab

**Files:**
- Create: `src/gui/tabs/restore_tab.py`
- Create: `src/gui/tabs/history_tab.py`

- [ ] **Step 1: 实现恢复 Tab**

```python
# src/gui/tabs/restore_tab.py
# -*- coding: utf-8 -*-
"""恢复 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt

from core.restore_manager import RestoreManager
from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager
from utils.logger import logger


class RestoreTab(QWidget):
    """恢复 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.restore_manager = RestoreManager()
        self.token_manager = TokenManager()
        self.storage = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 来源选择
        source_group = QGroupBox("选择备份来源")
        source_layout = QVBoxLayout(source_group)

        self.local_radio = QCheckBox("本地文件")
        self.local_radio.setChecked(True)
        source_layout.addWidget(self.local_radio)

        browse_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        browse_layout.addWidget(self.file_path_label)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._on_browse)
        browse_layout.addWidget(browse_btn)
        source_layout.addLayout(browse_layout)

        self.cloud_radio = QCheckBox("云端备份（需登录）")
        source_layout.addWidget(self.cloud_radio)

        layout.addWidget(source_group)

        # 云端备份列表
        self.backup_list = QListWidget()
        self.backup_list.setVisible(False)
        layout.addWidget(self.backup_list)

        # 恢复选项
        options_group = QGroupBox("恢复选项")
        options_layout = QVBoxLayout(options_group)

        self.backup_current = QCheckBox("恢复前备份当前配置")
        self.backup_current.setChecked(True)
        options_layout.addWidget(self.backup_current)

        self.skip_existing = QCheckBox("跳过已存在的文件")
        options_layout.addWidget(self.skip_existing)

        layout.addWidget(options_group)

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.restore_btn = QPushButton("开始恢复")
        self.restore_btn.clicked.connect(self._on_restore)
        self.restore_btn.setStyleSheet("background-color: #2196F3; color: white;")
        btn_layout.addWidget(self.restore_btn)

        layout.addLayout(btn_layout)

        # 连接信号
        self.local_radio.stateChanged.connect(self._on_source_changed)
        self.cloud_radio.stateChanged.connect(self._on_source_changed)

    def _on_source_changed(self):
        """来源改变"""
        self.local_radio.setChecked(not self.local_radio.isChecked())
        self.cloud_radio.setChecked(not self.cloud_radio.isChecked())
        self.backup_list.setVisible(self.cloud_radio.isChecked())

        if self.cloud_radio.isChecked():
            self._load_cloud_backups()

    def _on_browse(self):
        """浏览本地文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择备份文件",
            "",
            "Claude Backup Files (*.ccb)"
        )

        if file_path:
            self.file_path_label.setText(file_path)
            self.selected_file = file_path

    def _load_cloud_backups(self):
        """加载云端备份列表"""
        token = self.token_manager.load_token()
        if not token:
            QMessageBox.warning(self, "提示", "请先登录")
            return

        self.storage = GitHubStorage(token)
        files = self.storage.list_files()

        self.backup_list.clear()
        for f in files:
            self.backup_list.addItem(f"{f['name']} ({f['size'] / 1024:.1f} KB)")

    def _on_restore(self):
        """执行恢复"""
        # 获取备份文件
        backup_file = None

        if self.local_radio.isChecked():
            if not hasattr(self, 'selected_file'):
                QMessageBox.warning(self, "提示", "请选择备份文件")
                return
            from pathlib import Path
            backup_file = Path(self.selected_file)

        # 执行恢复
        try:
            self.restore_btn.setEnabled(False)
            self.restore_btn.setText("恢复中...")

            result = self.restore_manager.restore(
                backup_file,
                skip_existing=self.skip_existing.isChecked(),
                create_rollback=self.backup_current.isChecked()
            )

            if result["success"]:
                QMessageBox.information(
                    self,
                    "成功",
                    f"恢复完成！\n共恢复 {len(result['restored_files'])} 个文件"
                )
            else:
                QMessageBox.critical(self, "错误", "\n".join(result["errors"]))

        except Exception as e:
            logger.error(f"恢复失败: {e}")
            QMessageBox.critical(self, "错误", f"恢复失败：{str(e)}")

        finally:
            self.restore_btn.setEnabled(True)
            self.restore_btn.setText("开始恢复")
```

- [ ] **Step 2: 实现历史 Tab**

```python
# src/gui/tabs/history_tab.py
# -*- coding: utf-8 -*-
"""历史 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt

from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager


class HistoryTab(QWidget):
    """历史 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.token_manager = TokenManager()
        self.storage = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QHBoxLayout()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._load_backups)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 备份列表
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "大小", "创建时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def _load_backups(self):
        """加载备份列表"""
        token = self.token_manager.load_token()
        if not token:
            return

        self.storage = GitHubStorage(token)
        files = self.storage.list_files()

        self.table.setRowCount(len(files))
        for row, f in enumerate(files):
            self.table.setItem(row, 0, QTableWidgetItem(f["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(f"{f['size'] / 1024:.1f} KB"))
            # 时间需要从 API 获取

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)

            restore_btn = QPushButton("恢复")
            restore_btn.clicked.connect(lambda checked, name=f["name"]: self._restore(name))
            btn_layout.addWidget(restore_btn)

            download_btn = QPushButton("下载")
            btn_layout.addWidget(download_btn)

            delete_btn = QPushButton("删除")
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 3, btn_widget)

    def _restore(self, filename: str):
        """恢复指定备份"""
        # 触发恢复 Tab
        pass
```

- [ ] **Step 3: 提交**

```bash
git add .
git commit -m "feat: 添加恢复 Tab 和历史 Tab"
```

---

### Task 6.4: 登录对话框

**Files:**
- Create: `src/gui/dialogs/login_dialog.py`

- [ ] **Step 1: 实现登录对话框**

```python
# src/gui/dialogs/login_dialog.py
# -*- coding: utf-8 -*-
"""登录对话框"""

import webbrowser
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from auth.github_oauth import GitHubOAuth
from auth.token_manager import TokenManager
from utils.config import get_config
from utils.logger import logger


class LoginThread(QThread):
    """登录线程"""
    success = pyqtSignal(str, dict)
    error = pyqtSignal(str)

    def __init__(self, oauth: GitHubOAuth):
        super().__init__()
        self.oauth = oauth

    def run(self):
        try:
            # 获取授权码
            code = self.oauth.start_callback_server(timeout=300)
            if not code:
                self.error.emit("授权超时")
                return

            # 换取 token
            token = self.oauth.exchange_code(code)

            # 获取用户信息
            user_info = self.oauth.get_user_info(token)

            self.success.emit(token, user_info)

        except Exception as e:
            self.error.emit(str(e))


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.token = None
        self.user_info = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("GitHub 登录")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)

        # 说明
        info_label = QLabel(
            "点击下方按钮将打开浏览器进行 GitHub 授权。\n\n"
            "授权后将自动创建私有仓库用于存储备份。"
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 不确定进度
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 按钮
        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.clicked.connect(self._start_login)
        btn_layout.addWidget(self.login_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _start_login(self):
        """开始登录流程"""
        config = get_config()

        client_id = config.get("github.client_id")
        client_secret = config.get("github.client_secret")
        redirect_port = config.get("github.redirect_port", 18080)

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "配置错误",
                "请先配置 GitHub Client ID 和 Secret"
            )
            return

        self.oauth = GitHubOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_port=redirect_port
        )

        # 打开浏览器
        auth_url = self.oauth.get_authorization_url()
        webbrowser.open(auth_url)

        # 启动登录线程
        self.progress.setVisible(True)
        self.login_btn.setEnabled(False)
        self.status_label.setText("等待授权...")

        self.login_thread = LoginThread(self.oauth)
        self.login_thread.success.connect(self._on_login_success)
        self.login_thread.error.connect(self._on_login_error)
        self.login_thread.start()

    def _on_login_success(self, token: str, user_info: dict):
        """登录成功"""
        self.progress.setVisible(False)
        self.status_label.setText(f"登录成功：{user_info['login']}")

        # 保存 token 和用户信息
        token_manager = TokenManager()
        token_manager.save_token(token)
        token_manager.save_user_info(user_info)

        self.token = token
        self.user_info = user_info

        QMessageBox.information(
            self,
            "登录成功",
            f"欢迎，{user_info['login']}！"
        )

        self.accept()

    def _on_login_error(self, error: str):
        """登录失败"""
        self.progress.setVisible(False)
        self.login_btn.setEnabled(True)
        self.status_label.setText("")

        QMessageBox.critical(self, "登录失败", error)

    def get_user_info(self) -> dict:
        """获取用户信息"""
        return self.user_info
```

- [ ] **Step 2: 提交**

```bash
git add .
git commit -m "feat: 添加登录对话框"
```

---

### Task 6.5: 设置 Tab

**Files:**
- Create: `src/gui/tabs/settings_tab.py`

- [ ] **Step 1: 实现设置 Tab**

```python
# src/gui/tabs/settings_tab.py
# -*- coding: utf-8 -*-
"""设置 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QGroupBox,
    QMessageBox
)
from PyQt5.QtCore import Qt

from utils.config import get_config
from utils.logger import logger


class SettingsTab(QWidget):
    """设置 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.config = get_config()

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # SSH 服务器配置
        ssh_group = QGroupBox("SSH 服务器配置")
        ssh_layout = QFormLayout(ssh_group)

        self.ssh_host = QLineEdit()
        self.ssh_host.setPlaceholderText("服务器 IP 地址")
        ssh_layout.addRow("服务器地址：", self.ssh_host)

        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        ssh_layout.addRow("SSH 端口：", self.ssh_port)

        self.ssh_user = QLineEdit()
        self.ssh_user.setPlaceholderText("用户名")
        ssh_layout.addRow("用户名：", self.ssh_user)

        self.ssh_password = QLineEdit()
        self.ssh_password.setEchoMode(QLineEdit.Password)
        self.ssh_password.setPlaceholderText("密码")
        ssh_layout.addRow("密码：", self.ssh_password)

        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self._test_ssh_connection)
        ssh_layout.addRow("", test_btn)

        layout.addWidget(ssh_group)

        # 备份配置
        backup_group = QGroupBox("备份配置")
        backup_layout = QFormLayout(backup_group)

        self.local_path = QLineEdit()
        self.local_path.setPlaceholderText("本地备份路径")
        backup_layout.addRow("本地备份目录：", self.local_path)

        layout.addWidget(backup_group)

        # 存储类型
        storage_group = QGroupBox("存储类型")
        storage_layout = QVBoxLayout(storage_group)

        from PyQt5.QtWidgets import QRadioButton
        self.github_radio = QRadioButton("GitHub 私有仓库（推荐）")
        self.github_radio.setChecked(True)
        storage_layout.addWidget(self.github_radio)

        self.ssh_radio = QRadioButton("SSH 服务器上传")
        storage_layout.addWidget(self.ssh_radio)

        self.local_radio = QRadioButton("仅本地")
        storage_layout.addWidget(self.local_radio)

        layout.addWidget(storage_group)

        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

    def _load_settings(self):
        """加载设置"""
        self.ssh_host.setText(self.config.get("ssh.host", ""))
        self.ssh_port.setValue(self.config.get("ssh.port", 22))
        self.ssh_user.setText(self.config.get("ssh.user", ""))
        self.local_path.setText(self.config.get("backup.local_path", ""))

    def _save_settings(self):
        """保存设置"""
        self.config.set("ssh.host", self.ssh_host.text())
        self.config.set("ssh.port", self.ssh_port.value())
        self.config.set("ssh.user", self.ssh_user.text())
        self.config.set("backup.local_path", self.local_path.text())

        self.config.save()

        QMessageBox.information(self, "成功", "设置已保存")
        logger.info("用户设置已保存")

    def _test_ssh_connection(self):
        """测试 SSH 连接"""
        host = self.ssh_host.text()
        port = self.ssh_port.value()
        user = self.ssh_user.text()

        if not host or not user:
            QMessageBox.warning(self, "提示", "请填写服务器地址和用户名")
            return

        # 测试连接逻辑
        QMessageBox.information(self, "提示", "连接测试功能开发中...")
```

- [ ] **Step 2: 提交**

```bash
git add .
git commit -m "feat: 添加设置 Tab"
```

---

## Chunk 7: 集成与打包

### Task 7.1: 主入口完善

**Files:**
- Modify: `src/main.py`
- Modify: `src/app.py`
- Create: `src/gui/__init__.py`

- [ ] **Step 1: 完善 i18n 支持**

```python
# src/utils/i18n.py
# -*- coding: utf-8 -*-
"""国际化支持"""

import os
from pathlib import Path
from PyQt5.QtCore import QTranslator, QLocale

LOCALES_DIR = Path(__file__).parent.parent.parent / "locales"


def setup_i18n(app, language: str = None):
    """设置国际化

    Args:
        app: QApplication
        language: 语言代码，如 "zh_CN"
    """
    if language is None:
        # 使用系统语言
        language = QLocale.system().name()

    translator = QTranslator()
    qm_file = LOCALES_DIR / f"{language}.qm"

    if qm_file.exists():
        translator.load(str(qm_file))
        app.installTranslator(translator)

    return translator
```

- [ ] **Step 2: 更新主入口**

```python
# src/app.py (更新)
def run(self):
    """运行应用"""
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    self.qt_app = QApplication(self.argv)
    self.qt_app.setApplicationName(APP_NAME)
    self.qt_app.setApplicationVersion(APP_VERSION)
    self.qt_app.setOrganizationName(APP_ORGANIZATION)

    # 设置样式
    self.qt_app.setStyle('Fusion')

    # 国际化
    from utils.i18n import setup_i18n
    setup_i18n(self.qt_app)

    # 主窗口
    from gui.main_window import MainWindow
    self.main_window = MainWindow()
    self.main_window.show()

    return self.qt_app.exec_()
```

- [ ] **Step 3: 提交**

```bash
git add .
git commit -m "feat: 完善主入口和国际化支持"
```

---

### Task 7.2: 打包配置

**Files:**
- Create: `scripts/build.py`
- Create: `scripts/run.py`

- [ ] **Step 1: 创建运行脚本**

```python
# scripts/run.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""开发运行脚本"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import main

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 创建打包脚本**

```python
# scripts/build.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""打包脚本"""

import PyInstaller.__main__
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

PyInstaller.__main__.run([
    str(PROJECT_ROOT / "src" / "main.py"),
    "--name=ClaudeConfigBackup",
    "--windowed",
    "--onefile",
    f"--add-data={PROJECT_ROOT / 'config'};config",
    f"--add-data={PROJECT_ROOT / 'locales'};locales",
    "--clean",
    f"--distpath={PROJECT_ROOT / 'dist'}",
    f"--workpath={PROJECT_ROOT / 'build'}",
    f"--specpath={PROJECT_ROOT}",
])
```

- [ ] **Step 3: 最终提交**

```bash
git add .
git commit -m "feat: MVP 开发完成"
```

---

## 执行计划摘要

| Chunk | 任务 | 文件数 | 状态 |
|-------|------|--------|------|
| 1 | 项目初始化 | 6 | ✅ 计划完成 |
| 2 | 数据库层 | 4 | ✅ 计划完成 |
| 3 | 备份模块系统 | 4 | ✅ 计划完成 |
| 4 | 安全层 | 4 | ✅ 计划完成 |
| 5 | GitHub 认证与存储 | 6 | ✅ 计划完成 |
| 6 | GUI 层 | 12 | ✅ 计划完成 |
| 7 | 集成与打包 | 3 | ✅ 计划完成 |

**总计**: 39 个文件，20+ 个任务，每个任务 4-6 步骤

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-24-claude-config-backup-mvp.md`. Ready to execute?**