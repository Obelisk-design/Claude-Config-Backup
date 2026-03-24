# -*- coding: utf-8 -*-
"""备份预览对话框"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt


class PreviewDialog(QDialog):
    """备份预览对话框"""

    def __init__(self, preview_data: dict, parent=None):
        super().__init__(parent)

        self.preview_data = preview_data
        self.setWindowTitle("备份预览")
        self.setMinimumSize(500, 400)

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 摘要信息
        total_size = self.preview_data.get('total_size', 0)
        total_files = self.preview_data.get('total_files', 0)
        summary = QLabel(
            f"共 {total_files} 个文件，"
            f"大小 {total_size / 1024:.1f} KB"
        )
        summary.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(summary)

        # 模块树
        tree = QTreeWidget()
        tree.setHeaderLabels(["模块", "文件数", "大小"])

        for module in self.preview_data.get("modules", []):
            item = QTreeWidgetItem([
                module["id"],
                str(module["files"]),
                f"{module['size'] / 1024:.1f} KB"
            ])
            tree.addTopLevelItem(item)

        layout.addWidget(tree)

        # 敏感信息警告
        sensitive = self.preview_data.get("sensitive_files", [])
        if sensitive:
            warning = QLabel(f"⚠️ 发现 {len(sensitive)} 个敏感文件，将被脱敏处理")
            warning.setStyleSheet("color: orange;")
            layout.addWidget(warning)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("确认备份")
        confirm_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)