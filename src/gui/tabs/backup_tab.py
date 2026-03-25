# -*- coding: utf-8 -*-
"""备份 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QMessageBox, QGroupBox, QCheckBox,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt

from gui.dialogs.preview_dialog import PreviewDialog
from core.backup_manager import BackupManager
from storage.github_storage import GitHubStorage
from auth.token_manager import TokenManager
from core.module_loader import ModuleLoader
from utils.config import get_config
from utils.logger import logger
from gui.styles import (
    PRIMARY, TEXT_PRIMARY, TEXT_MUTED, BG_BASE, BG_ELEVATED,
    BORDER_DEFAULT, RADIUS_MD
)


class BackupTab(QWidget):
    """备份 Tab 页面"""

    def __init__(self):
        super().__init__()
        self.backup_manager = BackupManager()
        self.token_manager = TokenManager()
        self.module_loader = ModuleLoader()
        self.config = get_config()
        self.checkboxes = {}
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

        # ===== 模块选择区域 =====
        module_group = QGroupBox("选择备份模块")
        module_layout = QVBoxLayout(module_group)
        module_layout.setSpacing(8)

        # 模块列表
        modules = self.module_loader.get_free_modules()
        for module in modules:
            display_text = f"{module.get('icon', '📦')} {module['name']} ({module['id']})"
            cb = QCheckBox(display_text)
            cb.setToolTip(module.get('description', ''))
            cb.setChecked(True)
            cb.module_id = module['id']
            cb.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 12px;
                    padding: 10px 16px;
                    color: {TEXT_PRIMARY};
                    font-size: 13px;
                    background-color: transparent;
                    border-radius: {RADIUS_MD};
                }}
                QCheckBox:hover {{
                    background-color: {BG_ELEVATED};
                }}
                QCheckBox::indicator {{
                    width: 22px;
                    height: 22px;
                    border-radius: 6px;
                    border: 2px solid {BORDER_DEFAULT};
                    background-color: {BG_BASE};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {PRIMARY};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {PRIMARY};
                    border-color: {PRIMARY};
                    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMwYTBlMTQiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiI+PC9wb2x5bGluZT48L3N2Zz4=);
                }}
            """)
            module_layout.addWidget(cb)
            self.checkboxes[module['id']] = cb

        # 全选按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        select_all_btn = QPushButton("✓ 全选")
        select_all_btn.setProperty("secondary", True)
        select_all_btn.clicked.connect(lambda: self.select_all(True))

        deselect_all_btn = QPushButton("✗ 取消全选")
        deselect_all_btn.setProperty("secondary", True)
        deselect_all_btn.clicked.connect(lambda: self.select_all(False))

        btn_row.addWidget(select_all_btn)
        btn_row.addWidget(deselect_all_btn)
        btn_row.addStretch()
        module_layout.addLayout(btn_row)

        layout.addWidget(module_group)

        # ===== 备份设置区域 =====
        settings_group = QGroupBox("备份设置")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(16)

        # 备份说明输入
        desc_layout = QHBoxLayout()
        desc_label = QLabel("备份说明")
        desc_label.setFixedWidth(80)
        desc_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px;")

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("可选，记录本次备份的目的")
        self.description_input.setMinimumHeight(36)
        self.description_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_BASE};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD};
                padding: 0 16px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:hover {{
                border-color: {TEXT_MUTED};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """)

        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.description_input, 1)
        settings_layout.addLayout(desc_layout)

        # 存储位置显示
        storage_layout = QHBoxLayout()
        storage_label = QLabel("存储位置")
        storage_label.setFixedWidth(80)
        storage_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 13px;")

        self.storage_value = QLabel()
        self.storage_value.setStyleSheet(f"color: {PRIMARY}; font-weight: 500; font-size: 13px;")

        storage_layout.addWidget(storage_label)
        storage_layout.addWidget(self.storage_value, 1)
        settings_layout.addLayout(storage_layout)

        layout.addWidget(settings_group)

        # ===== 操作按钮 =====
        action_row = QHBoxLayout()
        action_row.setSpacing(16)
        action_row.addStretch()

        preview_btn = QPushButton("👁 预览")
        preview_btn.setProperty("secondary", True)
        preview_btn.setMinimumWidth(130)
        preview_btn.setMinimumHeight(44)
        preview_btn.clicked.connect(self._on_preview)
        action_row.addWidget(preview_btn)

        self.backup_btn = QPushButton("🚀 开始备份")
        self.backup_btn.setProperty("success", True)
        self.backup_btn.setMinimumWidth(180)
        self.backup_btn.setMinimumHeight(44)
        self.backup_btn.clicked.connect(self._on_backup)
        action_row.addWidget(self.backup_btn)

        layout.addLayout(action_row)
        layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 初始化存储位置显示
        self._update_storage_display()

    def _update_storage_display(self):
        """更新存储位置显示"""
        storage_type = self.config.get("storage.type", "github")

        storage_names = {
            "github": "☁️ GitHub 私有仓库",
            "ssh": "🖥️ SSH 服务器",
            "local": "📁 本地存储"
        }
        self.storage_value.setText(storage_names.get(storage_type, "GitHub 私有仓库"))

    def showEvent(self, event):
        """页面显示时更新存储位置"""
        super().showEvent(event)
        self._update_storage_display()

    def select_all(self, checked: bool = True):
        """全选/取消全选"""
        for cb in self.checkboxes.values():
            cb.setChecked(checked)

    def get_selected_modules(self) -> list:
        """获取选中的模块"""
        return [
            module_id for module_id, cb in self.checkboxes.items()
            if cb.isChecked()
        ]

    def _on_preview(self):
        """预览备份内容"""
        modules = self.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        preview = self.backup_manager.get_preview(modules)
        dialog = PreviewDialog(preview, self)
        dialog.exec_()

    def _on_backup(self):
        """执行备份"""
        storage_type = self.config.get("storage.type", "github")

        # GitHub 存储需要登录
        if storage_type == "github":
            token = self.token_manager.load_token()
            if not token:
                QMessageBox.warning(self, "提示", "GitHub 存储需要先登录")
                return

        modules = self.get_selected_modules()
        if not modules:
            QMessageBox.warning(self, "提示", "请选择至少一个备份模块")
            return

        user_info = self.token_manager.load_user_info()
        username = user_info.get("login", "unknown") if user_info else "unknown"

        try:
            self.backup_btn.setEnabled(False)
            self.backup_btn.setText("⏳ 备份中...")

            backup_id, backup_file = self.backup_manager.create_backup(
                module_ids=modules,
                description=self.description_input.text(),
                username=username
            )

            if storage_type == "github":
                token = self.token_manager.load_token()
                storage = GitHubStorage(token)
                remote_name = backup_file.name
                if storage.upload(backup_file, remote_name):
                    size_kb = backup_file.stat().st_size / 1024
                    QMessageBox.information(
                        self, "备份成功",
                        f"文件：{remote_name}\n大小：{size_kb:.1f} KB\n已上传到 GitHub"
                    )
                else:
                    raise Exception("上传失败")
            elif storage_type == "ssh":
                QMessageBox.information(self, "提示", "SSH 存储功能开发中...")
            else:
                # 本地存储
                size_kb = backup_file.stat().st_size / 1024
                QMessageBox.information(
                    self, "备份成功",
                    f"文件：{backup_file.name}\n大小：{size_kb:.1f} KB\n已保存到本地"
                )

        except Exception as e:
            logger.error(f"备份失败: {e}")
            QMessageBox.critical(self, "备份失败", str(e))

        finally:
            self.backup_btn.setEnabled(True)
            self.backup_btn.setText("🚀 开始备份")