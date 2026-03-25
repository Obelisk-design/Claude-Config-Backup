# Claude Config Backup 用户手册

## 简介

Claude Config Backup 是一款专为 Claude Code 用户设计的配置备份工具，支持将 Claude Code 的配置文件安全备份到多种存储位置，实现跨设备同步和团队协作。

## 功能特性

- **一键备份**：选择需要备份的模块，一键完成配置备份
- **多种存储**：支持 GitHub 私有仓库、SSH 服务器、本地存储
- **敏感信息过滤**：自动识别并脱敏 API Token、密码等敏感信息
- **跨设备同步**：在新设备上快速恢复所有 Claude Code 配置
- **历史版本管理**：支持查看历史备份，随时恢复到任意版本
- **回滚保护**：恢复前自动创建回滚点，防止配置丢失

## 系统要求

- Windows 10 或更高版本
- 网络连接（用于 GitHub API 访问）

## 安装

### 方式一：直接运行 exe（推荐）

1. 下载 `ClaudeConfigBackup.exe`
2. 双击运行即可

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/Obelisk-design/Claude-Config-Backup.git
cd Claude-Config-Backup

# 安装依赖
pip install -r requirements.txt

# 运行
python src/main.py
```

## 首次使用配置

### 步骤 1：创建 GitHub OAuth 应用

1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. 填写以下信息：
   - **Application name**: Claude Config Backup
   - **Homepage URL**: http://localhost:18080
   - **Authorization callback URL**: http://localhost:18080/callback
4. 创建后，记录 **Client ID** 和 **Client Secret**

### 步骤 2：配置应用

1. 启动应用，点击 "设置" 标签
2. 填写 GitHub 配置：
   - **Client ID**: 步骤 1 获取的 Client ID
   - **Client Secret**: 步骤 1 获取的 Client Secret
   - **回调端口**: 18080（默认）
3. 点击 "保存设置"

### 步骤 3：登录 GitHub

1. 点击右上角 "GitHub 登录"
2. 浏览器将自动打开 GitHub 授权页面
3. 点击 "Authorize" 授权应用
4. 授权成功后自动返回应用

## 使用指南

### 备份配置

1. 点击 "备份" 标签
2. 选择需要备份的模块：
   - **核心配置**: settings.json、config.json 等
   - **技能文件**: 自定义技能文件
   - **自定义命令**: 斜杠命令
   - **记忆文件**: Claude 记忆系统文件
   - **MCP 服务器**: MCP 服务器配置
   - **工具配置**: 工具相关配置
3. （可选）填写备份说明
4. 点击 "预览" 查看备份内容
5. 点击 "开始备份" 执行备份

### 恢复配置

1. 点击 "恢复" 标签
2. 选择备份来源：
   - **本地文件**: 从本地 .ccb 文件恢复
   - **云端备份**: 从 GitHub 仓库恢复
3. 选择恢复选项：
   - 恢复前备份当前配置（推荐勾选）
   - 跳过已存在的文件
4. 点击 "开始恢复"

### 查看历史

1. 点击 "历史" 标签
2. 查看所有云端备份记录
3. 可以进行以下操作：
   - 恢复指定备份
   - 下载备份到本地
   - 删除备份

## 备份模块说明

| 模块 | 说明 | 文件路径 |
|------|------|----------|
| 核心配置 | Claude Code 核心设置 | settings.json, config.json |
| 技能文件 | 自定义技能 | ~/.claude/skills/**/* |
| 自定义命令 | 斜杠命令 | ~/.claude/commands/**/*.md |
| 记忆文件 | Claude 记忆系统 | ~/.claude/memory/**/* |
| MCP 服务器 | MCP 服务器配置 | ~/.claude/mcp-servers/**/* |
| 工具配置 | 工具相关配置 | ~/.claude/tools/**/* |

## 敏感信息处理

备份时会自动识别并处理以下敏感信息：

- API Token（如 `API_TOKEN`、`ANTHROPIC_AUTH_TOKEN`）
- 密码字段（如 `DB_PASSWORD`、`mysql_password`）
- 密钥字段（如 `SECRET_KEY`、`*_SECRET`）

处理方式：
- **脱敏**：将敏感值替换为 `***MASKED***`
- **排除**：某些字段完全排除（如 `ANTHROPIC_AUTH_TOKEN`）

## .ccb 文件格式

备份文件采用 .ccb 格式（基于 ZIP），包含：

```
backup.ccb
├── manifest.json     # 备份清单（版本、时间、模块等）
├── snapshot.json     # 文件快照（路径、大小、哈希）
├── checksum.json     # 校验信息（SHA256）
└── data/             # 实际文件
    ├── core/
    ├── skills/
    └── ...
```

## 常见问题

### Q: 登录失败怎么办？

A: 请检查：
1. GitHub OAuth 应用配置是否正确
2. 回调端口（18080）是否被占用
3. 网络连接是否正常

### Q: 备份失败怎么办？

A: 请检查：
1. 是否已成功登录 GitHub
2. GitHub 仓库配额是否充足
3. 查看日志文件：`~/.claude-backup/logs/`

### Q: 如何在新设备上恢复配置？

A:
1. 在新设备上安装并配置应用
2. 使用同一 GitHub 账号登录
3. 从 "历史" 标签选择备份恢复

### Q: 敏感信息会被上传吗？

A: 默认情况下，敏感信息会被脱敏处理。如需保留原始值，可在备份时勾选 "包含敏感信息"。

## 技术支持

- **问题反馈**: https://github.com/Obelisk-design/Claude-Config-Backup/issues
- **项目主页**: https://github.com/Obelisk-design/Claude-Config-Backup

## 版本历史

### v1.1.0 (2026-03-25)

- 🎯 全新侧边栏导航设计，类似 VS Code 风格
- 💾 支持多种存储类型：GitHub、SSH 服务器、本地存储
- 🔐 智能登录提示：根据存储类型决定是否需要登录
- 📋 优化设置页面交互，根据存储类型显示相关配置
- 🎨 统一 UI 风格，优化间距和排版
- 🐛 修复恢复页面复选框崩溃问题

### v1.0.0 (2026-03-24)

- 首个正式版本
- 支持 GitHub OAuth 登录
- 支持模块化备份
- 支持敏感信息过滤
- 支持云端存储和历史管理