# -*- coding: utf-8 -*-
"""历史 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt

from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager


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

        # 工具栏
        toolbar = QHBoxLayout()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._load_backups)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 备份列表
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["文件名", "大小", "创建时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def _load_backups(self):
        """加载备份列表"""
        token = self.token_manager.load_token()
        if not token:
            return

        self.storage = GitHubStorage(token)
        files = self.storage.list_files()

        self.table.setRowCount(len(files))
        for row, f in enumerate(files):
            self.table.setItem(row, 0, QTableWidgetItem(f["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(f"{f['size'] / 1024:.1f} KB"))
            self.table.setItem(row, 2, QTableWidgetItem("-"))

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)

            restore_btn = QPushButton("恢复")
            restore_btn.clicked.connect(lambda checked, name=f["name"]: self._restore(name))
            btn_layout.addWidget(restore_btn)

            download_btn = QPushButton("下载")
            btn_layout.addWidget(download_btn)

            delete_btn = QPushButton("删除")
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 3, btn_widget)

    def _restore(self, filename: str):
        """恢复指定备份"""
        # 触发恢复 Tab
        pass