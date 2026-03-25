# Claude Config Backup

<p align="center">
  <strong>🌿 安全、便捷的 Claude Code 配置备份工具</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-52b788" alt="version">
  <img src="https://img.shields.io/badge/platform-Windows-2d6a4f" alt="platform">
  <img src="https://img.shields.io/badge/license-MIT-40916c" alt="license">
</p>

---

## 功能特性

- **📦 一键备份** - 选择需要备份的模块，一键完成配置备份
- **☁️ 多种存储** - 支持 GitHub 私有仓库、SSH 服务器、本地存储
- **🔒 安全可靠** - 自动识别并脱敏 API Token、密码等敏感信息
- **🔄 跨设备同步** - 在新设备上快速恢复所有 Claude Code 配置
- **📋 历史管理** - 支持查看历史备份，随时恢复到任意版本

## 截图

> 清新简洁的用户界面，让配置管理变得轻松愉快

## 快速开始

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

## 支持的备份模块

| 模块 | 说明 |
|------|------|
| 核心配置 | settings.json、config.json 等 |
| 技能文件 | 自定义技能文件 |
| 自定义命令 | 斜杠命令 |
| 记忆文件 | Claude 记忆系统文件 |
| MCP 服务器 | MCP 服务器配置 |
| 工具配置 | 工具相关配置 |

## 文档

- [用户手册](docs/USER_MANUAL.md)
- [在线文档](https://obelisk-design.github.io/Claude-Config-Backup/)

## 项目结构

```
claudeFi/
├── src/
│   ├── gui/           # 图形界面
│   ├── core/          # 核心功能
│   ├── storage/       # 存储管理
│   ├── auth/          # 认证模块
│   ├── security/      # 安全模块
│   └── utils/         # 工具函数
├── config/            # 配置文件
├── locales/           # 国际化
├── docs/              # 文档
└── tests/             # 测试文件
```

## 开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest tests/
```

## 许可证

MIT License

---

<p align="center">
  用心设计，安心备份 ✨
</p>