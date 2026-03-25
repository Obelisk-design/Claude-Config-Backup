# -*- coding: utf-8 -*-
"""恢复 Tab"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt

from core.restore_manager import RestoreManager
from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager
from utils.logger import logger


class RestoreTab(QWidget):
    """恢复 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.restore_manager = RestoreManager()
        self.token_manager = TokenManager()
        self.storage = None
        self.selected_file = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a222d;
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #3d4a5c;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00f0ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        # 滚动内容
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(20)

        # 来源选择
        source_group = QGroupBox("选择备份来源")
        source_layout = QVBoxLayout(source_group)
        source_layout.setSpacing(12)

        self.local_radio = QCheckBox("本地文件")
        self.local_radio.setChecked(True)
        source_layout.addWidget(self.local_radio)

        browse_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        browse_layout.addWidget(self.file_path_label)
        browse_btn = QPushButton("浏览...")
        browse_btn.setProperty("secondary", True)
        browse_btn.clicked.connect(self._on_browse)
        browse_layout.addWidget(browse_btn)
        source_layout.addLayout(browse_layout)

        self.cloud_radio = QCheckBox("云端备份（需登录）")
        source_layout.addWidget(self.cloud_radio)

        layout.addWidget(source_group)

        # 云端备份列表
        self.backup_list = QListWidget()
        self.backup_list.setVisible(False)
        self.backup_list.setMinimumHeight(150)
        layout.addWidget(self.backup_list)

        # 恢复选项
        options_group = QGroupBox("恢复选项")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(12)

        self.backup_current = QCheckBox("恢复前备份当前配置")
        self.backup_current.setChecked(True)
        options_layout.addWidget(self.backup_current)

        self.skip_existing = QCheckBox("跳过已存在的文件")
        options_layout.addWidget(self.skip_existing)

        layout.addWidget(options_group)

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.restore_btn = QPushButton("🔄 开始恢复")
        self.restore_btn.setProperty("primary", True)
        self.restore_btn.setMinimumWidth(160)
        self.restore_btn.setMinimumHeight(44)
        self.restore_btn.clicked.connect(self._on_restore)
        btn_layout.addWidget(self.restore_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 连接信号
        self.local_radio.stateChanged.connect(self._on_source_changed)
        self.cloud_radio.stateChanged.connect(self._on_source_changed)

    def _on_source_changed(self):
        """来源改变"""
        self.local_radio.setChecked(not self.local_radio.isChecked())
        self.cloud_radio.setChecked(not self.cloud_radio.isChecked())
        self.backup_list.setVisible(self.cloud_radio.isChecked())

        if self.cloud_radio.isChecked():
            self._load_cloud_backups()

    def _on_browse(self):
        """浏览本地文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择备份文件",
            "",
            "Claude Backup Files (*.ccb)"
        )

        if file_path:
            self.file_path_label.setText(file_path)
            self.selected_file = file_path

    def _load_cloud_backups(self):
        """加载云端备份列表"""
        token = self.token_manager.load_token()
        if not token:
            QMessageBox.warning(self, "提示", "请先登录")
            return

        self.storage = GitHubStorage(token)
        files = self.storage.list_files()

        self.backup_list.clear()
        for f in files:
            self.backup_list.addItem(f"{f['name']} ({f['size'] / 1024:.1f} KB)")

    def _on_restore(self):
        """执行恢复"""
        # 获取备份文件
        backup_file = None

        if self.local_radio.isChecked():
            if not self.selected_file:
                QMessageBox.warning(self, "提示", "请选择备份文件")
                return
            backup_file = Path(self.selected_file)

        # 执行恢复
        try:
            self.restore_btn.setEnabled(False)
            self.restore_btn.setText("⏳ 恢复中...")

            result = self.restore_manager.restore(
                backup_file,
                skip_existing=self.skip_existing.isChecked(),
                create_rollback=self.backup_current.isChecked()
            )

            if result["success"]:
                QMessageBox.information(
                    self,
                    "成功",
                    f"恢复完成！\n共恢复 {len(result['restored_files'])} 个文件"
                )
            else:
                QMessageBox.critical(self, "错误", "\n".join(result["errors"]))

        except Exception as e:
            logger.error(f"恢复失败: {e}")
            QMessageBox.critical(self, "错误", f"恢复失败：{str(e)}")

        finally:
            self.restore_btn.setEnabled(True)
            self.restore_btn.setText("🔄 开始恢复")