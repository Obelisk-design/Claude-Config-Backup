# CLAUDE.md - Claude Config Backup 项目指南

> 本文档为 Claude Code 助手提供项目上下文、设计原则和开发规范。

---

## 项目概述

**Claude Config Backup** 是一款专为 Claude Code 用户设计的配置备份与管理工具，提供安全、便捷的配置备份、跨设备同步和版本管理能力。

### 核心功能

- **一键备份**：选择模块，一键完成配置备份
- **多种存储**：支持 GitHub 私有仓库、SSH 服务器、本地存储
- **敏感信息过滤**：自动识别并脱敏 API Token、密码等
- **跨设备同步**：在新设备上快速恢复所有配置
- **历史版本管理**：支持查看历史备份，随时恢复到任意版本

### 目标用户

- 国内使用 Claude Code 的开发者（使用国产模型代理）
- 需要多设备配置同步的用户
- 关注配置安全和敏感信息保护的用户

---

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| GUI 框架 | Python + PyQt5 |
| 后端服务 | Python FastAPI（预留） |
| 数据库 | MySQL 8.0 + SQLite（离线缓存） |
| 存储方案 | GitHub 私有仓库、SSH 服务器、COS（预留） |
| 认证方式 | GitHub OAuth 2.0 |
| 加密算法 | AES-256（敏感数据加密） |

### 项目结构

```
claudeFi/
├── src/
│   ├── main.py              # 程序入口
│   ├── app.py               # 应用类
│   ├── gui/                 # 图形界面
│   │   ├── main_window.py   # 主窗口
│   │   ├── styles.py        # 样式系统
│   │   ├── widgets/         # 自定义控件
│   │   │   ├── sidebar.py   # 侧边栏
│   │   │   ├── status_bar.py
│   │   │   └── module_list.py
│   │   ├── tabs/            # 页面标签
│   │   │   ├── backup_tab.py
│   │   │   ├── restore_tab.py
│   │   │   ├── history_tab.py
│   │   │   └── settings_tab.py
│   │   └── dialogs/         # 对话框
│   │       ├── login_dialog.py
│   │       └── preview_dialog.py
│   ├── core/                # 核心功能
│   │   ├── backup_manager.py
│   │   ├── restore_manager.py
│   │   ├── module_loader.py
│   │   └── exceptions.py
│   ├── storage/             # 存储驱动
│   │   ├── base.py          # 存储基类
│   │   ├── github_storage.py
│   │   ├── ssh_storage.py
│   │   └── cloud_storage.py # 云存储预留
│   ├── auth/                # 认证模块
│   │   ├── github_oauth.py
│   │   └── token_manager.py
│   ├── security/            # 安全模块
│   │   ├── crypto.py
│   │   └── sensitive_filter.py
│   ├── database/            # 数据库
│   │   ├── mysql_client.py
│   │   └── sqlite_cache.py
│   └── utils/               # 工具函数
│       ├── config.py
│       ├── logger.py
│       └── ssh_helper.py
├── config/                  # 配置文件
│   ├── settings.yaml
│   ├── modules.yaml
│   └── sensitive_fields.yaml
├── tests/                   # 测试文件
└── docs/                    # 文档
```

---

## 设计原则（基于深度审美研究）

### 设计哲学

**核心风格**：清新花园风（Fresh Garden Aesthetic）

以森林绿为主色调，搭配温暖米白背景，营造自然、舒适、专业的视觉体验。

### 设计原则详解

#### 1. 视觉层级原则（Visual Hierarchy）

**核心理念**：用户应在 3 秒内找到最重要的信息。

**实施要点**：
- **F型阅读模式**：重要信息放置在左上角和顶部
- **大小对比**：标题 > 正文 > 辅助信息（字号比例 1.5:1:0.85）
- **颜色对比**：主要信息使用主色调，次要信息使用次要色
- **间距分离**：不同层级之间使用充足的留白

```
视觉层级示例：
┌────────────────────────────────────────┐
│ 📦 备份                    [页面标题区]
│ ─────────────────────────────────────  │
│                                        │
│ 模块选择               [主内容区，优先]
│ ☑ 核心配置                            │
│ ☑ 技能文件                            │
│                                        │
│ ─────────────────────────────────────  │
│ 说明：可选输入           [辅助区域]    │
└────────────────────────────────────────┘
```

