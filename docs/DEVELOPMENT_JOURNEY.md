# Claude Config Backup 开发历程文档

> 本文档记录了使用 Claude Code 从零开发 Claude Config Backup 工具的完整过程，供后续开发者参考。

## 一、项目概述

### 1.1 产品定位

**产品名称**：Claude Config Backup

**核心价值**：解决 Claude Code 用户配置丢失、迁移困难、多设备同步等问题

**目标用户**：使用 Claude Code 的开发者

**技术栈**：
- GUI 框架：Python + PyQt5
- 后端服务：Python FastAPI（预留）
- 数据库：MySQL 8.0
- 存储方案：GitHub 私有仓库（主）、SSH 服务器、本地存储
- 认证方式：GitHub OAuth 2.0

### 1.2 功能特性

- **一键备份**：选择需要备份的模块，一键完成配置备份
- **多种存储**：支持 GitHub 私有仓库、SSH 服务器、本地存储
- **安全可靠**：自动识别并脱敏 API Token、密码等敏感信息
- **跨设备同步**：在新设备上快速恢复所有 Claude Code 配置
- **历史管理**：支持查看历史备份，随时恢复到任意版本

---

## 二、开发阶段划分

### 阶段一：MVP 实现（2026-03-24）

| 日期 | 提交 | 内容 |
|------|------|------|
| 2026-03-24 | `8b1cac6` | Claude Config Backup MVP implementation |
| 2026-03-24 | `1c4329a` | 添加打包脚本和 spec 文件 |
| 2026-03-24 | `cb44ea6` | 修复打包路径问题 |

### 阶段二：UI 优化与功能完善（2026-03-25）

| 日期 | 提交 | 内容 |
|------|------|------|
| 2026-03-25 | `8a32cf0` | 优化 UI 布局和交互体验 |
| 2026-03-25 | `f8b2c4a` | 添加文档和打包脚本优化 |
| 2026-03-25 | `df816cf` | 重构为侧边栏导航，优化存储类型联动 |
| 2026-03-25 | `191dc81` | 添加应用图标和更新打包配置 |
| 2026-03-25 | `75ee068` | 更新文档，添加 v1.1.0 版本说明 |

### 阶段三：Bug 修复与细节打磨（2026-03-25）

| 日期 | 提交 | 内容 |
|------|------|------|
| 2026-03-25 | `08dff64` | 修复备份参数名称错误 |
| 2026-03-25 | `2ccf290` | 修复备份返回值解包错误 |
| 2026-03-25 | `6006406` | 使用 QThread 在后台执行备份操作，避免 UI 卡死 |
| 2026-03-25 | `76612ba` | 跳过二进制文件的敏感信息过滤，避免 UTF-8 解码错误 |
| 2026-03-25 | `c3c0813` | 支持自定义本地存储路径 |

### 阶段四：UI 风格与文档完善（2026-03-25）

| 日期 | 提交 | 内容 |
|------|------|------|
| 2026-03-25 | `77f776c` | 更新 UI 为清新花园风格，优化用户文档 |
| 2026-03-25 | `5b6a9d6` | 添加下载按钮链接到 GitHub Release |

---

## 三、开发过程详解

### 3.1 项目初始化

#### 使用的 Skills

1. **superpowers:brainstorming** - 用于探索产品需求和功能设计
2. **superpowers:writing-plans** - 用于编写 MVP 实现计划
3. **superpowers:executing-plans** - 用于执行实现计划

#### 关键对话要点

1. **需求分析**：
   - 用户痛点：Claude Code 配置分散在多个位置，难以备份和迁移
   - 解决方案：统一的备份工具，支持多种存储方式
   - 核心功能：备份、恢复、历史管理

2. **技术选型**：
   - 选择 PyQt5 作为 GUI 框架（跨平台、成熟稳定）
   - 选择 GitHub 私有仓库作为主存储（免费、可靠、用户可控）
   - 选择 MySQL 作为远程数据库（支持用户管理、备份记录）

