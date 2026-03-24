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