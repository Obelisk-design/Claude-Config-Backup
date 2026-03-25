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
    f"--paths={PROJECT_ROOT / 'src'}",  # 添加 src 目录到 Python 路径
    "--clean",
    f"--distpath={PROJECT_ROOT / 'dist'}",
    f"--workpath={PROJECT_ROOT / 'build'}",
    f"--specpath={PROJECT_ROOT}",
    # PyQt5 模块
    "--hidden-import=PyQt5",
    "--hidden-import=PyQt5.QtCore",
    "--hidden-import=PyQt5.QtWidgets",
    "--hidden-import=PyQt5.QtGui",
    # 项目模块
    "--hidden-import=app",
    "--hidden-import=gui",
    "--hidden-import=gui.main_window",
    "--hidden-import=gui.tabs",
    "--hidden-import=gui.tabs.backup_tab",
    "--hidden-import=gui.tabs.restore_tab",
    "--hidden-import=gui.tabs.history_tab",
    "--hidden-import=gui.tabs.settings_tab",
    "--hidden-import=gui.dialogs",
    "--hidden-import=gui.dialogs.login_dialog",
    "--hidden-import=gui.dialogs.preview_dialog",
    "--hidden-import=gui.widgets",
    "--hidden-import=gui.widgets.status_bar",
    "--hidden-import=gui.widgets.module_list",
    "--hidden-import=gui.styles",
    "--hidden-import=core",
    "--hidden-import=core.backup_manager",
    "--hidden-import=core.restore_manager",
    "--hidden-import=core.module_loader",
    "--hidden-import=core.exceptions",
    "--hidden-import=auth",
    "--hidden-import=auth.github_oauth",
    "--hidden-import=auth.token_manager",
    "--hidden-import=storage",
    "--hidden-import=storage.github_storage",
    "--hidden-import=storage.base",
    "--hidden-import=security",
    "--hidden-import=security.crypto",
    "--hidden-import=security.sensitive_filter",
    "--hidden-import=database",
    "--hidden-import=database.mysql_client",
    "--hidden-import=database.sqlite_cache",
    "--hidden-import=utils",
    "--hidden-import=utils.logger",
    "--hidden-import=utils.config",
    # 第三方库
    "--hidden-import=github",
    "--hidden-import=pymysql",
    "--hidden-import=cryptography",
    "--hidden-import=yaml",
    "--hidden-import=requests",
])

print(f"\n打包完成！输出文件: {PROJECT_ROOT / 'dist' / 'ClaudeConfigBackup.exe'}")