#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""打包脚本 - 使用 PyInstaller 打包为 exe"""

import PyInstaller.__main__
from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"

def generate_icon():
    """生成应用图标"""
    print("生成应用图标...")

    from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QPen, QPainterPath, QBrush
    from PyQt5.QtCore import Qt
    from PIL import Image

    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor('#00d4ff'))
    gradient.setColorAt(1, QColor('#0099cc'))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor('#00d4ff'), 4))
    painter.drawRoundedRect(20, 20, size - 40, size - 40, 50, 50)

    painter.setPen(QPen(QColor('#0d1117'), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    path = QPainterPath()
    path.moveTo(160, 70)
    path.cubicTo(80, 70, 80, 186, 160, 186)
    painter.drawPath(path)
    painter.end()

    ASSETS_DIR.mkdir(exist_ok=True)
    png_path = ASSETS_DIR / "icon.png"
    pixmap.save(str(png_path), 'PNG')
    print(f"PNG 图标已保存: {png_path}")

    # 转换为 ICO
    img = Image.open(png_path)
    img.save(str(ICON_PATH), format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    print(f"ICO 图标已保存: {ICON_PATH}")


def build():
    """打包应用"""
    # 确保图标存在
    if not ICON_PATH.exists():
        generate_icon()

    print("开始打包 Claude Config Backup...")

    args = [
        str(PROJECT_ROOT / "src" / "main.py"),
        "--name=ClaudeConfigBackup",
        "--windowed",
        "--onefile",
        f"--add-data={PROJECT_ROOT / 'config'};config",
        f"--paths={PROJECT_ROOT / 'src'}",
        "--clean",
        f"--distpath={PROJECT_ROOT / 'dist'}",
        f"--workpath={PROJECT_ROOT / 'build'}",
        f"--specpath={PROJECT_ROOT}",
        f"--icon={ICON_PATH}",
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
        "--hidden-import=gui.widgets.sidebar",
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
    ]

    PyInstaller.__main__.run(args)

    print(f"\n打包完成！输出文件: {PROJECT_ROOT / 'dist' / 'ClaudeConfigBackup.exe'}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--icon-only":
        generate_icon()
    else:
        build()