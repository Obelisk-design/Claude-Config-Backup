# -*- coding: utf-8 -*-
"""自定义状态栏"""

from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtCore import Qt


class CustomStatusBar(QStatusBar):
    """自定义状态栏"""

    def __init__(self):
        super().__init__()

        self.message_label = QLabel()
        self.addWidget(self.message_label, 1)

        self.progress_label = QLabel()
        self.addPermanentWidget(self.progress_label)

        self.show_message("就绪")

    def show_message(self, message: str):
        """显示消息"""
        self.message_label.setText(message)

    def show_progress(self, current: int, total: int, text: str = ""):
        """显示进度"""
        if total > 0:
            percent = int(current / total * 100)
            progress_text = f"{percent}% ({current}/{total})"
            if text:
                progress_text = f"{text} - {progress_text}"
            self.progress_label.setText(progress_text)
        else:
            self.progress_label.clear()

    def clear_progress(self):
        """清除进度"""
        self.progress_label.clear()