#### 2. 一致性原则（Consistency）

**核心理念**：相同功能应有相同的视觉表现。

**实施要点**：
- **组件复用**：相同 UI 元素使用统一样式
- **交互一致**：所有按钮遵循相同的悬停/点击/禁用状态
- **间距一致**：使用 8px 基础单位（xs=4, sm=8, md=16, lg=24, xl=32）
- **圆角一致**：sm=8px, md=12px, lg=18px

#### 3. 反馈即时性原则（Immediate Feedback）

**核心理念**：所有操作都有明确的即时反馈。

**反馈类型**：
| 操作 | 反馈方式 | 时长 |
|------|---------|------|
| 按钮点击 | 颜色变化 + 触感下沉 | 立即 |
| 表单提交 | 按钮状态变为"处理中" | <100ms |
| 操作完成 | Toast 通知 | 3-5s |
| 操作失败 | 内联错误提示 + Toast | 需手动关闭 |
| 长操作 | 进度条 + 百分比 | 持续更新 |

#### 4. 容错性原则（Error Tolerance）

**核心理念**：预防错误发生，错误发生后提供清晰恢复路径。

**实施要点**：
- 危险操作需要二次确认
- 恢复前自动创建回滚点
- 错误信息包含：发生了什么 + 为什么 + 怎么解决
- 提供"撤销"选项

#### 5. 无障碍原则（Accessibility）

**核心理念**：确保所有用户都能使用产品。

**实施要点**：
- 颜色对比度：主要文字 vs 背景 ≥ 4.5:1
- 触摸目标：最小 44×44px
- 键盘导航：Tab/Enter/Escape 完全可用
- 焦点指示：清晰的焦点环

---

## 视觉风格指南

### 颜色系统

#### 主色调（森林绿）

| 名称 | 色值 | 用途 |
|------|------|------|
| PRIMARY | `#2d6a4f` | 主要操作、品牌色 |
| PRIMARY_LIGHT | `#40916c` | 悬停状态 |
| PRIMARY_LIGHTER | `#52b788` | 激活状态、渐变终点 |
| PRIMARY_PALE | `#d8f3dc` | 选中背景、淡色填充 |

#### 语义色

| 名称 | 色值 | 用途 |
|------|------|------|
| SUCCESS | `#2d6a4f` | 成功状态、确认按钮 |
| ERROR | `#c44536` | 错误状态、危险操作 |
| WARNING | `#d4a373` | 警告提示 |
| INFO | `#457b9d` | 信息提示 |

#### 背景色

| 名称 | 色值 | 用途 |
|------|------|------|
| BG_BASE | `#faf8f5` | 页面背景（温暖米白） |
| BG_SURFACE | `#ffffff` | 卡片、面板背景 |
| BG_ELEVATED | `#f4f1eb` | 悬浮元素、悬停背景 |
| BG_HOVER | `#ebe7df` | 激活状态背景 |

#### 文字色

| 名称 | 色值 | 用途 |
|------|------|------|
| TEXT_PRIMARY | `#1b3a2f` | 主要文字 |
| TEXT_SECONDARY | `#4a6c5c` | 次要文字、说明 |
| TEXT_MUTED | `#7a9988` | 禁用、提示文字 |

### 排版规范

#### 字体栈

```css
/* 主要字体 */
font-family: "Microsoft YaHei UI", "Segoe UI", "PingFang SC", sans-serif;

/* 代码/路径 */
font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
```

#### 字号层级

| 名称 | 字号 | 行高 | 字重 | 用途 |
|------|------|------|------|------|
| xxl | 24px | 1.3 | 600 | 页面标题 |
| xl | 18px | 1.4 | 600 | 区块标题 |
| lg | 16px | 1.5 | 500 | 小标题 |
| base | 14px | 1.5 | 400 | 正文 |
| sm | 13px | 1.5 | 400 | 次要文字 |
| xs | 11px | 1.4 | 400 | 辅助信息 |

### 组件规范

#### 按钮

**尺寸**：
- 默认高度：44px
- 大号高度：52px
- 最小宽度：110px
- 圆角：12px

