# -*- coding: utf-8 -*-
"""历史 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLabel, QMessageBox, QStackedWidget, QGroupBox
)
from PyQt5.QtCore import Qt

from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager


class EmptyStateWidget(QFrame):
    """空状态组件"""

    def __init__(self, icon: str, title: str, description: str, button_text: str = None, button_callback=None):
        super().__init__()
        self.setObjectName("emptyState")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 56px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #7d8590;")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 按钮
        if button_text and button_callback:
            btn = QPushButton(button_text)
            btn.setProperty("primary", True)
            btn.setMinimumWidth(180)
            btn.clicked.connect(button_callback)
            layout.addSpacing(8)
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        layout.addStretch()


class HistoryTab(QWidget):
    """历史 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.token_manager = TokenManager()
        self.storage = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setProperty("secondary", True)
        self.refresh_btn.clicked.connect(self._load_backups)
        toolbar.addWidget(self.refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 使用 StackedWidget 切换状态
        self.stack = QStackedWidget()

        # 空状态页面
        self.empty_state = EmptyStateWidget(
            icon="📦",
            title="暂无备份记录",
            description="您还没有创建过备份，点击下方按钮开始备份您的 Claude 配置",
            button_text="创建第一个备份",
            button_callback=self._go_to_backup
        )
        self.stack.addWidget(self.empty_state)

        # 加载状态页面
        self.loading_state = QWidget()
        loading_layout = QVBoxLayout(self.loading_state)
        loading_layout.setAlignment(Qt.AlignCenter)
        loading_label = QLabel("⏳ 加载中...")
        loading_label.setStyleSheet("font-size: 16px; color: #8b949e;")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(loading_label)
        self.stack.addWidget(self.loading_state)

        # 备份列表页面
        self.table_widget = QWidget()
        table_layout = QVBoxLayout(self.table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "大小", "创建时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)

        self.stack.addWidget(self.table_widget)

        # 默认显示空状态
        self.stack.setCurrentWidget(self.empty_state)
        layout.addWidget(self.stack)

    def showEvent(self, event):
        """页面显示时加载数据"""
        super().showEvent(event)
        self._load_backups()

    def _load_backups(self):
        """加载备份列表"""
        token = self.token_manager.load_token()
        if not token:
            self.stack.setCurrentWidget(self.empty_state)
            return

        # 显示加载状态
        self.stack.setCurrentWidget(self.loading_state)
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ 刷新中...")

        try:
            self.storage = GitHubStorage(token)
            files = self.storage.list_files()

            if not files:
                # 显示空状态
                self.stack.setCurrentWidget(self.empty_state)
            else:
                # 显示列表
                self.table.setRowCount(len(files))
                for row, f in enumerate(files):
                    self.table.setItem(row, 0, QTableWidgetItem(f["name"]))
                    self.table.setItem(row, 1, QTableWidgetItem(f"{f['size'] / 1024:.1f} KB"))
                    self.table.setItem(row, 2, QTableWidgetItem("-"))

                    # 操作按钮
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(8, 4, 8, 4)
                    btn_layout.setSpacing(8)

                    restore_btn = QPushButton("恢复")
                    restore_btn.setProperty("secondary", True)
                    restore_btn.clicked.connect(lambda checked, name=f["name"]: self._restore(name))
                    btn_layout.addWidget(restore_btn)

                    download_btn = QPushButton("下载")
                    download_btn.setProperty("secondary", True)
                    btn_layout.addWidget(download_btn)

                    delete_btn = QPushButton("删除")
                    delete_btn.setProperty("danger", True)
                    delete_btn.clicked.connect(lambda checked, name=f["name"]: self._delete(name))
                    btn_layout.addWidget(delete_btn)

                    self.table.setCellWidget(row, 3, btn_widget)

                self.stack.setCurrentWidget(self.table_widget)

        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"无法加载备份列表：{str(e)}")
            self.stack.setCurrentWidget(self.empty_state)

        finally:
            self.refresh_btn.setEnabled(True)
            self.refresh_btn.setText("🔄 刷新")

    def _restore(self, filename: str):
        """恢复指定备份"""
        QMessageBox.information(self, "提示", f"即将恢复备份：{filename}")

    def _delete(self, filename: str):
        """删除指定备份"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除备份 {filename} 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "提示", "删除功能开发中...")

    def _go_to_backup(self):
        """跳转到备份页面"""
        # 获取主窗口并切换到备份 Tab
        parent = self.parent()
        while parent:
            if hasattr(parent, 'tab_widget'):
                parent.tab_widget.setCurrentIndex(0)
                break
            parent = parent.parent()