### 3.2 MVP 实现计划

计划文档位于：`docs/superpowers/plans/2026-03-24-claude-config-backup-mvp.md`

#### Chunk 1: 项目初始化与基础架构

**Task 1.1: 项目结构初始化**
```
mkdir -p src/{gui/{widgets,tabs,dialogs},core,storage,auth,security,database,utils}
mkdir -p config locales tests
```

**Task 1.2: 异常体系与日志系统**
- 创建 `src/core/exceptions.py` - 统一异常体系
- 创建 `src/utils/logger.py` - 日志工具

**Task 1.3: 配置管理系统**
- 创建 `config/settings.yaml` - 默认配置
- 创建 `src/utils/config.py` - 配置管理器

#### Chunk 2: 数据库层

**Task 2.1: MySQL 客户端**
- 创建 `src/database/mysql_client.py`
- 创建 `src/database/sqlite_cache.py` - 本地缓存

#### Chunk 3: 安全模块

**Task 3.1: 加密工具**
- 创建 `src/security/crypto.py` - AES-256 加密

**Task 3.2: 敏感信息过滤器**
- 创建 `src/security/sensitive_filter.py`
- 创建 `config/sensitive_fields.yaml` - 敏感字段配置

#### Chunk 4: 认证模块

**Task 4.1: GitHub OAuth**
- 创建 `src/auth/github_oauth.py`
- 创建 `src/auth/token_manager.py`

#### Chunk 5: 存储模块

**Task 5.1: 存储抽象层**
- 创建 `src/storage/base.py` - 存储接口基类
- 创建 `src/storage/github_storage.py` - GitHub 存储实现

#### Chunk 6: 备份模块

**Task 6.1: 模块加载器**
- 创建 `src/core/module_loader.py`
- 创建 `config/modules.yaml` - 模块配置

**Task 6.2: 备份管理器**
- 创建 `src/core/backup_manager.py`
- 创建 `src/core/restore_manager.py`

#### Chunk 7: GUI 界面

**Task 7.1: 主窗口**
- 创建 `src/gui/main_window.py`
- 创建 `src/gui/styles.py` - 样式定义

**Task 7.2: 功能标签页**
- 创建 `src/gui/tabs/backup_tab.py`
- 创建 `src/gui/tabs/restore_tab.py`
- 创建 `src/gui/tabs/history_tab.py`
- 创建 `src/gui/tabs/settings_tab.py`

**Task 7.3: 对话框和组件**
- 创建 `src/gui/dialogs/login_dialog.py`
- 创建 `src/gui/dialogs/preview_dialog.py`
- 创建 `src/gui/widgets/sidebar.py`
- 创建 `src/gui/widgets/module_list.py`

### 3.3 关键问题解决

#### 问题 1: UI 卡死

**现象**：备份操作执行时，界面无响应

**原因**：备份操作在主线程执行，阻塞了 UI 事件循环

**解决方案**：使用 QThread 在后台执行备份操作

```python
# 使用 QThread 在后台执行备份操作
class BackupWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, backup_manager, modules, description, storage_type):
        super().__init__()
        self.backup_manager = backup_manager
        self.modules = modules
        self.description = description
        self.storage_type = storage_type

    def run(self):
        try:
            success, message = self.backup_manager.backup(...)
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))
```

**相关提交**：`6006406` - 使用 QThread 在后台执行备份操作，避免 UI 卡死

#### 问题 2: 二进制文件过滤错误

**现象**：备份包含二进制文件时，敏感信息过滤失败

**原因**：尝试用 UTF-8 解码二进制文件

**解决方案**：在敏感信息过滤前检测文件类型，跳过二进制文件

```python
def is_binary_file(content: bytes) -> bool:
    """检测是否为二进制文件"""
    # 检查 null bytes
    if b'\x00' in content:
        return True
    # 检查非文本字符比例
    text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    non_text = sum(1 for byte in content if byte not in text_chars)
    return non_text / len(content) > 0.3 if content else False
```