**状态样式**：
```css
/* 默认状态 */
background: BG_SURFACE;
border: 1px solid BORDER_DEFAULT;
color: TEXT_PRIMARY;

/* 悬停状态 */
background: BG_ELEVATED;
border-color: TEXT_MUTED;

/* 按下状态 */
background: PRIMARY_LIGHTER;
color: white;

/* 禁用状态 */
background: BG_ELEVATED;
color: TEXT_MUTED;
```

**按钮类型**：
| 类型 | 样式 | 用途 |
|------|------|------|
| Primary | PRIMARY 背景，白色文字 | 主要操作 |
| Secondary | 透明背景，边框 | 次要操作 |
| Success | SUCCESS 边框，SUCCESS 文字 | 确认操作 |
| Danger | ERROR 边框，ERROR 文字 | 危险操作 |

#### 输入框

**尺寸**：
- 高度：44px
- 内边距：0 16px
- 圆角：12px

**状态样式**：
```css
/* 默认状态 */
background: BG_SURFACE;
border: 1px solid BORDER_DEFAULT;

/* 悬停状态 */
border-color: TEXT_MUTED;
background: BG_ELEVATED;

/* 聚焦状态 */
border: 2px solid #40916c;

/* 错误状态 */
border-color: ERROR;
```

#### 卡片

**尺寸**：
- 内边距：24px
- 圆角：18px
- 边框：1px solid BORDER_DEFAULT

---

## UI 验收标准

### 视觉验收清单

每次前端改动后，对照以下标准进行检查：

#### 布局验收

- [ ] 页面布局符合设计稿
- [ ] 间距使用 8px 基础单位
- [ ] 元素对齐一致（左对齐/居中对齐）
- [ ] 响应式布局正常（最小宽度 950px）

#### 颜色验收

- [ ] 主色调使用正确（森林绿 #2d6a4f）
- [ ] 背景色层次分明
- [ ] 文字颜色对比度足够
- [ ] 语义色使用正确

#### 组件验收

- [ ] 按钮状态完整（default/hover/active/disabled）
- [ ] 输入框状态完整（default/hover/focus/error/disabled）
- [ ] 复选框/单选按钮样式一致
- [ ] 列表项样式正确

#### 交互验收

- [ ] 悬停效果正常
- [ ] 点击反馈即时
- [ ] 加载状态明确
- [ ] 错误提示清晰

#### 文字验收

- [ ] 字体使用正确
- [ ] 字号层级分明
- [ ] 行高舒适（1.4-1.5）
- [ ] 文字截断处理正确

### 交互验收清单

#### 导航验收

- [ ] 侧边栏导航正常
- [ ] 页面切换流畅
- [ ] 当前页面高亮正确
- [ ] 键盘 Tab 导航正常

#### 表单验收

- [ ] 必填项标识清晰
- [ ] 验证反馈即时
- [ ] 错误信息位置正确
- [ ] 提交按钮状态正确

#### 反馈验收

- [ ] Toast 通知位置正确（右上角）
- [ ] Toast 自动消失时间合适（3-5s）
- [ ] 进度条显示正确
- [ ] 空状态设计友好

---

## 自动化验证规则

### 前端改动后自动检查

当 `src/gui/` 目录下的文件发生改动时，执行以下验证：

#### 1. 样式一致性检查

```bash
# 检查样式文件语法
python -c "from src.gui.styles import *; print('Styles OK')"

# 检查颜色值是否在调色板中
grep -r "#[0-9a-fA-F]\{6\}" src/gui/styles.py
```

**验收标准**：
- 所有颜色值应在定义的调色板中
- 不应有硬编码的颜色值

#### 2. 组件导入检查

```bash
# 检查所有组件可正常导入
python -c "
from src.gui.main_window import MainWindow
from src.gui.tabs.backup_tab import BackupTab
from src.gui.tabs.restore_tab import RestoreTab
from src.gui.tabs.history_tab import HistoryTab
from src.gui.tabs.settings_tab import SettingsTab
print('All imports OK')
"
```

#### 3. UI 启动测试

```bash
# 启动应用并截图验证
python src/main.py &
sleep 3
# 使用 gstack browse 截图验证
```

**验收标准**：
- 应用启动无错误
- 主窗口显示正常
- 侧边栏渲染正确
- 各 Tab 可正常切换

#### 4. 响应式测试

