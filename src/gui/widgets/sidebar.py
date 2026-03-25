# -*- coding: utf-8 -*-
"""侧边栏导航组件"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from gui.styles import (
    PRIMARY, PRIMARY_DIM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    BG_SURFACE, BG_ELEVATED, BG_HOVER, BORDER_DEFAULT, RADIUS_MD
)
from utils.config import get_config


class NavButton(QPushButton):
    """导航按钮"""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.text_label = text
        self._active = False

        self.setText(f"  {icon}  {text}")
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)

        self._update_style()

    def set_active(self, active: bool):
        """设置激活状态"""
        self._active = active
        self._update_style()

    def _update_style(self):
        """更新样式"""
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_HOVER};
                    color: {PRIMARY};
                    border: none;
                    border-radius: {RADIUS_MD};
                    padding: 0 16px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: {RADIUS_MD};
                    padding: 0 16px;
                    text-align: left;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {BG_ELEVATED};
                    color: {TEXT_PRIMARY};
                }}
            """)


class Sidebar(QFrame):
    """侧边栏"""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.nav_buttons = []
        self._current_index = 0
        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {BG_SURFACE};
                border-right: 1px solid {BORDER_DEFAULT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)

        # 应用标题
        title_layout = QHBoxLayout()
        title_label = QLabel("Claude Config Backup")
        title_label.setStyleSheet(f"""
            color: {PRIMARY};
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {BORDER_DEFAULT}; border: none; max-height: 1px;")
        line.setFixedHeight(1)
        layout.addSpacing(16)
        layout.addWidget(line)
        layout.addSpacing(8)

        # 导航按钮
        nav_items = [
            ("📦", "备份"),
            ("📥", "恢复"),
            ("📋", "历史"),
            ("⚙️", "设置"),
        ]

        for i, (icon, text) in enumerate(nav_items):
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self._on_nav_click(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 设置第一个为激活状态
        self.nav_buttons[0].set_active(True)

        layout.addStretch()

        # 底部用户信息
        self.user_section = QFrame()
        user_layout = QVBoxLayout(self.user_section)
        user_layout.setContentsMargins(8, 12, 8, 12)
        user_layout.setSpacing(8)

        # 分割线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet(f"background-color: {BORDER_DEFAULT}; border: none; max-height: 1px;")
        line2.setFixedHeight(1)
        layout.addWidget(line2)
        layout.addSpacing(12)

        # 用户状态
        self.user_label = QLabel("未登录")
        self.user_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        user_layout.addWidget(self.user_label)

        # 登录按钮
        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {PRIMARY};
                color: {PRIMARY};
                border-radius: {RADIUS_MD};
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 240, 255, 0.1);
            }}
        """)
        user_layout.addWidget(self.login_btn)

        # 退出按钮（默认隐藏）
        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {BORDER_DEFAULT};
                color: {TEXT_SECONDARY};
                border-radius: {RADIUS_MD};
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                border-color: #ff3366;
                color: #ff3366;
            }}
        """)
        self.logout_btn.setVisible(False)
        user_layout.addWidget(self.logout_btn)

        # 存储类型提示
        self.storage_hint = QLabel()
        self.storage_hint.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        user_layout.addWidget(self.storage_hint)

        layout.addWidget(self.user_section)

        # 初始化显示
        self._update_login_visibility()

    def _on_nav_click(self, index: int):
        """导航按钮点击"""
        if index == self._current_index:
            return

        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

        self._current_index = index
        self.page_changed.emit(index)

    def set_current_page(self, index: int):
        """设置当前页面"""
        self._on_nav_click(index)

    def update_user_info(self, username: str = None):
        """更新用户信息"""
        if username:
            self.user_label.setText(f"✓ {username}")
            self.user_label.setStyleSheet(f"color: {PRIMARY}; font-size: 12px;")
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)
        else:
            self.user_label.setText("未登录")
            self.user_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
            self._update_login_visibility()

    def _update_login_visibility(self):
        """根据存储类型更新登录按钮显示"""
        storage_type = self.config.get("storage.type", "github")

        if storage_type == "github":
            self.login_btn.setVisible(True)
            self.storage_hint.setText("需要 GitHub 登录")
            self.user_label.setVisible(True)
        elif storage_type == "ssh":
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(False)
            self.storage_hint.setText("SSH 服务器存储")
            self.user_label.setVisible(False)
        else:  # local
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(False)
            self.storage_hint.setText("本地存储，无需登录")
            self.user_label.setVisible(False)

    def refresh_storage_type(self):
        """刷新存储类型显示"""
        self._update_login_visibility()