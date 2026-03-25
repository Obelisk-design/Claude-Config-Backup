# -*- coding: utf-8 -*-
"""恢复 Tab"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox, QScrollArea, QFrame, QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from core.restore_manager import RestoreManager
from storage.github_storage import GitHubStorage
from storage.ssh_storage import SSHStorage
from auth.token_manager import TokenManager
from security.crypto import Crypto
from utils.config import get_config
from utils.logger import logger

class LoadCloudBackupsWorker(QThread):
    """加载云端备份工作线程"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, storage, is_ssh):
        super().__init__()
        self.storage = storage
        self.is_ssh = is_ssh

    def run(self):
        try:
            if self.is_ssh:
                with self.storage:
                    files = self.storage.list_files()
            else:
                files = self.storage.list_files()
            self.finished.emit(files)
        except Exception as e:
            from utils.ssh_helper import get_friendly_ssh_error
            self.error.emit(get_friendly_ssh_error(str(e)))

class RestoreWorker(QThread):
    """恢复工作线程"""
    finished = pyqtSignal(dict)  # result_dict
    error = pyqtSignal(str)

    def __init__(self, restore_manager, backup_file, skip_existing, create_rollback):
        super().__init__()
        self.restore_manager = restore_manager
        self.backup_file = backup_file
        self.skip_existing = skip_existing
        self.create_rollback = create_rollback

    def run(self):
        try:
            result = self.restore_manager.restore(
                self.backup_file,
                skip_existing=self.skip_existing,
                create_rollback=self.create_rollback
            )
            self.finished.emit(result)
        except Exception as e:
            from utils.ssh_helper import get_friendly_ssh_error
            self.error.emit(get_friendly_ssh_error(str(e)))

class DownloadWorker(QThread):
    """下载工作线程"""
    finished = pyqtSignal(object)  # cache_path (Path)
    error = pyqtSignal(str)

    def __init__(self, storage, cloud_file, cache_path, is_ssh=False):
        super().__init__()
        self.storage = storage
        self.cloud_file = cloud_file
        self.cache_path = cache_path
        self.is_ssh = is_ssh

    def run(self):
        try:
            if self.is_ssh:
                with self.storage:
                    self.storage.download(self.cloud_file["path"], self.cache_path)
            else:
                self.storage.download(self.cloud_file["path"], self.cache_path)
            self.finished.emit(self.cache_path)
        except Exception as e:
            from utils.ssh_helper import get_friendly_ssh_error
            self.error.emit(get_friendly_ssh_error(str(e)))


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
            from utils.ssh_helper import get_ssh_storage
            self.storage = get_ssh_storage(self.config)
            if not self.storage:
                self._refresh_source_ui()
                return
        else:
            # 本地存储不支持云端备份
            return

        self.backup_list.clear()
        self.selected_cloud_file = None

        # 添加加载中提示
        item = QListWidgetItem("⏳ 正在加载云端备份...")
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable) # 设置为不可选中
        self.backup_list.addItem(item)

        is_ssh = storage_type == "ssh" and isinstance(self.storage, SSHStorage)
        self.load_worker = LoadCloudBackupsWorker(self.storage, is_ssh)
        self.load_worker.finished.connect(self._on_load_cloud_backups_finished)
        self.load_worker.error.connect(self._on_load_cloud_backups_error)
        self.load_worker.finished.connect(self.load_worker.deleteLater)
        self.load_worker.start()

    def _on_load_cloud_backups_finished(self, files: list):
        """加载云端备份完成回调"""
        self.backup_list.clear()

        for f in files:
            item = QListWidgetItem(
                f"{f['name']} · {f['size'] / 1024:.1f} KB"
            )
            item.setData(Qt.UserRole, f)
            self.backup_list.addItem(item)

        if self.backup_list.count() > 0:
            self.backup_list.setCurrentRow(0)

        # 如果是预选操作，在这里恢复预选
        if hasattr(self, '_pending_select_path') and self._pending_select_path:
            for index in range(self.backup_list.count()):
                item = self.backup_list.item(index)
                metadata = item.data(Qt.UserRole) or {}
                if metadata.get("path") == self._pending_select_path:
                    self.backup_list.setCurrentRow(index)
                    break
            self._pending_select_path = None

    def _on_load_cloud_backups_error(self, error_msg: str):
        """加载云端备份失败回调"""
        self.backup_list.clear()
        item = QListWidgetItem(f"❌ 加载失败: {error_msg}")
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        self.backup_list.addItem(item)

    def select_cloud_backup(self, backup_file: dict):
        """从其他页面预选云端备份"""
        self.cloud_radio.setChecked(True)
        self._pending_select_path = backup_file.get("path")
        self._load_cloud_backups()

    def _on_restore(self):
        """执行恢复"""
        if self.local_radio.isChecked():
            if not self.selected_file:
                QMessageBox.warning(self, "提示", "请选择备份文件")
                return
            self._start_restore_process(Path(self.selected_file), None)
            return

        if not self.selected_cloud_file:
            QMessageBox.warning(self, "提示", "请选择云端备份")
            return

        cache_path = self.restore_manager.cache_dir / self.selected_cloud_file["name"]
        storage_type = self.config.get("storage.type", "github")
        is_ssh = storage_type == "ssh" and isinstance(self.storage, SSHStorage)

        self.restore_btn.setEnabled(False)
        self.restore_btn.setText("⏳ 下载中...")

        self.download_worker = DownloadWorker(self.storage, self.selected_cloud_file, cache_path, is_ssh)
        self.download_worker.finished.connect(lambda cp: self._start_restore_process(cp, cp))
        self.download_worker.error.connect(self._on_download_error)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_worker.start()

    def _on_download_error(self, error_msg: str):
        """下载失败回调"""
        self.restore_btn.setEnabled(True)
        self.restore_btn.setText("🔄 开始恢复")
        logger.error(f"下载备份失败: {error_msg}")
        QMessageBox.critical(self, "错误", f"下载备份失败：{error_msg}")

    def _start_restore_process(self, backup_file: Path, cleanup_path: Path):
        """启动恢复线程"""
        self.restore_btn.setEnabled(False)
        self.restore_btn.setText("⏳ 恢复中...")

        self.current_cleanup_path = cleanup_path

        self.restore_worker = RestoreWorker(
            self.restore_manager,
            backup_file,
            self.skip_existing.isChecked(),
            self.backup_current.isChecked()
        )
        self.restore_worker.finished.connect(self._on_restore_finished)
        self.restore_worker.error.connect(self._on_restore_error)
        self.restore_worker.finished.connect(self.restore_worker.deleteLater)
        self.restore_worker.start()

    def _on_restore_finished(self, result: dict):
        """恢复完成回调"""
        if result["success"]:
            QMessageBox.information(
                self,
                "成功",
                f"恢复完成！\n共恢复 {len(result['restored_files'])} 个文件"
            )
        else:
            QMessageBox.critical(self, "错误", "\n".join(result["errors"]))

        self._cleanup_and_reset()

    def _on_restore_error(self, error_msg: str):
        """恢复失败回调"""
        logger.error(f"恢复失败: {error_msg}")
        QMessageBox.critical(self, "错误", f"恢复失败：{error_msg}")
        self._cleanup_and_reset()

    def _cleanup_and_reset(self):
        """清理缓存并重置 UI"""
        if hasattr(self, 'current_cleanup_path') and self.current_cleanup_path and self.current_cleanup_path.exists():
            try:
                self.current_cleanup_path.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"无法清理缓存文件: {e}")

        self.restore_btn.setEnabled(True)
        self.restore_btn.setText("🔄 开始恢复")
