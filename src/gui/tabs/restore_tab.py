# -*- coding: utf-8 -*-
"""恢复 Tab"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox, QScrollArea, QFrame, QRadioButton
)
from PyQt5.QtCore import Qt

from core.restore_manager import RestoreManager
from storage.github_storage import GitHubStorage
from storage.ssh_storage import SSHStorage
from auth.token_manager import TokenManager
from security.crypto import Crypto
from utils.config import get_config
from utils.logger import logger


class RestoreTab(QWidget):
    """恢复 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.restore_manager = RestoreManager()
        self.token_manager = TokenManager()
        self.config = get_config()
        self.storage = None
        self.selected_file = None
        self.selected_cloud_file = None

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

        self.local_radio = QRadioButton("本地文件")
        self.local_radio.setChecked(True)
        source_layout.addWidget(self.local_radio)

        browse_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        browse_layout.addWidget(self.file_path_label)
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setProperty("secondary", True)
        self.browse_btn.clicked.connect(self._on_browse)
        browse_layout.addWidget(self.browse_btn)
        source_layout.addLayout(browse_layout)

        self.cloud_radio = QRadioButton("云端备份（需登录）")
        source_layout.addWidget(self.cloud_radio)

        layout.addWidget(source_group)

        # 云端备份列表
        self.backup_list = QListWidget()
        self.backup_list.setVisible(False)
        self.backup_list.setMinimumHeight(150)
        self.backup_list.itemSelectionChanged.connect(self._on_cloud_selection_changed)
        layout.addWidget(self.backup_list)

        # 登录提示区域
        self.login_hint_widget = QWidget()
        login_hint_layout = QVBoxLayout(self.login_hint_widget)
        login_hint_layout.setAlignment(Qt.AlignCenter)
        login_hint_label = QLabel("需要登录 GitHub 以查看云端备份")
        login_hint_label.setStyleSheet(f"color: #7d8590; font-size: 13px;")
        login_hint_btn = QPushButton("前往登录")
        login_hint_btn.setProperty("primary", True)
        login_hint_btn.clicked.connect(self._go_to_login)
        login_hint_layout.addWidget(login_hint_label, alignment=Qt.AlignCenter)
        login_hint_layout.addWidget(login_hint_btn, alignment=Qt.AlignCenter)
        self.login_hint_widget.setVisible(False)
        layout.addWidget(self.login_hint_widget)

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

        self.local_radio.toggled.connect(self._on_source_changed)
        self.cloud_radio.toggled.connect(self._on_source_changed)
        self._refresh_source_ui()

    def _on_source_changed(self):
        """来源切换"""
        self._refresh_source_ui()

        if self.cloud_radio.isChecked():
            self._load_cloud_backups()

    def _refresh_source_ui(self):
        """刷新来源 UI"""
        is_local = self.local_radio.isChecked()
        storage_type = self.config.get("storage.type", "github")

        # GitHub 存储需要登录
        if storage_type == "github":
            is_logged_in = self.token_manager.is_logged_in()
            self.login_hint_widget.setVisible(not is_local and not is_logged_in)
            self.backup_list.setVisible(not is_local and is_logged_in)
        elif storage_type == "ssh":
            # SSH 存储需要配置
            has_ssh_config = bool(self.config.get("ssh.host", ""))
            self.login_hint_widget.setVisible(not is_local and not has_ssh_config)
            self.backup_list.setVisible(not is_local and has_ssh_config)
            # 更新登录提示文本
            if storage_type == "ssh":
                for child in self.login_hint_widget.findChildren(QLabel):
                    child.setText("请先在设置中配置 SSH 连接信息")
        else:
            # 本地存储
            self.login_hint_widget.setVisible(False)
            self.backup_list.setVisible(False)

        self.file_path_label.setVisible(is_local)
        self.browse_btn.setVisible(is_local)

    def _go_to_login(self):
        """跳转到登录"""
        parent = self.parent()
        while parent:
            if hasattr(parent, '_on_login_click'):
                parent._on_login_click()
                break
            parent = parent.parent()

    def _on_cloud_selection_changed(self):
        """更新云端备份选择"""
        item = self.backup_list.currentItem()
        self.selected_cloud_file = item.data(Qt.UserRole) if item else None

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
        storage_type = self.config.get("storage.type", "github")

        if storage_type == "github":
            token = self.token_manager.load_token()
            if not token:
                self._refresh_source_ui()
                return
            self.storage = GitHubStorage(token)
        elif storage_type == "ssh":
            ssh_host = self.config.get("ssh.host", "")
            if not ssh_host:
                self._refresh_source_ui()
                return

            # 获取 SSH 配置
            password = self.config.get("ssh.password", "")
            password_encrypted = self.config.get("ssh.password_encrypted", "")
            if password_encrypted:
                crypto = Crypto()
                password = crypto.decrypt(password_encrypted)

            self.storage = SSHStorage(
                host=ssh_host,
                port=self.config.get("ssh.port", 22),
                user=self.config.get("ssh.user", ""),
                password=password
            )
        else:
            # 本地存储不支持云端备份
            return

        files = self.storage.list_files()

        self.backup_list.clear()
        self.selected_cloud_file = None

        for f in files:
            item = QListWidgetItem(
                f"{f['name']} · {f['size'] / 1024:.1f} KB"
            )
            item.setData(Qt.UserRole, f)
            self.backup_list.addItem(item)

        if self.backup_list.count() > 0:
            self.backup_list.setCurrentRow(0)
        else:
            QMessageBox.information(self, "提示", "当前云端还没有可恢复的备份")

    def select_cloud_backup(self, backup_file: dict):
        """从其他页面预选云端备份"""
        self.cloud_radio.setChecked(True)
        self._load_cloud_backups()

        for index in range(self.backup_list.count()):
            item = self.backup_list.item(index)
            metadata = item.data(Qt.UserRole) or {}
            if metadata.get("path") == backup_file.get("path"):
                self.backup_list.setCurrentRow(index)
                break

    def _resolve_backup_file(self):
        """解析当前选择的备份文件"""
        if self.local_radio.isChecked():
            if not self.selected_file:
                QMessageBox.warning(self, "提示", "请选择备份文件")
                return None, None
            return Path(self.selected_file), None

        if not self.selected_cloud_file:
            QMessageBox.warning(self, "提示", "请选择云端备份")
            return None, None

        cache_path = self.restore_manager.cache_dir / self.selected_cloud_file["name"]

        # 根据存储类型下载
        storage_type = self.config.get("storage.type", "github")
        if storage_type == "ssh" and isinstance(self.storage, SSHStorage):
            # SSH 需要 context manager
            with self.storage:
                self.storage.download(self.selected_cloud_file["path"], cache_path)
        else:
            self.storage.download(self.selected_cloud_file["path"], cache_path)

        return cache_path, cache_path

    def _on_restore(self):
        """执行恢复"""
        backup_file = None
        cleanup_path = None

        try:
            backup_file, cleanup_path = self._resolve_backup_file()
            if not backup_file:
                return

            self.restore_btn.setEnabled(False)
            self.restore_btn.setText("⏳ 恢复中...")

            # 执行同步恢复
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
            if cleanup_path and cleanup_path.exists():
                cleanup_path.unlink(missing_ok=True)
            self.restore_btn.setEnabled(True)
            self.restore_btn.setText("🔄 开始恢复")