**相关提交**：`76612ba` - 跳过二进制文件的敏感信息过滤

#### 问题 3: 备份参数名称错误

**现象**：备份功能调用时参数名称不匹配

**解决方案**：检查并修正函数签名与调用处的参数名称一致性

**相关提交**：`08dff64` - 修复备份参数名称错误

---

## 四、项目结构

```
claudeFi/
├── src/
│   ├── main.py              # 程序入口
│   ├── app.py               # 应用配置
│   ├── gui/                 # GUI 界面
│   │   ├── main_window.py   # 主窗口
│   │   ├── styles.py        # 样式定义
│   │   ├── tabs/            # 功能标签页
│   │   │   ├── backup_tab.py
│   │   │   ├── restore_tab.py
│   │   │   ├── history_tab.py
│   │   │   └── settings_tab.py
│   │   ├── dialogs/         # 对话框
│   │   │   ├── login_dialog.py
│   │   │   └── preview_dialog.py
│   │   └── widgets/         # 自定义组件
│   │       ├── sidebar.py
│   │       ├── module_list.py
│   │       └── status_bar.py
│   ├── core/                # 核心业务逻辑
│   │   ├── exceptions.py    # 异常定义
│   │   ├── module_loader.py # 模块加载器
│   │   ├── backup_manager.py# 备份管理器
│   │   └── restore_manager.py# 恢复管理器
│   ├── storage/             # 存储驱动
│   │   ├── base.py          # 存储接口
│   │   └── github_storage.py# GitHub 存储
│   ├── auth/                # 认证模块
│   │   ├── github_oauth.py  # GitHub OAuth
│   │   └── token_manager.py # Token 管理
│   ├── security/            # 安全模块
│   │   ├── crypto.py        # 加密工具
│   │   └── sensitive_filter.py# 敏感信息过滤
│   ├── database/            # 数据库
│   │   ├── mysql_client.py  # MySQL 客户端
│   │   └── sqlite_cache.py  # SQLite 缓存
│   └── utils/               # 工具函数
│       ├── config.py        # 配置管理
│       └── logger.py        # 日志工具
├── config/                  # 配置文件
│   ├── settings.yaml        # 应用配置
│   ├── modules.yaml         # 备份模块配置
│   └── sensitive_fields.yaml# 敏感字段配置
├── locales/                 # 国际化（预留）
├── docs/                    # 文档
│   ├── USER_MANUAL.md       # 用户手册
│   └── superpowers/         # 开发文档
│       ├── specs/           # 设计文档
│       └── plans/           # 实现计划
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
└── README.md                # 项目说明
```

---

## 五、使用的 Skills 列表

### 5.1 规划类 Skills

| Skill | 用途 | 使用时机 |
|-------|------|----------|
| `superpowers:brainstorming` | 探索需求和功能设计 | 项目开始时 |
| `superpowers:writing-plans` | 编写实现计划 | 需求明确后 |
| `EnterPlanMode` | 进入规划模式 | 复杂任务开始前 |

### 5.2 执行类 Skills

| Skill | 用途 | 使用时机 |
|-------|------|----------|
| `superpowers:executing-plans` | 执行实现计划 | 计划编写完成后 |
| `superpowers:subagent-driven-development` | 子代理驱动开发 | 多任务并行时 |
| `superpowers:test-driven-development` | 测试驱动开发 | 实现功能时 |

### 5.3 验证类 Skills

| Skill | 用途 | 使用时机 |
|-------|------|----------|
| `superpowers:verification-before-completion` | 完成前验证 | 任务完成前 |
| `superpowers:requesting-code-review` | 请求代码审查 | 功能实现后 |

### 5.4 调试类 Skills

