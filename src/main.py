#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Claude Config Backup - Claude Code 配置备份工具"""

import sys
from app import Application


def main():
    """程序入口"""
    app = Application(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())