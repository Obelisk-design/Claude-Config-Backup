# Claude Config Backup

Claude Code 配置备份工具 - 用于备份和管理 Claude Code 的配置文件。

## 功能特性

- 配置文件备份与恢复
- GitHub 仓库同步
- 本地加密存储
- 多环境管理

## 项目结构

```
claudeFi/
├── src/
│   ├── gui/           # 图形界面
│   ├── core/          # 核心功能
│   ├── storage/       # 存储管理
│   ├── auth/          # 认证模块
│   ├── security/      # 安全模块
│   ├── database/      # 数据库模块
│   └── utils/         # 工具函数
├── config/            # 配置文件
├── locales/           # 国际化
└── tests/             # 测试文件
```

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python src/main.py
```

## 许可证

MIT License