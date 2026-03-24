#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""打包脚本 - 使用 PyInstaller 打包为 exe"""

import PyInstaller.__main__
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

print("开始打包 Claude Config Backup...")

PyInstaller.__main__.run([
    str(PROJECT_ROOT / "src" / "main.py"),
    "--name=ClaudeConfigBackup",
    "--windowed",  # 不显示控制台窗口
    "--onefile",   # 打包成单个文件
    f"--add-data={PROJECT_ROOT / 'config'};config",
    "--clean",
    f"--distpath={PROJECT_ROOT / 'dist'}",
    f"--workpath={PROJECT_ROOT / 'build'}",
    f"--specpath={PROJECT_ROOT}",
    "--hidden-import=PyQt5",
    "--hidden-import=PyQt5.QtCore",
    "--hidden-import=PyQt5.QtWidgets",
    "--hidden-import=PyQt5.QtGui",
    "--hidden-import=github",
    "--hidden-import=pymysql",
    "--hidden-import=cryptography",
    "--hidden-import=yaml",
    "--hidden-import=requests",
])

print(f"\n打包完成！输出文件: {PROJECT_ROOT / 'dist' / 'ClaudeConfigBackup.exe'}")