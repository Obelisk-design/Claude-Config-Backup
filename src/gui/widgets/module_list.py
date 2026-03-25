# -*- coding: utf-8 -*-
"""模块列表控件"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel
from PyQt5.QtCore import Qt, pyqtSignal

from core.module_loader import ModuleLoader
from gui.styles import (
    PRIMARY, PRIMARY_DIM, TEXT_PRIMARY, TEXT_MUTED,
    BG_BASE, BG_ELEVATED, BORDER_DEFAULT, RADIUS_MD
)


class ModuleListWidget(QWidget):
    """模块列表控件"""

    selection_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.module_loader = ModuleLoader()
        self.checkboxes = {}
        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 模块列表
        modules = self.module_loader.get_free_modules()
        for module in modules:
            # 显示格式：图标 名称 (英文ID)
            display_text = f"{module.get('icon', '📦')} {module['name']} ({module['id']})"
            cb = QCheckBox(display_text)
            cb.setToolTip(module.get('description', ''))
            cb.setChecked(True)
            cb.module_id = module['id']

            # 自定义样式 - 带对号的复选框
            cb.setStyleSheet(f"""
                QCheckBox {{
                    spacing: 12px;
                    padding: 12px 16px;
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

            cb.stateChanged.connect(self._on_state_changed)
            layout.addWidget(cb)
            self.checkboxes[module['id']] = cb

        layout.addStretch()

    def _on_state_changed(self, state):
        """选择状态改变"""
        self.selection_changed.emit(self.get_selected_modules())

    def get_selected_modules(self) -> list:
        """获取选中的模块"""
        return [
            module_id for module_id, cb in self.checkboxes.items()
            if cb.isChecked()
        ]

    def select_all(self, checked: bool = True):
        """全选/取消全选"""
        for cb in self.checkboxes.values():
            cb.setChecked(checked)