| Skill | 用途 | 使用时机 |
|-------|------|----------|
| `superpowers:systematic-debugging` | 系统化调试 | 遇到 bug 时 |

---

## 六、开发经验总结

### 6.1 架构设计

1. **分层架构**：
   - GUI 层 → 业务逻辑层 → 存储抽象层 → 数据库层
   - 各层职责清晰，便于测试和维护

2. **插件化设计**：
   - 备份模块采用 YAML 配置驱动
   - 新增模块只需修改配置文件，无需改动代码

3. **存储抽象**：
   - 定义统一的存储接口（`storage/base.py`）
   - 支持多种存储方式切换

### 6.2 开发流程

1. **TDD 开发**：
   - 先写测试，再写实现
   - 每个模块都有对应的测试文件

2. **增量提交**：
   - 每个功能点独立提交
   - 提交信息清晰描述变更内容

3. **问题驱动优化**：
   - 发现问题立即修复
   - 记录问题和解决方案

### 6.3 用户偏好

根据 memory 记录，用户偏好：

1. **自主执行**：用户不在电脑前时，自动确认所有操作
2. **简洁响应**：用户喜欢简洁直接的回复
3. **GitHub 存储**：项目推送到 `Obelisk-design/Claude-Config-Backup`

### 6.4 避免的坑

1. **UI 线程阻塞**：耗时操作必须放在后台线程
2. **编码问题**：处理文件时要注意区分文本和二进制
3. **参数一致性**：函数签名和调用处要仔细检查

---

## 七、后续开发建议

### 7.1 待实现功能

根据设计文档，以下功能预留但未实现：

- [ ] 自动定时备份（付费功能）
- [ ] 历史记录对比（付费功能）
- [ ] 多配置方案切换
- [ ] 云端服务器备份
- [ ] 版本检测与自动更新
- [ ] 多语言支持

### 7.2 技术债务

- [ ] 完善单元测试覆盖率
- [ ] 添加集成测试
- [ ] 优化大文件备份性能
- [ ] 完善错误处理和用户提示

### 7.3 开发环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v

# 运行应用
python src/main.py

# 打包为 exe
pyinstaller ClaudeConfigBackup.spec
```

---

## 八、参考资源

### 8.1 项目文档

- [设计文档](docs/superpowers/specs/2026-03-24-claude-config-backup-design.md)
- [MVP 计划](docs/superpowers/plans/2026-03-24-claude-config-backup-mvp.md)
- [用户手册](docs/USER_MANUAL.md)

### 8.2 外部资源

- [PyQt5 文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [PyGithub 库](https://pygithub.readthedocs.io/)

### 8.3 GitHub 仓库

- 仓库地址：https://github.com/Obelisk-design/Claude-Config-Backup
- SSH URL：git@github.com:Obelisk-design/Claude-Config-Backup.git

---

## 附录：完整 Git 历史

```
5b6a9d6 docs: 添加下载按钮链接到 GitHub Release
77f776c style: 更新 UI 为清新花园风格，优化用户文档
c3c0813 feat: 支持自定义本地存储路径
76612ba fix: 跳过二进制文件的敏感信息过滤，避免UTF-8解码错误
6006406 fix: 使用QThread在后台执行备份操作，避免UI卡死
2ccf290 fix: 修复备份返回值解包错误
08dff64 fix: 修复备份参数名称错误
75ee068 docs: 更新文档，添加 v1.1.0 版本说明
191dc81 chore: 添加应用图标和更新打包配置
df816cf feat: 重构为侧边栏导航，优化存储类型联动
f8b2c4a docs: 添加文档和打包脚本优化
8a32cf0 style: 优化 UI 布局和交互体验
cb44ea6 fix: 修复打包路径问题
1c4329a feat: 添加打包脚本和 spec 文件
8b1cac6 feat: Claude Config Backup MVP implementation
```

---

*文档生成时间：2026-03-25*
*本文档基于项目实际开发过程整理，供后续开发者参考。*