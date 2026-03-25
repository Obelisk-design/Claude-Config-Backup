# -*- coding: utf-8 -*-
"""主窗口"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient, QPen

from gui.tabs.backup_tab import BackupTab
from gui.tabs.restore_tab import RestoreTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.settings_tab import SettingsTab
from gui.dialogs.login_dialog import LoginDialog
from gui.widgets.status_bar import CustomStatusBar
from gui.styles import (
    get_app_style, get_user_bar_style, get_status_bar_style, get_ad_bar_style
)
from auth.token_manager import TokenManager
from utils.logger import logger


def create_app_icon():
    """创建应用图标 - 科技风格"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 绘制圆角矩形背景
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#00d4ff"))
    gradient.setColorAt(1, QColor("#0099cc"))

    from PyQt5.QtGui import QBrush
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor("#00d4ff"), 2))
    painter.drawRoundedRect(6, 6, size - 12, size - 12, 14, 14)

    # 绘制 C 字母
    painter.setPen(QPen(QColor("#0d1117"), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
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
        self.setMinimumSize(950, 800)

        # 应用全局样式
        self.setStyleSheet(get_app_style())

        # 设置窗口图标
        self.setWindowIcon(create_app_icon())

        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 用户信息栏
        self._create_user_bar(layout)

        # 内容区域
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 24)

        # Tab 页面
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Segoe UI", 10))

        # 创建各 Tab
        self.backup_tab = BackupTab()
        self.restore_tab = RestoreTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()

        self.tab_widget.addTab(self.backup_tab, "📦 备份")
        self.tab_widget.addTab(self.restore_tab, "📥 恢复")
        self.tab_widget.addTab(self.history_tab, "📋 历史")
        self.tab_widget.addTab(self.settings_tab, "⚙️ 设置")

        content_layout.addWidget(self.tab_widget)
        layout.addWidget(content, 1)

        # 状态栏
        self.status_bar = CustomStatusBar()
        self.setStatusBar(self.status_bar)

        # 广告位
        self._create_ad_bar(layout)

    def _create_user_bar(self, parent_layout):
        """创建用户信息栏"""
        bar = QFrame()
        bar.setObjectName("userBar")
        bar.setStyleSheet(get_user_bar_style())
        bar.setFixedHeight(72)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)

        # 应用图标和标题
        title_layout = QHBoxLayout()
        title_layout.setSpacing(14)

        icon_label = QLabel()
        icon_label.setPixmap(create_app_icon().pixmap(36, 36))
        title_layout.addWidget(icon_label)

        app_title = QLabel("Claude Config Backup")
        app_title.setObjectName("appTitle")
        app_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_layout.addWidget(app_title)

        layout.addLayout(title_layout)
        layout.addStretch()

        # 用户信息
        self.user_label = QLabel("未登录")
        self.user_label.setObjectName("userLabel")
        self.user_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.user_label)

        layout.addSpacing(20)

        # 登录/退出按钮
        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.clicked.connect(self._on_login_click)
        layout.addWidget(self.login_btn)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.clicked.connect(self._on_logout_click)
        self.logout_btn.setVisible(False)
        layout.addWidget(self.logout_btn)

        parent_layout.addWidget(bar)

    def _create_ad_bar(self, parent_layout):
        """创建广告位"""
        ad_bar = QFrame()
        ad_bar.setObjectName("adBar")
        ad_bar.setStyleSheet(get_ad_bar_style())
        ad_bar.setFixedHeight(52)
        layout = QHBoxLayout(ad_bar)

        ad_label = QLabel("⚡ PRO 功能即将推出 · 更多存储选项 · 团队协作")
        ad_label.setObjectName("adLabel")
        ad_label.setAlignment(Qt.AlignCenter)
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

        self.user_label.setText(f"✓ {username}")
        self.user_label.setStyleSheet("color: #00ff88;")
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
            self.user_label.setStyleSheet("")
            self.login_btn.setVisible(True)
            self.logout_btn.setVisible(False)
            self.logout_success.emit()