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