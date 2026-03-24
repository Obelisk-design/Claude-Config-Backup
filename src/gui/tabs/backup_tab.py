# -*- coding: utf-8 -*-
"""备份 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

from gui.widgets.module_list import ModuleListWidget
from gui.dialogs.preview_dialog import PreviewDialog
from core.backup_manager import BackupManager
from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager
from utils.logger import logger


class BackupTab(QWidget):
    """备份 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.backup_manager = BackupManager()
        self.token_manager = TokenManager()

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # 模块选择
        self.module_list = ModuleListWidget()
        layout.addWidget(self.module_list, 1)

        # 全选按钮
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(lambda: self.module_list.select_all(True))
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(lambda: self.module_list.select_all(False))

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 备份说明
        desc_layout = QHBoxLayout()
        desc_label = QLabel("备份说明：")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("可选，记录本次备份的目的")
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)

        # 存储位置选择
        storage_label = QLabel("存储位置：GitHub 私有仓库")
        layout.addWidget(storage_label)

        # 操作按钮
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self._on_preview)
        action_layout.addWidget(preview_btn)

        self.backup_btn = QPushButton("开始备份")
        self.backup_btn.clicked.connect(self._on_backup)
        self.backup_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        action_layout.addWidget(self.backup_btn)

        layout.addLayout(action_layout)

    def _on_preview(self):
        """预览备份内容"""
        modules = self.module_list.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        preview = self.backup_manager.get_preview(modules)

        dialog = PreviewDialog(preview, self)
        dialog.exec_()

    def _on_backup(self):
        """执行备份"""
        # 检查登录
        token = self.token_manager.load_token()
        if not token:
            QMessageBox.warning(self, "提示", "请先登录")
            return

        modules = self.module_list.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        user_info = self.token_manager.load_user_info()
        username = user_info.get("login", "unknown") if user_info else "unknown"

        try:
            # 创建备份
            self.backup_btn.setEnabled(False)
            self.backup_btn.setText("备份中...")

            backup_file = self.backup_manager.create_backup(
                modules=modules,
                description=self.description_input.text(),
                username=username
            )

            # 上传到 GitHub
            storage = GitHubStorage(token)
            remote_name = backup_file.name
            if storage.upload(backup_file, remote_name):
                QMessageBox.information(
                    self,
                    "成功",
                    f"备份完成！\n文件：{remote_name}\n大小：{backup_file.stat().st_size / 1024:.1f} KB"
                )
            else:
                raise Exception("上传失败")

        except Exception as e:
            logger.error(f"备份失败: {e}")
            QMessageBox.critical(self, "错误", f"备份失败：{str(e)}")

        finally:
            self.backup_btn.setEnabled(True)
            self.backup_btn.setText("开始备份")