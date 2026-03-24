# -*- coding: utf-8 -*-
"""主窗口"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from gui.tabs.backup_tab import BackupTab
from gui.tabs.restore_tab import RestoreTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.settings_tab import SettingsTab
from gui.dialogs.login_dialog import LoginDialog
from gui.widgets.status_bar import CustomStatusBar
from auth.token_manager import TokenManager
from utils.logger import logger


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
        self.setMinimumSize(800, 600)

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 用户信息栏
        self._create_user_bar(layout)

        # Tab 页面
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Microsoft YaHei", 10))

        # 创建各 Tab
        self.backup_tab = BackupTab()
        self.restore_tab = RestoreTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()

        self.tab_widget.addTab(self.backup_tab, "备份")
        self.tab_widget.addTab(self.restore_tab, "恢复")
        self.tab_widget.addTab(self.history_tab, "历史")
        self.tab_widget.addTab(self.settings_tab, "设置")

        layout.addWidget(self.tab_widget)

        # 状态栏
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)

        # 广告位（预留）
        self._create_ad_bar(layout)

    def _create_user_bar(self, parent_layout):
        """创建用户信息栏"""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 5, 10, 5)

        # 用户标签
        self.user_label = QLabel("未登录")
        self.user_label.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.user_label)

        layout.addStretch()

        # 登录/退出按钮
        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.clicked.connect(self._on_login_click)
        layout.addWidget(self.login_btn)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.clicked.connect(self._on_logout_click)
        self.logout_btn.setVisible(False)
        layout.addWidget(self.logout_btn)

        parent_layout.addWidget(bar)

    def _create_ad_bar(self, parent_layout):
        """创建广告位（预留）"""
        ad_bar = QWidget()
        ad_bar.setFixedHeight(60)
        ad_bar.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        layout = QHBoxLayout(ad_bar)

        ad_label = QLabel("高级功能，即将上线")
        ad_label.setAlignment(Qt.AlignCenter)
        ad_label.setStyleSheet("color: #666;")
        layout.addWidget(ad_label)

        parent_layout.addWidget(ad_bar)

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

        self.user_label.setText(f"{username} (GitHub)")
        self.login_btn.setVisible(False)
        self.logout_btn.setVisible(True)

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
            self.user_label.setText("未登录")
            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)
            self.logout_success.emit()