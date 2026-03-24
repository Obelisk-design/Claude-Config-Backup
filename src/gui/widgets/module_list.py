# -*- coding: utf-8 -*-
"""模块列表控件"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal

from core.module_loader import ModuleLoader


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

        # 标题
        title = QLabel("选择备份模块")
        layout.addWidget(title)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 模块列表
        modules = self.module_loader.get_free_modules()
        for module in modules:
            cb = QCheckBox(f"{module.get('icon', '📦')} {module['name']}")
            cb.setToolTip(module.get('description', ''))
            cb.setChecked(True)
            cb.module_id = module['id']

            cb.stateChanged.connect(self._on_state_changed)
            scroll_layout.addWidget(cb)
            self.checkboxes[module['id']] = cb

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

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