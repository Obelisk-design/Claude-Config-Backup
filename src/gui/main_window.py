# -*- coding: utf-8 -*-
"""主窗口 - 侧边栏导航版本"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QMessageBox, QStackedWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient, QPen

from gui.widgets.sidebar import Sidebar
from gui.tabs.backup_tab import BackupTab
from gui.tabs.restore_tab import RestoreTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.settings_tab import SettingsTab
from gui.dialogs.login_dialog import LoginDialog
from gui.widgets.status_bar import CustomStatusBar
from gui.styles import get_app_style, get_status_bar_style
from auth.token_manager import TokenManager
from utils.logger import logger


def create_app_icon():
    """创建应用图标 - 清新花园风格"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 绘制圆角矩形背景
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#52b788"))
    gradient.setColorAt(1, QColor("#2d6a4f"))

    from PyQt5.QtGui import QBrush
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor("#40916c"), 2))
    painter.drawRoundedRect(6, 6, size - 12, size - 12, 14, 14)

    # 绘制 C 字母
    painter.setPen(QPen(QColor("#ffffff"), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    from PyQt5.QtGui import QPainterPath
    path = QPainterPath()
    path.moveTo(40, 18)
    path.cubicTo(20, 18, 20, 46, 40, 46)
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    """主窗口"""

    login_success = pyqtSignal(dict)
    logout_success = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.token_manager = TokenManager()
        self.user_info = None

        self._init_ui()
        self._check_login()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Claude Config Backup")
        self.setMinimumSize(950, 700)

        # 应用全局样式
        self.setStyleSheet(get_app_style())

        # 设置窗口图标
        self.setWindowIcon(create_app_icon())

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_page_changed)
        self.sidebar.login_btn.clicked.connect(self._on_login_click)
        self.sidebar.logout_btn.clicked.connect(self._on_logout_click)
        main_layout.addWidget(self.sidebar)

        # 右侧内容区域
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 16)
        content_layout.setSpacing(0)

        # 页面堆栈
        self.stack = QStackedWidget()

        # 创建各页面
        self.backup_tab = BackupTab()
        self.restore_tab = RestoreTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()

        # 连接设置变化信号
        self.settings_tab.settings_changed.connect(self._on_settings_changed)

        self.stack.addWidget(self.backup_tab)
        self.stack.addWidget(self.restore_tab)
        self.stack.addWidget(self.history_tab)
        self.stack.addWidget(self.settings_tab)

        content_layout.addWidget(self.stack, 1)

        # 状态栏
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)

        main_layout.addWidget(content, 1)

    def _on_page_changed(self, index: int):
        """页面切换"""
        self.stack.setCurrentIndex(index)

        # 历史页面显示时加载数据
        if index == 2:
            self.history_tab._load_backups()

    def _on_settings_changed(self):
        """设置变化"""
        # 刷新侧边栏登录显示
        self.sidebar.refresh_storage_type()
        # 刷新备份页面存储位置
        self.backup_tab._update_storage_display()

    def _check_login(self):
        """检查登录状态"""
        if self.token_manager.is_logged_in():
            user_info = self.token_manager.load_user_info()
            if user_info:
                self._update_user_info(user_info)

    def _update_user_info(self, user_info: dict):
        """更新用户信息显示"""
        self.user_info = user_info
        username = user_info.get("login", "User")
        self.sidebar.update_user_info(username)
        self.login_success.emit(user_info)

    def _on_login_click(self):
        """点击登录"""
        dialog = LoginDialog(self)
        if dialog.exec_():
            user_info = dialog.get_user_info()
            if user_info:
                self._update_user_info(user_info)

    def _on_logout_click(self):
        """点击退出"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.token_manager.clear_token()
            self.user_info = None
            self.sidebar.update_user_info(None)
            self.logout_success.emit()