验证窗口尺寸变化时布局正常：
- 最小尺寸（950×700）
- 标准尺寸（1280×800）
- 宽屏尺寸（1920×1080）

### 自动截图验证流程

当前端代码改动后，执行以下步骤：

```bash
# 1. 启动应用
python src/main.py &
APP_PID=$!
sleep 3

# 2. 使用 gstack browse 截图（如果应用有 Web 界面）
# 或使用系统截图工具

# 3. 对比截图与设计稿
# 检查：布局、颜色、间距、组件样式

# 4. 关闭应用
kill $APP_PID
```

### 错误检查规则

#### 运行时错误检查

```bash
# 运行测试
pytest tests/ -v

# 检查是否有导入错误
python -m py_compile src/gui/**/*.py
```

#### 日志检查

```bash
# 查看应用日志
tail -f ~/.claude-backup/logs/app.log
```

**错误级别处理**：
| 级别 | 处理方式 |
|------|---------|
| CRITICAL | 立即修复，阻止发布 |
| ERROR | 必须修复 |
| WARNING | 评估后决定是否修复 |
| INFO | 正常日志 |

---

## 开发规范

### 代码风格

```python
# 使用 UTF-8 编码声明
# -*- coding: utf-8 -*-

# 导入顺序：标准库 → 第三方库 → 本地模块
import os
import sys
from typing import Optional, List

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from gui.styles import PRIMARY, TEXT_PRIMARY
from utils.logger import logger
```

### 命名规范

| 类型 | 命名风格 | 示例 |
|------|---------|------|
| 类名 | PascalCase | `BackupTab`, `MainWindow` |
| 函数名 | snake_case | `create_backup()`, `get_file_list()` |
| 变量名 | snake_case | `backup_path`, `user_info` |
| 常量 | UPPER_SNAKE | `PRIMARY_COLOR`, `MAX_RETRIES` |
| 信号 | snake_case | `login_success`, `backup_complete` |

### 样式代码规范

```python
# 样式定义使用 f-string 便于变量引用
BUTTON_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY};
    border-radius: {RADIUS_MD};
    color: white;
}}
"""

# 组件样式使用单独的函数
def get_button_style():
    return BUTTON_STYLE
```

### 提交规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `style`: 样式修改
- `docs`: 文档更新
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```
feat(backup): 添加备份进度显示

- 显示当前处理文件
- 添加进度百分比
- 支持取消操作

Closes #123
```

---

## 测试规范

### 单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_backup_manager.py -v

# 运行带覆盖率的测试
pytest tests/ --cov=src --cov-report=html
```

### 测试文件命名

- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试方法：`test_<method_name>_<scenario>`

### GUI 测试要点

- 测试组件初始化
- 测试信号/槽连接
- 测试状态变化
- 测试用户交互

---

## 文档资源

| 文档 | 路径 | 内容 |
|------|------|------|
| 设计系统 | [DESIGN.md](DESIGN.md) | 视觉设计规范 |
| 产品文档 | [docs/PRODUCT_DOCUMENT.md](docs/PRODUCT_DOCUMENT.md) | 产品需求和用户场景 |
| 用户手册 | [docs/USER_MANUAL.md](docs/USER_MANUAL.md) | 使用说明 |
| 设计规格 | [docs/superpowers/specs/](docs/superpowers/specs/) | 功能设计文档 |

---

## 关键决策记录

### 为什么选择森林绿作为主色调？

1. **差异化**：区别于常见的蓝色系工具软件
2. **舒适感**：绿色对眼睛友好，减少视觉疲劳
3. **专业感**：深绿色传达可靠、专业的品牌形象
4. **情感连接**：自然、成长、安全的联想

### 为什么选择 PyQt5？

1. **跨平台**：支持 Windows/macOS/Linux
2. **成熟稳定**：社区活跃，文档完善
3. **样式灵活**：支持 QSS 自定义样式
4. **性能良好**：原生应用性能

### 为什么使用 YAML 配置文件？

1. **可读性强**：人类可读，便于维护
2. **支持注释**：方便添加说明
3. **结构灵活**：支持嵌套和列表
4. **Python 原生支持**：通过 PyYAML 轻松解析

---

*文档版本：1.0 | 最后更新：2026-03-26*