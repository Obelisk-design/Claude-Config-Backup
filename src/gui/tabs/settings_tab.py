# -*- coding: utf-8 -*-
"""设置 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QGroupBox,
    QMessageBox, QRadioButton
)
from PyQt5.QtCore import Qt

from utils.config import get_config
from utils.logger import logger


class SettingsTab(QWidget):
    """设置 Tab 页面"""

    def __init__(self):
        super().__init__()

        self.config = get_config()

        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        # GitHub 配置
        github_group = QGroupBox("GitHub 配置")
        github_layout = QFormLayout(github_group)

        self.client_id = QLineEdit()
        self.client_id.setPlaceholderText("GitHub OAuth Client ID")
        github_layout.addRow("Client ID：", self.client_id)

        self.client_secret = QLineEdit()
        self.client_secret.setEchoMode(QLineEdit.Password)
        self.client_secret.setPlaceholderText("GitHub OAuth Client Secret")
        github_layout.addRow("Client Secret：", self.client_secret)

        self.redirect_port = QSpinBox()
        self.redirect_port.setRange(1024, 65535)
        self.redirect_port.setValue(18080)
        github_layout.addRow("回调端口：", self.redirect_port)

        layout.addWidget(github_group)

        # SSH 服务器配置
        ssh_group = QGroupBox("SSH 服务器配置")
        ssh_layout = QFormLayout(ssh_group)

        self.ssh_host = QLineEdit()
        self.ssh_host.setPlaceholderText("服务器 IP 地址")
        ssh_layout.addRow("服务器地址：", self.ssh_host)

        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        ssh_layout.addRow("SSH 端口：", self.ssh_port)

        self.ssh_user = QLineEdit()
        self.ssh_user.setPlaceholderText("用户名")
        ssh_layout.addRow("用户名：", self.ssh_user)

        self.ssh_password = QLineEdit()
        self.ssh_password.setEchoMode(QLineEdit.Password)
        self.ssh_password.setPlaceholderText("密码")
        ssh_layout.addRow("密码：", self.ssh_password)

        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self._test_ssh_connection)
        ssh_layout.addRow("", test_btn)

        layout.addWidget(ssh_group)

        # 存储类型
        storage_group = QGroupBox("存储类型")
        storage_layout = QVBoxLayout(storage_group)

        self.github_radio = QRadioButton("GitHub 私有仓库（推荐）")
        self.github_radio.setChecked(True)
        storage_layout.addWidget(self.github_radio)

        self.ssh_radio = QRadioButton("SSH 服务器上传")
        storage_layout.addWidget(self.ssh_radio)

        self.local_radio = QRadioButton("仅本地")
        storage_layout.addWidget(self.local_radio)

        layout.addWidget(storage_group)

        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

    def _load_settings(self):
        """加载设置"""
        self.client_id.setText(self.config.get("github.client_id", ""))
        self.client_secret.setText(self.config.get("github.client_secret", ""))
        self.redirect_port.setValue(self.config.get("github.redirect_port", 18080))
        self.ssh_host.setText(self.config.get("ssh.host", ""))
        self.ssh_port.setValue(self.config.get("ssh.port", 22))
        self.ssh_user.setText(self.config.get("ssh.user", ""))

    def _save_settings(self):
        """保存设置"""
        self.config.set("github.client_id", self.client_id.text())
        self.config.set("github.client_secret", self.client_secret.text())
        self.config.set("github.redirect_port", self.redirect_port.value())
        self.config.set("ssh.host", self.ssh_host.text())
        self.config.set("ssh.port", self.ssh_port.value())
        self.config.set("ssh.user", self.ssh_user.text())

        self.config.save()

        QMessageBox.information(self, "成功", "设置已保存")
        logger.info("用户设置已保存")

    def _test_ssh_connection(self):
        """测试 SSH 连接"""
        host = self.ssh_host.text()
        port = self.ssh_port.value()
        user = self.ssh_user.text()

        if not host or not user:
            QMessageBox.warning(self, "提示", "请填写服务器地址和用户名")
            return

        # 测试连接逻辑
        QMessageBox.information(self, "提示", "连接测试功能开发中...")